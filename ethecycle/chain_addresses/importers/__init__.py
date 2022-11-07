"""
Drop DB, recreate empty DB, and reimport all chain address data sources.

TODO: Other possible sources:
    - https://github.com/Skyba/safuhack
    - https://github.com/aogunwoolu/Ethereum-analysis
    - https://github.com/DavidJCullen/Data-Science-Portfolio-/blob/af86c1fb04a5f78b97432a9d855741f965c4bd67/MapReduce%20(Hadoop%20Cluster):/PartD/Popular%20Scams/Scams.csv
    - https://github.com/dawsbot/evm-labels
    - https://github.com/Zaehyeon2/FDGNN-Fraud-Address-Detection-on-Ethereum-using-Graph-Neural-Network
    - https://raw.githubusercontent.com/GuillermoEscobero/fraud-in-ethereum/main/dark_addresses.yaml
    - https://www.bitcoinabuse.com/api/download/forever?api_token={API_TOKEN}
    - Searching for google sheets: 'blockchain addresses site:docs.google.com sheet'
"""
from ethecycle.chain_addresses.address_db import drop_and_recreate_tables, get_db_connection
from ethecycle.config import Config

from .coin_market_cap_repo_importer import import_coin_market_cap_repo_addresses
from .cryptoscamdb_addresses_importer import import_cryptoscamdb_addresses
from .ethereum_lists_repo_importer import import_ethereum_lists_addresses
from .etherscan_labels_importer import import_etherscan_labels_repo
from .etherscan_contract_crawler_importer import import_ethereum_contract_crawler_addresses
from .etherscrape_importer import import_etherscrape_chain_addresses
from .google_sheets_importer import import_google_sheets
from .hand_collated_address_importer import import_hand_collated_addresses
from .hardcoded_addresses_importer import import_hardcoded_addresses
from .my_ether_wallet_repo_importer import import_my_ether_wallet_addresses
from .trustwallet_assets_importer import import_trust_wallet_repo
from .wallets_from_dune_importer import import_wallets_from_dune
from .w_mcdonald_etherscan_repo_importer import import_w_mcdonald_etherscan_addresses


def rebuild_chain_addresses_db():
    """Drop all tables and rebuild from source data."""
    Config.skip_load_from_db = True
    drop_and_recreate_tables()
    # Import hand collated results first so they have priority
    import_hand_collated_addresses()
    import_hardcoded_addresses()
    import_coin_market_cap_repo_addresses()
    import_cryptoscamdb_addresses()
    import_ethereum_contract_crawler_addresses()
    import_ethereum_lists_addresses()
    import_etherscan_labels_repo()
    import_etherscrape_chain_addresses()
    import_google_sheets()
    import_my_ether_wallet_addresses()
    import_trust_wallet_repo()
    import_wallets_from_dune()
    import_w_mcdonald_etherscan_addresses()
    get_db_connection().disconnect()
    Config.skip_load_from_db = False
