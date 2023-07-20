from connectors import ethereum_api_connector, etherscan_connector, moralis_connector, infura_connector
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)


def measure_block_request_times_from_all_providers(block_identifier: Union[str, int], timeframe: str):
    # ethereum api
    start_time = datetime.now()
    ethereum_api_connector.get_block(block_identifier)
    ethereum_api_time = (datetime.now() - start_time).total_seconds()
    # etherscan
    start_time = datetime.now()
    etherscan_connector.get_block(block_identifier)
    etherscan_time = (datetime.now() - start_time).total_seconds()
    # infura
    start_time = datetime.now()
    infura_connector.get_block(block_identifier)
    infura_time = (datetime.now() - start_time).total_seconds()
    # moralis
    start_time = datetime.now()
    moralis_connector.get_block(block_identifier)
    moralis_time = (datetime.now() - start_time).total_seconds()

    request_time = {
        "ethereum_api": ethereum_api_time,
        "etherscan": etherscan_time,
        "infura": infura_time,
        "moralis": moralis_time
    }

    return {
        "method": "get_block",
        "timeframe": timeframe,
        "block_identifier": block_identifier,
        "request_time": request_time
    }


def measure_transaction_request_times_from_all_providers(transaction_hash: str, timeframe: str):
    # ethereum api
    start_time = datetime.now()
    ethereum_api_connector.get_transaction(transaction_hash)
    ethereum_api_time = (datetime.now() - start_time).total_seconds()
    # etherscan
    start_time = datetime.now()
    etherscan_connector.get_transaction(transaction_hash)
    etherscan_time = (datetime.now() - start_time).total_seconds()
    # infura
    start_time = datetime.now()
    infura_connector.get_transaction(transaction_hash)
    infura_time = (datetime.now() - start_time).total_seconds()
    # moralis
    start_time = datetime.now()
    moralis_connector.get_transaction(transaction_hash)
    moralis_time = (datetime.now() - start_time).total_seconds()

    request_time = {
        "ethereum_api": ethereum_api_time,
        "etherscan": etherscan_time,
        "infura": infura_time,
        "moralis": moralis_time
    }

    return {
        "method": "get_transaction",
        "timeframe": timeframe,
        "transacion_hash": transaction_hash,
        "request_time": request_time
    }


def process_timeframe_block_sample(block_sample, timeframe: str):
    request_time_performance = []

    for idx, block_identifier in enumerate(block_sample):
        request_time = measure_block_request_times_from_all_providers(
            block_identifier, timeframe)

        request_time_performance.append(request_time)

        logging.info(
            f"Block: {block_identifier} done [{idx+1}/{len(block_sample)}]")

    return request_time_performance


def process_timeframe_transaction_sample(transaction_sample, timeframe: str):
    request_time_performance = []

    for idx, transaction_hash in enumerate(transaction_sample):
        try:
            request_time = measure_transaction_request_times_from_all_providers(
                transaction_hash, timeframe)

            request_time_performance.append(request_time)

            logging.info(
                f"Transaction: {transaction_hash} done [{idx+1}/{len(transaction_sample)}]")
        except:
            logging.error(
                f"Transaction: {transaction_hash} error [{idx+1}/{len(transaction_sample)}]")

    return request_time_performance


def evaluate_single_request_time_performance(request_time_performance: list, method: str, timeframe: str):
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

    percentile_25_dict = {key: np.percentile(value, 25)
                          for key, value in request_time_dict.items()}

    percentile_75_dict = {key: np.percentile(value, 75)
                          for key, value in request_time_dict.items()}

    percentile_95_dict = {key: np.percentile(value, 95)
                          for key, value in request_time_dict.items()}

    return {
        "method": method,
        "timeframe": timeframe,
        "min_request_time": min_request_time_dict,
        "max_request_time": max_request_time_dict,
        "average_request_time": average_request_time_dict,
        "25th_percentile": percentile_25_dict,
        "75th_percentile": percentile_75_dict,
        "95th_percentile": percentile_95_dict
    }


