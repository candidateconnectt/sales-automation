import requests

# Your deployed FastAPI endpoint
url = "https://sales-automation-lkoj.vercel.app/merge-files/"

# Direct download links for your files
sales_file_url = "https://drive.google.com/uc?export=download&id=1csv_UNQcmeLEpbNrDt0Cb9ncJ91veSfM"
weight_file_url = "https://drive.google.com/uc?export=download&id=1oKTzq6X_Ota7JG9ZowLi_fe5tLktfMXs"

# If your FastAPI endpoint expects JSON (BaseModel version)
payload = {
    "sales_file_url": sales_file_url,
    "weight_file_url": weight_file_url
}

response = requests.post(url, json=payload)

print("Status code:", response.status_code)
print("Response:", response.text)
