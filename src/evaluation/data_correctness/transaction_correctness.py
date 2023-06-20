from connectors import ethereum_api_connector, etherscan_connector, moralis_connector, infura_connector
from deepdiff import DeepDiff
import itertools
import copy
import matplotlib.pyplot as plt
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)


def get_transaction_from_all_providers(transaction_hash: str) -> dict:
    # TODO: change to ethereum api connector
    transaction_by_provider = {
        "ethereum_api": infura_connector.get_transaction(transaction_hash),
        "etherscan": etherscan_connector.get_transaction(transaction_hash),
        "infura": infura_connector.get_transaction(transaction_hash),
        "moralis": moralis_connector.get_transaction(transaction_hash)
    }
    return transaction_by_provider


def preprocess_transaction_for_all_providers(transaction_by_provider: dict) -> dict:
    # init transaction by provider
    ethereum_api_transaction = transaction_by_provider["ethereum_api"]
    etherscan_transaction = transaction_by_provider["etherscan"]["result"]
    infura_transaction = transaction_by_provider["infura"]["result"]
    moralis_transaction = transaction_by_provider["moralis"]

    # rename keys for moralis
    for key in list(moralis_transaction.keys()):
        if "_" in key:
            new_key = [s.capitalize() for s in key.split("_")]
            new_key[0] = new_key[0].lower()
            new_key = "".join(new_key)
            moralis_transaction[new_key] = moralis_transaction.pop(key)

    # filter for matching keys
    matching_keys = list(set(ethereum_api_transaction.keys()) & set(
        etherscan_transaction.keys()) & set(infura_transaction.keys()) & set(moralis_transaction.keys()))

    for transaction in [ethereum_api_transaction, etherscan_transaction, infura_transaction, moralis_transaction]:
        for key in list(transaction.keys()):
            # remove keys that are not in mathing keys
            if key not in matching_keys:
                transaction.pop(key)
                continue
            # convert int to hex values
            value = transaction[key]
            if type(value) == int or type(value) == str and value.isdigit():
                transaction[key] = hex(int(value))

            # all values to lower case
            value = transaction[key]
            if type(value) == str:
                transaction[key] = value.lower()

    return {
        "ethereum_api": ethereum_api_transaction,
        "etherscan": etherscan_transaction,
        "infura": infura_transaction,
        "moralis": moralis_transaction
    }


def process_transaction_conformity(transaction_by_provider: dict, transaction_hash: str):
    transaction_conformity = {}

    # create all combinations of apis
    provider_combinations = list(
        itertools.combinations(transaction_by_provider.keys(), 2))

    # compare
    for combination in provider_combinations:
        conformity = DeepDiff(
            transaction_by_provider[combination[0]], transaction_by_provider[combination[1]], ignore_order=True)

        transaction_conformity[f"{combination[0]} - {combination[1]}"] = not bool(
            conformity.to_dict())

    return {
        "transaction_hash": transaction_hash,
        "conformity": transaction_conformity
    }


def process_transaction_sample(transaction_sample: list):
    transaction_sample_conformity = []

    for idx, transaction_hash in enumerate(transaction_sample):
        try:
            transaction_by_provider = get_transaction_from_all_providers(
                transaction_hash)

            preprocessed_transaction = preprocess_transaction_for_all_providers(
                transaction_by_provider)

            transaction_conformity = process_transaction_conformity(
                preprocessed_transaction, transaction_hash)

            transaction_sample_conformity.append(transaction_conformity)

            logging.info(
                f"Transaction: {transaction_hash} done [{idx+1}/{len(transaction_sample)}]")
        except:
            logging.error(
                f"Transaction: {transaction_hash} error [{idx+1}/{len(transaction_sample)}]")

    return transaction_sample_conformity


def evaluate_transaction_sample_conformity(transaction_sample_conformity: list):
    transaction_sample_evaluation = {}
    evaluation_error = {}

    for key in transaction_sample_conformity[0]["conformity"].keys():
        transaction_sample_evaluation[key] = 0
        evaluation_error[key] = []

    for transaction in transaction_sample_conformity:
        for key, value in transaction["conformity"].items():
            # increase counter if conformity queals true
            if value:
                transaction_sample_evaluation[key] += 1
            else:
                evaluation_error[key].append(transaction["block_identifier"])

    evaluation_ratio = {key: (value/len(transaction_sample_conformity))
                        for key, value in transaction_sample_evaluation.items()}

    return {
        "transaction_sample_size": len(transaction_sample_conformity),
        "transaction_sample_evaluation": transaction_sample_evaluation,
        "evaluation_ratio": evaluation_ratio,
        "evaluation_error": evaluation_error
    }


def create_transaction_correctness_chart(transaction_sample_evaluation: dict, file_path: str):
    evaluation_ratio = transaction_sample_evaluation["evaluation_ratio"]

    comparison_labels = evaluation_ratio.keys()
    comparison_values = evaluation_ratio.values()

    y_pos = np.arange(len(comparison_labels))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, comparison_values)
    plt.xticks(y_pos, comparison_labels, rotation=90)
    plt.ylabel("Ratio")

    plt.title(f"Data Correctness Evaluation: Transaction Correctness (block count: {transaction_sample_evaluation['transaction_sample_size']})", {
              "fontsize": 10})
    plt.tight_layout()
    plt.savefig(file_path, format="PNG")


def inspect_transaction(transaction_hash):
    transaction_by_provider = get_transaction_from_all_providers(
        transaction_hash)

    preprocessed_transaction = preprocess_transaction_for_all_providers(
        copy.deepcopy(transaction_by_provider))

    transaction_conformity = process_transaction_conformity(
        preprocessed_transaction, transaction_hash)

    return {
        "transaction_by_provider": transaction_by_provider,
        "preprocessed_transaction": preprocessed_transaction,
        "transaction_conformity": transaction_conformity
    }
