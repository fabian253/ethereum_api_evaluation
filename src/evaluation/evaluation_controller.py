from connectors import sql_db_connector
import connectors.connector_config as connector_config
import evaluation.data_correctness as data_correctness
import evaluation.heuristic as heuristic
import evaluation.performance as performance
import evaluation.research_question as research_question
import json
import logging
from typing import Union

logging.basicConfig(level=logging.INFO)


class EvaluationController():

    def __init__(self,
                 block_sample,
                 transaction_sample,
                 wallet_address_sample,
                 timeframe_block_sample,
                 timeframe_transaction_sample,
                 contract_address_sample) -> None:
        self.block_sample = block_sample
        self.transaction_sample = transaction_sample
        self.wallet_address_sample = wallet_address_sample
        self.timeframe_block_sample = timeframe_block_sample
        self.timeframe_transaction_sample = timeframe_transaction_sample
        self.contract_address_sample = contract_address_sample

    def evaluate_data_correctness(self, eval_block_correctness: bool, eval_transaction_correctness: bool, file_path: str):
        # evaluate block correctness
        if eval_block_correctness:
            logging.info(
                "Data Correctness Evaluation started (Block Correctness)")

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

            logging.info(
                "Data Correctness Evaluation done (Block Correctness)")

        # evaluate transaction correctness
        if eval_transaction_correctness:
            logging.info(
                "Data Correctness Evaluation started (Transaction Correctness)")

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

            logging.info(
                "Data Correctness Evaluation done (Transaction Correctness)")

    def evaluate_heuristic(self, eval_transaction_count: bool, eval_wallet_balance: bool, file_path: str):
        # evaluate transaction count
        if eval_transaction_count:
            logging.info("Heuristic Evaluation started (Transaction Count)")

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

            logging.info("Heuristic Evaluation done (Transaction Count)")

        # evaluate wallet balance
        if eval_wallet_balance:
            logging.info("Heuristic Evaluation started (Wallet Balance)")

            wallet_balance_sample_conformity = heuristic.process_balance_sample(
                self.wallet_address_sample)

            with open(f"{file_path}/wallet_balance_sample_conformity.json", "w") as f:
                json.dump(wallet_balance_sample_conformity, f, indent=4)

            wallet_balance_sample_evaluation = heuristic.evaluate_wallet_address_sample_conformity(
                wallet_balance_sample_conformity)

            with open(f"{file_path}/wallet_balance_sample_evaluation.json", "w") as f:
                json.dump(wallet_balance_sample_evaluation, f, indent=4)

            heuristic.create_wallet_balance_correctness_chart(
                wallet_balance_sample_evaluation, f"{file_path}/wallet_balance_evaluation.png")

            logging.info("Heuristic Evaluation done (Wallet Balance)")

    def evaluate_performance(self, eval_api_provider_performance: bool, eval_timeframe_performance: bool, file_path: str):
        # api provider performance
        if eval_api_provider_performance:
            logging.info("Performance Evaluation started (API Provider)")

            block_request_time_performance = performance.process_block_sample(
                self.block_sample)

            transaction_request_time_performance = performance.process_transaction_sample(
                self.transaction_sample)

            request_time_performance = block_request_time_performance + \
                transaction_request_time_performance

            with open(f"{file_path}/api_provider_performance.json", "w") as f:
                json.dump(request_time_performance, f, indent=4)

            request_performance_evaluation = performance.evaluate_request_time_performance(
                request_time_performance)

            with open(f"{file_path}/api_performance_evaluation.json", "w") as f:
                json.dump(request_performance_evaluation, f, indent=4)

            performance.create_request_time_performance_chart(
                request_performance_evaluation, file_path)

            logging.info("Performance Evaluation done (API Provider)")

        # timeframe performance
        if eval_timeframe_performance:
            logging.info("Performance Evaluation started (Timeframe)")

            old_block_request_time_performance = performance.process_timeframe_block_sample(
                self.timeframe_block_sample["old_block_sample"], "old")
            new_block_request_time_performance = performance.process_timeframe_block_sample(
                self.timeframe_block_sample["new_block_sample"], "new")

            old_transaction_request_time_performance = performance.process_timeframe_transaction_sample(
                self.timeframe_transaction_sample["old_transaction_sample"], "old")
            new_transaction_request_time_performance = performance.process_timeframe_transaction_sample(
                self.timeframe_transaction_sample["new_transaction_sample"], "new")

            request_time_performance = old_block_request_time_performance + new_block_request_time_performance + \
                old_transaction_request_time_performance + \
                new_transaction_request_time_performance

            with open(f"{file_path}/timeframe_performance.json", "w") as f:
                json.dump(request_time_performance, f, indent=4)

            request_performance_evaluation = performance.evaluate_timeframe_request_time_performance(
                request_time_performance)

            with open(f"{file_path}/timeframe_performance_evaluation.json", "w") as f:
                json.dump(request_performance_evaluation, f, indent=4)

            performance.create_timeframe_request_time_performance_chart(
                request_performance_evaluation, file_path)

            logging.info("Performance Evaluation done (Timeframe)")

    def evaluate_research_question_token_evolution(self, eval_token_evolution_descriptive: bool, eval_token_evolution_pattern: bool, contract_address: str, token_id: int, file_path: str, use_db: bool = True):
        # token evolution decriptive
        if eval_token_evolution_descriptive:
            logging.info(
                "Research Question Evaluation started (Token Evolution Descriptive)")

            # get contract transactions
            if use_db:
                contract_transactions = sql_db_connector.query_contract_transaction_data(
                    connector_config.SQL_DATABASE_TABLE_TRANSACTION, contract_address)
            else:
                with open("src/dataset/transaction_dataset.json", "r") as f:
                    transaction_dataset = json.load(f)

                contract_transactions = [
                    t for t in transaction_dataset if t["contract_address"] == contract_address]

            research_question.create_token_transaction_graph(
                contract_transactions, contract_address, token_id, file_path)

            research_question.create_contract_transaction_frequency_chart(
                contract_transactions, contract_address, file_path)

            research_question.create_contract_transaction_history(
                contract_transactions, contract_address, file_path)

            logging.info(
                "Research Question Evaluation done (Token Evolution Descriptive)")

        # token evolution pattern
        if eval_token_evolution_pattern:
            logging.info(
                "Research Question Evaluation started (Token Evolution Pattern)")

            # open transaction dataset
            with open("src/dataset/transaction_dataset.json", "r") as f:
                transaction_dataset = json.load(f)

            # open contract dataset
            with open("src/dataset/contract_dataset.json", "r") as f:
                contract_dataset = json.load(f)

            contract_list_fit = research_question.fit_contract_list_powerlaw(
                transaction_dataset, contract_dataset, self.contract_address_sample)

            with open(f"{file_path}/contract_list_fit.json", "w") as f:
                json.dump(contract_list_fit, f, indent=4)

            contract_list_fit_evaluation = research_question.evaluate_contract_list_fit(
                contract_list_fit)

            research_question.create_contract_list_fit_chart(
                contract_list_fit_evaluation, file_path)

            logging.info(
                "Research Question Evaluation done (Token Evolution Pattern)")

    def evaluate_research_question_contract_evolution(self, eval_contract_evolution: bool, file_path: str, from_block: Union[int, None] = None, to_block: Union[int, None] = None):
        # contract evolution
        if eval_contract_evolution:
            logging.info(
                "Research Question Evaluation started (Contract Evolution)")

            # get contract data
            contract_data = sql_db_connector.query_contract_data(
                connector_config.SQL_DATABASE_TABLE_CONTRACT,
                with_block_deployed=True,
                with_token_standards=True,
                limit=10000000)

            research_question.create_contract_deploy_history(
                contract_data, file_path=file_path)

            if from_block is not None and to_block is None:
                research_question.create_contract_deploy_history(
                    contract_data, from_block=from_block, file_path=file_path)
            if from_block is None and to_block is not None:
                research_question.create_contract_deploy_history(
                    contract_data, to_block=to_block, file_path=file_path)
            if from_block is not None and to_block is not None:
                research_question.create_contract_deploy_history(
                    contract_data, from_block=from_block, to_block=to_block, file_path=file_path)

            logging.info(
                "Research Question Evaluation done (Contract Evolution)")

    def evaluate_research_question_dao_contract_evolution(self, eval_dao_contract_evolution_descriptive: bool, eval_dao_contract_evolution_analysis: bool, contract_address: str, file_path: str):
        # dao contract evolution descriptive
        if eval_dao_contract_evolution_descriptive:
            logging.info(
                "Research Question Evaluation started (DAO Contract Evolution Descriptive)")

            # get dao contract transactions
            dao_contract_transactions = sql_db_connector.query_contract_transaction_data(
                connector_config.SQL_DATABASE_TABLE_TRANSACTION, contract_address
            )
            #
            holder_history_stats = research_question.create_holder_history_stats(
                dao_contract_transactions)
            holder_value_state = research_question.create_holder_value_state(
                dao_contract_transactions)

            research_question.create_holder_history_chart(
                holder_history_stats, contract_address, file_path)

            research_question.create_holder_change_history_chart(
                holder_history_stats, contract_address, file_path)

            research_question.create_holder_value_state_distribution_chart(
                holder_value_state, contract_address, file_path)

            research_question.create_transaction_history_chart(
                dao_contract_transactions, contract_address, file_path)

            logging.info(
                "Research Question Evaluation done (DAO Contract Evolution Descriptive)")

        # dao contract evolution analysis
        if eval_dao_contract_evolution_analysis:
            logging.info(
                "Research Question Evaluation started (DAO Contract Evolution Analysis)")

            # open dao contract list
            with open("src/dataset/dao_contract_list.json", "r") as f:
                dao_contract_list = json.load(f)

            # open dao transaction dataset
            with open("src/dataset/dao_transaction_dataset.json", "r") as f:
                dao_transaction_dataset = json.load(f)

            contract_gini_intervall, contract_gini_evaluation = research_question.evaluate_contract_measure_evolution(
                dao_transaction_dataset, dao_contract_list, research_question.gini_coefficient, 100)

            research_question.create_measure_evolution_chart(
                contract_gini_evaluation, file_path, "Gini")

            research_question.create_contract_measure_chart(
                contract_gini_intervall, 0, file_path, "Gini")

            research_question.create_contract_measure_chart(
                contract_gini_intervall, 49, file_path, "Gini")

            research_question.create_contract_measure_chart(
                contract_gini_intervall, 99, file_path, "Gini")

            contract_herfindahl_intervall, contract_herfindahl_evaluation = research_question.evaluate_contract_measure_evolution(
                dao_transaction_dataset, dao_contract_list, research_question.herfindahl_index, 100)

            research_question.create_measure_evolution_chart(
                contract_herfindahl_evaluation, file_path, "Herfindahl")

            research_question.create_contract_measure_chart(
                contract_herfindahl_intervall, 0, file_path, "Herfindahl")

            research_question.create_contract_measure_chart(
                contract_herfindahl_intervall, 49, file_path, "Herfindahl")

            research_question.create_contract_measure_chart(
                contract_herfindahl_intervall, 99, file_path, "Herfindahl")

            logging.info(
                "Research Question Evaluation done (DAO Contract Evolution Analysis)")
