from connectors import ethereum_api_connector, etherscan_connector, moralis_connector, infura_connector
from deepdiff import DeepDiff
from datetime import datetime, timezone
import itertools
import copy
import matplotlib.pyplot as plt
import numpy as np
from typing import Union


def get_block_from_all_providers(block_identifier: Union[int, str]) -> dict:
    block_by_provider = {
        "ethereum_api": ethereum_api_connector.get_block(block_identifier),
        "etherscan": etherscan_connector.get_block(block_identifier),
        "infura": infura_connector.get_block(block_identifier),
        "moralis": moralis_connector.get_block(block_identifier)
    }
    return block_by_provider


def preprocess_block_for_all_providers(block_by_provider: dict) -> dict:
    # init block by provider
    ethereum_api_block = block_by_provider["ethereum_api"]
    etherscan_block = block_by_provider["etherscan"]["result"]
    infura_block = block_by_provider["infura"]["result"]
    moralis_block = block_by_provider["moralis"]

    # rename keys for moralis
    for key in list(moralis_block.keys()):
        if "_" in key:
            new_key = [s.capitalize() for s in key.split("_")]
            new_key[0] = new_key[0].lower()
            new_key = "".join(new_key)
            moralis_block[new_key] = moralis_block.pop(key)

    # date to hex for moralis
    moralis_block["timestamp"] = hex(int(datetime.strptime(
        moralis_block["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp()))

    # filter for matching keys
    matching_keys = list(set(ethereum_api_block.keys()) & set(
        etherscan_block.keys()) & set(infura_block.keys()) & set(moralis_block.keys()))

    # remove single keys
    if "totalDifficulty" in matching_keys:
        matching_keys.remove("totalDifficulty")

    for block in [ethereum_api_block, etherscan_block, infura_block, moralis_block]:
        for key in list(block.keys()):
            # remove keys that are not in mathing keys
            if key not in matching_keys:
                block.pop(key)
                continue
            # convert int to hex values
            value = block[key]
            if type(value) == int or type(value) == str and value.isdigit():
                block[key] = hex(int(value))

            # all values to lower case
            value = block[key]
            if type(value) == str:
                block[key] = value.lower()

    return {
        "ethereum_api": ethereum_api_block,
        "etherscan": etherscan_block,
        "infura": infura_block,
        "moralis": moralis_block
    }


def process_block_conformity(block_by_provider: dict, block_identifier: Union[str, int]):
    block_conformity = {}

    # create all combinations of apis
    provider_combinations = list(
        itertools.combinations(block_by_provider.keys(), 2))

    # compare
    for combination in provider_combinations:
        conformity = DeepDiff(
            block_by_provider[combination[0]], block_by_provider[combination[1]], ignore_order=True)

        block_conformity[f"{combination[0]} - {combination[1]}"] = not bool(
            conformity.to_dict())

    return {
        "block_identifier": block_identifier,
        "conformity": block_conformity
    }


def process_block_sample(block_sample: list):
    block_sample_conformity = []

    for idx, block_identifier in enumerate(block_sample):
        block_by_provider = get_block_from_all_providers(block_identifier)

        preprocessed_block = preprocess_block_for_all_providers(
            block_by_provider)

        block_conformity = process_block_conformity(
            preprocessed_block, block_identifier)

        block_sample_conformity.append(block_conformity)

        print(f"Block: {block_identifier} done [{idx+1}/{len(block_sample)}]")

    return block_sample_conformity


def evaluate_block_sample_conformity(block_sample_conformity: list):
    block_sample_evaluation = {}
    evaluation_error = {}

    for key in block_sample_conformity[0]["conformity"].keys():
        block_sample_evaluation[key] = 0
        evaluation_error[key] = []

    for block in block_sample_conformity:
        for key, value in block["conformity"].items():
            # increase counter if conformity queals true
            if value:
                block_sample_evaluation[key] += 1
            else:
                evaluation_error[key].append(block["block_identifier"])

    evaluation_ratio = {key: (value/len(block_sample_conformity))
                        for key, value in block_sample_evaluation.items()}

    return {
        "block_sample_size": len(block_sample_conformity),
        "block_sample_evaluation": block_sample_evaluation,
        "evaluation_ratio": evaluation_ratio,
        "evaluation_error": evaluation_error
    }


def create_block_correctness_chart(block_sample_evaluation: dict, file_path: str):
    evaluation_ratio = block_sample_evaluation["evaluation_ratio"]

    comparison_labels = evaluation_ratio.keys()
    comparison_values = evaluation_ratio.values()

    y_pos = np.arange(len(comparison_labels))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, comparison_values)
    plt.xticks(y_pos, comparison_labels, rotation=90)
    plt.ylabel("Ratio")

    plt.title(f"Data Correctness Evaluation: Block Correctness (block count: {block_sample_evaluation['block_sample_size']})", {
              "fontsize": 10})
    plt.tight_layout()
    plt.savefig(file_path, format="PNG")


def inspect_block(block_identifier):
    block_by_provider = get_block_from_all_providers(block_identifier)

    preprocessed_block = preprocess_block_for_all_providers(
        copy.deepcopy(block_by_provider))

    block_conformity = process_block_conformity(
        preprocessed_block, block_identifier)

    return {
        "block_by_provider": block_by_provider,
        "preprocessed_block": preprocessed_block,
        "block_conformity": block_conformity
    }
