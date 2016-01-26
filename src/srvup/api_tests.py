import requests
import json

base_url = 'http://127.0.0.1:8000/api/'

login_url = base_url + "auth/token/"

videos_url = base_url + "videos/"

data = {
    "username": "labete",
    "password": "123"
}

login_request = requests.post(login_url, data=data)

json_data = login_request.json()


print(json.dumps(json_data, indent=2))
token = json_data["token"]
print(token)

headers = {
    "Authorization": "JWT {0}".format(token),
}

products_request = requests.get(videos_url, headers=headers)
print(products_request.text)
print(json.dumps(products_request.json(), indent=2))
