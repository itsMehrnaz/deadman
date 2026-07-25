import requests
import jdatetime
import subprocess
import time

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IntcIlVzZXJJcFwiOm51bGwsXCJVc2VySWRcIjoxNjMzMzQ3NyxcIlNlc3Npb25LZXlcIjpudWxsfSIsImV4cCI6MTc5OTk3MTUzNywiaWF0IjoxNzg0MDczOTM3LCJuYmYiOjE3ODQwNzM5Mzd9.1sP_FB2FfkfPUVAcax8bUdKdyVd5-80E3j13NUMCC7I"  
KEYWORD = "بعثت 10"

def get_outages(bill_id, from_date, to_date):
    url = 'https://uiapi2.saapa.ir/api/ebills/PlannedBlackoutsReport'

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    json_p = {"bill_id": bill_id, "from_date": from_date, "to_date": to_date}

    o = requests.post(url, json=json_p, headers=headers, proxies={"http": None, "https": None})

    data = o.json()["data"]

    my_outages = [item for item in data if KEYWORD in item["outage_address"]]

    return my_outages


outages = get_outages("1465176505229", "1405/04/24", "1405/04/29")

print(outages)



def check_shutdown(outages):
    now = jdatetime.datetime.now()
    today = jdatetime.date.today()
    for outage in outages:
        if (str(outage["outage_date"]) == str(today)):
                now_minuts = int(now.hour * 60 + now.minute)
                start_time = outage["outage_time"]
                start_time_minutes = start_time.split(":")
                start_time = int(start_time_minutes[0]) * 60 + int(start_time_minutes[1])
                print(now_minuts)   
                print(start_time)   
                diff = start_time - now_minuts
                print(diff) 
                if (diff <= 10 and diff > 0):
                     print("shutdown")
                     ###subprocess.run(["shutdown", "-h", "now"])

    return "ok"

check_shutdown(outages)


i = 0

while True:
     check_shutdown(outages)
     time.sleep(60)

     i = i + 1

     if i == 60:
          outages = get_outages("1465176505229", "1405/04/24", "1405/04/29")
          i = 0
          print("still working")     
    
     