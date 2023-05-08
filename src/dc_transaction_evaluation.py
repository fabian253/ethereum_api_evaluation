from connectors.etherscan_connector import EtherscanConnector
from connectors.moralis_connector import MoralisConnector
from connectors.infura_connector import InfuraConnector
from connectors.ethereum_api_connector import EthereumApiConnector
import config
import json
import itertools
from deepdiff import DeepDiff
import copy
import matplotlib.pyplot as plt
import numpy as np

with_inspect = False
with_compare_transactions = False
with_transaction_comparison_evaluation = False
with_transaction_comparison_chart = True

etherscan_connector = EtherscanConnector(
    config.ETHERSCAN_IP, config.ETHERSCAN_API_KEY)

moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)

infura_connector = InfuraConnector(config.INFURA_IP, config.INFURA_API_KEY)

ethereum_api_connector = EthereumApiConnector(
    config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)


def query_transaction_from_all_apis(transaction_hash):
    transactions = {
        "etherscan": etherscan_connector.get_transaction(transaction_hash),
        "moralis": moralis_connector.get_transaction(transaction_hash),
        "infura": infura_connector.get_transaction(transaction_hash),
        "ethereum_api": ethereum_api_connector.get_transaction(transaction_hash),
    }

    return transactions


def prepare_transaction_from_all_apis(transactions):
    # etherscan
    etherscan_dict = transactions["etherscan"]["result"]

    # remove keys that are not present in all responses
    etherscan_del_keys = ["type", "chainId", "v", "r", "s",
                          "maxFeePerGas", "maxPriorityFeePerGas", "accessList"]
    for del_key in etherscan_del_keys:
        etherscan_dict.pop(del_key, None)

    # moralis
    moralis_dict = transactions["moralis"]

    # remove keys that are not present in all responses
    moralis_del_keys = ["receipt_cumulative_gas_used", "receipt_gas_used", "receipt_contract_address",
                        "receipt_root", "receipt_status", "block_timestamp", "transfer_index"]
    for del_key in moralis_del_keys:
        moralis_dict.pop(del_key, None)

    # format and rename moralis dict
    rename_dict = {
        "transaction_index": "transactionIndex",
        "from_address": "from",
        "to_address": "to",
        "gas_price": "gasPrice",
        "block_number": "blockNumber",
        "block_hash": "blockHash"
    }
    for old_key, new_key in rename_dict.items():
        moralis_dict[new_key] = moralis_dict.pop(old_key)

    # hex to int
    hex_to_int_list = ["nonce", "value", "transactionIndex",
                       "gasPrice", "blockNumber", "gas"]
    for hex_to_int in hex_to_int_list:
        moralis_dict[hex_to_int] = hex(int(moralis_dict[hex_to_int]))

    # infura
    infura_dict = transactions["infura"]["result"]

    # remove keys that are not present in all responses
    infura_del_keys = ["type", "chainId", "v", "r", "s",
                       "maxFeePerGas", "maxPriorityFeePerGas", "accessList"]
    for del_key in infura_del_keys:
        infura_dict.pop(del_key, None)

    # ethereum api
    ethereum_api_dict = transactions["ethereum_api"]

    # remove keys that are not present in all responses
    ethereum_del_keys = ["type", "chainId", "v", "r", "s",
                         "maxFeePerGas", "maxPriorityFeePerGas", "accessList"]
    for del_key in ethereum_del_keys:
        ethereum_api_dict.pop(del_key, None)

    # hex to int
    hex_to_int_list = ["nonce", "value", "transactionIndex",
                       "gasPrice", "blockNumber", "gas"]
    for hex_to_int in hex_to_int_list:
        ethereum_api_dict[hex_to_int] = hex(int(ethereum_api_dict[hex_to_int]))

    ethereum_api_dict["from"] = ethereum_api_dict["from"].lower()
    ethereum_api_dict["to"] = ethereum_api_dict["to"].lower()

    return {
        "etherscan_dict": etherscan_dict,
        "moralis_dict": moralis_dict,
        "infura_dict": infura_dict,
        "ethereum_api_dict": ethereum_api_dict
    }


