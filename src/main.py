import evalutation_config as config
from evaluation.evaluation_controller import EvaluationController
from data_sample import *

evaluation_controller = EvaluationController(
    block_sample,
    transaction_sample,
    wallet_address_sample,
    early_late_block_sample,
    early_late_transaction_sample
)


if __name__ == "__main__":
    # evaluate data correctness
    evaluation_controller.evaluate_data_correctness(
        config.DATA_CORRECTNESS_EVALUATE_BLOCK_CORRECTNESS, config.DATA_CORRECTNESS_EVALUATE_TRANSACTION_CORRECTNESS, config.DATA_CORRECTNESS_FILE_PATH)

    # evaluate heuristic
    evaluation_controller.evaluate_heuristic(
        config.HEURISTIC_EVALUATE_TRANSACTION_COUNT, config.HEURISTIC_EVALUATE_WALLET_BALANCE, config.HEURISTIC_FILE_PATH)
