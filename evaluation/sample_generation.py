from connectors.moralis_connector import MoralisConnector
import config
import random
import json

# params
sample_folder = "evaluation/data_samples"

block_sample_name = "block_sample"
transaction_sample_name = "transaction_sample"
wallet_address_sample_name = "wallet_address_sample"

generate_block_sample = False
block_sample_size = 10

generate_transaction_sample = False
transaction_sample_size = 10

generate_wallet_address_sample = False
wallet_address_sample_size = 10

earliest_block = 0
latest_block = 16777791


# create moralis connector
moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)


def generate_random_block_sample(earliest_block: int, latest_block: int, sample_size: int, file_path: str):
    sample = random.sample(range(earliest_block, latest_block+1), sample_size)

    sample_json = json.dumps(sample, indent=4)

    with open(file_path, "w") as outfile:
        outfile.write(sample_json)


def generate_random_transaction_sample(earliest_block: int, latest_block: int, sample_size: int, file_path: str):
    block_sample = random.sample(
        range(earliest_block, latest_block+1), sample_size)

    transaction_sample = []

    # get a single transaction from each random block
    for block_identifier in block_sample:
        block = moralis_connector.get_block(block_identifier, False)

        transaction = random.choice(block["transactions"])

        transaction_sample.append(transaction)

    sample_json = json.dumps(transaction_sample, indent=4)

    with open(file_path, "w") as outfile:
        outfile.write(sample_json)


def generate_random_wallet_address_sample(earliest_block: int, latest_block: int, sample_size: int, file_path: str):
    block_sample = random.sample(
        range(earliest_block, latest_block+1), sample_size)

    wallet_address_sample = []

    # get a single transaction from each random block and get from address from the transaction
    for block_identifier in block_sample:
        block = moralis_connector.get_block(block_identifier, False)

        transaction_hash = random.choice(block["transactions"])

        transaction = moralis_connector.get_transaction(transaction_hash)

        wallet_address = transaction["from_address"]

        wallet_address_sample.append(wallet_address)

    sample_json = json.dumps(wallet_address_sample, indent=4)

    with open(file_path, "w") as outfile:
        outfile.write(sample_json)


if __name__ == "__main__":
    # generate block sample
    if generate_block_sample:
        generate_random_block_sample(
            earliest_block, latest_block, block_sample_size, f"{sample_folder}/{block_sample_name}.json")

    # generate block sample
    if generate_transaction_sample:
        generate_random_transaction_sample(
            earliest_block, latest_block, transaction_sample_size, f"{sample_folder}/{transaction_sample_name}.json")

    # generate address sample
    if generate_wallet_address_sample:
        generate_random_wallet_address_sample(
            earliest_block, latest_block, wallet_address_sample_size, f"{sample_folder}/{wallet_address_sample_name}.json")
