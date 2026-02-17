from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
import pandas as pd, io, datetime, requests

app = FastAPI(title="Sales Data Automation API")

def convert_drive_link(link: str) -> str:
    """Convert Google Drive share link to direct download link."""
    if "file/d/" in link:
        file_id = link.split("file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return link

def sanitize_url(url: str) -> str:
    """Remove accidental prefixes like 'string' and ensure proper formatting."""
    return url.replace("string", "").strip()

def read_csv_response(response, header_row=0):
    text_preview = response.content[:200].decode(errors="ignore")
    if "<html" in text_preview.lower():
        raise ValueError("Got HTML instead of CSV. Check your Google Drive link permissions.")
    return pd.read_csv(io.BytesIO(response.content), header=header_row, low_memory=False)

def clean_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ['Product', 'Size', 'Item', 'Quantity', 'Location', 'Date']
    sales_df = sales_df[required_columns].copy()
    sales_df = sales_df.drop_duplicates()
    sales_df = sales_df.dropna(subset=['Size', 'Location'])
    sales_df['Quantity'] = pd.to_numeric(sales_df['Quantity'], errors='coerce')
    sales_df = sales_df[sales_df['Quantity'].notna()]
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')
    sales_df = sales_df[sales_df['Date'].notna()]
    return sales_df

def clean_weights_data(weights_df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ['Product', 'Weight of Indv. Product (lb)']
    return weights_df[required_columns].copy()

def merge_and_calculate(sales_df: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
    merged_df = pd.merge(sales_df, weights_df, on='Product', how='left')
    merged_df['Total Weight (lb)'] = merged_df['Quantity'] * merged_df['Weight of Indv. Product (lb)']
    merged_df['Total Weight (tons)'] = merged_df['Total Weight (lb)'] / 2000
    merged_df = merged_df.sort_values(by=['Date', 'Product', 'Item'], ascending=[False, True, True])
    output_columns = [
        'Product', 'Size', 'Item', 'Quantity', 'Location', 'Date',
        'Weight of Indv. Product (lb)', 'Total Weight (lb)', 'Total Weight (tons)'
    ]
    return merged_df[output_columns]

@app.post("/merge-files/")
async def merge_files(sales_file_url: str = Form(...), weight_file_url: str = Form(...)):
    # Convert and sanitize links
    sales_url = sanitize_url(convert_drive_link(sales_file_url))
    weight_url = sanitize_url(convert_drive_link(weight_file_url))

    # Download
    sales_response = requests.get(sales_url)
    weight_response = requests.get(weight_url)
    sales_response.raise_for_status()
    weight_response.raise_for_status()

    # Parse CSVs
    sales_df = read_csv_response(sales_response, header_row=1)
    weights_df = read_csv_response(weight_response, header_row=0)

    # Clean + merge
    sales_df = clean_sales_data(sales_df)
    weights_df = clean_weights_data(weights_df)
    merged_df = merge_and_calculate(sales_df, weights_df)

    # Save to in-memory buffer
    buffer = io.BytesIO()
    merged_df.to_excel(buffer, index=False)
    buffer.seek(0)

    # Return as downloadable file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=final_merged_{timestamp}.xlsx"}
    )
