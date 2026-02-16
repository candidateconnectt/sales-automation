import pandas as pd

def clean_and_merge(sales_df, weights_df):
    sales_df = sales_df[['Product', 'Size', 'Item', 'Quantity', 'Location', 'Date']]
    weights_df = weights_df[['Product', 'Weight of Indv. Product (lb)']]

    sales_df = sales_df.drop_duplicates()
    sales_df = sales_df.dropna(subset=['Product', 'Item', 'Quantity', 'Date'])
    sales_df['Quantity'] = pd.to_numeric(sales_df['Quantity'], errors='coerce')
    sales_df = sales_df.dropna(subset=['Quantity'])
    sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')

    merged_df = pd.merge(sales_df, weights_df, on='Product', how='left')
    merged_df['Total Weight (lb)'] = merged_df['Quantity'] * merged_df['Weight of Indv. Product (lb)']
    merged_df['Total Weight (tons)'] = merged_df['Total Weight (lb)'] / 2000

    merged_df = merged_df.sort_values(by=['Date', 'Product', 'Item'], ascending=[False, True, True])
    merged_df = merged_df.dropna()  # eliminate null rows

    return merged_df
