from connectors.etherscan_connector import EtherscanConnector
from connectors.moralis_connector import MoralisConnector
from connectors.infura_connector import InfuraConnector
from connectors.ethereum_api_connector import EthereumApiConnector
import config
import json
from datetime import datetime
import numpy as np

etherscan_connector = EtherscanConnector(
    config.ETHERSCAN_IP, config.ETHERSCAN_API_KEY)

moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)

infura_connector = InfuraConnector(config.INFURA_IP, config.INFURA_API_KEY)

ethereum_api_connector = EthereumApiConnector(
    config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)


def measure_block_request_times_from_all_apis(block_identifier, timeframe: str):
    # etherscan
    start_time = datetime.now()
    etherscan_connector.get_block(block_identifier)
    etherscan_time = (datetime.now() - start_time).total_seconds()
    # moralis
    start_time = datetime.now()
    moralis_connector.get_block(block_identifier)
    moralis_time = (datetime.now() - start_time).total_seconds()
    # infura
    start_time = datetime.now()
    infura_connector.get_block(block_identifier)
    infura_time = (datetime.now() - start_time).total_seconds()
    # ethereum api
    start_time = datetime.now()
    ethereum_api_connector.get_block(block_identifier)
    ethereum_api_time = (datetime.now() - start_time).total_seconds()

    request_time = {
        "etherscan": etherscan_time,
        "moralis": moralis_time,
        "infura": infura_time,
        "ethereum_api": ethereum_api_time,
    }

    return {
        "method": "get_block",
        "timeframe": timeframe,
        "block_identifier": block_identifier,
        "request_time": request_time
    }


def measure_transaction_request_times_from_all_apis(transaction_hash, timeframe: str):
    # etherscan
    start_time = datetime.now()
    etherscan_connector.get_transaction(transaction_hash)
    etherscan_time = (datetime.now() - start_time).total_seconds()
    # moralis
    start_time = datetime.now()
    moralis_connector.get_transaction(transaction_hash)
    moralis_time = (datetime.now() - start_time).total_seconds()
    # infura
    start_time = datetime.now()
    infura_connector.get_transaction(transaction_hash)
    infura_time = (datetime.now() - start_time).total_seconds()
    # ethereum api
    start_time = datetime.now()
    ethereum_api_connector.get_transaction(transaction_hash)
    ethereum_api_time = (datetime.now() - start_time).total_seconds()

    request_time = {
        "etherscan": etherscan_time,
        "moralis": moralis_time,
        "infura": infura_time,
        "ethereum_api": ethereum_api_time,
    }

    return {
        "method": "get_transaction",
        "timeframe": timeframe,
        "transacion_hash": transaction_hash,
        "request_time": request_time
    }


def process_block_sample(block_sample, timeframe: str):
    request_time_performance = []

    for idx, block_identifier in enumerate(block_sample):
        request_time = measure_block_request_times_from_all_apis(
            block_identifier, timeframe)

        request_time_performance.append(request_time)

        print(f"Block: {block_identifier} done [{idx+1}/{len(block_sample)}]")

    return request_time_performance


def process_transaction_sample(transaction_sample, timeframe: str):
    request_time_performance = []

    for idx, transaction_hash in enumerate(transaction_sample):
        request_time = measure_transaction_request_times_from_all_apis(
            transaction_hash, timeframe)

        request_time_performance.append(request_time)

        print(
            f"Transaction: {transaction_hash} done [{idx+1}/{len(transaction_sample)}]")

    return request_time_performance


