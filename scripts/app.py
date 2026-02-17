from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd, io, datetime, requests
from scripts.utils import clean_and_merge

app = FastAPI(title="Sales Data Automation API")

class FileURLs(BaseModel):
    sales_file_url: str
    weight_file_url: str

@app.post("/merge-files/")
async def merge_files(payload: FileURLs):
    sales_response = requests.get(payload.sales_file_url)
    weight_response = requests.get(payload.weight_file_url)

    sales_response.raise_for_status()
    weight_response.raise_for_status()

    sales_df = pd.read_csv(io.BytesIO(sales_response.content))  # CSV
    weights_df = pd.read_csv(io.BytesIO(weight_response.content))

    merged_df = clean_and_merge(sales_df, weights_df)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/final_merged_{timestamp}.csv"
    merged_df.to_csv(output_file, index=False)

    return {
        "message": f"Final merged data saved to {output_file}",
        "total_rows": len(merged_df),
        "columns": merged_df.columns.tolist()
    }
