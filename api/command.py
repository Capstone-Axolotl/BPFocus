import requests

ip_address = input("Client IP: ")
command = input("Command: ")

url = f"http://{ip_address}:5000/execute"
payload = {
    "command": command
}

response = requests.post(url, json=payload)

print("Status Code:", response.status_code)
print("Response:")
print(response.text)

