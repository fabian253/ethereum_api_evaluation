import evaluation.data_correctness as data_correctness
import evaluation.heuristic as heuristic
import json


class EvaluationController():

    def __init__(self,
                 block_sample,
                 transaction_sample,
                 wallet_address_sample,
                 early_late_block_sample,
                 early_late_transaction_sample) -> None:
        self.block_sample = block_sample
        self.transaction_sample = transaction_sample
        self.wallet_address_sample = wallet_address_sample
        self.early_late_block_sample = early_late_block_sample
        self.early_late_transaction_sample = early_late_transaction_sample

    def evaluate_data_correctness(self, eval_block_correctness: bool, eval_transaction_correctness: bool, file_path: str):
        # evaluate block correctness
        if eval_block_correctness:
            block_sample_conformity = data_correctness.process_block_sample(
                self.block_sample)

            with open(f"{file_path}/block_sample_conformity.json", "w") as f:
                json.dump(block_sample_conformity, f, indent=4)

            block_sample_evaluation = data_correctness.evaluate_block_sample_conformity(
                block_sample_conformity)

            with open(f"{file_path}/block_sample_evaluation.json", "w") as f:
                json.dump(block_sample_evaluation, f, indent=4)

            data_correctness.create_block_correctness_chart(
                block_sample_evaluation, f"{file_path}/block_correctness_evaluation.png")

        # evaluate transaction correctness
        if eval_transaction_correctness:
            transaction_sample_conformity = data_correctness.process_transaction_sample(
                self.transaction_sample)

            with open(f"{file_path}/transaction_sample_conformity.json", "w") as f:
                json.dump(transaction_sample_conformity, f, indent=4)

            transaction_sample_evaluation = data_correctness.evaluate_transaction_sample_conformity(
                transaction_sample_conformity)

            with open(f"{file_path}/transaction_sample_evaluation.json", "w") as f:
                json.dump(transaction_sample_evaluation, f, indent=4)

            data_correctness.create_transaction_correctness_chart(
                transaction_sample_evaluation, f"{file_path}/transaction_correctness_evaluation.png")

    def evaluate_heuristic(self, eval_transaction_count: bool, eval_wallet_balance: bool, file_path: str):
        # evaluate transaction count
        if eval_transaction_count:
            transaction_count_sample_conformity = heuristic.process_transaction_count_sample(
                self.block_sample)

            with open(f"{file_path}/transaction_count_sample_conformity.json", "w") as f:
                json.dump(transaction_count_sample_conformity, f, indent=4)

            transaction_count_sample_evaluation = heuristic.evaluate_transaction_count_sample_conformity(
                transaction_count_sample_conformity)

            with open(f"{file_path}/transaction_count_sample_evaluation.json", "w") as f:
                json.dump(transaction_count_sample_evaluation, f, indent=4)

            heuristic.create_transaction_count_correctness_chart(
                transaction_count_sample_evaluation, f"{file_path}/transaction_count_evaluation.png")

        # evaluate wallet balance
        if eval_wallet_balance:
            wallet_balance_sample_conformity = heuristic.process_balance_sample(
                self.wallet_address_sample)

            with open(f"{file_path}/wallet_balance_sample_conformity.json", "w") as f:
                json.dump(wallet_balance_sample_conformity, f, indent=4)

            wallet_balance_sample_evaluation = heuristic.evaluate_wallet_address_sample_conformity(
                wallet_balance_sample_conformity)

            with open(f"{file_path}/wallet_balance_sample_evaluation.json", "w") as f:
                json.dump(wallet_balance_sample_evaluation, f, indent=4)

            heuristic.create_wallet_balance_correctness_chart(
                transaction_count_sample_evaluation, f"{file_path}/wallet_balance_evaluation.png")
