from connectors.etherscan_connector import EtherscanConnector
from connectors.moralis_connector import MoralisConnector
from connectors.infura_connector import InfuraConnector
from connectors.ethereum_api_connector import EthereumApiConnector
import config
import json
from deepdiff import DeepDiff
from datetime import datetime, timezone
import itertools
import copy

etherscan_connector = EtherscanConnector(
    config.ETHERSCAN_IP, config.ETHERSCAN_API_KEY)

moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)

infura_connector = InfuraConnector(config.INFURA_IP, config.INFURA_API_KEY)

ethereum_api_connector = EthereumApiConnector(
    config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)


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
    etherscan_del_keys = ["mixHash", "uncles"]
    for del_key in etherscan_del_keys:
        etherscan_dict.pop(del_key, None)

    # moralis
    moralis_dict = blocks["moralis"]

    # remove keys that are not present in all responses
    moralis_del_keys = ["transaction_count", "base_fee_per_gas"]
    for del_key in moralis_del_keys:
        moralis_dict.pop(del_key, None)

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

    hex_to_int_list = ["number", "size", "totalDifficulty",
                       "gasLimit", "gasUsed", "difficulty"]
    for hex_to_int in hex_to_int_list:
        moralis_dict[hex_to_int] = hex(int(moralis_dict[hex_to_int]))

    # infura
    infura_dict = blocks["infura"]["result"]

    # remove keys that are not present in all responses
    infura_del_keys = ["mixHash", "uncles"]
    for del_key in infura_del_keys:
        infura_dict.pop(del_key, None)

    # ethereum api
    ethereum_api_dict = blocks["ethereum_api"]

    # remove keys that are not present in all responses
    ethereum_api_keys = ["mixHash", "uncles"]
    for del_key in ethereum_api_keys:
        ethereum_api_dict.pop(del_key, None)

    # hex to int or date
    hex_to_int_list = ["number", "size", "totalDifficulty",
                       "gasLimit", "gasUsed", "difficulty", "timestamp"]
    for hex_to_int in hex_to_int_list:
        ethereum_api_dict[hex_to_int] = hex(int(ethereum_api_dict[hex_to_int]))

    ethereum_api_dict["miner"] = ethereum_api_dict["miner"].lower()
    

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
    comparison_error_dict = {}

    for key in block_comparison[0]["comparison"].keys():
        evaluation_dict[key] = 0
        comparison_error_dict[key] = []

    for block_compare in block_comparison:
        for key, value in block_compare["comparison"].items():
            # increase counter if comparison euqals true
            if value:
                evaluation_dict[key] += 1
            else:
                comparison_error_dict[key].append(
                    block_compare["block_identifier"])

    evaluation_ratio = {key: (value/len(block_comparison))
                        for key, value in evaluation_dict.items()}

    return {
        "block_count": len(block_comparison),
        "evaluation_count": evaluation_dict,
        "evaluation_ratio": evaluation_ratio,
        "comparison_error": comparison_error_dict
    }


def inspect_block(block_identifier):
    block = query_block_from_all_apis(block_identifier)

    prepared_block = prepare_block_from_all_apis(copy.deepcopy(block))

    compare = compare_block_from_all_apis(
        prepared_block, block_identifier)

    return {
        "block": block,
        "prepared_block": prepared_block,
        "compare": compare
    }


if __name__ == "__main__":
    inspect = False

    # inspect block
    if inspect:
        inspection = inspect_block(11237854)

        with open("evaluation/data_correctness_evaluation/block_inspection.json", "w") as outfile:
            json.dump(inspection, outfile, indent=4)

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
