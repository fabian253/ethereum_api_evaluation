import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)


def create_contract_deploy_history_hist(contract_data: list, token_standard: str, from_block: Union[int, None] = None, to_block: Union[int, None] = None, file_path: str = None):
    block_occurrence = [contract["block_deployed"]
                        for contract in contract_data]

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
        f"Research Question Contract Evolution: Contract Deploy History ({token_standard})\n[{from_block}, {to_block}]", {"fontsize": 10})
    plt.tight_layout()
    plt.savefig(
        f"{file_path}/contract_deploy_history_{token_standard}_{from_block}_{to_block}.png", format="PNG")

    logging.info(
        f"Contract Deploy History created (token_standard: {token_standard}, from_block: {from_block}, to_block: {to_block})")


def create_contract_deploy_history(contract_data: list, from_block: Union[int, None] = None, to_block: Union[int, None] = None, file_path: str = None):
    contracts = [
        contract for contract in contract_data if contract["block_deployed"] is not None]

    contract_block_deployed_list = list([contract["block_deployed"]
                                         for contract in contracts])

    if from_block is None:
        from_block = min(contract_block_deployed_list)
    else:
        contracts = [
            contract for contract in contracts if contract["block_deployed"] >= from_block]

    if to_block is None:
        to_block = max(contract_block_deployed_list)
    else:
        contracts = [
            contract for contract in contracts if contract["block_deployed"] <= to_block]

    erc20_contracts = [
        contract for contract in contracts if contract["ERC20"] == 1]

    erc721_contracts = [
        contract for contract in contracts if contract["ERC721"] == 1]

    other_contracts = [
        contract for contract in contracts if contract["ERC20"] == 0 and contract["ERC721"] == 0]

    create_contract_deploy_history_hist(
        contracts, "all", from_block, to_block, file_path)
    create_contract_deploy_history_hist(
        erc20_contracts, "ERC20", from_block, to_block, file_path)
    create_contract_deploy_history_hist(
        erc721_contracts, "ERC721", from_block, to_block, file_path)
    create_contract_deploy_history_hist(
        other_contracts, "other", from_block, to_block, file_path)
