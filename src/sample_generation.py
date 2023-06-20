from connectors.moralis_connector import MoralisConnector
from connectors.infura_connector import InfuraConnector
import connectors.connector_config as connector_config
import random
import json

# params
sample_folder = "src/data_samples"

block_sample_name = "block_sample"
transaction_sample_name = "transaction_sample"
wallet_address_sample_name = "wallet_address_sample"
timeframe_block_sample_name = "timeframe_block_sample"
timeframe_transaction_sample_name = "timeframe_transaction_sample"

generate_block_sample = False
block_sample_size = 1000

generate_transaction_sample = False
transaction_sample_size = 1000

generate_wallet_address_sample = True
wallet_address_sample_size = 1000

generate_timeframe_block_sample = False
timeframe_block_sample_size = 1000

generate_timeframe_transaction_sample = True
timeframe_transaction_sample_size = 1000

earliest_block = 0
newst_block = 17000000

old_sample_earliest_block = 1000000
old_sample_newst_block = 2000000

new_sample_earliest_block = 16000000
new_sample_newst_block = 17000000


# create moralis connector
infura_connector = InfuraConnector(
    connector_config.INFURA_IP, connector_config.INFURA_API_KEY)


def generate_random_block_sample(earliest_block: int, newst_block: int, sample_size: int):
    sample = random.sample(range(earliest_block, newst_block+1), sample_size)

    return sample


def generate_random_transaction_sample(earliest_block: int, newst_block: int, sample_size: int):
    block_sample = random.sample(
        range(earliest_block, newst_block+1), sample_size)

    transaction_sample = []

    # get a single transaction from each random block
    for block_identifier in block_sample:
        block = infura_connector.get_block(block_identifier, False)

        block = block["result"]

        if len(block["transactions"]) != 0:
            transaction = random.choice(block["transactions"])

            transaction_sample.append(transaction)
        else:
            new_block_identifier = block_sample[0]
            while new_block_identifier in block_sample:
                new_block_identifier = random.randint(
                    earliest_block, newst_block+1)

            block_sample.append(new_block_identifier)

    return transaction_sample


def generate_random_wallet_address_sample(earliest_block: int, newst_block: int, sample_size: int):
    transaction_sample = generate_random_transaction_sample(
        earliest_block, newst_block, sample_size)

    wallet_address_sample = []

    # get a single transaction from each random block and get from address from the transaction
    for transaction_hash in transaction_sample:
        transaction = infura_connector.get_transaction(transaction_hash)

        transaction = transaction["result"]

        wallet_address = transaction["from"]

        wallet_address_sample.append(wallet_address)

    return wallet_address_sample


def generate_random_timeframe_block_sample(old_sample_earliest_block: int, old_sample_newst_block: int, new_sample_earliest_block: int, new_sample_newst_block: int, sample_size: int):
    old_block_sample = generate_random_block_sample(
        old_sample_earliest_block, old_sample_newst_block, sample_size)
    new_block_sample = generate_random_block_sample(
        new_sample_earliest_block, new_sample_newst_block, sample_size)

    return {
        "old_block_sample": old_block_sample,
        "new_block_sample": new_block_sample
    }


def generate_random_timeframe_transaction_sample(old_sample_earliest_block: int, old_sample_newst_block: int, new_sample_earliest_block: int, new_sample_newst_block: int, sample_size: int):
    old_transaction_sample = generate_random_transaction_sample(
        old_sample_earliest_block, old_sample_newst_block, sample_size)
    new_transaction_sample = generate_random_transaction_sample(
        new_sample_earliest_block, new_sample_newst_block, sample_size)

    return {
        "old_transaction_sample": old_transaction_sample,
        "new_transaction_sample": new_transaction_sample
    }


def write_sample_to_json(sample: list, sample_folder: str, sample_name: str):
    sample_json = json.dumps(sample, indent=4)

    with open(f"{sample_folder}/{sample_name}.json", "w") as outfile:
        outfile.write(sample_json)


if __name__ == "__main__":
    # generate block sample
    if generate_block_sample:
        sample = generate_random_block_sample(
            earliest_block, newst_block, block_sample_size)

        write_sample_to_json(sample, sample_folder, block_sample_name)
        print("Block sample generated")

    # generate transaction sample
    if generate_transaction_sample:
        transaction_sample = generate_random_transaction_sample(
            earliest_block, newst_block, transaction_sample_size)

        write_sample_to_json(transaction_sample,
                             sample_folder, transaction_sample_name)
        print("Transaction sample generated")

    # generate address sample
    if generate_wallet_address_sample:
        wallet_address_sample = generate_random_wallet_address_sample(
            earliest_block, newst_block, wallet_address_sample_size)

        write_sample_to_json(wallet_address_sample,
                             sample_folder, wallet_address_sample_name)
        print("Wallet Address sample generated")

    # generate old-new block sample
    if generate_timeframe_block_sample:
        timeframe_block_sample = generate_random_timeframe_block_sample(
            old_sample_earliest_block, old_sample_newst_block, new_sample_earliest_block, new_sample_newst_block, timeframe_block_sample_size)

        write_sample_to_json(timeframe_block_sample,
                             sample_folder, timeframe_block_sample_name)
        print("Timeframe Block sample generated")

    # generate old-new transaction sample
    if generate_timeframe_transaction_sample:
        timeframe_transaction_sample = generate_random_timeframe_transaction_sample(
            old_sample_earliest_block, old_sample_newst_block, new_sample_earliest_block, new_sample_newst_block, timeframe_transaction_sample_size)

        write_sample_to_json(timeframe_transaction_sample,
                             sample_folder, timeframe_transaction_sample_name)
        print("Timeframe Transaction sample generated")
