import requests

# Your deployed FastAPI endpoint
url = "https://sales-automation-lkoj.vercel.app/merge-files/"   # use local server
# Or if deployed: url = "https://sales-automation-lkoj.vercel.app/merge-files/"

# Example Google Drive direct download links
sales_file_url = "https://drive.google.com/uc?export=download&id=1csv_UNQcmeLEpbNrDt0Cb9ncJ91veSfM"
weight_file_url = "https://drive.google.com/uc?export=download&id=1oKTzq6X_Ota7JG9ZowLi_fe5tLktfMXs"

# Send POST request with form data
response = requests.post(
    url,
    data={
        "sales_file_url": sales_file_url,
        "weight_file_url": weight_file_url,
    }
)

# Print results
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
