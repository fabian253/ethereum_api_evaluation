import requests


class EthereumApiConnector:

    def __init__(self, ethereum_api_ip: str, ethereum_api_username: str, ethereum_api_password: str) -> None:
        self.client_ip = ethereum_api_ip
        self.username = ethereum_api_username

        form_data = {
            "grant_type": "password",
            "username": ethereum_api_username,
            "password": ethereum_api_password
        }

        self.access_token = requests.post(
            f"{ethereum_api_ip}/token", data=form_data).json()["access_token"]

        self.request_header = {
            'accept': 'application/json',
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_block(self, block_identifier, full_transactions=False):
        params = {
            'block_identifier': block_identifier,
            'full_transactions': full_transactions,
        }

        response = requests.get(
            f"{self.client_ip}/execution_client/history/get_block", params=params, headers=self.request_header)

        return response.json()

    def get_transaction(self, transaction_hash: str):
        params = {
            'transaction_hash': transaction_hash
        }

        response = requests.get(
            f"{self.client_ip}/execution_client/history/get_transaction", params=params, headers=self.request_header)

        return response.json()

    def get_block_transaction_count(self, block_identifier):
        params = {
            'block_identifier': block_identifier
        }

        response = requests.get(
            f"{self.client_ip}/execution_client/history/get_block_transaction_count", params=params, headers=self.request_header)

        return response.json()

    def get_wallet_balance(self, wallet_address, block_identifier):
        params = {
            "wallet_address": wallet_address,
            'block_identifier': block_identifier
        }

        response = requests.get(
            f"{self.client_ip}/execution_client/state/get_balance", params=params, headers=self.request_header)

        return response.json()
