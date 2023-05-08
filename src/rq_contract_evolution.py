from connectors.ethereum_api_connector import EthereumApiConnector
from connectors.sql_database_connector import SqlDatabaseConnector
import db_metadata.sql_tables as tables
import config
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from typing import Union

# analysis flags
with_contract_mint_history = True

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


def create_contract_mint_history(from_block: Union[int, None] = None, to_block: Union[int, None] = None):
    def create_contract_mint_history_hist(contracts, token_standard, from_block, to_block):
        block_occurrence = [contract["block_minted"]
                            for contract in contracts]

        total_intervall = to_block - from_block
        bin_count = 50
        bin_size = total_intervall / bin_count

        bins = [int(from_block + bin*bin_size)
                for bin in range(bin_count+1)]

        binned_block_occurrence = np.digitize(block_occurrence, bins)

        binned_block_occurrence_dict = dict(sorted(
            Counter(binned_block_occurrence).items()))

        for bin_index in range(1, bin_count+2):
            if bin_index not in binned_block_occurrence_dict.keys():
                binned_block_occurrence_dict[bin_index] = 0

        sorted_binned_block_occurrence_dict = {
            i: binned_block_occurrence_dict[i] for i in range(1, bin_count+2)}

        sorted_binned_block_occurrence_counter = list(
            sorted_binned_block_occurrence_dict.values())

        y_pos = np.arange(len(bins))
        plt.figure(figsize=(12, 6))
        plt.bar(y_pos, sorted_binned_block_occurrence_counter)
        plt.xticks(y_pos-0.5, bins, rotation=90)
        plt.xlabel("Block Number")
        plt.ylabel("Contract Count")

        plt.title(
            f"Contract Mint History ({token_standard})\n[{from_block}, {to_block}]", {"fontsize": 10})
        plt.tight_layout()
        plt.savefig(
            f"src/research_question_evaluation_ce/contract_mint_history_{token_standard}_{from_block}_{to_block}.png", format="PNG")

    contracts = sql_db_connector.query_data(
        config.SQL_DATABASE_TABLE_CONTRACT, ["contract_address", "block_minted", "ERC20", "ERC721"], limit=100000)

    contracts = [
        contract for contract in contracts if contract["block_minted"] is not None]

    contract_block_minted_list = list([contract["block_minted"]
                                       for contract in contracts])

    if from_block is None:
        from_block = min(contract_block_minted_list)
    else:
        contracts = [
            contract for contract in contracts if contract["block_minted"] >= from_block]

    if to_block is None:
        to_block = max(contract_block_minted_list)
    else:
        contracts = [
            contract for contract in contracts if contract["block_minted"] <= to_block]

    erc20_contracts = [
        contract for contract in contracts if contract["ERC20"] == 1]

    erc721_contracts = [
        contract for contract in contracts if contract["ERC721"] == 1]

    other_contracts = [
        contract for contract in contracts if contract["ERC20"] == 0 and contract["ERC721"] == 0]

    create_contract_mint_history_hist(contracts, "all", from_block, to_block)
    create_contract_mint_history_hist(
        erc20_contracts, "ERC20", from_block, to_block)
    create_contract_mint_history_hist(
        erc721_contracts, "ERC721", from_block, to_block)
    create_contract_mint_history_hist(
        other_contracts, "other", from_block, to_block)


if __name__ == "__main__":
    if with_contract_mint_history:
        create_contract_mint_history()
        create_contract_mint_history(from_block=10000000)
