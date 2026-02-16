from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io, os, datetime

app = FastAPI(title="Sales Data Automation API")

@app.post("/merge-files/")
async def merge_files(
    sales_file: UploadFile = File(...),
    weight_file: UploadFile = File(...)
):
    # -------------------------
    # 1. Read both files with correct headers
    # -------------------------
    sales_contents = await sales_file.read()
    weight_contents = await weight_file.read()

    sales_df = pd.read_excel(io.BytesIO(sales_contents), header=1)
    weights_df = pd.read_excel(io.BytesIO(weight_contents), header=0)

    # -------------------------
    # 2. Keep Only Required Columns
    # -------------------------
    sales_columns = ['Product', 'Size', 'Item', 'Quantity', 'Location', 'Date']
    weights_columns = ['Product', 'Weight of Indv. Product (lb)']

    sales_df = sales_df[[col for col in sales_columns if col in sales_df.columns]]
    weights_df = weights_df[[col for col in weights_columns if col in weights_df.columns]]

    # -------------------------
    # 3. Clean Sales Data
    # -------------------------
    sales_df = sales_df.drop_duplicates()
    #  Drop nulls from ALL critical columns including Size + Location
    sales_df = sales_df.dropna(subset=['Product', 'Item', 'Quantity', 'Date', 'Location', 'Size'])
    sales_df['Quantity'] = pd.to_numeric(sales_df['Quantity'], errors='coerce')
    sales_df = sales_df.dropna(subset=['Quantity'])
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')
    sales_df = sales_df.dropna(subset=['Date'])

    # -------------------------
    # 4. Merge Sales with Weights
    # -------------------------
    merged_df = pd.merge(
        sales_df,
        weights_df,
        on='Product',
        how='left'
    )

    # -------------------------
    # 5. Calculate Totals
    # -------------------------
    merged_df['Total Weight (lb)'] = merged_df['Quantity'] * merged_df['Weight of Indv. Product (lb)']
    merged_df['Total Weight (tons)'] = merged_df['Total Weight (lb)'] / 2000

    # -------------------------
    # 6. Sort Data Professionally
    # -------------------------
    merged_df = merged_df.sort_values(by=['Date', 'Product', 'Item'], ascending=[False, True, True])

    # -------------------------
    # 7. Save Final Output
    # -------------------------
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/final_merged_{timestamp}.xlsx"
    merged_df.to_excel(output_file, index=False)

    return {
        "message": f"Final merged data saved to {output_file}",
        "total_rows": len(merged_df)
    }
