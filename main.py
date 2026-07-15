import requests


def get_outages(bill_id, from_date, to_date):

    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IntcIlVzZXJJcFwiOm51bGwsXCJVc2VySWRcIjoxNjMzMzQ3NyxcIlNlc3Npb25LZXlcIjpudWxsfSIsImV4cCI6MTc5OTk3MTUzNywiaWF0IjoxNzg0MDczOTM3LCJuYmYiOjE3ODQwNzM5Mzd9.1sP_FB2FfkfPUVAcax8bUdKdyVd5-80E3j13NUMCC7I"

    url = 'https://uiapi2.saapa.ir/api/ebills/PlannedBlackoutsReport'

    Headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    json_p = {"bill_id": bill_id, "from_date": from_date, "to_date": to_date}
    o = requests.post(url, headers=Headers, json=json_p)

    return o.json()["data"]

outages = get_outages("1465176505229", "1405/04/24", "1405/04/29")
print(outages)
