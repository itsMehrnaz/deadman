import requests
import jdatetime
import subprocess
import time
from datetime import timedelta
import os

def load_token():
    with open(".env") as f:
        for line in f:
            if line.startswith("TOKEN="):
                return line.strip().split("=", 1)[1]

TOKEN = load_token()

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





today = jdatetime.date.today()
formatted_today = today.strftime("%Y/%m/%d")

end = today + timedelta(days=3)
formatted_end = end.strftime("%Y/%m/%d")


def check_shutdown(outages):
    now = jdatetime.datetime.now()
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
                if 0 < diff <= 5:
                    subprocess.run(["systemctl", "poweroff", "-i"])
                    return "shutdown"
                elif 5 < diff <= 15:
                    subprocess.run(["notify-send", "shutdown alert!!", "There's only few minutes to shutdown! save your work!"])

    return "ok"

outages = get_outages("1465176505229", formatted_today, formatted_end)
print(outages)

check_shutdown(outages)


i = 0

try:
    while True:
        check_shutdown(outages)
        time.sleep(60)

        i = i + 1

        if i == 60:
            try:
                outages = get_outages("1465176505229", formatted_today, formatted_end)
            except Exception as e:
                print("i had problem to fetch data, i'll try again:", e)
            i = 0
            print("still working")     
except KeyboardInterrupt:
    print("Program terminated by user.")    

     