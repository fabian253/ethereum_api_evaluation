from connectors.ethereum_api_connector import EthereumApiConnector
from connectors.sql_database_connector import SqlDatabaseConnector
import db_metadata.sql_tables as tables
import config
import matplotlib.pyplot as plt
import numpy as np
from typing import Union
import json

# analysis flags
with_holder_count_history = False
with_holder_change_history = False
with_distribution_of_token_holder_count = False
with_transaction_history = True

ethereum_api_connector = EthereumApiConnector(
    config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)

# init sql database connector
sql_db_connector = SqlDatabaseConnector(
    config.SQL_DATABASE_HOST,
    config.SQL_DATABASE_PORT,
    config.SQL_DATABASE_USER,
    config.SQL_DATABASE_PASSWORD,
    config.SQL_DATABASE_NAME
)
sql_db_connector.use_database(config.SQL_DATABASE_NAME)
sql_db_connector.create_table(tables.TRANSACTION_TABLE)


def query_dao_transactions(contract_address: str):
    contract_transactions = sql_db_connector.query_erc20_contract_transactions(
        config.SQL_DATABASE_TABLE_TRANSACTION, contract_address)

    with open("src/research_question_evaluation_dao/dao_transactions.json", "w") as f:
        json.dump(contract_transactions, f, indent=4)


def create_holder_history_stats() -> dict:
    """
    Structure of list per dict key:
    - holder_count
    - holder_change
    - new_holder_count
    - old_holder_count
    - average_value
    """
    with open("src/research_question_evaluation_dao/dao_transactions.json", "r") as f:
        contract_transactions = json.load(f)

    blocks = list(set([t["block_number"]
                  for t in contract_transactions if t["block_number"] is not None]))
    blocks.sort()

    previous_block = {}
    block = {}
    holder_statistic = {b: [] for b in blocks}

    for index, block_number in enumerate(blocks):
        transactions = [
            t for t in contract_transactions if t["block_number"] == block_number]

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

        if index % 10 == 0:
            print(f"Block [{index}/{len(blocks)}]")

    with open("src/research_question_evaluation_dao/holder_history_stats.json", "w") as f:
        json.dump(holder_statistic, f, indent=4)

    return holder_statistic


def create_holder_value_state(block_number: Union[int, None] = None):
    with open("src/research_question_evaluation_dao/dao_transactions.json", "r") as f:
        contract_transactions = json.load(f)

    blocks = list(set([t["block_number"]
                  for t in contract_transactions if t["block_number"] is not None]))

    blocks.sort()

    if block_number is not None:
        blocks = [b for b in blocks if b <= block_number]
    else:
        block_number = blocks[-1]

    previous_block = {}
    block = {}

    for index, block_number in enumerate(blocks):
        transactions = [
            t for t in contract_transactions if t["block_number"] == block_number]

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

        if index % 10 == 0:
            print(f"Block [{index}/{len(blocks)}]")

    with open(f"src/research_question_evaluation_dao/holder_value_state_{block_number}.json", "w") as f:
        json.dump(block, f, indent=4)


def create_holder_history(contract_address: str):
    with open("src/research_question_evaluation_dao/holder_history_stats.json", "r") as f:
        holder_history_stats = json.load(f)

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

    plt.title(
        f"DAO Token Holder Count History ({contract_address})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"src/research_question_evaluation_dao/token_holder_history.png", format="PNG")


def create_holder_change_history(contract_address: str):
    with open("src/research_question_evaluation_dao/holder_history_stats.json", "r") as f:
        holder_history_stats = json.load(f)

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

    plt.title(
        f"DAO Token Holder Change History ({contract_address})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"src/research_question_evaluation_dao/token_holder_change_history.png", format="PNG")


def create_holder_value_state_distribution(contract_address: str):
    with open(f"src/research_question_evaluation_dao/holder_value_state_17136896.json", "r") as f:
        holder_value_state = json.load(f)

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

    plt.title(
        f"DAO Holder Value Distribution ({contract_address})\n[{from_value}, {to_value}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"src/research_question_evaluation_dao/holder_value_distribution.png", format="PNG")


def create_transaction_history(contract_address: str):
    with open("src/research_question_evaluation_dao/dao_transactions.json", "r") as f:
        contract_transactions = json.load(f)

    blocks = list(set([t["block_number"]
                  for t in contract_transactions if t["block_number"] is not None]))
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
        bin_transactions = [v for v in contract_transactions if v["block_number"]
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

    plt.title(
        f"DAO Transaction Count Distribution ({contract_address})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"src/research_question_evaluation_dao/transaction_count_distribution.png", format="PNG")

    y_pos = np.arange(len(bins))
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, binned_transaction_value)
    plt.xticks(y_pos-0.5, bins, rotation=90)

    plt.title(
        f"DAO Transaction Value Distribution ({contract_address})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"src/research_question_evaluation_dao/transaction_value_distribution.png", format="PNG")


if __name__ == "__main__":
    contract_address = "0x1a4b46696b2bb4794eb3d4c26f1c55f9170fa4c5"

    if with_holder_count_history:
        # create_holder_history_stats()
        create_holder_history(contract_address)

    if with_holder_change_history:
        create_holder_change_history(contract_address)

    if with_distribution_of_token_holder_count:
        # create_holder_value_state()
        create_holder_value_state_distribution(contract_address)

    if with_transaction_history:
        create_transaction_history(contract_address)
