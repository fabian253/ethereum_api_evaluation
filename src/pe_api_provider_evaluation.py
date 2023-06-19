from connectors.etherscan_connector import EtherscanConnector
from connectors.moralis_connector import MoralisConnector
from connectors.infura_connector import InfuraConnector
from connectors.ethereum_api_connector import EthereumApiConnector
import connectors.connector_config as connector_config
import json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import numpy as np

with_request_time_evaluation = False
with_request_time_processing = False
with_performance_evaluation_chart = True

etherscan_connector = EtherscanConnector(
    connector_config.ETHERSCAN_IP, connector_config.ETHERSCAN_API_KEY)

moralis_connector = MoralisConnector(
    connector_config.MORALIS_IP, connector_config.MORALIS_API_KEY)

infura_connector = InfuraConnector(connector_config.INFURA_IP, connector_config.INFURA_API_KEY)

ethereum_api_connector = EthereumApiConnector(
    connector_config.ETHEREUM_API_IP, connector_config.ETHEREUM_API_USERNAME, connector_config.ETHEREUM_API_PASSWORD)


def measure_block_request_times_from_all_apis(block_identifier):
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
        "block_identifier": block_identifier,
        "request_time": request_time
    }


def measure_transaction_request_times_from_all_apis(transaction_hash):
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
        "transacion_hash": transaction_hash,
        "request_time": request_time
    }


def process_block_sample(block_sample):
    request_time_performance = []

    for idx, block_identifier in enumerate(block_sample):
        request_time = measure_block_request_times_from_all_apis(
            block_identifier)

        request_time_performance.append(request_time)

        print(f"Block: {block_identifier} done [{idx+1}/{len(block_sample)}]")

    return request_time_performance


def process_transaction_sample(transaction_sample):
    request_time_performance = []

    for idx, transaction_hash in enumerate(transaction_sample):
        request_time = measure_transaction_request_times_from_all_apis(
            transaction_hash)

        request_time_performance.append(request_time)

        print(
            f"Transaction: {transaction_hash} done [{idx+1}/{len(transaction_sample)}]")

    return request_time_performance


def evaluate_single_request_time_performance(request_time_performance, method):
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
        "min_request_time": min_request_time_dict,
        "max_request_time": max_request_time_dict,
        "average_request_time": average_request_time_dict,
        "95th_percentile": percentile_95_dict,
        "99th_percentile": percentile_99_dict
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


def create_comparison_chart(request_performance_evaluation: dict):
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

        x = np.arange(5)
        width = 0.2

        plt.figure(figsize=(12, 6))
        plt.bar(x-0.3, etherscan_perf, width, color='cyan')
        plt.bar(x-0.1, moralis_perf, width, color='orange')
        plt.bar(x+0.1, infura_perf, width, color='green')
        plt.bar(x+0.3, ethereum_api_perf, width, color='blue')
        plt.xticks(x, x_labels)
        plt.ylabel("Time (s)")
        plt.legend(["etherscan", "moralis", "infura", "ethereum_api"])
        plt.title(f"Request Performance Comparison: {performance['method']}\nblock_count: {block_count}, transaction_count: {transaction_count}", {
                  "fontsize": 10})
        plt.tight_layout()
        plt.savefig(
            f"src/performance_evaluation/request_performance_{performance['method']}.png", format="PNG")

    create_chart(request_performance_evaluation["overall_performance"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"])
    create_chart(request_performance_evaluation["get_block_performance"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"])
    create_chart(request_performance_evaluation["get_transaction_performance"],
                 request_performance_evaluation["block_count"], request_performance_evaluation["transaction_count"])


if __name__ == "__main__":
    if with_request_time_processing:
        # read sample
        with open("src/data_samples/block_sample.json", "r") as infile:
            block_sample = json.load(infile)

        # read sample
        with open("src/data_samples/transaction_sample.json", "r") as infile:
            transaction_sample = json.load(infile)

        # process block sample
        block_request_time_performance = process_block_sample(block_sample)

        # process transaction sample
        transaction_request_time_performance = process_transaction_sample(
            transaction_sample)

        request_time_performance = block_request_time_performance + \
            transaction_request_time_performance

        with open("src/performance_evaluation/api_performance.json", "w") as outfile:
            json.dump(request_time_performance, outfile, indent=4)

    # evaluate request time performance
    if with_request_time_evaluation:
        request_performance_evaluation = evaluate_request_time_performance(
            request_time_performance)

        with open("src/performance_evaluation/api_performance_evaluation.json", "w") as outfile:
            json.dump(request_performance_evaluation, outfile, indent=4)

    # create chart
    if with_performance_evaluation_chart:
        with open("src/performance_evaluation/api_performance_evaluation.json", "r") as f:
            request_performance_evaluation = json.load(f)
        create_comparison_chart(request_performance_evaluation)
