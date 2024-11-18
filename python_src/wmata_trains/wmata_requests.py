import urllib.request
import json

from wmata_trains import LOGGER

BASE_URL = "https://api.wmata.com/Rail.svc/json/"
HDR = {
    # Request headers
    'Cache-Control': 'no-cache',
    'api_key': None
        }


def request(target, api_key):
    hdr = HDR.copy()
    hdr['api_key'] = api_key
    req = urllib.request.Request(BASE_URL + target, headers=hdr)
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
    return request('jStations', api_key)


def station_times(stations: list, api_key):
    station_codes = ','.join(station for station in stations)
    target = f'GetPrediction/{station_codes}'
    return request(target, api_key)
