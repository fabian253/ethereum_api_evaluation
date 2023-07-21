import requests
from typing import Union
import json

url = "http://134.155.111.231:8000"
user = "admin"
password = "admin"


def authenticate(url: str, user: str, password: str):
    form_data = {
        "grant_type": "password",
        "username": user,
        "password": password
    }

    access_token = requests.post(
        f"{url}/auth/token", data=form_data).json()["access_token"]

    request_header = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    return access_token, request_header


def get_block(url: str, request_header: dict,  block_identifier: Union[int, str], full_transactions=False):
    params = {
        "block_identifier": block_identifier,
        "full_transactions": full_transactions,
    }

    response = requests.get(
        f"{url}/mainnet/history/block", params=params, headers=request_header)

    return response.json()


def get_contract_metadata(url: str, request_header: dict, contract_address: str):
    params = {
        "contract_address": contract_address
    }

    response = requests.get(
        f"{url}/mainnet/contract/metadata", params=params, headers=request_header)

    return response.json()


if __name__ == "__main__":
    access_token, request_header = authenticate(url, user, password)

    # block = get_block(url, request_header, "latest", False)

    with open("src/dataset/dao_contract_list.json", "r") as f:
        contracts = json.load(f)

    metadata = []

    for contract in contracts:
        contract_metadata = get_contract_metadata(
            url, request_header, contract)

        metadata.append(contract_metadata)

    with open("src/dataset/dao_contract_list.json", "w") as f:
        json.dump(metadata, f, indent=4)
