import requests

url = "https://sales-automation-phi.vercel.app/merge-files/"

sales_file_url = "https://drive.google.com/uc?export=download&id=1csv_UNQcmeLEpbNrDt0Cb9ncJ91veSfM"
weight_file_url = "https://drive.google.com/uc?export=download&id=1oKTzq6X_Ota7JG9ZowLi_fe5tLktfMXs"

response = requests.post(
    url,
    data={
        "sales_file_url": sales_file_url,
        "weight_file_url": weight_file_url,
    }
)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
