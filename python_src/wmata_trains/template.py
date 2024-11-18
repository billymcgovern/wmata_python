"""
Support for getting collected information from PVOutput.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.pvoutput/
"""
import logging
import json
import voluptuous as vol

from datetime import timedelta

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.components.rest.data import RestData
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME)

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'wmata'
DEFAULT_NAME = 'Virginia Square Metro'

SCAN_INTERVAL = timedelta(seconds=30)

STATION_INFO_URL = 'https://api.wmata.com/Rail.svc/json/jLines?api_key={api_key}'
NEXT_TRAIN_URL = 'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/{station_code}?api_key={api_key}'
MY_STOP = 'K03'
LINE_COLOR1 = 'SV'
LINE_COLOR2 = 'OR'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the PVOutput sensor."""
    name = config.get(CONF_NAME, DEFAULT_NAME)
    api_key = config.get(CONF_API_KEY, '')
    station_info_url = STATION_INFO_URL.format(api_key=api_key)
    next_train_url = NEXT_TRAIN_URL.format(station_code=MY_STOP, api_key=api_key)

    method = 'GET'
    verify_ssl = headers = payload = auth = None

    station_rest = RestData(hass, method, station_info_url, auth, headers, None, payload, verify_ssl)
    train_rest = RestData(hass, method, next_train_url, auth, headers, None, payload, verify_ssl)
    await station_rest.async_update()
    await train_rest.async_update()

    if None in [station_rest.data, train_rest.data]:
        _LOGGER.warning("Platform not ready")

    metro_obj = VirginiaSquareMetro(station_rest, train_rest, name)
    add_entities([metro_obj], True)


class Station(object):
    def __init__(self, station_json):
        self.station_json = station_json
        for key, val in station_json.items():
            '''
            "LineCode": "BL",
            "DisplayName": "Blue",
            "StartStationCode": "J03",
            "EndStationCode": "G05",
            "InternalDestination1": "",
            "InternalDestination2": ""
            '''
            setattr(self, key, val)

    @property
    def start(self):
        if self.InternalDestination1:
            return self.InternalDestination1
        return self.StartStationCode

    @property
    def end(self):
        if self.InternalDestination2:
            return self.InternalDestination2
        return self.EndStationCode


class VirginiaSquareMetro(Entity):

    def __init__(self, station_rest, train_rest, name):
        self.station_rest = station_rest
        self.train_rest = train_rest
        self._name = name
        self.train_out = None
        self.station_out = None
        self.end_of_line = []
        self.times = {}
        _LOGGER.info("Virginia Square Metro custom component loaded")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        if self.metro_out is not None:
            return self.times
        return None

    @property
    def unit_of_measurement(self):
        return 'Minutes'

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the monitored installation."""
        if self.station_out is not None:
            self.end_of_line = []
            for station in self.station_out['Lines']:
                if station['LineCode'] in [LINE_COLOR1, LINE_COLOR2]:
                    self.end_of_line.append(Station(station))

        if self.metro_out is not None:
            self.times = {}
            for train in self.metro_out['Trains']:
                for station_inst in self.end_of_line:
                    if train['DestinationCode'] == station_inst.start:
                        self.times[f'{station_inst.LineCode}West'] = train['Min']

        return self.times

    async def async_update(self):
        """Get the latest data from the PVOutput API and updates the state."""
        try:
            _LOGGER.info("METRO TRY GET TRAIN")
            await self.station_rest.async_update()
            await self.train_rest.async_update()
            self.train_out = json.loads(self.train_rest.data)
            self.station_out = json.loads(self.train_rest.data)
            _LOGGER.info(f"GOT EM {self.metro_out}")
        except BaseException:
            _LOGGER.exception('[METRO] Could not get trains')
            _LOGGER.error(
                "Unable to fetch data from WMATA")
