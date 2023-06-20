from connectors import ethereum_api_connector, etherscan_connector, moralis_connector, infura_connector
from deepdiff import DeepDiff
import itertools
import matplotlib.pyplot as plt
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)


def get_balance_from_all_providers(wallet_address: str, block_identifier="latest") -> dict:
    balance_by_provider = {
        "ethereum_api": ethereum_api_connector.get_wallet_balance(wallet_address, block_identifier),
        "etherscan": etherscan_connector.get_wallet_balance(wallet_address, block_identifier),
        "infura": infura_connector.get_wallet_balance(wallet_address, block_identifier),
        "moralis": moralis_connector.get_wallet_balance(wallet_address, block_identifier)
    }
    return balance_by_provider


def preprocess_balance_for_all_providers(balance_by_provider: dict) -> dict:
    # ethereum api
    ethereum_api_balance = {}
    ethereum_api_balance["transaction_count"] = hex(int(
        balance_by_provider["ethereum_api"]["balance"]))

    # etherscan
    etherscan_balance = {}
    etherscan_balance["transaction_count"] = hex(
        int(balance_by_provider["etherscan"]["result"]))

    # infura
    infura_balance = {}
    infura_balance["transaction_count"] = balance_by_provider["infura"]["result"]

    # moralis
    moralis_balance = {}
    moralis_balance["transaction_count"] = hex(
        int(balance_by_provider["moralis"]["balance"]))

    return {
        "ethereum_api": ethereum_api_balance,
        "etherscan": etherscan_balance,
        "infura": infura_balance,
        "moralis": moralis_balance
    }


def process_balance_conformity(balance_by_provider: dict, wallet_address: str):
    balance_conformity = {}

    # create all combinations of apis
    provider_combinations = list(
        itertools.combinations(balance_by_provider.keys(), 2))

    # compare
    for combination in provider_combinations:
        conformity = DeepDiff(
            balance_by_provider[combination[0]], balance_by_provider[combination[1]], ignore_order=True)

        balance_conformity[f"{combination[0]} - {combination[1]}"] = not bool(
            conformity.to_dict())

    return {
        "wallet_address": wallet_address,
        "conformity": balance_conformity
    }


def process_balance_sample(wallet_address_sample: list, block_identifier="latest"):
    wallet_address_sample_conformity = []

    for idx, wallet_address in enumerate(wallet_address_sample):
        try:
            balance_by_provider = get_balance_from_all_providers(
                wallet_address, block_identifier)

            preprocessed_balance = preprocess_balance_for_all_providers(
                balance_by_provider)

            balance_conformity = process_balance_conformity(
                preprocessed_balance, wallet_address)

            wallet_address_sample_conformity.append(
                balance_conformity)

            logging.info(
                f"Wallet Address: {wallet_address} done [{idx+1}/{len(wallet_address_sample)}]")
        except:
            logging.error(
                f"Wallet Address: {wallet_address} error [{idx+1}/{len(wallet_address_sample)}]")

    return wallet_address_sample_conformity


def evaluate_wallet_address_sample_conformity(wallet_address_sample_conformity: list):
    wallet_address_sample_evaluation = {}
    evaluation_error = {}

    for key in wallet_address_sample_conformity[0]["conformity"].keys():
        wallet_address_sample_evaluation[key] = 0
        evaluation_error[key] = []

    for wallet_address in wallet_address_sample_conformity:
        for key, value in wallet_address["conformity"].items():
            # increase counter if conformity queals true
            if value:
                wallet_address_sample_evaluation[key] += 1
            else:
                evaluation_error[key].append(
                    wallet_address["block_identifier"])

    evaluation_ratio = {key: (value/len(wallet_address_sample_conformity))
                        for key, value in wallet_address_sample_evaluation.items()}

    return {
        "wallet_address_sample_size": len(wallet_address_sample_conformity),
        "wallet_address_sample_evaluation": wallet_address_sample_evaluation,
        "evaluation_ratio": evaluation_ratio,
        "evaluation_error": evaluation_error
    }


def create_wallet_balance_correctness_chart(wallet_address_sample_evaluation: dict, file_path: str):
    evaluation_ratio = wallet_address_sample_evaluation["evaluation_ratio"]

    comparison_labels = evaluation_ratio.keys()
    comparison_values = evaluation_ratio.values()

    y_pos = np.arange(len(comparison_labels))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, comparison_values)
    plt.xticks(y_pos, comparison_labels, rotation=90)
    plt.ylabel("Ratio")

    plt.title(f"Heuristic Evaluation: Wallet Balance Correctness (block count: {wallet_address_sample_evaluation['wallet_address_sample_size']})", {
              "fontsize": 10})
    plt.tight_layout()
    plt.savefig(file_path, format="PNG")
