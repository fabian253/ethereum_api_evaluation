import matplotlib.pyplot as plt
import numpy as np
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)


def create_holder_history_stats(dao_contract_transactions: list) -> dict:
    """
    Structure of list per dict key:
    - holder_count
    - holder_change
    - new_holder_count
    - old_holder_count
    - average_value
    """
    blocks = list(set([t["block_number"]
                  for t in dao_contract_transactions if t["block_number"] is not None]))
    blocks.sort()

    previous_block = {}
    block = {}
    holder_statistic = {b: [] for b in blocks}

    for index, block_number in enumerate(blocks):
        transactions = [
            t for t in dao_contract_transactions if t["block_number"] == block_number]

        block = {}

        if previous_block is None:
            for transaction in transactions:
                block[transaction["to_address"]] = int(transaction["value"])
        else:
            for transaction in transactions:
                from_address = transaction["from_address"]
                to_address = transaction["to_address"]
                value = int(transaction["value"])
                # copy holder of previous block
                block = previous_block.copy()
                # add from_address to block
                if not from_address in block:
                    block[from_address] = 0
                # add to_adress to block
                if not to_address in block:
                    block[to_address] = 0

                # perform transaction
                block[from_address] -= value
                block[to_address] += value

            # remove holders with no balance
            block = {key: value for key, value in block.items() if value > 0}

        # create holder statistic
        holder_count = len(block.keys())
        holder_count_change = len(block.keys()) - len(previous_block.keys())
        holder_count_old = len(
            list(set(previous_block.keys()) & set(block.keys())))
        holder_count_new = holder_count - holder_count_old
        average_value = sum(block.values())/len(block.values())

        holder_statistic[block_number] = [
            holder_count, holder_count_change, holder_count_old, holder_count_new, average_value]

        # set previous block for next block transactions
        previous_block = block

    logging.info("Holder History Stats created")

    return holder_statistic


def create_holder_value_state(dao_contract_transactions: list, block_number: Union[int, None] = None):
    blocks = list(set([t["block_number"]
                  for t in dao_contract_transactions if t["block_number"] is not None]))

    blocks.sort()

    if block_number is not None:
        blocks = [b for b in blocks if b <= block_number]
    else:
        block_number = blocks[-1]

    previous_block = {}
    block = {}

    for index, block_number in enumerate(blocks):
        transactions = [
            t for t in dao_contract_transactions if t["block_number"] == block_number]

        block = {}

        if previous_block is None:
            for transaction in transactions:
                block[transaction["to_address"]] = int(transaction["value"])
        else:
            for transaction in transactions:
                from_address = transaction["from_address"]
                to_address = transaction["to_address"]
                value = int(transaction["value"])
                # copy holder of previous block
                block = previous_block.copy()
                # add from_address to block
                if not from_address in block:
                    block[from_address] = 0
                # add to_adress to block
                if not to_address in block:
                    block[to_address] = 0

                # perform transaction
                block[from_address] -= value
                block[to_address] += value

            # remove holders with no balance
            block = {key: value for key, value in block.items() if value > 0}

        # set previous block for next block transactions
        previous_block = block

    logging.info("Holder Value State created")

    return block


def create_holder_history_chart(holder_history_stats, contract_address: str, file_path: str):
    from_block = int(list(holder_history_stats.keys())[0])
    to_block = int(list(holder_history_stats.keys())[-1])
    total_intervall = to_block - from_block
    bin_count = 50
    bin_size = total_intervall / bin_count

    bins = [int(from_block + bin*bin_size)
            for bin in range(bin_count+1)]

    binned_stats = []

    for index, bin in enumerate(bins):
        bin_stats = {k: v for k, v in holder_history_stats.items()
                     if int(k) >= bin and int(k) < bin+bin_size}

        if len(bin_stats) == 0:
            bin_holder_count = binned_stats[index-1]
        else:
            bin_holder_count = list(bin_stats.values())[0][0]

        binned_stats.append(bin_holder_count)

    y_pos = np.arange(len(bins))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, binned_stats)
    plt.xticks(y_pos-0.5, bins, rotation=90)
    plt.xlabel("Block Number")
    plt.ylabel("Holder Count")

    plt.title(
        f"Research Question DAO Contract Evolution: Token Holder Count History ({contract_address})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/token_holder_history.png", format="PNG")

    logging.info(
        f"Token Holder Count History created (contract_address: {contract_address}, from_block: {from_block}, to_block: {to_block})")


