from fastapi import FastAPI, Form
import pandas as pd
import io
import datetime
import requests
from scripts.utils import clean_and_merge

app = FastAPI(title="Sales Data Automation API")

@app.post("/merge-files/")
async def merge_files(
    sales_file_url: str = Form(...),
    weight_file_url: str = Form(...)
):
    # Download files from provided URLs
    sales_response = requests.get(sales_file_url)
    weight_response = requests.get(weight_file_url)

    # Raise error if download fails
    sales_response.raise_for_status()
    weight_response.raise_for_status()

    # Read Excel files into DataFrames
    sales_df = pd.read_excel(io.BytesIO(sales_response.content), header=1)
    weights_df = pd.read_excel(io.BytesIO(weight_response.content), header=0)

    # Clean, merge, and calculate
    merged_df = clean_and_merge(sales_df, weights_df)

    # Save output with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/final_merged_{timestamp}.xlsx"
    merged_df.to_excel(output_file, index=False)

    return {
        "message": f"Final merged data saved to {output_file}",
        "total_rows": len(merged_df),
        "columns": merged_df.columns.tolist()
    }
