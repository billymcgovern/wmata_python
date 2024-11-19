import dataclasses
import enum

from collections import namedtuple
from rich.table import Table
from rich.console import Console
from rich.text import Text

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
"Car": "6",
        "Destination": "Glenmont",
        "DestinationCode": "B11",
        "DestinationName": "Glenmont",
        "Group": "1",
        "Line": "RD",
        "LocationCode": "B03",
        "LocationName": "Union Station",
        "Min": "BRD"
        '''


@dataclasses.dataclass
class NextTrain(object):
    Car: int
    Destination: str
    DestinationCode: str
    DestinationName: str
    Group: int
    Line: StationCode
    LocationCode: str
    LocationName: str
    Min: str

    def __post_init__(self):
        if not isinstance(self.Line, StationCode):
            self.Line = StationCode[self.Line]

    @property
    def as_row(self):
        return [Text.from_ansi(self.Line.value.color(self.Line.name)), Text.from_ansi(self.Line.value.color(self.Car)), self.DestinationName, self.Min]


@dataclasses.dataclass
class NextTrainList(object):
    next_trains: []

    def __iter__(self):
        return list(self.next_trains)

    def __str__(self):
        table = Table(show_header=True)
        table.add_column("LN", justify='center')
        table.add_column("CAR", justify='center')
        table.add_column("DEST")
        table.add_column("MIN", justify='center')

        for train in self.next_trains:
            table.add_row(*train.as_row)

        console = Console()
        with console.capture() as capture:
            console.print(table)

        return capture.get()

    @classmethod
    def from_json(cls, trains):
        next_trains = []
        for train in trains:
            next_trains.append(NextTrain(**train))

        return cls(next_trains)


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
        output = f'{self.Name} ({self.Code})\n'
        output += f'{str(self.Address)}\n'
        output += f'{self.line_code_str}\n'
        return output

    @classmethod
    def from_json(cls, station):
        StationAddressInst = StationAddress(**station.pop('Address'))
        station['Address'] = StationAddressInst
        return cls(**station)

    def list_str(self):
        return f'[{self.Code}] {self.Name} {self.line_code_str}'

    @property
    def line_code_str(self):
        line_code_str = ', '.join(lc.value.color(f'  {lc.value.name}  ') for lc in self.line_codes if lc)
        return line_code_str

    @property
    def line_codes(self):
        return [self.__getattribute__(f'LineCode{i}') for i in range(1, 5)]

    def next_trains(self, api_key):
        trains_json = wmata_requests.station_times([self.Code], api_key)

        NextTrains = NextTrainList.from_json(trains_json['Trains'])
        return NextTrains


@dataclasses.dataclass
class StationList(object):
    stations: []

    def __iter__(self):
        return list(self.stations)

    def __str__(self):
        output = '\n'.join(str(station) for station in self.stations)
        return output

    def station_by_code(self, code):
        for station in self.stations:
            if station.Code.lower() == code.lower():
                return station
        return None


def get_station_list(api_key):
    global STATION_LIST
    if STATION_LIST is not None:
        return STATION_LIST

    _station_list = []

    station_list = wmata_requests.station_list(api_key)
    for station in station_list['Stations']:
        StationInst = Station.from_json(station)
        _station_list.append(StationInst)

    STATION_LIST = StationList(_station_list)

    return STATION_LIST


def get_station_info(api_key, station_code):
    global STATION_LIST
    if STATION_LIST is not None:
        return STATION_LIST.station_by_code(station_code)

    return Station.from_json(wmata_requests.station_info(api_key, station_code))
