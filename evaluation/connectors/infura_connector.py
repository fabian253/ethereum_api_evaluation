import requests
from typing import Union


class InfuraConnector:

    def __init__(self, infura_ip: str, infura_api_key: str) -> None:
        self.client_ip = infura_ip
        self.api_key = infura_api_key
        self.request_headers = {
            'accept': 'application/json'
        }

    def get_block(self, block_identifier: Union[str, int], full_transactions=False):
        if type(block_identifier) is str:
            method = "eth_getBlockByHash"
        else:
            method = "eth_getBlockByNumber"
            block_identifier = hex(block_identifier)

        json_data = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': method,
            'params': [
                block_identifier,
                full_transactions,
            ]
        }

        response = requests.post(
            f"{self.client_ip}/{self.api_key}", headers=self.request_headers, json=json_data)

        return response.json()

    def get_transaction(self, transaction_hash: str):
        json_data = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': "eth_getTransactionByHash",
            'params': [
                transaction_hash
            ]
        }

        response = requests.post(
            f"{self.client_ip}/{self.api_key}", headers=self.request_headers, json=json_data)

        return response.json()

    def get_block_transaction_count(self, block_identifier: Union[str, int]):
        if type(block_identifier) is str:
            method = "eth_getBlockTransactionCountByHash"
        else:
            method = "eth_getBlockTransactionCountByNumber"
            block_identifier = hex(block_identifier)

        json_data = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': method,
            'params': [
                block_identifier
            ]
        }

        response = requests.post(
            f"{self.client_ip}/{self.api_key}", headers=self.request_headers, json=json_data)

        return response.json()

    def get_wallet_balance(self, wallet_address, block_identifier="latest"):
        # type conveserion for hex
        if type(block_identifier) is int:
            block_identifier = hex(block_identifier)

        json_data = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': "eth_getBalance",
            'params': [
                wallet_address,
                block_identifier
            ]
        }

        response = requests.post(
            f"{self.client_ip}/{self.api_key}", headers=self.request_headers, json=json_data)

        return response.json()
