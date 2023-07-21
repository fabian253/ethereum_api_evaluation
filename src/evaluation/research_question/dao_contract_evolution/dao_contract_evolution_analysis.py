import matplotlib.pyplot as plt
import numpy as np
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)


def calc_token_balance(transactions: list, contract_address: str = Union[str, None], block_number:  Union[int, None] = None) -> dict:
    if contract_address is not None:
        transactions = [
            t for t in transactions if t["contract_address"] == contract_address]

    if block_number is not None:
        transactions = [
            t for t in transactions if t["block_number"] <= block_number]

    balance = {}

    for transaction in transactions:
        if transaction["value"] > 0:
            if transaction["from_address"] in balance.keys():
                if balance[transaction["from_address"]] - transaction["value"] <= 0:
                    del balance[transaction["from_address"]]
            if transaction["to_address"] in balance.keys():
                balance[transaction["to_address"]] += transaction["value"]
            else:
                balance[transaction["to_address"]] = transaction["value"]

    return balance


def gini_coefficient(array: list):
    array = np.array(list(array))
    array = array.flatten()
    if np.amin(array) < 0:
        # Values cannot be negative:
        array -= np.amin(array)
    # Values cannot be 0:
    array = array + 0.0000001
    # Values must be sorted:
    array = np.sort(array)
    # Index per array element:
    index = np.arange(1, array.shape[0]+1)
    # Number of array elements:
    n = array.shape[0]
    # Gini coefficient:
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))


def herfindahl_index(array: list):
    array = np.array(list(array))
    return np.square(array/array.sum()).sum()


def calc_interval(transactions: list, contract_address: str, block_intervals: list, func):
    measure_interval = {}

    for block_number in block_intervals:
        balance = calc_token_balance(
            transactions, contract_address, int(block_number))
        measure = func(balance.values())

        measure_interval[block_number] = measure

    return measure_interval


def calc_interval_fast(transactions: list, contract_address: str, block_intervals: list, func):
    transactions = [
        t for t in transactions if t["contract_address"] == contract_address]

    measure_interval = {}
    start_block_number = 0
    balance = {}

    for end_block_number in block_intervals:

        interval_transactions = [
            t for t in transactions if t["block_number"] > start_block_number and t["block_number"] <= end_block_number]

        for transaction in interval_transactions:
            if transaction["value"] > 0:
                if transaction["from_address"] in balance.keys():
                    if balance[transaction["from_address"]] - transaction["value"] <= 0:
                        del balance[transaction["from_address"]]
                if transaction["to_address"] in balance.keys():
                    balance[transaction["to_address"]] += transaction["value"]
                else:
                    balance[transaction["to_address"]] = transaction["value"]

        measure = func(balance.values())

        measure_interval[end_block_number] = measure

        start_block_number = end_block_number

    return measure_interval


def calc_contract_measure(contracts: list, transactions: list, func, interval_count: int = 10):
    contract_interval = []

    for contract in contracts:
        contract_transactions = [
            t for t in transactions if t["contract_address"] == contract["address"]]

        if len(contract_transactions) > 0:
            contract_block_numbers = [t["block_number"]
                                      for t in contract_transactions]

            contract_block_intervals = list(np.linspace(
                min(contract_block_numbers), max(contract_block_numbers), interval_count + 1, dtype=int))
            del contract_block_intervals[0]

            measure_interval = calc_interval_fast(contract_transactions,
                                                  contract["address"], contract_block_intervals, func)

            contract_interval.append(
                {
                    "contract_address": contract["address"],
                    "contract_symbol": contract["symbol"],
                    "transaction_count": len(contract_transactions),
                    "measure_interval": measure_interval
                }
            )

    return contract_interval


def evaluate_contract_measure(contract_interval: list, interval_count: int = 10):
    combined_interval = []

    for interval in range(interval_count):
        tmp_gini_interval = {
            "min": 1,
            "max": 0,
            "avg": 0
        }

        for contract in contract_interval:
            tmp_gini = list(contract["measure_interval"].values())[interval]
            if tmp_gini < tmp_gini_interval["min"]:
                tmp_gini_interval["min"] = tmp_gini
            if tmp_gini > tmp_gini_interval["max"]:
                tmp_gini_interval["max"] = tmp_gini
            tmp_gini_interval["avg"] += tmp_gini / \
                len(contract_interval)

        combined_interval.append(tmp_gini_interval)

    return {
        "contract_count": len(contract_interval),
        "interval_count": interval_count,
        "combined_interval": combined_interval
    }


def evaluate_contract_measure_evolution(transactions: list, contracts: list, func, interval_count: int = 10):
    transactions = [
        t for t in transactions if t["value"] is not None]

    for transaction in transactions:
        transaction["value"] = int(transaction["value"])

    contract_measure_intervall = calc_contract_measure(
        contracts, transactions, func, interval_count)

    contract_measure_evaluation = evaluate_contract_measure(
        contract_measure_intervall, interval_count)

    return contract_measure_intervall, contract_measure_evaluation


def create_measure_evolution_chart(contract_evaluation: dict, file_path: str, func_name: str):
    min_list = [g["min"]
                for g in contract_evaluation["combined_interval"]]
    max_list = [g["max"]
                for g in contract_evaluation["combined_interval"]]
    avg_list = [g["avg"]
                for g in contract_evaluation["combined_interval"]]

    x = np.arange(contract_evaluation["interval_count"])
    plt.figure(figsize=(12, 6))
    plt.plot(x, min_list)
    plt.plot(x, max_list)
    plt.plot(x, avg_list, color="red", linestyle="--")
    plt.fill_between(x, min_list, max_list, color='blue', alpha=.1)
    plt.xlabel("Interval")
    plt.ylabel(f"{func_name} Coefficient")

    plt.title(
        f"Research Question DAO Contract Evolution: Contract {func_name} Coefficient Evolution\n(contract_count: {contract_evaluation['contract_count']}, interval_count: {contract_evaluation['interval_count']})", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/contract_{func_name.lower()}_evolution.png", format="PNG")

    logging.info(
        f"Contract {func_name} Coefficient Evolution created (contract_count: {contract_evaluation['contract_count']}, interval_count: {contract_evaluation['interval_count']})")


def create_contract_measure_chart(contract_measure_intervall: dict, interval: int, file_path: str, func_name: str):
    contracts = {(c["contract_address"], c["contract_symbol"]): list(c["measure_interval"].values())[interval]
                 for c in contract_measure_intervall}

    sorted_contracts = dict(
        sorted(contracts.items(), key=lambda x: x[1], reverse=True))

    sorted_contract_symbols = [c[1] for c in sorted_contracts.keys()]

    contract_measure_values = list(sorted_contracts.values())

    avg_measure_values = sum(contract_measure_values) / \
        len(contract_measure_values)

    x = np.arange(len(contract_measure_values))
    fig = plt.figure(figsize=(12, 6))
    ax = fig.gca()
    plt.bar(x, contract_measure_values)
    plt.axhline(avg_measure_values, color="red", linestyle="--")
    plt.xlabel("Contract")
    plt.ylabel(f"{func_name} Coefficient")
    plt.xticks(x)
    ax.set_xticklabels(sorted_contract_symbols, rotation=90)

    plt.title(
        f"Research Question DAO Contract Evolution: Contract {func_name} Coefficient Interval\n(contract_count: {len(contract_measure_values)}, interval: {interval})", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/contract_{func_name.lower()}_interval_{interval}.png", format="PNG")

    logging.info(
        f"Contract {func_name} Coefficient Interval created (contract_count: {len(contract_measure_values)}, interval: {interval})")
