from connectors.moralis_connector import MoralisConnector
import config
import random
import json

# params
sample_folder = "evaluation/data_samples"

block_sample_name = "block_sample"
transaction_sample_name = "transaction_sample"
wallet_address_sample_name = "wallet_address_sample"
early_late_block_sample_name = "early_late_block_sample"
early_late_transaction_sample_name = "early_late_transaction_sample"

generate_block_sample = False
block_sample_size = 10

generate_transaction_sample = False
transaction_sample_size = 10

generate_wallet_address_sample = False
wallet_address_sample_size = 10

generate_early_late_block_sample = True
early_late_block_sample_size = 10

generate_early_late_transaction_sample = True
early_late_transaction_sample_size = 10

earliest_block = 0
latest_block = 16777791

early_sample_earliest_block = 1000000
early_sample_latest_block = 2000000

late_sample_earliest_block = 16000000
late_sample_latest_block = 16777791


# create moralis connector
moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)


def generate_random_block_sample(earliest_block: int, latest_block: int, sample_size: int):
    sample = random.sample(range(earliest_block, latest_block+1), sample_size)

    return sample


def generate_random_transaction_sample(earliest_block: int, latest_block: int, sample_size: int):
    block_sample = random.sample(
        range(earliest_block, latest_block+1), sample_size)

    transaction_sample = []

    # get a single transaction from each random block
    for block_identifier in block_sample:
        block = moralis_connector.get_block(block_identifier, False)

        if len(block["transactions"]) != 0:
            transaction = random.choice(block["transactions"])

            transaction_sample.append(transaction)
        else:
            new_block_identifier = block_sample[0]
            while new_block_identifier in block_sample:
                new_block_identifier = random.randint(
                    earliest_block, latest_block+1)

            block_sample.append(new_block_identifier)

    return transaction_sample


def generate_random_wallet_address_sample(earliest_block: int, latest_block: int, sample_size: int):
    transaction_sample = generate_random_transaction_sample(
        earliest_block, latest_block, sample_size)

    wallet_address_sample = []

    # get a single transaction from each random block and get from address from the transaction
    for transaction_hash in transaction_sample:
        transaction = moralis_connector.get_transaction(transaction_hash)

        wallet_address = transaction["from_address"]

        wallet_address_sample.append(wallet_address)

    return wallet_address_sample


def generate_random_early_late_block_sample(early_sample_earliest_block: int, early_sample_latest_block: int, late_sample_earliest_block: int, late_sample_latest_block: int, sample_size: int):
    early_block_sample = generate_random_block_sample(
        early_sample_earliest_block, early_sample_latest_block, sample_size)
    late_block_sample = generate_random_block_sample(
        late_sample_earliest_block, late_sample_latest_block, sample_size)

    return {
        "early_block_sample": early_block_sample,
        "late_block_sample": late_block_sample
    }


def generate_random_early_late_transaction_sample(early_sample_earliest_block: int, early_sample_latest_block: int, late_sample_earliest_block: int, late_sample_latest_block: int, sample_size: int):
    early_transaction_sample = generate_random_transaction_sample(
        early_sample_earliest_block, early_sample_latest_block, sample_size)
    late_transaction_sample = generate_random_transaction_sample(
        late_sample_earliest_block, late_sample_latest_block, sample_size)

    return {
        "early_transaction_sample": early_transaction_sample,
        "late_transaction_sample": late_transaction_sample
    }


def write_sample_to_json(sample: list, sample_folder: str, sample_name: str):
    sample_json = json.dumps(sample, indent=4)

    with open(f"{sample_folder}/{sample_name}.json", "w") as outfile:
        outfile.write(sample_json)


if __name__ == "__main__":
    # generate block sample
    if generate_block_sample:
        sample = generate_random_block_sample(
            earliest_block, latest_block, block_sample_size)

        write_sample_to_json(sample, sample_folder, block_sample_name)

    # generate transaction sample
    if generate_transaction_sample:
        transaction_sample = generate_random_transaction_sample(
            earliest_block, latest_block, transaction_sample_size)

        write_sample_to_json(transaction_sample,
                             sample_folder, transaction_sample_name)

    # generate address sample
    if generate_wallet_address_sample:
        wallet_address_sample = generate_random_wallet_address_sample(
            earliest_block, latest_block, wallet_address_sample_size)

        write_sample_to_json(wallet_address_sample,
                             sample_folder, wallet_address_sample_name)

    # generate early-late block sample
    if generate_early_late_block_sample:
        early_late_block_sample = generate_random_early_late_block_sample(
            early_sample_earliest_block, early_sample_latest_block, late_sample_earliest_block, late_sample_latest_block, early_late_block_sample_size)

        write_sample_to_json(early_late_block_sample,
                             sample_folder, early_late_block_sample_name)

    # generate early-late transaction sample
    if generate_early_late_transaction_sample:
        early_late_transaction_sample = generate_random_early_late_transaction_sample(
            early_sample_earliest_block, early_sample_latest_block, late_sample_earliest_block, late_sample_latest_block, early_late_block_sample_size)

        write_sample_to_json(early_late_transaction_sample,
                             sample_folder, early_late_transaction_sample_name)
