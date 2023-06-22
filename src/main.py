import evalutation_config as config
from evaluation.evaluation_controller import EvaluationController
from data_sample import *

old_block_sample = timeframe_block_sample["old_block_sample"][:2]
new_block_sample = timeframe_block_sample["new_block_sample"][:2]

timeframe_block_sample["old_block_sample"] = old_block_sample
timeframe_block_sample["new_block_sample"] = new_block_sample

old_transaction_sample = timeframe_transaction_sample["old_transaction_sample"][:2]
new_transaction_sample = timeframe_transaction_sample["new_transaction_sample"][:2]

timeframe_transaction_sample["old_transaction_sample"] = old_transaction_sample
timeframe_transaction_sample["new_transaction_sample"] = new_transaction_sample


evaluation_controller = EvaluationController(
    block_sample[:2],
    transaction_sample[:2],
    wallet_address_sample[:2],
    timeframe_block_sample,
    timeframe_transaction_sample
)


if __name__ == "__main__":
    # evaluate data correctness
    evaluation_controller.evaluate_data_correctness(
        config.DATA_CORRECTNESS_EVALUATE_BLOCK_CORRECTNESS,
        config.DATA_CORRECTNESS_EVALUATE_TRANSACTION_CORRECTNESS,
        config.DATA_CORRECTNESS_FILE_PATH)

    # evaluate heuristic
    evaluation_controller.evaluate_heuristic(
        config.HEURISTIC_EVALUATE_TRANSACTION_COUNT,
        config.HEURISTIC_EVALUATE_WALLET_BALANCE,
        config.HEURISTIC_FILE_PATH)

    # evaluate performance
    evaluation_controller.evaluate_performance(
        config.PERFORMANCE_EVALUATE_API_PROVIDER,
        config.PERFORMANCE_EVALUATE_TIMEFRAME,
        config.PERFORMANCE_FILE_PATH)

    # evaluate research question token evolution
    evaluation_controller.evaluate_research_question_token_evolution(
        config.RESEARCH_QUESTION_TOKEN_EVOLUTION_DESCRIPTIVE,
        config.RESEARCH_QUESTION_TOKEN_EVOLUTION_CONTRACT_ADDRESS,
        config.RESEARCH_QUESTION_TOKEN_EVOLUTION_TOKEN_ID,
        config.RESEARCH_QUESTION_TOKEN_EVOLUTION_FILE_PATH)

    # evaluate research question contract evolution
    evaluation_controller.evaluate_research_question_contract_evolution(
        config.RESEARCH_QUESTION_CONTRACT_EVOLUTION,
        config.RESEARCH_QUESTION_CONTRACT_EVOLUTION_FILE_PATH
    )

    # evaluate research question dao contract evolution
    evaluation_controller.evaluate_research_question_dao_contract_evolution(
        config.RESEARCH_QUESTION_DAO_CONTRACT_EVOLUTION,
        config.RESEARCH_QUESTION_DAO_CONTRACT_EVOLUTION_CONTRACT_ADDRESS,
        config.RESEARCH_QUESTION_DAO_CONTRACT_EVOLUTION_FILE_PATH
    )
