import evalutation_config as config
from evaluation.evaluation_controller import EvaluationController
from data_sample import *


evaluation_controller = EvaluationController(
    block_sample,
    transaction_sample,
    wallet_address_sample,
    timeframe_block_sample,
    timeframe_transaction_sample,
    contract_address_sample
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
        config.RESEARCH_QUESTION_TOKEN_EVOLUTION_PATTERN,
        config.RESEARCH_QUESTION_TOKEN_EVOLUTION_CONTRACT_ADDRESS,
        config.RESEARCH_QUESTION_TOKEN_EVOLUTION_TOKEN_ID,
        config.RESEARCH_QUESTION_TOKEN_EVOLUTION_FILE_PATH)

    # evaluate research question contract evolution
    evaluation_controller.evaluate_research_question_contract_evolution(
        config.RESEARCH_QUESTION_CONTRACT_EVOLUTION,
        config.RESEARCH_QUESTION_CONTRACT_EVOLUTION_FILE_PATH,
        config.RESEARCH_QUESTION_CONTRACT_EVOLUTION_FROM_BLOCK,
        config.RESEARCH_QUESTION_CONTRACT_EVOLUTION_TO_BLOCK
    )

    # evaluate research question dao contract evolution
    evaluation_controller.evaluate_research_question_dao_contract_evolution(
        config.RESEARCH_QUESTION_DAO_CONTRACT_EVOLUTION_DESCRIPTIVE,
        config.RESEARCH_QUESTION_DAO_CONTRACT_EVOLUTION_ANALYSIS,
        config.RESEARCH_QUESTION_DAO_CONTRACT_EVOLUTION_CONTRACT_ADDRESS,
        config.RESEARCH_QUESTION_DAO_CONTRACT_EVOLUTION_FILE_PATH
    )
