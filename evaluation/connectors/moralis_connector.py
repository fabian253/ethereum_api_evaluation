import requests


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
            transactions = [transaction["hash"]
                            for transaction in response["transactions"]]

            response["transactions"] = transactions

        return response

    def get_transaction(self, transaction_hash: str, with_logs: bool = False, with_internal_transactions: bool = False):
        params = {
            'chain': 'eth',
            'include': 'internal_transactions'
        }

        response = requests.get(
            f"{self.client_ip}/transaction/{transaction_hash}", params=params, headers=self.request_headers).json()

        del response["logs"]
        del response["internal_transactions"]
        
        return response

    def get_block_transaction_count(self, block_identifier):
        response = self.get_block(block_identifier)

        transaction_count = response["transaction_count"]

        return {"transaction_count": transaction_count}
