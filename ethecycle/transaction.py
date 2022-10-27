from collections import defaultdict
from dataclasses import dataclass
from typing import List

from rich.pretty import pprint
from rich.text import Text

from ethecycle.blockchains import get_chain_info
from ethecycle.export.neo4j import MISSING_ADDRESS

COL_NAMES = ['token_address', 'from_address', 'to_address', 'value', 'transaction_hash', 'log_index', 'block_number']


@dataclass
class Txn():
    blockchain: str
    token_address: str
    from_address: str
    to_address: str
    csv_value: str  # num_tokens
    transaction_hash: str
    log_index: str
    block_number: int

    def __post_init__(self):
        # Some txns have multiple internal transfers so append log_index to achieve uniqueness
        self.transaction_id = f"{self.transaction_hash}-{self.log_index}"
        chain_info = get_chain_info(self.blockchain)
        self.token = chain_info.token_symbol(self.token_address)
        self.num_tokens = float(self.csv_value) / 10 ** chain_info.token_decimals(self.token_address)
        self.num_tokens_str = "{:,.18f}".format(self.num_tokens)
        self.block_number = int(self.block_number)

        if len(self.from_address or '') == 0:
            self.from_address = MISSING_ADDRESS
        if len(self.to_address or '') == 0:
            self.to_address = MISSING_ADDRESS

        self.scanner_url = chain_info.scanner_url(self.transaction_hash)

    def __rich__(self) -> Text:
        txt = Text('<').append(self.transaction_hash[:8], style='magenta')
        txt.append(', To: ').append(self.to_address[:8], style='color(222)').append(', value: ')
        return txt.append(f"{self.num_tokens_str}", style='cyan').append('>')

    def __str__(self) -> str:
        return self.__rich__().plain

    def __eq__(self, other: 'Txn'):
        return self.transaction_id == other.transaction_id

    @classmethod
    def count_col_vals(cls, txns: List['Txn'], col: str) -> None:
        """Given a list of txns and a column name, count occurences of each value and show top 100"""
        counts = defaultdict(lambda: 0)

        for txn in txns:
            counts[getattr(txn, col)] += 1

        pprint(sorted(counts.items(), key=lambda r: r[1], reverse=True)[0:100])
