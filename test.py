import requests

url = "http://127.0.0.1:8000/merge-files/"
payload = {
    "sales_file_url": "https://drive.google.com/uc?export=download&id=1csv_UNQcmeLEpbNrDt0Cb9ncJ91veSfM",
    "weight_file_url": "https://drive.google.com/uc?export=download&id=1oKTzq6X_Ota7JG9ZowLi_fe5tLktfMXs"
}
response = requests.post(url, data=payload)
print(response.status_code)
print(response.text)
