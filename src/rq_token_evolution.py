from connectors.ethereum_api_connector import EthereumApiConnector
import config
import json

ethereum_api_connector = EthereumApiConnector(
    config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)

if __name__ == "__main__":
    contract_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"

    response = ethereum_api_connector.get_erc721_token_transfers(
        contract_address, token_id=8000)

    with open("src/research_question_evaluation/token_evolution.json", "w") as f:
        json.dump(response, f, indent=4)
