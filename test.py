import requests

url = "https://sales-automation-lkoj.vercel.app/merge-files/"
payload = {
    "sales_file_url": "https://drive.google.com/uc?export=download&id=1csv_UNQcmeLEpbNrDt0Cb9ncJ91veSfM",
    "weight_file_url": "https://drive.google.com/uc?export=download&id=1oKTzq6X_Ota7JG9ZowLi_fe5tLktfMXs"
}
response = requests.post(url, json=payload)
print(response.status_code)
print(response.text)
