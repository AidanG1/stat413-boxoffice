import os

assert os.path.basename(os.getcwd()) == "stat413-boxoffice"

# read the data from data_link.txt
with open("data_link.txt", "r") as f:
    data_link = f.read().strip()

# download the data
import requests
import time

print(f"downloading boxoffice data from {data_link}")

start_time = time.time()

response = requests.get(data_link)

# check if the request was successful
assert response.status_code == 200

# print the size of the response
print(f"data size: {len(response.content)}")
print(f"download time: {time.time() - start_time} seconds")

# now place that response in boxoffice/db/data/data.sqlite
with open("boxoffice/db/data/data.sqlite", "wb") as f:
    f.write(response.content)

print("data downloaded successfully, saved to boxoffice/db/data/data.sqlite")
