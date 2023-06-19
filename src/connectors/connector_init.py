import connectors.connector_config as config
import connectors.sql_tables as tables
from connectors import EthereumApiConnector, EtherscanConnector, InfuraConnector, MoralisConnector, SqlDatabaseConnector

ethereum_api_connector = EthereumApiConnector(
    config.ETHEREUM_API_IP, config.ETHEREUM_API_USERNAME, config.ETHEREUM_API_PASSWORD)

etherscan_connector = EtherscanConnector(
    config.ETHERSCAN_IP, config.ETHERSCAN_API_KEY)

moralis_connector = MoralisConnector(
    config.MORALIS_IP, config.MORALIS_API_KEY)

infura_connector = InfuraConnector(
    config.INFURA_IP, config.INFURA_API_KEY)

# init sql database connector
sql_db_connector = SqlDatabaseConnector(
    config.SQL_DATABASE_HOST,
    config.SQL_DATABASE_PORT,
    config.SQL_DATABASE_USER,
    config.SQL_DATABASE_PASSWORD,
    config.SQL_DATABASE_NAME,
    [tables.CONTRACT_TABLE, tables.TRANSACTION_TABLE]
)
