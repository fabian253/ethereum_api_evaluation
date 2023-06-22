import json

with open("src/data_sample/block_sample.json", "r") as f:
    block_sample = json.load(f)

with open("src/data_sample/transaction_sample.json", "r") as f:
    transaction_sample = json.load(f)

with open("src/data_sample/wallet_address_sample.json", "r") as f:
    wallet_address_sample = json.load(f)

with open("src/data_sample/timeframe_block_sample.json", "r") as f:
    timeframe_block_sample = json.load(f)

with open("src/data_sample/timeframe_transaction_sample.json", "r") as f:
    timeframe_transaction_sample = json.load(f)

with open("src/data_sample/contract_address_sample.json", "r") as f:
    contract_address_sample = json.load(f)
