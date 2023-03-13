import requests
from typing import Union


class MoralisConnector:

    def __init__(self, moralis_ip: str, moralis_api_key: str) -> None:
        self.client_ip = moralis_ip
        self.api_key = moralis_api_key
        self.request_headers = {
            'accept': 'application/json',
            'X-API-Key': moralis_api_key,
        }

    def get_block(self, block_identifier, full_transactions=False):
        params = {
            'chain': 'eth',
            'include': 'internal_transactions'
        }

        response = requests.get(
            f"{self.client_ip}/block/{block_identifier}", params=params, headers=self.request_headers)

        response = response.json()

        if not full_transactions:
            if len(response["transactions"]) != 0:
                transactions = [transaction["hash"]
                                for transaction in response["transactions"]]
            else:
                transactions = []

            response["transactions"] = transactions

        return response

    def get_transaction(self, transaction_hash: str, with_logs: bool = False, with_internal_transactions: bool = False):
        params = {
            'chain': 'eth',
            'include': 'internal_transactions'
        }

        response = requests.get(
            f"{self.client_ip}/transaction/{transaction_hash}", params=params, headers=self.request_headers).json()

        if not with_logs:
            del response["logs"]

        if not with_internal_transactions:
            del response["internal_transactions"]

        return response

    def get_block_transaction_count(self, block_identifier):
        response = self.get_block(block_identifier)

        transaction_count = response["transaction_count"]

        return {"transaction_count": transaction_count}

    def get_wallet_balance(self, wallet_address, block_identifier: Union[int, str] = None):
        params = {
            'chain': 'eth'
        }

        if block_identifier is not None and type(block_identifier) is not str:
            params["to_block"] = block_identifier

        response = requests.get(
            f"{self.client_ip}/{wallet_address}/balance", params=params, headers=self.request_headers).json()

        return response
