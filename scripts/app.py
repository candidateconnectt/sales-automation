from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
import pandas as pd, io, datetime, requests

app = FastAPI(title="Sales Data Automation API")

def convert_drive_link(link: str) -> str:
    if "file/d/" in link:
        file_id = link.split("file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return link

def sanitize_url(url: str) -> str:
    return url.replace("string", "").strip()

def read_csv_response(response, header_row=0):
    preview = response.content[:200].decode(errors="ignore")
    if "<html" in preview.lower():
        raise ValueError("Got HTML instead of CSV. Check Google Drive link permissions.")
    return pd.read_csv(io.BytesIO(response.content), header=header_row, low_memory=False)

def clean_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    cols = ['Product', 'Size', 'Item', 'Quantity', 'Location', 'Date']
    sales_df = sales_df[cols].copy().drop_duplicates()
    sales_df = sales_df.dropna(subset=['Size', 'Location'])
    sales_df['Quantity'] = pd.to_numeric(sales_df['Quantity'], errors='coerce')
    sales_df = sales_df[sales_df['Quantity'].notna()]
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')
    return sales_df[sales_df['Date'].notna()]

def clean_weights_data(weights_df: pd.DataFrame) -> pd.DataFrame:
    return weights_df[['Product', 'Weight of Indv. Product (lb)']].copy()

def merge_and_calculate(sales_df: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
    merged = pd.merge(sales_df, weights_df, on='Product', how='left')
    merged['Total Weight (lb)'] = merged['Quantity'] * merged['Weight of Indv. Product (lb)']
    merged['Total Weight (tons)'] = merged['Total Weight (lb)'] / 2000
    merged = merged.sort_values(by=['Date', 'Product', 'Item'], ascending=[False, True, True])
    return merged[['Product', 'Size', 'Item', 'Quantity', 'Location', 'Date',
                   'Weight of Indv. Product (lb)', 'Total Weight (lb)', 'Total Weight (tons)']]

@app.post("/merge-files/")
async def merge_files(sales_file_url: str = Form(...), weight_file_url: str = Form(...)):
    sales_url = sanitize_url(convert_drive_link(sales_file_url))
    weight_url = sanitize_url(convert_drive_link(weight_file_url))

    sales_resp = requests.get(sales_url)
    weight_resp = requests.get(weight_url)
    sales_resp.raise_for_status()
    weight_resp.raise_for_status()

    sales_df = read_csv_response(sales_resp, header_row=1)
    weights_df = read_csv_response(weight_resp, header_row=0)

    sales_df = clean_sales_data(sales_df)
    weights_df = clean_weights_data(weights_df)
    merged_df = merge_and_calculate(sales_df, weights_df)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        merged_df.to_excel(writer, sheet_name="SalesData", startrow=7, index=False)
        workbook, worksheet = writer.book, writer.sheets["SalesData"]

        data_start = 8
        last_row = len(merged_df) + 7

        worksheet.write("A1", "Sales Data Filters")
        worksheet.write("A3", "From Date")
        worksheet.write("A4", "To Date")
        worksheet.write("A5", "Location")

        worksheet.write_formula("B3", f"=F{data_start}")
        worksheet.write_formula("B4", f"=F{data_start}")
        worksheet.write_formula("B5", f"=E{data_start}")

        worksheet.data_validation("B5", {
            "validate": "list",
            "source": f"=$E${data_start}:$E${last_row}"
        })

        helper_col = merged_df.shape[1]
        worksheet.write(data_start-1, helper_col, "Include?")
        for i in range(len(merged_df)):
            r = i + data_start
            worksheet.write_formula(r-1, helper_col,
                                    f'=AND($F{r}>=B3,$F{r}<=B4,$E{r}=B5)')

        worksheet.autofilter(data_start-1, 0, last_row, helper_col)
        worksheet.freeze_panes(data_start, 0)

    buffer.seek(0)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=final_merged_{ts}.xlsx"}
    )
