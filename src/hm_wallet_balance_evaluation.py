from connectors.etherscan_connector import EtherscanConnector
from connectors.moralis_connector import MoralisConnector
from connectors.infura_connector import InfuraConnector
from connectors.ethereum_api_connector import EthereumApiConnector
import config
import json
import itertools
from deepdiff import DeepDiff


etherscan_connector = EtherscanConnector(
    config.ETHERSCAN_IP, config.ETHERSCAN_API_KEY)

moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)

infura_connector = InfuraConnector(config.INFURA_IP, config.INFURA_API_KEY)

ethereum_api_connector = EthereumApiConnector(
    config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)


def query_balance_from_all_apis(wallet_address, block_identifier="latest"):
    balance = {
        "etherscan": etherscan_connector.get_wallet_balance(wallet_address, block_identifier),
        "moralis": moralis_connector.get_wallet_balance(wallet_address, block_identifier),
        "infura": infura_connector.get_wallet_balance(wallet_address, block_identifier),
        "ethereum_api": ethereum_api_connector.get_wallet_balance(wallet_address, block_identifier),
    }

    return balance


def prepare_balance_from_all_apis(balance):
    # etherscan
    etherscan_dict = {}
    etherscan_dict["balance"] = balance["etherscan"]["result"]

    # hex to int
    etherscan_dict["balance"] = hex(int(etherscan_dict["balance"]))

    # moralis
    moralis_dict = {}
    moralis_dict["balance"] = balance["moralis"]["balance"]

    # hex to int
    moralis_dict["balance"] = hex(int(moralis_dict["balance"]))

    # infura
    infura_dict = {}
    infura_dict["balance"] = balance["infura"]["result"]

    # ethereum api
    ethereum_api_dict = {}
    ethereum_api_dict["balance"] = balance["ethereum_api"]["balance"]

    # hex to int
    ethereum_api_dict["balance"] = hex(int(ethereum_api_dict["balance"]))

    return {
        "etherscan_dict": etherscan_dict,
        "moralis_dict": moralis_dict,
        "infura_dict": infura_dict,
        "ethereum_api_dict": ethereum_api_dict
    }


def compare_balance_from_all_apis(balance, wallet_address):

    comparison_dict = {}

    # create all combinations of apis
    api_combinations = list(
        itertools.combinations(balance.keys(), 2))

    # compare
    for combi in api_combinations:
        comparison = DeepDiff(
            balance[combi[0]], balance[combi[1]], ignore_order=True)

        # comparison_json = json.loads(comparison.to_json())

        comparison_dict[f"{combi[0]} - {combi[1]}"] = not bool(
            comparison.to_dict())

    return {
        "wallet_address": wallet_address,
        "comparison": comparison_dict
    }


def process_block_sample(block_sample, block_identifier="latest"):
    balance_comparison = []

    for idx, wallet_address in enumerate(block_sample):
        balance = query_balance_from_all_apis(
            wallet_address, block_identifier)

        # with open("src/data_correctness_evaluation/blocks.json", "w") as outfile:
        #    json.dump(blocks, outfile, indent=4)

        prepared_balance = prepare_balance_from_all_apis(
            balance)

        compare = compare_balance_from_all_apis(
            prepared_balance, wallet_address)

        balance_comparison.append(compare)

        print(
            f"Wallet Address: {wallet_address} done [{idx+1}/{len(block_sample)}]")

    return balance_comparison


def evaluate_balance_comparison(balance_comparison):
    evaluation_dict = {}
    comparison_error_dict = {}

    for key in balance_comparison[0]["comparison"].keys():
        evaluation_dict[key] = 0
        comparison_error_dict[key] = []

    for block_compare in balance_comparison:
        for key, value in block_compare["comparison"].items():
            # increase counter if comparison euqals true
            if value:
                evaluation_dict[key] += 1
            else:
                comparison_error_dict[key].append(
                    block_compare["wallet_address"])

    evaluation_ratio = {key: (value/len(balance_comparison))
                        for key, value in evaluation_dict.items()}

    return {
        "wallet_count": len(balance_comparison),
        "evaluation_count": evaluation_dict,
        "evaluation_ratio": evaluation_ratio,
        "comparison_error": comparison_error_dict
    }


if __name__ == "__main__":
    # param (only latest is working -> etherscan premium endpoint needed)
    block_identifier = "latest"

    # read sample
    with open("src/data_samples/wallet_address_sample.json", "r") as infile:
        block_sample = json.load(infile)

    # compare blocks
    block_comparison = process_block_sample(block_sample, block_identifier)

    with open("src/heuristic_evaluation/balance_comparison.json", "w") as outfile:
        json.dump(block_comparison, outfile, indent=4)

    # evaluate block comparison
    balance_comparison_evaluation = evaluate_balance_comparison(
        block_comparison)

    with open("src/heuristic_evaluation/balance_comparison_evaluation.json", "w") as outfile:
        json.dump(balance_comparison_evaluation, outfile, indent=4)
