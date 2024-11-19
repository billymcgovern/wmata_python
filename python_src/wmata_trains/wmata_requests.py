import urllib.request
import json

from wmata_trains import LOGGER

BASE_URL = "https://api.wmata.com"
RAIL_URL = f'{BASE_URL}/Rail.svc/json/'
STATION_PREDICT_URL = f'{BASE_URL}/StationPrediction.svc/json/GetPrediction/'
HDR = {
    # Request headers
    'Cache-Control': 'no-cache',
    'api_key': None
}


def request(target, api_key):
    LOGGER.debug(f'Request: {target}')
    hdr = HDR.copy()
    hdr['api_key'] = api_key
    req = urllib.request.Request(target, headers=hdr)
    req.get_method = lambda: 'GET'

    try:
        response = urllib.request.urlopen(req)
        LOGGER.debug(f'[{response.getcode()}] {target}')
        resp = json.loads(response.read())
    except Exception as e:
        LOGGER.exception(e)
        resp = {}

    return resp


def station_list(api_key):
    return request(f'{RAIL_URL}jStations', api_key)


def station_info(api_key, station_code):
    return request(f'{RAIL_URL}jStationInfo?StationCode={station_code}', api_key)


def station_times(stations: list, api_key):
    station_codes = ','.join(station for station in stations)
    target = f'{STATION_PREDICT_URL}{station_codes}'
    return request(target, api_key)
