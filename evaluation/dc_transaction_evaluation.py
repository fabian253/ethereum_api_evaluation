from connectors.etherscan_connector import EtherscanConnector
from connectors.moralis_connector import MoralisConnector
from connectors.infura_connector import InfuraConnector
from connectors.ethereum_api_connector import EthereumApiConnector
import config
import json

if __name__ == "__main__":
    etherscan_connector = EtherscanConnector(
        config.ETHERSCAN_IP, config.ETHERSCAN_API_KEY)

    moralis_connector = MoralisConnector(
        config.MORALIS_IP, config.MORALIS_API_KEY)

    infura_connector = InfuraConnector(config.INFURA_IP, config.INFURA_API_KEY)

    ethereum_api_connector = EthereumApiConnector(
        config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)

    #response = etherscan_connector.get_transaction("0xbc78ab8a9e9a0bca7d0321a27b2c03addeae08ba81ea98b03cd3dd237eabed44")

    #response = moralis_connector.get_transaction("0xbc78ab8a9e9a0bca7d0321a27b2c03addeae08ba81ea98b03cd3dd237eabed44")

    #response = infura_connector.get_transaction("0xbc78ab8a9e9a0bca7d0321a27b2c03addeae08ba81ea98b03cd3dd237eabed44")

    response = ethereum_api_connector.get_transaction(
        "0xbc78ab8a9e9a0bca7d0321a27b2c03addeae08ba81ea98b03cd3dd237eabed44")

    json_object = json.dumps(response, indent=4)

    with open("evaluation/data_correctness_evaluation/test.json", "w") as outfile:
        outfile.write(json_object)
