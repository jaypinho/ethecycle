"""
Turn a transactions file into CSVs Neo4j admin tool can import and import it.
Unclear if there's a way to just load from a single CSV and have it create nodes on the fly.

Docs: https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/neo4j-admin-import/

Data types: int, long, float, double, boolean, byte, short, char, string, point, date,
            localtime, time, localdatetime, datetime, duration
"""
import csv
import time
from datetime import datetime
from os import path
from subprocess import check_output
from typing import List, Optional

from rich.text import Text

from ethecycle.config import Config
from ethecycle.transaction import Txn
from ethecycle.util.filesystem_helper import OUTPUT_DIR, timestamp_for_filename
from ethecycle.util.logging import console
from ethecycle.util.string_constants import ETHEREUM
from ethecycle.wallet import Wallet

# Path on the docker container
NEO4J_DB = 'neo4j'
NEO4J_ADMIN_EXECUTABLE = '/var/lib/neo4j/bin/neo4j-admin'
NEO4J_SSH = f"ssh root@neo4j -o StrictHostKeyChecking=accept-new "
CSV_IMPORT_CMD = f"{NEO4J_ADMIN_EXECUTABLE} database import "
STOP_SERVER_CMD = f"{NEO4J_ADMIN_EXECUTABLE} server stop "
START_SERVER_CMD = f"{NEO4J_ADMIN_EXECUTABLE} server start "

# TODO: could use the chain for labeling e.g. 'eth_wallet' and 'eth_txn'
NODE_LABEL = 'Wallet'
EDGE_LABEL = 'TXN'
INDENT = '      '

WALLET_CSV_HEADER = [
    'address:ID',
    'blockchain',
    'label',
    'category',
    'extracted_at:datetime',
]

TXN_CSV_HEADER = [
    'transactionID',  # Combination of transaction_hash and log_index
    'blockchain',
    'token_address',
    'token',
    ':START_ID',  # from_address
    ':END_ID',  # to_address
    'num_tokens:double',
    'block_number:int',
    'extracted_at:datetime',
]

# Keys will be prefixed with '--' in the final command
LOADER_CLI_ARGS = {
    'id-type': 'string',
    'skip-duplicate-nodes': 'true'
}

INCREMENTAL_INSTRUCTIONS = Text() + Text(f"Incremental import to current DB '{NEO4J_DB}'...\n\n", style='magenta bold') + \
    Text(f"You must stop the server to run incremental import:\n") + \
    Text(f"      {STOP_SERVER_CMD}\n", style='bright_cyan') + \
    Text(f"Afterwards restart with:\n") + \
    Text(f"      {START_SERVER_CMD}\n\n", style='bright_cyan') + \
    Text(
        f"Incremental load via neo4j-admin doesn't seem to work; use --drop options or LOAD CSV instead\n",
        style='bright_red bold blink reverse',
        justify='center'
    ) + \
    Text(f"(If you messed up and forgot the --drop option, replace command with:\n   {CSV_IMPORT_CMD} full --id-type=string --skip-duplicate-nodes=true --overwrite-destination=true", style='dim')


class Neo4jCsvs:
    def __init__(self, csv_basename: Optional[str] = None) -> None:
        """Generates filenames based on the timestamp."""
        csv_basename = csv_basename or timestamp_for_filename()
        build_csv_path = lambda label: path.join(OUTPUT_DIR, f"{label}_{csv_basename}.csv")
        self.wallet_csv_path = build_csv_path(NODE_LABEL)
        self.txn_csv_path = build_csv_path(EDGE_LABEL)

    @staticmethod
    def admin_load_bash_command(neo4j_csvs: List['Neo4jCsvs']) -> str:
        """Generate shell command to bulk load a set of CSVs."""
        neo4j_csvs = [write_header_csvs()] + neo4j_csvs
        wallet_csvs = [n.wallet_csv_path for n in neo4j_csvs]
        txn_csvs = [n.txn_csv_path for n in neo4j_csvs]

        if Config.drop_database:
            msg = f"WARNING: This command will overwrite current DB '{NEO4J_DB}'!\n"
            console.print(msg, style='red blink bold', justify='center')
            LOADER_CLI_ARGS['overwrite-destination'] = 'true'
            subcommand = 'full'
        else:
            console.print(INCREMENTAL_INSTRUCTIONS)
            LOADER_CLI_ARGS['force'] = 'true'  # Apparently required for incremental load
            #LOADER_CLI_ARGS['stage'] = 'build'
            subcommand = 'incremental'

        load_args = [f"--{k}={v}" for k, v in LOADER_CLI_ARGS.items()]
        load_args.append(f"--nodes={NODE_LABEL}={','.join(wallet_csvs)}")
        load_args.append(f"--relationships={EDGE_LABEL}={','.join(txn_csvs)}")
        return f"{CSV_IMPORT_CMD} {subcommand} {' '.join(load_args)} {NEO4J_DB}"

    @staticmethod
    def load_to_db(neo4j_csvs: List['Neo4jCsvs']) -> None:
        """Load into the Neo4J database via bulk load."""
        ssh_cmd = f"{NEO4J_SSH} {Neo4jCsvs.admin_load_bash_command(neo4j_csvs)}"
        console.print("About to actually execute:\n", style='bright_red')
        console.print(ssh_cmd, style='yellow')
        ssh_result = check_output(ssh_cmd.split(' ')).decode()
        console.print(f"\nRESULT:\n{ssh_result}")


def generate_neo4j_csvs(txns: List[Txn], blockchain: str = ETHEREUM) -> Neo4jCsvs:
    """Break out wallets and txions into two CSV files for nodes and edges."""
    extracted_at = datetime.utcnow().replace(microsecond=0).isoformat()
    neo4j_csvs = Neo4jCsvs()
    start_time = time.perf_counter()

    # Wallet nodes
    with open(neo4j_csvs.wallet_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        for wallet in Wallet.extract_wallets_from_transactions(txns):
            csv_writer.writerow(wallet.to_neo4j_csv_row() + [extracted_at])

    wallet_csv_duration = time.perf_counter() - start_time
    console.print(f"     Wrote wallet CSV in {wallet_csv_duration:02.2f} seconds...", style='benchmark')

    # Transaction edges
    with open(neo4j_csvs.txn_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        for txn in txns:
            csv_writer.writerow(txn.to_neo4j_csv_row() + [extracted_at])

    txn_csv_duration = time.perf_counter() - wallet_csv_duration - start_time
    console.print(f"     Wrote txn CSV in {txn_csv_duration:02.2f} seconds...", style='benchmark')
    return neo4j_csvs


# NOTE: Had bizarre issues with this on macOS... removed WALLET_header.csv but could not write to
#       Wallet_header.csv until I did a `touch /ethecycle/Wallet_header.csv`.
#       I assume it has something to do w/macOS's lack of case sensitivity.
def write_header_csvs() -> Neo4jCsvs:
    """Write single row CSVs with header info for nodes and edges."""
    header_csvs = Neo4jCsvs('header')

    with open(header_csvs.txn_csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(TXN_CSV_HEADER)

    with open(header_csvs.wallet_csv_path, 'w') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(WALLET_CSV_HEADER)

    return header_csvs
