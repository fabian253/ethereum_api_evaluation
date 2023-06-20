from connectors import ethereum_api_connector, etherscan_connector, moralis_connector, infura_connector
from deepdiff import DeepDiff
import itertools
import matplotlib.pyplot as plt
import numpy as np
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)


def get_transaction_count_from_all_providers(block_identifier: Union[int, str]) -> dict:
    transaction_count_by_provider = {
        "ethereum_api": ethereum_api_connector.get_block_transaction_count(block_identifier),
        "etherscan": etherscan_connector.get_block_transaction_count(block_identifier),
        "infura": infura_connector.get_block_transaction_count(block_identifier),
        "moralis": moralis_connector.get_block_transaction_count(block_identifier)
    }
    return transaction_count_by_provider


def preprocess_transaction_count_for_all_providers(transaction_count_by_provider: dict) -> dict:
    # ethereum api
    ethereum_api_transaction_count = {}
    ethereum_api_transaction_count["transaction_count"] = hex(
        transaction_count_by_provider["ethereum_api"]["block_transaction_count"])

    # etherscan
    etherscan_transaction_count = {}
    etherscan_transaction_count["transaction_count"] = transaction_count_by_provider["etherscan"]["result"]

    # infura
    infura_transaction_count = {}
    infura_transaction_count["transaction_count"] = transaction_count_by_provider["infura"]["result"]

    # moralis
    moralis_transaction_count = {}
    moralis_transaction_count["transaction_count"] = hex(
        int(transaction_count_by_provider["moralis"]["transaction_count"]))

    return {
        "ethereum_api": ethereum_api_transaction_count,
        "etherscan": etherscan_transaction_count,
        "infura": infura_transaction_count,
        "moralis": moralis_transaction_count
    }


def process_transaction_count_conformity(transaction_count_by_provider: dict, block_identifier: Union[str, int]):
    transaction_count_conformity = {}

    # create all combinations of apis
    provider_combinations = list(
        itertools.combinations(transaction_count_by_provider.keys(), 2))

    # compare
    for combination in provider_combinations:
        conformity = DeepDiff(
            transaction_count_by_provider[combination[0]], transaction_count_by_provider[combination[1]], ignore_order=True)

        transaction_count_conformity[f"{combination[0]} - {combination[1]}"] = not bool(
            conformity.to_dict())

    return {
        "block_identifier": block_identifier,
        "conformity": transaction_count_conformity
    }


def process_transaction_count_sample(block_sample: list):
    transaction_count_sample_conformity = []

    for idx, block_identifier in enumerate(block_sample):
        try:
            transaction_count_by_provider = get_transaction_count_from_all_providers(
                block_identifier)

            preprocessed_transaction_count = preprocess_transaction_count_for_all_providers(
                transaction_count_by_provider)

            transaction_count_conformity = process_transaction_count_conformity(
                preprocessed_transaction_count, block_identifier)

            transaction_count_sample_conformity.append(
                transaction_count_conformity)

            logging.info(
                f"Block: {block_identifier} done [{idx+1}/{len(block_sample)}]")
        except:
            logging.error(
                f"Block: {block_identifier} error [{idx+1}/{len(block_sample)}]")

    return transaction_count_sample_conformity


def evaluate_transaction_count_sample_conformity(transaction_count_sample_conformity: list):
    transaction_count_sample_evaluation = {}
    evaluation_error = {}

    for key in transaction_count_sample_conformity[0]["conformity"].keys():
        transaction_count_sample_evaluation[key] = 0
        evaluation_error[key] = []

    for block in transaction_count_sample_conformity:
        for key, value in block["conformity"].items():
            # increase counter if conformity queals true
            if value:
                transaction_count_sample_evaluation[key] += 1
            else:
                evaluation_error[key].append(block["block_identifier"])

    evaluation_ratio = {key: (value/len(transaction_count_sample_conformity))
                        for key, value in transaction_count_sample_evaluation.items()}

    return {
        "block_sample_size": len(transaction_count_sample_conformity),
        "transaction_count_sample_evaluation": transaction_count_sample_evaluation,
        "evaluation_ratio": evaluation_ratio,
        "evaluation_error": evaluation_error
    }


def create_transaction_count_correctness_chart(transaction_count_sample_evaluation: dict, file_path: str):
    evaluation_ratio = transaction_count_sample_evaluation["evaluation_ratio"]

    comparison_labels = evaluation_ratio.keys()
    comparison_values = evaluation_ratio.values()

    y_pos = np.arange(len(comparison_labels))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, comparison_values)
    plt.xticks(y_pos, comparison_labels, rotation=90)
    plt.ylabel("Ratio")

    plt.title(f"Heuristic Evaluation: Transaction Count Correctness (block count: {transaction_count_sample_evaluation['block_sample_size']})", {
              "fontsize": 10})
    plt.tight_layout()
    plt.savefig(file_path, format="PNG")
