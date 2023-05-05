from connectors.ethereum_api_connector import EthereumApiConnector
from connectors.sql_database_connector import SqlDatabaseConnector
import db_metadata.sql_tables as tables
import config
import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

# analysis flags
with_token_transaction_graph = False
with_token_transaction_frequency = False
with_contract_transaction_history = True

# init ethereum api connector
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


def create_token_transaction_graph(contract_address, token_id):
    token_transactions = sql_db_connector.query_token_transactions(
        config.SQL_DATABASE_TABLE_TRANSACTION, contract_address, token_id)

    token_transactions = [(transaction["from_address"], transaction["to_address"])
                          for transaction in token_transactions]

    graph = nx.DiGraph()

    graph.add_edges_from(token_transactions)

    edge_labels = {transaction: index for index,
                   transaction in enumerate(token_transactions)}

    pos = nx.kamada_kawai_layout(graph)

    plt.margins(x=0.4)
    plt.title(
        f"Token Transactions \nContract: {contract_address}, Token: {token_id}", {"fontsize": 10})

    nx.draw(graph, pos=pos)
    nx.draw_networkx_labels(graph, pos, font_size=7)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=7)

    plt.savefig(
        "src/research_question_evaluation_te/token_transaction_graph.png", format="PNG")


def create_token_transaction_frequency_graph(contract_address: str):
    contract_transactions = sql_db_connector.query_erc721_contract_transactions(
        config.SQL_DATABASE_TABLE_TRANSACTION, contract_address)

    token_occurrence = [transaction["token_id"]
                        for transaction in contract_transactions]

    token_occurrence_counter = dict(sorted(
        Counter(token_occurrence).items()))

    token_occurrence_counter_array = np.array(
        list(token_occurrence_counter.values()))

    plt.hist(token_occurrence_counter_array, bins=np.arange(
        token_occurrence_counter_array.min(), token_occurrence_counter_array.max()+1), log=True)

    plt.title(
        f"Token Transaction Frequency \nContract: {contract_address}", {"fontsize": 10})
    plt.savefig(
        "src/research_question_evaluation_te/token_transaction_frequency.png", format="PNG")


def create_contract_transaction_history(contract_address: str):
    contract_transactions = sql_db_connector.query_erc721_contract_transactions(
        config.SQL_DATABASE_TABLE_TRANSACTION, contract_address)

    block_occurrence = [transaction["block_number"]
                        for transaction in contract_transactions]

    block_occurrence_counter_array = np.array(
        list(block_occurrence))

    total_intervall = block_occurrence_counter_array.max() - \
        block_occurrence_counter_array.min()
    bin_count = 50
    bin_size = total_intervall / bin_count

    bins = [int(block_occurrence_counter_array.min() + bin*bin_size)
            for bin in range(bin_count+1)]

    binned_block_occurrence = np.digitize(block_occurrence, bins)

    binned_block_occurrence_counter = list(dict(sorted(
        Counter(binned_block_occurrence).items())).values())

    y_pos = np.arange(len(bins))
    plt.figure(figsize=(12,6))
    plt.bar(y_pos, binned_block_occurrence_counter)
    plt.xticks(y_pos-0.5, bins, rotation=90)

    plt.title(
        f"Contract Transaction History \nContract: {contract_address}", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        "src/research_question_evaluation_te/contract_transaction_history.png", format="PNG")


if __name__ == "__main__":
    contract_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
    token_id = 4361

    if with_token_transaction_graph:
        create_token_transaction_graph(
            contract_address, token_id)

    if with_token_transaction_frequency:
        create_token_transaction_frequency_graph(contract_address)

    if with_contract_transaction_history:
        create_contract_transaction_history(contract_address)
