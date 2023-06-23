from connectors import ethereum_api_connector, etherscan_connector, moralis_connector, infura_connector
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)


def measure_block_request_times_from_all_providers(block_identifier: Union[str, int]) -> dict:
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
        "block_identifier": block_identifier,
        "request_time": request_time
    }


def measure_transaction_request_times_from_all_providers(transaction_hash: str) -> dict:
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
        "transacion_hash": transaction_hash,
        "request_time": request_time
    }


def process_block_sample(block_sample: list):
    request_time_performance = []

    for idx, block_identifier in enumerate(block_sample):
        request_time = measure_block_request_times_from_all_providers(
            block_identifier)

        request_time_performance.append(request_time)

        logging.info(
            f"Block: {block_identifier} done [{idx+1}/{len(block_sample)}]")

    return request_time_performance


def process_transaction_sample(transaction_sample: list):
    request_time_performance = []

    for idx, transaction_hash in enumerate(transaction_sample):
        try:
            request_time = measure_transaction_request_times_from_all_providers(
                transaction_hash)

            request_time_performance.append(request_time)

            logging.info(
                f"Transaction: {transaction_hash} done [{idx+1}/{len(transaction_sample)}]")
        except:
            logging.error(
                f"Transaction: {transaction_hash} error [{idx+1}/{len(transaction_sample)}]")

    return request_time_performance


def evaluate_single_request_time_performance(request_time_performance: list, method: str):
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
        "min_request_time": min_request_time_dict,
        "max_request_time": max_request_time_dict,
        "average_request_time": average_request_time_dict,
        "25th_percentile": percentile_25_dict,
        "75th_percentile": percentile_75_dict,
        "95th_percentile": percentile_95_dict
    }


def evaluate_request_time_performance(request_time_performance):
    request_time_performance_dict = {}

    for request_time in request_time_performance:
        if not request_time["method"] in request_time_performance_dict.keys():
            request_time_performance_dict[request_time["method"]] = []

        request_time_performance_dict[request_time["method"]].append(
            request_time)

    return_dict = {
        "block_count": len(request_time_performance_dict["get_block"]),
        "transaction_count": len(request_time_performance_dict["get_transaction"]),
        "overall_performance": evaluate_single_request_time_performance(request_time_performance, "overall")
    }

    for key, value in request_time_performance_dict.items():
        return_dict[f"{key}_performance"] = evaluate_single_request_time_performance(
            value, key)

    return return_dict


def create_request_time_performance_chart(request_performance_evaluation: dict, file_path: str):
    def create_chart(performance: dict, block_count: int, transaction_count: int):
        etherscan_perf = []
        moralis_perf = []
        infura_perf = []
        ethereum_api_perf = []
        x_labels = []

        for k, v in performance.items():
            if k != "method":
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
        plt.ylabel("Time (s)")
        plt.legend(["ethereum_api", "etherscan", "infura", "moralis"])
        plt.title(f"Performance Evaluation: API Provider Comparison ({performance['method']})\nblock_count: {block_count}, transaction_count: {transaction_count}", {
                  "fontsize": 10})
        plt.tight_layout()
        plt.savefig(
            f"{file_path}/request_performance_{performance['method']}.png", format="PNG")

    create_chart(request_performance_evaluation["overall_performance"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"])
    create_chart(request_performance_evaluation["get_block_performance"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"])
    create_chart(request_performance_evaluation["get_transaction_performance"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"])
