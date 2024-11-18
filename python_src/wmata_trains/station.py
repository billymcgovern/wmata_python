import dataclasses
import enum

from collections import namedtuple

from . import wmata_requests
from . import colors

STATION_LIST = None


code_tuple = namedtuple('StationCodeTuple', ['color', 'name'])


@enum.unique
class StationCode(enum.Enum):
    GR = code_tuple(colors.WHITE_GREEN_BACKGROUND, 'Green')
    BL = code_tuple(colors.WHITE_BLUE_BACKGROUND, 'Blue')
    OR = code_tuple(colors.WHITE_ORANGE_BACKGROUND, 'Orange')
    RD = code_tuple(colors.WHITE_RED_BACKGROUND, 'Red')
    SV = code_tuple(colors.WHITE_GREY_BACKGROUND, 'Silver')
    YL = code_tuple(colors.WHITE_YELLOW_BACKGROUND, 'Yellow')


'''
"Code": "N11",
        "Name": "Loudoun Gateway",
        "StationTogether1": "",
        "StationTogether2": "",
        "LineCode1": "SV",
        "LineCode2": null,
        "LineCode3": null,
        "LineCode4": null,
        "Lat": 38.99204,
        "Lon": -77.460685,
        "Address": {
            "Street": "22505 Lockridge Rd",
            "City": "Ashburn",
            "State": "VA",
            "Zip": "20166"
        }
'''


@dataclasses.dataclass
class StationAddress(object):
    Street: str
    City: str
    State: str
    Zip: int

    def __str__(self):
        return f'{self.Street}\n{self.City}, {self.State} {self.Zip}'


@dataclasses.dataclass
class Station(object):
    Code: str
    Name: str
    StationTogether1: str
    StationTogether2: str
    LineCode1: str
    LineCode2: str
    LineCode3: str
    LineCode4: str
    Lat: float
    Lon: float
    Address: StationAddress

    def __post_init__(self):
        for idx, lc in enumerate(self.line_codes):
            if lc:
                self.__setattr__(f'LineCode{idx + 1}', StationCode[lc])

    def __str__(self):
        line_code_str = ', '.join(lc.value.color(f'  {lc.value.name}  ') for lc in self.line_codes if lc)

        return f'[{self.Code}] {self.Name} {line_code_str}'

    @property
    def line_codes(self):
        return [self.__getattribute__(f'LineCode{i}') for i in range(1, 5)]


@dataclasses.dataclass
class StationList(object):
    stations: []

    def __iter__(self):
        return list(self.stations)

    def __str__(self):
        output = '\n'.join(str(station) for station in self.stations)
        return output


def get_station_list(api_key):
    global STATION_LIST
    if STATION_LIST is not None:
        return STATION_LIST

    _station_list = []

    station_list = wmata_requests.station_list(api_key)
    for station in station_list['Stations']:
        StationAddresInst = station.pop('Address')
        station['Address'] = StationAddresInst
        StationInst = Station(**station)
        _station_list.append(StationInst)

    STATION_LIST = StationList(_station_list)

    return STATION_LIST
