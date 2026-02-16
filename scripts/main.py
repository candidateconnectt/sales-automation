import pandas as pd
import os

# -------------------------
# 1. File Paths
# -------------------------
sales_file = "Input/Project 1 - Input a- Sales Data Sample File.xlsx"
weights_file = "Input/Project 1 - Input b- Weight Reference File.xlsx"
output_file = "output/final_merged.xlsx"

# -------------------------
# 2. Load Input Files
# -------------------------
sales_df = pd.read_excel(sales_file, header=1)
weights_df = pd.read_excel(weights_file, header=0)

print("Sales rows:", len(sales_df))
print("Weights rows:", len(weights_df))
print("Sales columns:", sales_df.columns.tolist())
print("Weights columns:", weights_df.columns.tolist())

# -------------------------
# 3. Keep Only Required Columns
# -------------------------
sales_columns = ['Product', 'Size', 'Item', 'Quantity', 'Location', 'Date']
sales_df = sales_df[sales_columns]

weights_columns = ['Product', 'Weight of Indv. Product (lb)']
weights_df = weights_df[weights_columns]

# -------------------------
# 4. Clean Sales Data
# -------------------------
sales_df = sales_df.drop_duplicates()
sales_df = sales_df.dropna(subset=['Product', 'Item', 'Quantity', 'Date'])
sales_df['Quantity'] = pd.to_numeric(sales_df['Quantity'], errors='coerce')
sales_df = sales_df.dropna(subset=['Quantity'])
sales_df['Date'] = pd.to_datetime(sales_df['Date'], errors='coerce')

# -------------------------
# 5. Merge Sales with Weights
# -------------------------
merged_df = pd.merge(
    sales_df,
    weights_df,
    on='Product',
    how='left'
)

# -------------------------
# 6. Calculate Total Weight per row
# -------------------------
merged_df['Total Weight (lb)'] = merged_df['Quantity'] * merged_df['Weight of Indv. Product (lb)']
merged_df['Total Weight (tons)'] = merged_df['Total Weight (lb)'] / 2000

# -------------------------
# 7. Sort Data Professionally
# -------------------------
merged_df = merged_df.sort_values(by=['Date', 'Product', 'Item'], ascending=[False, True, True])

# -------------------------
# 8. Save Final Output
# -------------------------
os.makedirs("output", exist_ok=True)
merged_df.to_excel(output_file, index=False)
print(f" Final merged data saved to {output_file}")