def compare_transaction_from_all_apis(transactions, transaction_hash):

    comparison_dict = {}

    # create all combinations of apis
    api_combinations = list(itertools.combinations(transactions.keys(), 2))

    # compare
    for combi in api_combinations:
        comparison = DeepDiff(
            transactions[combi[0]], transactions[combi[1]], ignore_order=True)

        # comparison_json = json.loads(comparison.to_json())

        comparison_dict[f"{combi[0]} - {combi[1]}"] = not bool(
            comparison.to_dict())

    return {
        "transaction_hash": transaction_hash,
        "comparison": comparison_dict
    }


def process_transaction_sample(transaction_sample):
    transaction_comparison = []

    for idx, transaction_hash in enumerate(transaction_sample):
        transaction = query_transaction_from_all_apis(transaction_hash)

        # with open("src/data_correctness_evaluation/transactions.json", "w") as outfile:
        #    json.dump(transaction, outfile, indent=4)

        prepared_transactions = prepare_transaction_from_all_apis(transaction)

        compare = compare_transaction_from_all_apis(
            prepared_transactions, transaction_hash)

        transaction_comparison.append(compare)

        print(
            f"Transaction: {transaction_hash} done [{idx+1}/{len(transaction_sample)}]")

    return transaction_comparison


def evaluate_transaction_comparison(transaction_comparison):
    evaluation_dict = {}
    comparison_error_dict = {}

    for key in transaction_comparison[0]["comparison"].keys():
        evaluation_dict[key] = 0
        comparison_error_dict[key] = []

    for transaction_compare in transaction_comparison:
        for key, value in transaction_compare["comparison"].items():
            # increase counter if comparison euqals true
            if value:
                evaluation_dict[key] += 1
            else:
                comparison_error_dict[key].append(
                    transaction_compare["transaction_hash"])

    evaluation_ratio = {key: (value/len(transaction_comparison))
                        for key, value in evaluation_dict.items()}

    return {
        "transaction_count": len(transaction_comparison),
        "evaluation_count": evaluation_dict,
        "evaluation_ratio": evaluation_ratio,
        "comparison_error": comparison_error_dict
    }


def inspect_transaction(transaction_hash):
    transaction = query_transaction_from_all_apis(transaction_hash)

    prepared_transactions = prepare_transaction_from_all_apis(
        copy.deepcopy(transaction))

    compare = compare_transaction_from_all_apis(
        prepared_transactions, transaction_hash)

    return {
        "transaction": transaction,
        "prepared_transactions": prepared_transactions,
        "compare": compare
    }


def create_comparison_chart(transaction_comparison_evaluation: dict):
    evaluation_ratio = transaction_comparison_evaluation["evaluation_ratio"]

    comparison_labels = [k.replace("_dict", "")
                         for k in evaluation_ratio.keys()]
    comparison_values = evaluation_ratio.values()

    y_pos = np.arange(len(comparison_labels))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, comparison_values)
    plt.xticks(y_pos, comparison_labels, rotation=90)
    plt.ylabel("Ratio")

    plt.title(f"Transaction Correctness Comparison (transaction count: {transaction_comparison_evaluation['transaction_count']})", {
              "fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"src/data_correctness_evaluation/transaction_correctness_comparison.png", format="PNG")


if __name__ == "__main__":
    # inspect transaction
    if with_inspect:
        inspection = inspect_transaction(
            "0xab0cb6beab255331efe34b1d4ce01ccae6cecd9af2aac66bf33185c305f638e5")

        with open("src/data_correctness_evaluation/transaction_inspection.json", "w") as outfile:
            json.dump(inspection, outfile, indent=4)

    # read sample
    with open("src/data_samples/transaction_sample.json", "r") as infile:
        transaction_sample = json.load(infile)

    # compare transactions
    if with_compare_transactions:
        transaction_comparison = process_transaction_sample(transaction_sample)

        with open("src/data_correctness_evaluation/transaction_comparison.json", "w") as outfile:
            json.dump(transaction_comparison, outfile, indent=4)

    # evaluate transaction comparison
    if with_transaction_comparison_evaluation:
        transaction_comparison_evaluation = evaluate_transaction_comparison(
            transaction_comparison)

        with open("src/data_correctness_evaluation/transaction_comparison_evaluation.json", "w") as outfile:
            json.dump(transaction_comparison_evaluation, outfile, indent=4)

    # create chart
    if with_transaction_comparison_chart:
        with open("src/data_correctness_evaluation/transaction_comparison_evaluation.json", "r") as f:
            transaction_comparison_evaluation = json.load(f)
        create_comparison_chart(transaction_comparison_evaluation)