def evaluate_single_request_time_performance(request_time_performance, method, timeframe: str):
    min_request_time_dict = {}
    max_request_time_dict = {}
    average_request_time_dict = {}
    request_time_dict = {}

    for key in request_time_performance[0]["request_time"].keys():
        min_request_time_dict[key] = 1000
        max_request_time_dict[key] = 0
        average_request_time_dict[key] = 0
        request_time_dict[key] = []

    for request_time in request_time_performance:
        for key, value in request_time["request_time"].items():
            # set min request time
            if value < min_request_time_dict[key]:
                min_request_time_dict[key] = value
            # set max request time
            if value > max_request_time_dict[key]:
                max_request_time_dict[key] = value
            # sum request times
            average_request_time_dict[key] += value

            # append to list or request times
            request_time_dict[key].append(value)

    average_request_time_dict = {key: (value/len(request_time_performance))
                                 for key, value in average_request_time_dict.items()}

    percentile_95_dict = {key: np.percentile(value, 95)
                          for key, value in request_time_dict.items()}

    percentile_99_dict = {key: np.percentile(value, 99)
                          for key, value in request_time_dict.items()}

    return {
        "method": method,
        "timeframe": timeframe,
        "min_request_time": min_request_time_dict,
        "max_request_time": max_request_time_dict,
        "average_request_time": average_request_time_dict,
        "95th_percentile": percentile_95_dict,
        "99th_percentile": percentile_99_dict
    }


def evaluate_request_time_performance(request_time_performance):
    request_time_performance_dict = {}

    # split request time for method and timeframe
    for request_time in request_time_performance:
        if not (request_time["method"], request_time["timeframe"]) in request_time_performance_dict.keys():
            request_time_performance_dict[(
                request_time["method"], request_time["timeframe"])] = []

        request_time_performance_dict[(request_time["method"], request_time["timeframe"])].append(
            request_time)

    # evaluate overall early and late performance
    overall_early_performance = evaluate_single_request_time_performance(request_time_performance_dict[(
        "get_block", "early")] + request_time_performance_dict[("get_transaction", "early")], "overall", "early")

    overall_late_performance = evaluate_single_request_time_performance(request_time_performance_dict[(
        "get_block", "late")] + request_time_performance_dict[("get_transaction", "late")], "overall", "late")

    # evaluate overall performance diff
    overall_performance_difference = {}
    for key in overall_late_performance.keys():
        if key == "method" or key == "timeframe":
            overall_performance_difference[key] = "overall"
        else:
            tmp_performance_comparison = {}
            for api_provider in overall_late_performance[key].keys():
                tmp_performance_comparison[api_provider] = overall_late_performance[key][api_provider] - \
                    overall_early_performance[key][api_provider]

                overall_performance_difference[key] = tmp_performance_comparison

    return_dict = {
        "block_count": len(request_time_performance_dict[("get_block", "early")]),
        "transaction_count": len(request_time_performance_dict[("get_transaction", "early")]),
        "overall_performance_difference": overall_performance_difference,
        "overall_early_performance": overall_early_performance,
        "overall_late_performance": overall_late_performance
    }

    for key, value in request_time_performance_dict.items():
        return_dict[f"{key[0]}_{key[1]}_performance"] = evaluate_single_request_time_performance(
            value, key[0], key[1])

    return return_dict


if __name__ == "__main__":
    # read sample
    with open("evaluation/data_samples/early_late_block_sample.json", "r") as infile:
        early_late_block_sample = json.load(infile)

    # read sample
    with open("evaluation/data_samples/early_late_transaction_sample.json", "r") as infile:
        early_late_transaction_sample = json.load(infile)

    # process block sample
    early_block_request_time_performance = process_block_sample(
        early_late_block_sample["early_block_sample"], "early")
    late_block_request_time_performance = process_block_sample(
        early_late_block_sample["late_block_sample"], "late")

    # process transaction sample
    early_transaction_request_time_performance = process_transaction_sample(
        early_late_transaction_sample["early_transaction_sample"], "early")
    late_transaction_request_time_performance = process_transaction_sample(
        early_late_transaction_sample["late_transaction_sample"], "late")

    request_time_performance = early_block_request_time_performance + late_block_request_time_performance + \
        early_transaction_request_time_performance + \
        late_transaction_request_time_performance

    with open("evaluation/performance_evaluation/early_late_performance.json", "w") as outfile:
        json.dump(request_time_performance, outfile, indent=4)

    # evaluate block comparison
    request_performance_evaluation = evaluate_request_time_performance(
        request_time_performance)

    with open("evaluation/performance_evaluation/early_late_performance_evaluation.json", "w") as outfile:
        json.dump(request_performance_evaluation, outfile, indent=4)
