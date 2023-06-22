import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)


def create_token_transaction_graph(contract_transactions: list, contract_address: str, token_id: int, file_path: str):
    token_transactions = [
        (transaction["from_address"], transaction["to_address"]) for transaction in contract_transactions if transaction["token_id"] == token_id]

    graph = nx.DiGraph()

    graph.add_edges_from(token_transactions)

    edge_labels = {transaction: index for index,
                   transaction in enumerate(token_transactions)}

    pos = nx.kamada_kawai_layout(graph)

    plt.figure(figsize=(12, 6))
    plt.margins(x=0.4)
    plt.title(
        f"Research Question Token Evolution: Token Transactions \nContract: {contract_address}, Token: {token_id}", {"fontsize": 10})

    nx.draw(graph, pos=pos)
    nx.draw_networkx_labels(graph, pos, font_size=7)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=7)

    plt.tight_layout()
    plt.savefig(
        f"{file_path}/token_transaction_graph.png", format="PNG")

    logging.info("Token Transaction Graph created")


def create_contract_transaction_frequency_chart(contract_transactions: list, contract_address: str, file_path: str):
    token_occurrence = [transaction["token_id"]
                        for transaction in contract_transactions]

    token_occurrence_counter = dict(sorted(
        Counter(token_occurrence).items()))

    token_occurrence_counter_array = np.array(
        list(token_occurrence_counter.values()))

    plt.figure(figsize=(12, 6))
    plt.hist(token_occurrence_counter_array, bins=np.arange(
        token_occurrence_counter_array.min(), token_occurrence_counter_array.max()+1), log=True)
    plt.xlabel("Transaction Count")
    plt.ylabel("Token Count")

    plt.title(
        f"Research Question Token Evolution: Contract Transaction Frequency \nContract: {contract_address}", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/contract_transaction_frequency.png", format="PNG")

    logging.info("Contract Transaction Frequency Chart created")


def create_contract_transaction_history(contract_transactions: list, contract_address: str, file_path: str):
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
    plt.figure(figsize=(12, 6))
    plt.bar(y_pos, binned_block_occurrence_counter)
    plt.xticks(y_pos-0.5, bins, rotation=90)
    plt.xlabel("Block Number")
    plt.ylabel("Transaction Count")

    plt.title(
        f"Research Question Token Evolution: Contract Transaction History \nContract: {contract_address}", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/contract_transaction_history.png", format="PNG")

    logging.info("Contract Transaction History created")
