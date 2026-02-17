import pandas as pd

def clean_and_merge(sales_df, weights_df):
    # Normalize headers again (defensive coding)
    sales_df.columns = sales_df.columns.str.strip().str.lower()
    weights_df.columns = weights_df.columns.str.strip().str.lower()

    # Required columns in lowercase
    required_cols = ['product', 'item', 'quantity', 'date', 'size', 'location']
    available_cols = [c for c in required_cols if c in sales_df.columns]

    if not available_cols:
        raise ValueError(f"None of the required columns found in sales_df. Actual columns: {sales_df.columns.tolist()}")

    # Drop rows missing required fields
    sales_df = sales_df.dropna(subset=available_cols)

    # Merge on product (adjust if needed)
    merged_df = pd.merge(
        sales_df,
        weights_df,
        on='product',
        how='left'
    )

    return merged_df
