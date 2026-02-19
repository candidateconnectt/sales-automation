import requests

url = "https://sales-automation-phi.vercel.app/merge-files/"
sales_file_url = "https://drive.google.com/uc?export=download&id=1csv_UNQcmeLEpbNrDt0Cb9ncJ91veSfM"
weight_file_url = "https://drive.google.com/uc?export=download&id=1oKTzq6X_Ota7JG9ZowLi_fe5tLktfMXs"

response = requests.post(url, data={
    "sales_file_url": sales_file_url,
    "weight_file_url": weight_file_url,
})

if response.status_code == 200:
    with open("final_merged.xlsx", "wb") as f:
        f.write(response.content)
    print(" File saved as final_merged.xlsx")
else:
    print(" Error:", response.status_code, response.text)
