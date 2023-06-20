import json

with open("src/data_sample/block_sample.json", "r") as infile:
    block_sample = json.load(infile)

with open("src/data_sample/transaction_sample.json", "r") as infile:
    transaction_sample = json.load(infile)

with open("src/data_sample/wallet_address_sample.json", "r") as infile:
    wallet_address_sample = json.load(infile)

with open("src/data_sample/timeframe_block_sample.json", "r") as infile:
    timeframe_block_sample = json.load(infile)

with open("src/data_sample/timeframe_transaction_sample.json", "r") as infile:
    timeframe_transaction_sample = json.load(infile)
