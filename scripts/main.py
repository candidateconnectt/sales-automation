import os
import pandas as pd


def load_data(sales_file: str, weights_file: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load sales and weights data from Excel files."""
    sales_df = pd.read_excel(sales_file, header=1)
    weights_df = pd.read_excel(weights_file, header=0)
    return sales_df, weights_df


def clean_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare sales data for merging."""
    required_columns = ['Product', 'Size', 'Item', 'Quantity', 'Location', 'Date']
    sales_df = sales_df[required_columns].copy()

    # Drop duplicates and rows missing critical fields (including Size + Location)
    sales_df = sales_df.drop_duplicates()
    sales_df = sales_df.dropna(subset=['Product', 'Item', 'Quantity', 'Date', 'Size', 'Location'])

    # Ensure numeric Quantity and valid Date
    sales_df['Quantity'] = pd.to_numeric(sales_df['Quantity'], errors='coerce')
    sales_df = sales_df.dropna(subset=['Quantity'])
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')
    sales_df = sales_df.dropna(subset=['Date'])

    return sales_df


def clean_weights_data(weights_df: pd.DataFrame) -> pd.DataFrame:
    """Keep only relevant columns in weights data."""
    required_columns = ['Product', 'Weight of Indv. Product (lb)']
    return weights_df[required_columns].copy()


def merge_and_calculate(sales_df: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
    """Merge sales with weights and calculate total weight."""
    merged_df = pd.merge(sales_df, weights_df, on='Product', how='left')

    # Calculate weights
    merged_df['Total Weight (lb)'] = (
        merged_df['Quantity'] * merged_df['Weight of Indv. Product (lb)']
    )
    merged_df['Total Weight (tons)'] = merged_df['Total Weight (lb)'] / 2000

    # Sort professionally
    merged_df = merged_df.sort_values(
        by=['Date', 'Product', 'Item'], ascending=[False, True, True]
    )

    return merged_df


def save_output(df: pd.DataFrame, output_file: str) -> None:
    """Save the final merged DataFrame to Excel."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_excel(output_file, index=False)
    print(f"Final merged data saved to {output_file}")


def main():
    # File paths
    sales_file = "input/Project 1 - Input a- Sales Data Sample File.xlsx"
    weights_file = "input/Project 1 - Input b- Weight Reference File.xlsx"
    output_file = "output/final_merged.xlsx"

    # Pipeline
    sales_df, weights_df = load_data(sales_file, weights_file)
    sales_df = clean_sales_data(sales_df)
    weights_df = clean_weights_data(weights_df)
    merged_df = merge_and_calculate(sales_df, weights_df)
    save_output(merged_df, output_file)


if __name__ == "__main__":
    main()
