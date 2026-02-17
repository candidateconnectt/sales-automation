from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io, datetime
from scripts.utils import clean_and_merge
import sys
import os

app = FastAPI(title="Sales Data Automation API")


@app.post("/merge-files/")
async def merge_files(
    sales_file: UploadFile = File(...),
    weight_file: UploadFile = File(...)
):
    # Read uploaded Excel files
    sales_contents = await sales_file.read()
    weight_contents = await weight_file.read()

    sales_df = pd.read_excel(io.BytesIO(sales_contents), header=1)
    weights_df = pd.read_excel(io.BytesIO(weight_contents), header=0)

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
