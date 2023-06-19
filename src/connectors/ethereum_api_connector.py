import requests
from typing import Union


class EthereumApiConnector:

    def __init__(self, ethereum_api_url: str, ethereum_api_username: str, ethereum_api_password: str) -> None:
        self.client_url = ethereum_api_url
        self.username = ethereum_api_username

        form_data = {
            "grant_type": "password",
            "username": ethereum_api_username,
            "password": ethereum_api_password
        }

        self.access_token = requests.post(
            f"{ethereum_api_url}/auth/token", data=form_data).json()["access_token"]

        self.request_header = {
            'accept': 'application/json',
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_block(self, block_identifier: Union[int, str], full_transactions=False):
        params = {
            'block_identifier': block_identifier,
            'full_transactions': full_transactions,
        }

        response = requests.get(
            f"{self.client_url}/mainnet/history/block", params=params, headers=self.request_header)

        return response.json()

    def get_transaction(self, transaction_hash: str):
        params = {
            'transaction_hash': transaction_hash
        }

        response = requests.get(
            f"{self.client_url}/mainnet/history/transaction", params=params, headers=self.request_header)

        return response.json()

    def get_block_transaction_count(self, block_identifier):
        params = {
            'block_identifier': block_identifier
        }

        response = requests.get(
            f"{self.client_url}/mainnet/history/block_transaction_count", params=params, headers=self.request_header)

        return response.json()

    def get_wallet_balance(self, wallet_address: str, block_identifier: Union[int, str, None] = None):
        params = {
            "wallet_address": wallet_address,
        }
        if block_identifier is not None:
            params["block_identifier"] = block_identifier

        response = requests.get(
            f"{self.client_url}/mainnet/state/balance", params=params, headers=self.request_header)

        return response.json()

    def get_contract_transfers(self,
                               contract_address: str,
                               from_block: Union[int, str] = 0,
                               to_block: Union[int, str] = "latest",
                               from_address: Union[str, None] = None,
                               to_address: Union[str, None] = None,
                               value: Union[int, None] = None,
                               token_id: Union[int, None] = None):
        params = {
            "contract_address": contract_address,
            "from_block": from_block,
            "to_block": to_block
        }
        if from_address is not None:
            params["from_address"] = from_address
        if to_address is not None:
            params["to_address"] = to_address
        if value is not None:
            params["value"] = value
        if token_id is not None:
            params["token_id"] = token_id

        response = requests.get(
            f"{self.client_url}/mainnet/contract/transfers", params=params, headers=self.request_header)

        return response.json()

    def get_contract_address_list(self,
                                  token_standard: Union[str, None] = None,
                                  with_name: bool = False,
                                  with_symbol: bool = False,
                                  with_block_deployed: bool = False,
                                  with_total_supply: bool = False,
                                  with_abi: bool = False,
                                  limit: Union[int, None] = None):
        params = {
            "with_name": with_name,
            "with_symbol": with_symbol,
            "with_block_deployed": with_block_deployed,
            "with_total_supply": with_total_supply,
            "with_abi": with_abi
        }
        if token_standard is not None:
            params["token_standard"] = token_standard
        if limit is not None:
            params["limit"] = limit

        response = requests.get(
            f"{self.client_url}/mainnet/contract/list", params=params, headers=self.request_header)

        return response.json()

    def get_contract_deploy_block(self, contract_address: str):
        params = {
            "contract_address": contract_address
        }

        response = requests.get(
            f"{self.client_url}/mainnet/contract/deploy_block", params=params, headers=self.request_header, timeout=(5, 60))

        return response.json()
