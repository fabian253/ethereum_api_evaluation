import json

if __name__ == "__main__":
    with open("src/dataset/transaction_dataset.json", "r") as f:
        dataset = json.load(f)

    print(len(dataset))