from connectors.moralis_connector import MoralisConnector
import config
import random
import json

# params
generate_block_sample = False
block_sample_size = 10

generate_transaction_sample = False
transaction_sample_size = 10

latest_block = 16777791


# create moralis connector
moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)


def generate_random_block_sample(latest_block: int, sample_size: int, file_path: str):
    sample = random.sample(range(0, latest_block+1), sample_size)

    sample_json = json.dumps(sample, indent=4)

    with open(file_path, "w") as outfile:
        outfile.write(sample_json)


def generate_random_transaction_sample(latest_block: int, sample_size: int, file_path: str):
    block_sample = random.sample(range(0, latest_block+1), sample_size)

    transaction_sample = []

    # get a single transaction from each random block
    for block_identifier in block_sample:
        block = moralis_connector.get_block(block_identifier, False)

        transaction = random.choice(block["transactions"])

        transaction_sample.append(transaction)

    sample_json = json.dumps(transaction_sample, indent=4)

    with open(file_path, "w") as outfile:
        outfile.write(sample_json)


if __name__ == "__main__":
    # generate sample
    if generate_block_sample:
        generate_random_block_sample(
            latest_block, block_sample_size, "evaluation/data_samples/block_sample.json")

    # generate sample
    if generate_transaction_sample:
        generate_random_transaction_sample(
            latest_block, transaction_sample_size, "evaluation/data_samples/transaction_sample.json")