def evaluate_timeframe_request_time_performance(request_time_performance):
    request_time_performance_dict = {}

    # split request time for method and timeframe
    for request_time in request_time_performance:
        if not (request_time["method"], request_time["timeframe"]) in request_time_performance_dict.keys():
            request_time_performance_dict[(
                request_time["method"], request_time["timeframe"])] = []

        request_time_performance_dict[(request_time["method"], request_time["timeframe"])].append(
            request_time)

    # evaluate overall old and new performance
    overall_old_performance = evaluate_single_request_time_performance(request_time_performance_dict[(
        "get_block", "old")] + request_time_performance_dict[("get_transaction", "old")], "overall", "old")

    overall_new_performance = evaluate_single_request_time_performance(request_time_performance_dict[(
        "get_block", "new")] + request_time_performance_dict[("get_transaction", "new")], "overall", "new")

    # evaluate overall performance diff (diff between new and old -> negative number: new is faster)
    overall_performance_difference = {}
    overall_performance_difference_percentage = {}
    for key in overall_new_performance.keys():
        if key == "method" or key == "timeframe":
            overall_performance_difference[key] = "overall"
            overall_performance_difference_percentage[key] = "overall"
        else:
            tmp_performance_comparison = {}
            tmp_performance_comparison_percentage = {}
            for api_provider in overall_new_performance[key].keys():
                # postive -> new is slower, negativ -> new is faster
                tmp_performance_comparison[api_provider] = overall_new_performance[key][api_provider] - \
                    overall_old_performance[key][api_provider]

                tmp_performance_comparison_percentage[api_provider] = tmp_performance_comparison[
                    api_provider] / overall_old_performance[key][api_provider] * 100

                overall_performance_difference[key] = tmp_performance_comparison
                overall_performance_difference_percentage[key] = tmp_performance_comparison_percentage

    return_dict = {
        "block_count": len(request_time_performance_dict[("get_block", "old")]),
        "transaction_count": len(request_time_performance_dict[("get_transaction", "old")]),
        "overall_performance_difference": overall_performance_difference,
        "overall_performance_difference_percentage": overall_performance_difference_percentage,
        "overall_old_performance": overall_old_performance,
        "overall_new_performance": overall_new_performance
    }

    for key, value in request_time_performance_dict.items():
        return_dict[f"{key[0]}_{key[1]}_performance"] = evaluate_single_request_time_performance(
            value, key[0], key[1])

    return return_dict


def create_timeframe_request_time_performance_chart(request_performance_evaluation: dict, file_path: str):
    def create_chart(performance: dict, block_count: int, transaction_count: int, type: str):
        etherscan_perf = []
        moralis_perf = []
        infura_perf = []
        ethereum_api_perf = []
        x_labels = []

        for k, v in performance.items():
            if k != "method" and k != "timeframe":
                etherscan_perf.append(v["etherscan"])
                moralis_perf.append(v["moralis"])
                infura_perf.append(v["infura"])
                ethereum_api_perf.append(v["ethereum_api"])
                x_labels.append(k)

        x = np.arange(6)
        width = 0.2

        plt.figure(figsize=(12, 6))
        plt.bar(x-0.3, ethereum_api_perf, width, color='blue')
        plt.bar(x-0.1, etherscan_perf, width, color='cyan')
        plt.bar(x+0.1, infura_perf, width, color='green')
        plt.bar(x+0.3, moralis_perf, width, color='orange')
        plt.xticks(x, x_labels)
        plt.ylabel("Time (%)") if "percentage" in type else plt.ylabel(
            "Time (s)")
        plt.legend(["ethereum_api", "etherscan", "infura", "moralis"])
        plt.title(f"Performance Evaluation: Timeframe Comparison ({performance['method']})\ntype: {type}, timeframe: {performance['timeframe']}, block_count: {block_count}, transaction_count: {transaction_count}", {
                  "fontsize": 10})
        plt.tight_layout()
        plt.savefig(
            f"{file_path}/request_performance_timeframe_{performance['method']}_{type}.png", format="PNG")

    create_chart(request_performance_evaluation["overall_performance_difference"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"], "difference")
    create_chart(request_performance_evaluation["overall_performance_difference_percentage"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"], "difference_percentage")
    create_chart(request_performance_evaluation["overall_old_performance"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"], "old")
    create_chart(request_performance_evaluation["overall_new_performance"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"], "new")
