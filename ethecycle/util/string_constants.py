ETHECYCLE = 'ethecyle'
DEBUG = 'DEBUG'

# Address stuff
ADDRESS = 'address'
FROM_ADDRESS = 'from_address'
MISSING_ADDRESS = 'no_address'
TO_ADDRESS = 'to_address'

# Chain stuff
BLOCKCHAIN = 'blockchain'
BLOCK_NUMBER = 'block_number'
CONTRACT = 'contract'
ERC20 = 'ERC20'
LOG_INDEX = 'log_index'
NFT = 'nft'
SYMBOL = 'symbol'
TOKEN_ADDRESS = 'token_address'
TOKEN = 'token'
TRANSACTION_HASH = 'transaction_hash'
TXN = 'transaction'
WALLET = 'wallet'

# Tokens
USDT = 'USDT'
WETH = 'WETH'

# Blockchains
ARBITRUM = 'arbitrum'
AVALANCHE = 'avalanche'
AVAX = 'avax'
BINANCE_SMART_CHAIN = 'binance_smart_chain'
BITCOIN = 'bitcoin'
BITCOIN_CASH = 'bitcoin_cash'
CARDANO = 'cardano'
ETHEREUM = 'ethereum'
LITECOIN = 'litecoin'
MATIC = 'matic'
OASIS = 'oasis'
OKEX = 'okx_chain'
POLYGON = 'polygon'
RIPPLE = 'ripple'
SOLANA = 'solana'
TRON = 'tron'

# Txn properties in the graph
EXTRACTED_AT = 'extracted_at'
NUM_TOKENS = 'num_tokens'
SCANNER_URL = 'scanner_url'

# Other column names
DATA_SOURCE = 'data_source'

# Industry
ALAMEDA = 'alameda'
BINANCE = 'binance'
USDT = 'USDT'
USDT_ETHEREUM_ADDRESS = '0xdac17f958d2ee523a2206206994597c13d831ec7'

# Social Media
BITCOINTALK = 'bitcointalk'
DISCORD = 'discord'
FACEBOOK = 'facebook'
INSTAGRAM = 'instragram'
LINKEDIN = 'linkedin'
REDDIT = 'reddit'
TELEGRAM = 'telegram'
TIKTOK = 'tiktok'
TWITTER = 'twitter'
YOUTUBE = 'youtube'

# Order matters when choosing label cols from GoogleSheetsImporter: higher cols are chosen first
# For this reason we prefer more public orgs over less public ones.
SOCIAL_MEDIA_ORGS = [
    LINKEDIN,
    INSTAGRAM,
    TWITTER,
    YOUTUBE,
    REDDIT,
    TIKTOK,
    FACEBOOK,
    TELEGRAM,
    BITCOINTALK,
]

# Wallet Categories
BRIDGE = 'bridge'
CATEGORY = 'category'
CEFI = 'cefi'
CEX = 'cex'
DAO = 'dao'
DEFI = 'defi'
DEX = 'dex'
EXCHANGE = 'exchange'
FTX = 'ftx'
HACKERS = 'hackers'
INDIVIDUAL = 'individual'
MIXER = 'mixer'
STABLECOIN = 'stablecoin'
VAULTS = 'vaults'
WALLET_PROVIDER = 'wallet provider'

# Misc
HTTPS = 'https://'
JSON = 'json'
NAME = 'name'

# GraphML
LABEL_E = 'labelE'
LABEL_V = 'labelV'


def social_media_url(col: str) -> str:
    if col == BITCOINTALK:
        tld = 'org'
    else:
        tld = 'com'

    return f"{col}.{tld}"
