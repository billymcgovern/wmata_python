import argparse
import time

from pathlib import Path
from rich.live import Live

from . import LOGGER, CONSOLE
from .logger import add_file_handler
from .station import get_station_list, get_station_info


parser = argparse.ArgumentParser(prog='WMATA trains')

parser.add_argument('--api-key', type=str, required=True, help='WMATA developer api-key')
parser.add_argument('--log-file', type=Path, help='Path (and name) of log file. Parent directories do not have to exist')
parser.add_argument('--debug', action='store_true', help='Log FILE will be verbose. Stream is always non-verbose')

subparsers = parser.add_subparsers(dest='task', required=True)

# Actions

# List all of the stations and their high level information
list_parser = subparsers.add_parser('list-stations', help='List station information and exit')

# Get specific information about a station
station_parser = subparsers.add_parser('station-info', help='Specific information about a station')
station_parser.add_argument('--station-code', required=True, type=str, help='Station code as seen in the list-stations argument.')
station_parser.add_argument('--next-trains', action='store_true', help='Using the station code, get the next train information.')

pargs = parser.parse_args()

if pargs.log_file:
    if not pargs.log_file.exists():
        pargs.log_file.parent.mkdir(parents=True)
    add_file_handler(pargs.log_file, debug=pargs.debug)

LOGGER.debug(pargs)

if 'list-stations' == pargs.task:
    LOGGER.print(get_station_list(pargs.api_key))
elif 'station-info' == pargs.task:
    station = get_station_info(pargs.api_key, pargs.station_code)
    LOGGER.print(station)
    if pargs.next_trains:
        with Live(console=CONSOLE, auto_refresh=False) as live:
            while True:
                next_trains = station.next_trains(pargs.api_key)
                # Live console
                live.update(next_trains)
                live.refresh()
                # Log file
                LOGGER.debug(next_trains)
                time.sleep(30)
