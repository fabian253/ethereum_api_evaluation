from connectors.etherscan_connector import EtherscanConnector
from connectors.moralis_connector import MoralisConnector
from connectors.infura_connector import InfuraConnector
from connectors.ethereum_api_connector import EthereumApiConnector
import config
import json
import random
from deepdiff import DeepDiff
from datetime import datetime, timezone
import itertools

etherscan_connector = EtherscanConnector(
    config.ETHERSCAN_IP, config.ETHERSCAN_API_KEY)

moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)

infura_connector = InfuraConnector(config.INFURA_IP, config.INFURA_API_KEY)

ethereum_api_connector = EthereumApiConnector(
    config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)


def generate_random_block_sample(latest_block: int, sample_size: int, file_path: str):
    sample = random.sample(range(0, latest_block+1), sample_size)

    sample_json = json.dumps(sample, indent=4)

    with open(file_path, "w") as outfile:
        outfile.write(sample_json)


def query_block_from_all_apis(block_identifier):
    blocks = {
        "etherscan": etherscan_connector.get_block(block_identifier),
        "moralis": moralis_connector.get_block(block_identifier),
        "infura": infura_connector.get_block(block_identifier),
        "ethereum_api": ethereum_api_connector.get_block(block_identifier),
    }

    return blocks


def prepare_block_from_all_apis(blocks):
    # etherscan
    etherscan_dict = blocks["etherscan"]["result"]

    # remove keys that are not present in all responses
    etherscan_dict.pop("mixHash")
    etherscan_dict.pop("uncles")

    # moralis
    moralis_dict = blocks["moralis"]

    # remove keys that are not present in all responses
    moralis_dict.pop("transaction_count")
    moralis_dict.pop("base_fee_per_gas")

    # format and rename moralis dict
    rename_dict = {
        "parent_hash": "parentHash",
        "sha3_uncles": "sha3Uncles",
        "logs_bloom": "logsBloom",
        "transactions_root": "transactionsRoot",
        "state_root": "stateRoot",
        "receipts_root": "receiptsRoot",
        "total_difficulty": "totalDifficulty",
        "extra_data": "extraData",
        "gas_limit": "gasLimit",
        "gas_used": "gasUsed",
    }
    for old_key, new_key in rename_dict.items():
        moralis_dict[new_key] = moralis_dict.pop(old_key)

    # hex to int or date
    moralis_dict["timestamp"] = hex(int(datetime.strptime(
        moralis_dict["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp()))

    moralis_dict["number"] = hex(int(moralis_dict["number"]))
    moralis_dict["size"] = hex(int(moralis_dict["size"]))
    moralis_dict["totalDifficulty"] = hex(int(moralis_dict["totalDifficulty"]))
    moralis_dict["gasLimit"] = hex(int(moralis_dict["gasLimit"]))
    moralis_dict["gasUsed"] = hex(int(moralis_dict["gasUsed"]))
    moralis_dict["difficulty"] = hex(int(moralis_dict["difficulty"]))

    # infura
    infura_dict = blocks["infura"]["result"]

    # remove keys that are not present in all responses
    infura_dict.pop("mixHash")
    infura_dict.pop("uncles")

    # ethereum api
    # TODO: implement when node is synced
    ethereum_api_dict = blocks["ethereum_api"]

    return {
        "etherscan_dict": etherscan_dict,
        "moralis_dict": moralis_dict,
        "infura_dict": infura_dict,
        "ethereum_api_dict": ethereum_api_dict
    }


def compare_block_from_all_apis(blocks, block_identifier):

    comparison_dict = {}

    # create all combinations of apis
    api_combinations = list(itertools.combinations(blocks.keys(), 2))

    # compare
    for combi in api_combinations:
        comparison = DeepDiff(
            blocks[combi[0]], blocks[combi[1]], ignore_order=True)

        # comparison_json = json.loads(comparison.to_json())

        comparison_dict[f"{combi[0]} - {combi[1]}"] = not bool(
            comparison.to_dict())

    return {
        "block_identifier": block_identifier,
        "comparison": comparison_dict
    }


def process_block_sample(block_sample):
    block_comparison = []

    for idx, block_identifier in enumerate(block_sample):
        blocks = query_block_from_all_apis(block_identifier)

        # with open("evaluation/data_correctness_evaluation/blocks.json", "w") as outfile:
        #    json.dump(blocks, outfile, indent=4)

        prepared_blocks = prepare_block_from_all_apis(blocks)

        compare = compare_block_from_all_apis(
            prepared_blocks, block_identifier)

        block_comparison.append(compare)

        print(f"Block: {block_identifier} done [{idx+1}/{len(block_sample)}]")

    return block_comparison


def evaluate_block_comparison(block_comparison):
    evaluation_dict = {}

    for key in block_comparison[0]["comparison"].keys():
        evaluation_dict[key] = 0

    for block_compare in block_comparison:
        for key, value in block_compare["comparison"].items():
            evaluation_dict[key] += (1 if value else 0)

    evaluation_ratio = {key: (value/len(block_comparison))
                        for key, value in evaluation_dict.items()}

    return {
        "block_count": len(block_comparison),
        "evaluation_count": evaluation_dict,
        "evaluation_ratio": evaluation_ratio
    }


if __name__ == "__main__":
    generate_sample = False

    # generate sample
    if generate_sample:
        generate_random_block_sample(
            16777791, 1000, "evaluation/data_samples/block_sample.json")

    # read sample
    with open("evaluation/data_samples/block_sample.json", "r") as infile:
        block_sample = json.load(infile)

    # compare blocks
    block_comparison = process_block_sample(block_sample)

    with open("evaluation/data_correctness_evaluation/block_comparison.json", "w") as outfile:
        json.dump(block_comparison, outfile, indent=4)

    # evaluate block comparison
    block_comparison_evaluation = evaluate_block_comparison(block_comparison)

    with open("evaluation/data_correctness_evaluation/block_comparison_evaluation.json", "w") as outfile:
        json.dump(block_comparison_evaluation, outfile, indent=4)
