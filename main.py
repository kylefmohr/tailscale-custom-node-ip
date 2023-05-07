import requests
import json
import os
import time
import ipaddress

HOSTNAME_TO_CHANGE = "KylesMacbook"  # typically the hostname of the computer this program is running on
TAILNET_NAME = "kylefmohr@gmail.com"  # I sign in with Google, so my tailnet name is my full gmail address
TAILSCALE_API_KEY = "tskey-api-<REDACTED>"  # click "Generate access token" on this page: https://login.tailscale.com/admin/settings/keys
TAILSCALE_REUSABLE_AUTH_KEY = "tskey-auth-<REDACTED>"  # click "Generate auth key", then *CHECK REUSABLE*, all other settings can be default: https://login.tailscale.com/admin/settings/keys
DESIRED_IP_PREFIXES = ["100.100", "100.69"]  # expects a list of IP Prefixes to search for, meaning the first two octets of the IPv4. Must be within the Tailscale subnet of 100.64.0.0/10

# optional
API_DELAY = 2.5  # seconds, multiply by how many hosts you're running this on concurrently

for ip in DESIRED_IP_PREFIXES:
    #  Verify that the IP addresses are in the 100.64.0.0/10 range.
    required_subnet = ipaddress.ip_network("100.64.0.0/10")
    desired_ip = None
    for ip_prefix in DESIRED_IP_PREFIXES:
        if ip_prefix.count(".") == 1:
            desired_ip = ip_prefix + ".0.0"
        elif ip_prefix.count(".") == 2:
            desired_ip = ip_prefix + ".0"
        elif ip_prefix.count(".") == 3:
            desired_ip = ip_prefix
        else:
            assert "Invalid entry for DESIRED_IP_PREFIXES"
        assert ipaddress.ip_address(desired_ip) in required_subnet, "IP address " + ip + " is not in the TailScale subnet (100.64.0.0/10)"


base_url = "https://api.tailscale.com/api/v2/"
headers = {"Authorization": "Bearer " + TAILSCALE_API_KEY}

def get_device_id(hostname):
    response = requests.get(base_url + "tailnet/" + TAILNET_NAME + "/devices", headers=headers)
    devices = json.loads(response.text)
    devices = devices["devices"]
    device_id = ""
    for device in devices:
        if device["hostname"] == hostname:
            device_id = device["id"]
            break
    return device_id


def remove_device_by_id(device_id):
    response = requests.delete(base_url + "device/" + device_id, headers=headers)
    return response.status_code


def rejoin_tailnet(auth_key):
    command = "tailscale up --reset --authkey=" + auth_key + " --hostname=" + HOSTNAME_TO_CHANGE + " --advertise-exit-node=true --force-reauth>/dev/null 2>&1"
    os.system(command)


def get_device_ip(hostname):
    response = requests.get(base_url + "tailnet/" + TAILNET_NAME + "/devices", headers=headers)
    devices = json.loads(response.text)
    devices = devices["devices"]
    device_ip = ""
    for device in devices:
        if device["hostname"] == hostname:
            device_ip = device["addresses"][0]
            break
    return device_ip


def change_ip():
    device_id = get_device_id(HOSTNAME_TO_CHANGE)
    remove_device_by_id(device_id)

    rejoin_tailnet(TAILSCALE_REUSABLE_AUTH_KEY)
    device_ip = get_device_ip(HOSTNAME_TO_CHANGE)
    print(device_ip)
    time.sleep(2.5)
    return device_ip


def ip_found():
    device_ip = get_device_ip(HOSTNAME_TO_CHANGE)
    device_ip_prefix = device_ip.split(".")[0] + "." + device_ip.split(".")[1]
    if device_ip_prefix in DESIRED_IP_PREFIXES:
        print("IP found: " + device_ip)
        return True
    else:
        return False


if __name__ == "__main__":
    while not ip_found():
        change_ip()
        time.sleep(API_DELAY)