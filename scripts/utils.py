import pandas as pd


def clean_and_merge(sales_df: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
    """Clean sales and weights data, then merge and calculate totals."""

    # Keep required columns safely
    sales_columns = ['Product', 'Size', 'Item', 'Quantity', 'Location', 'Date']
    weights_columns = ['Product', 'Weight of Indv. Product (lb)']

    sales_df = sales_df[[col for col in sales_columns if col in sales_df.columns]].copy()
    weights_df = weights_df[[col for col in weights_columns if col in weights_df.columns]].copy()

    # Clean sales data (drop rows with nulls in critical fields)
    sales_df = sales_df.drop_duplicates()
    sales_df = sales_df.dropna(subset=['Product', 'Item', 'Quantity', 'Date', 'Size', 'Location'])
    sales_df['Quantity'] = pd.to_numeric(sales_df['Quantity'], errors='coerce')
    sales_df = sales_df.dropna(subset=['Quantity'])
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')
    sales_df = sales_df.dropna(subset=['Date'])

    # Merge with weights
    merged_df = pd.merge(sales_df, weights_df, on='Product', how='left')

    # Calculate totals
    merged_df['Total Weight (lb)'] = (
        merged_df['Quantity'] * merged_df['Weight of Indv. Product (lb)']
    )
    merged_df['Total Weight (tons)'] = merged_df['Total Weight (lb)'] / 2000

    # Sort professionally
    merged_df = merged_df.sort_values(
        by=['Date', 'Product', 'Item'], ascending=[False, True, True]
    )

    return merged_df