def create_holder_change_history_chart(holder_history_stats, contract_address: str, file_path: str):
    from_block = int(list(holder_history_stats.keys())[0])
    to_block = int(list(holder_history_stats.keys())[-1])
    total_intervall = to_block - from_block
    bin_count = 50
    bin_size = total_intervall / bin_count

    bins = [int(from_block + bin*bin_size)
            for bin in range(bin_count+1)]

    binned_stats = []

    for index, bin in enumerate(bins):
        bin_stats = {k: v for k, v in holder_history_stats.items()
                     if int(k) >= bin and int(k) < bin+bin_size}

        if len(bin_stats) == 0:
            bin_holder_count = binned_stats[index-1]
        else:
            bin_holder_count = list(
                bin_stats.values())[-1][0] - list(bin_stats.values())[0][0]

        binned_stats.append(bin_holder_count)

    y_pos = np.arange(len(bins))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, binned_stats)
    plt.xticks(y_pos-0.5, bins, rotation=90)
    plt.xlabel("Block Number")
    plt.ylabel("Holder Count")

    plt.title(
        f"Research Question DAO Contract Evolution: Token Holder Change History ({contract_address})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/token_holder_change_history.png", format="PNG")

    logging.info(
        f"Token Holder Change History created (contract_address: {contract_address}, from_block: {from_block}, to_block: {to_block})")


def create_holder_value_state_distribution_chart(holder_value_state, contract_address: str, file_path: str):
    from_value = min(list(holder_value_state.values()))
    to_value = max(list(holder_value_state.values()))
    total_intervall = to_value - from_value
    bin_count = 50
    bin_size = total_intervall / bin_count

    bins = [int(from_value + bin*bin_size)
            for bin in range(bin_count+1)]

    binned_state = []

    for index, bin in enumerate(bins):
        bin_state = {k: v for k, v in holder_value_state.items()
                     if v >= bin and v < bin+bin_size}

        bin_holder_value_count = len(bin_state)

        binned_state.append(bin_holder_value_count)

    y_pos = np.arange(len(bins))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, binned_state)
    plt.xticks(y_pos-0.5, bins, rotation=90)
    plt.yscale('log')
    plt.xlabel("Value")
    plt.ylabel("Holder Count")

    plt.title(
        f"Research Question DAO Contract Evolution: Holder Value Distribution ({contract_address})\n[{from_value}, {to_value}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/holder_value_distribution.png", format="PNG")

    logging.info(
        f"Holder Value Distribution created (contract_address: {contract_address}, from_value: {from_value}, to_value: {to_value})")


def create_transaction_history_chart(dao_contract_transactions: list, contract_address: str, file_path: str):
    blocks = list(set([t["block_number"]
                  for t in dao_contract_transactions if t["block_number"] is not None]))
    blocks.sort()

    from_block = min(blocks)
    to_block = max(blocks)
    total_intervall = to_block - from_block
    bin_count = 50
    bin_size = total_intervall / bin_count

    bins = [int(from_block + bin*bin_size)
            for bin in range(bin_count+1)]

    binned_transaction_count = []
    binned_transaction_value = []

    for index, bin in enumerate(bins):
        bin_transactions = [v for v in dao_contract_transactions if v["block_number"]
                            >= bin and v["block_number"] < bin + bin_size]

        bin_trans_count = len(bin_transactions)
        bin_value = list([int(t["value"]) for t in bin_transactions])
        bin_trans_value = sum(bin_value)

        binned_transaction_count.append(bin_trans_count)
        binned_transaction_value.append(bin_trans_value)

    y_pos = np.arange(len(bins))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, binned_transaction_count)
    plt.xticks(y_pos-0.5, bins, rotation=90)
    plt.xlabel("Block Number")
    plt.ylabel("Transaction Count")

    plt.title(
        f"Research Question DAO Contract Evolution: Transaction Count Distribution ({contract_address})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/transaction_count_distribution.png", format="PNG")

    logging.info(
        f"Transaction Count Distribution created (contract_address: {contract_address}, from_block: {from_block}, to_block: {to_block})")

    y_pos = np.arange(len(bins))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, binned_transaction_value)
    plt.xticks(y_pos-0.5, bins, rotation=90)
    plt.xlabel("Block Number")
    plt.ylabel("Transaction Value")

    plt.title(
        f"Research Question DAO Contract Evolution: Transaction Value Distribution ({contract_address})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/transaction_value_distribution.png", format="PNG")

    logging.info(
        f"Transaction Value Distribution created (contract_address: {contract_address}, from_block: {from_block}, to_block: {to_block})")
