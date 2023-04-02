"""The main file that will be run by the grader.
"""
from __future__ import annotations

import csv
import codecs
from datetime import datetime
from py7zr import SevenZipFile

from python_ta.contracts import check_contracts

from network import IATACode, DayHourMinute
from network import MIN_LAYOVER_TIME, MAX_LAYOVER_TIME, MAX_LAYOVER, TOP_K_RESULTS
from network import Network, Airport, Flight, Ticket
from flightsearcher import AbstractFlightSearcher, NaiveFlightSearcher, DijkstraFlightSearcher


def unpack_csv(flight_file: str) -> None:
    """Unpack /data/clean_no_dupe_itineraries.7z to /data/clean_no_dupe_itineraries.csv
    """

    with SevenZipFile('../data/' + flight_file + '.7z', mode='r') as z:
        z.extractall()

    # print('Finished extracting.')


def read_csv_file(airport_file: str, flight_file: str) -> Network:
    """
    Read and load the CSV file into a network

    Preconditions:
        - airport_file[-4:] == '.csv'
        - flight_file[-4:] == '.csv'

    """
    res_network = Network()

    with open(airport_file) as csv_file:
        reader = csv.DictReader(csv_file)
        header = {
            'iata_code',
            'name',
            'municipality'
        }
        assert set(reader.fieldnames) == header

        for row in reader:
            airport = Airport(
                iata=row['iata_code'],
                name=row['name'],
                city=row['municipality']
            )
            res_network.add_airport(airport)

    with open(flight_file) as csv_file:
        reader = csv.DictReader(csv_file)
        header = {
            'legId',
            'isNonStop',
            'totalFare',
            'segmentsDepartureAirportCode',
            'segmentsArrivalAirportCode',
            'segmentsAirlineName',
            'segmentsDepartureWeekday',
            'segmentsDepartureTimeOfDay',
            'segmentsArrivalWeekday',
            'segmentsArrivalTimeOfDay',
            'startingAirport',
            'destinationAirport'
        }
        assert set(reader.fieldnames) == header

        airport_ticket = {}  # dict[str, list[Ticket]]
        for row in reader:
            flight_id = row['legId']
            airline = row['segmentsAirlineName'].split('||')
            price = float(row['totalFare'])

            origin = res_network.get_airport_from_iata(row['startingAirport'])
            destination = res_network.get_airport_from_iata(row['destinationAirport'])

            departure = row['segmentsDepartureAirportCode'].split('||')
            departure = [res_network.get_airport_from_iata(airport_d) for airport_d in departure]

            departure_weekday = list(map(int, row['segmentsDepartureWeekday'].split('||')))
            departure_timeday = row['segmentsDepartureTimeOfDay'].split('||')
            departure_timeday = [tuple(map(int, timeday.split(':'))) for timeday in departure_timeday]

            arrival = row['segmentsArrivalAirportCode'].split('||')
            arrival = [res_network.get_airport_from_iata(airport_a) for airport_a in arrival]

            arrival_weekday = list(map(int, row['segmentsArrivalWeekday'].split('||')))
            arrival_timeday = row['segmentsArrivalTimeOfDay'].split('||')
            arrival_timeday = [tuple(map(int, timeday.split(':'))) for timeday in arrival_timeday]

            assert origin == departure[0] and destination == arrival[-1]
            assert len(departure) == len(arrival)

            flights = []
            for i in range(len(departure)):
                flight = Flight(
                    airline=airline[i],
                    flight_id=flight_id,
                    origin=departure[i],
                    destination=arrival[i],
                    departure_time=DayHourMinute(
                        day=departure_weekday[0], hour=departure_timeday[i][0], minute=departure_timeday[i][1]
                    ),
                    arrival_time=DayHourMinute(
                        day=arrival_weekday[0], hour=arrival_timeday[i][0], minute=arrival_timeday[i][1]
                    )
                )
                flights.append(flight)

            ticket = Ticket(
                origin=origin,
                destination=destination,
                departure_time=flights[0].departure_time,
                arrival_time=flights[-1].arrival_time,
                flights=flights,
                price=price
            )

            if origin not in airport_ticket:
                airport_ticket[origin] = []
            airport_ticket[origin].append(ticket)

        for origin in airport_ticket:
            tickets = airport_ticket[origin]
            tickets.sort(key=lambda x: x.departure_time)

            for ticket in tickets:
                origin.add_ticket(ticket)

    return res_network


