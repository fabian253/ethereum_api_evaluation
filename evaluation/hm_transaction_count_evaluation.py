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


def query_transaction_count_from_all_apis(block_identifier):
    transaction_count = {
        "etherscan": etherscan_connector.get_block_transaction_count(block_identifier),
        "moralis": moralis_connector.get_block_transaction_count(block_identifier),
        "infura": infura_connector.get_block_transaction_count(block_identifier),
        "ethereum_api": ethereum_api_connector.get_block_transaction_count(block_identifier),
    }

    return transaction_count


def prepare_transaction_count_from_all_apis(transaction_count):
    # etherscan
    etherscan_dict = {}
    etherscan_dict["transaction_count"] = transaction_count["etherscan"]["result"]

    # moralis
    moralis_dict = {}
    moralis_dict["transaction_count"] = transaction_count["moralis"]["transaction_count"]

    # hex to int
    moralis_dict["transaction_count"] = hex(
        int(moralis_dict["transaction_count"]))

    # infura
    infura_dict = {}
    infura_dict["transaction_count"] = transaction_count["infura"]["result"]

    # ethereum api
    # TODO: implement when node is synced
    ethereum_api_dict = {}
    ethereum_api_dict["transaction_count"] = transaction_count["ethereum_api"]

    return {
        "etherscan_dict": etherscan_dict,
        "moralis_dict": moralis_dict,
        "infura_dict": infura_dict,
        "ethereum_api_dict": ethereum_api_dict
    }


def compare_transaction_count_from_all_apis(transaction_count, block_identifier):

    comparison_dict = {}

    # create all combinations of apis
    api_combinations = list(
        itertools.combinations(transaction_count.keys(), 2))

    # compare
    for combi in api_combinations:
        comparison = DeepDiff(
            transaction_count[combi[0]], transaction_count[combi[1]], ignore_order=True)

        # comparison_json = json.loads(comparison.to_json())

        comparison_dict[f"{combi[0]} - {combi[1]}"] = not bool(
            comparison.to_dict())

    return {
        "block_identifier": block_identifier,
        "comparison": comparison_dict
    }


def process_block_sample(block_sample):
    transaction_count_comparison = []

    for idx, block_identifier in enumerate(block_sample):
        transaction_count = query_transaction_count_from_all_apis(
            block_identifier)

        # with open("evaluation/data_correctness_evaluation/blocks.json", "w") as outfile:
        #    json.dump(blocks, outfile, indent=4)

        prepared_transaction_count = prepare_transaction_count_from_all_apis(
            transaction_count)

        compare = compare_transaction_count_from_all_apis(
            prepared_transaction_count, block_identifier)

        transaction_count_comparison.append(compare)

        print(f"Block: {block_identifier} done [{idx+1}/{len(block_sample)}]")

    return transaction_count_comparison


def evaluate_transaction_count_comparison(transaction_count_comparison):
    evaluation_dict = {}
    comparison_error_dict = {}

    for key in transaction_count_comparison[0]["comparison"].keys():
        evaluation_dict[key] = 0
        comparison_error_dict[key] = []

    for block_compare in transaction_count_comparison:
        for key, value in block_compare["comparison"].items():
            # increase counter if comparison euqals true
            if value:
                evaluation_dict[key] += 1
            else:
                comparison_error_dict[key].append(
                    block_compare["block_identifier"])

    evaluation_ratio = {key: (value/len(transaction_count_comparison))
                        for key, value in evaluation_dict.items()}

    return {
        "block_count": len(transaction_count_comparison),
        "evaluation_count": evaluation_dict,
        "evaluation_ratio": evaluation_ratio,
        "comparison_error": comparison_error_dict
    }


if __name__ == "__main__":
    # read sample
    with open("evaluation/data_samples/block_sample.json", "r") as infile:
        block_sample = json.load(infile)

    # compare blocks
    block_comparison = process_block_sample(block_sample)

    with open("evaluation/heuristic_evaluation/transaction_count_comparison.json", "w") as outfile:
        json.dump(block_comparison, outfile, indent=4)

    # evaluate block comparison
    transaction_count_comparison_evaluation = evaluate_transaction_count_comparison(
        block_comparison)

    with open("evaluation/heuristic_evaluation/transaction_count_comparison_evaluation.json", "w") as outfile:
        json.dump(transaction_count_comparison_evaluation, outfile, indent=4)