def get_naive_searcher() -> AbstractFlightSearcher:
    """ Return a naive searcher
    """
    airport_file = '../data/airport_class_1000.csv'
    flight_file = '../data/clean_no_dupe_itineraries_1000.csv'

    flight_network = read_csv_file(airport_file, flight_file)
    return NaiveFlightSearcher(flight_network)


def get_pruned_landmark_labelling() -> AbstractFlightSearcher:
    """ TODO DOCSTRING
    """


def _get_iata_input(prompt_city: str, prompt_airport: str, flight_network: Network) -> str:
    city = None
    while True:
        print(prompt_city, end=' ')
        city = input()

        if city not in flight_network.city_airport:
            print('Please input a valid city.')
        else:
            break
    assert city is not None

    print('\nList of Airports')
    for iata in flight_network.city_airport[city]:
        print(f'{flight_network.airports[iata].name}({iata})')

    iata = None
    while True:
        print(prompt_airport, end=' ')
        iata = input()

        if iata not in flight_network.airports:
            print('Please input a valid IATA code.')
        else:
            break
    assert iata is not None

    return iata


def run(airport_file: str, flight_file: str, searcher_type: str) -> None:
    """ Docstring here
    """
    flight_network = read_csv_file(airport_file, flight_file)

    searcher = None
    if searcher_type == 'naive':
        searcher = NaiveFlightSearcher(flight_network)
    elif searcher_type == 'dijsktra':
        searcher = DijkstraFlightSearcher
    else:
        raise ValueError('Invalid Flight Searcher')
    assert searcher is not None

    # Asks for Airport Departure/Arrival
    departure_airport = _get_iata_input(
        prompt_city='Input the city you will be departing from:',
        prompt_airport='Choose your departure airport by inputting its three-character IATA code:',
        flight_network=flight_network
    )
    arrival_airport = _get_iata_input(
        prompt_city='Input the city of your destination:',
        prompt_airport='Choose your arrival airport by inputting its three-character IATA code:',
        flight_network=flight_network
    )

    # Asks for Departure date
    departure_date = None
    while True:
        print('Input your departure date (YYYY/MM/DD):', end=' ')
        try:
            departure_date = datetime.strptime(input(), '%Y/%m/%d')
        except ValueError:
            print('Please input a valid Date.')
        else:
            break
    assert departure_date is not None

    # Asks for sorting preference
    sort_by = None
    while True:
        print('Sort by flight duration(d) or ticket price(p)? Input (d/p):', end=' ')
        sort_by = input()

        if sort_by not in {'d', 'p'}:
            print('Please input a valid sorting preference.')
        else:
            break
    assert sort_by is not None

    if sort_by == 'duration':
        tickets = searcher.search_shortest_flight(source=departure_airport,
                                                  destination=arrival_airport,
                                                  departure_time=departure_date)
    else:
        tickets = searcher.search_cheapest_flight(source=departure_airport,
                                                  destination=arrival_airport,
                                                  departure_time=departure_date)

    print('Here are the tickets from your departure airport to your arrival airport: ')
    for ticket in tickets:
        print(ticket)
        

if __name__ == '__main__':
    # AIRPORTFILE = 'clean_no_dupe_itineraries'
    # FLIGHTFILE = 'clean_no_dupe_itineraries'
    AIRPORTFILE = '../data/airport_class_1000.csv'
    FLIGHTFILE = '../data/clean_no_dupe_itineraries_1000.csv'

    # run(AIRPORTFILE, FLIGHTFILE, 'naive')

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['datetime', 'csv', 'codecs', 'py7zr', 'network', 'flightsearcher', 'datetime'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
        'allowed-io': ['read_csv_file', 'run', '_get_iata_input']
    })
