"""The main file that will be run by the grader.
"""
from __future__ import annotations

import sys
import csv
import codecs
import os
from datetime import datetime
from py7zr import SevenZipFile
from typing import Optional

from python_ta.contracts import check_contracts

from network import IATACode, DayHourMinute
from network import MIN_LAYOVER_TIME, MAX_LAYOVER_TIME, MAX_LAYOVER, TOP_K_RESULTS
from network import Network, Airport, Flight, Ticket
from flightsearcher import AbstractFlightSearcher, NaiveFlightSearcher, PrunedLandmarkLabeling, DijkstraFlightSearcher

sys.path.append(os.path.join(os.getcwd(), '..', 'data'))

import airport_data_cleaner
import flight_data_cleaner
import testcase_generator


def unpack_csv() -> None:
    """Unpack /data/clean_no_dupe_itineraries.7z to /data/clean_no_dupe_itineraries.csv
    """

    with SevenZipFile(os.path.join(os.getcwd(), '..', 'data', 'clean_no_dupe_itineraries.7z'), mode='r') as z:
        z.extractall(path=os.path.join(os.getcwd(), '..', 'data'))

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

            try:
                assert origin == departure[0] and destination == arrival[-1]
            except AssertionError:
                print(row)
                exit()
            assert len(departure) == len(arrival)

            flights = []
            for i in range(len(departure)):
                flight = Flight(
                    airline=airline[i],
                    flight_id=flight_id,
                    origin=departure[i],
                    destination=arrival[i],
                    departure_time=DayHourMinute(
                        day=departure_weekday[i], hour=departure_timeday[i][0], minute=departure_timeday[i][1]
                    ),
                    arrival_time=DayHourMinute(arrival_weekday[i], arrival_timeday[i][0], arrival_timeday[i][1])
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
    pass


def generate_data_from_scratch() -> None:
    """Generate the data from scratch.
    WARNING: might take up to 8GB of disk space and 8GB of RAM!
    """

    flight_data_cleaner.download_flight_data()
    flight_data_cleaner.select_useful_columns(columns=flight_data_cleaner.KAGGLE_COLUMNS)
    flight_data_cleaner.select_unique_flights()
    flight_data_cleaner.unique_itineraries()
    flight_data_cleaner.epoch_to_weekday_time_itineraries()

    airport_data_cleaner.download_airport_data()
    airport_data_cleaner.airport_class_file()


def ask_yes_no(question: str, default: Optional[bool]) -> bool:
    """Ask a yes/no question in the prompt."""
    if default is None:
        prompt = ' [y/n] '
    elif default is True:
        prompt = ' [Y/n] '
    elif default is False:
        prompt = ' [y/N] '
    else:
        raise ValueError(f'Invalid default answer {default}')

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()

        if default is not None and choice == '':
            return default
        elif choice[0] == 'y':
            print('Yes selected')
            return True
        elif choice[0] == 'n':
            print('No selected')
            return False
        else:
            sys.stdout.write('Invalid response, please respond with \'y\' (yes) or \'n\' (no) .\n')


def run(airport_file: str, flight_file: str) -> None:
    """ Docstring here
    """
    flight_network = read_csv_file(airport_file, flight_file)
    dijkstra_searcher = DijkstraFlightSearcher(flight_network)

    # do some operations with naive searcher
    # naive_searcher.search_shortest_flight(city_1, city_2)

    tickets = dijkstra_searcher.search_shortest_flight('ATL', 'EWR', datetime(2023, 4, 6))
    for ticket in tickets:
        print(ticket)

    # for x in flight_network.city_airport:
    #     print(x, flight_network.city_airport[x])

    # for x in flight_network.airports:
    #     print(x, flight_network.airports[x])
    #     for ticket in flight_network.airports[x].tickets:
    #         print(ticket)
    #         for flight in ticket.flights:
    #             print(flight)
    #     print()


if __name__ == '__main__':
    # AIRPORTFILE = 'clean_no_dupe_itineraries'
    # FLIGHTFILE = 'clean_no_dupe_itineraries'
    ALWAYS_NO = False

    if not ALWAYS_NO and ask_yes_no(
            """Do you want to download and construct the data from scratch,'
            instead of using the precomputed data?
            
            WARNING: This action will use ~8GB of memory, disk space, and internet data,
            as well as around 10 minutes depending on the computer's processing power
            and download speed. Proceed with caution.
            """, default=False):
        generate_data_from_scratch()
    else:
        unpack_csv()

    # testcase_generator.generate_testcase_general(
    #     'clean_no_dupe_itineraries.csv', '../data/airport_class.csv', 1000, seed=65537)
    # testcase_generator.generate_testcase_direct_flight(
    #     'clean_no_dupe_itineraries.csv', '../data/airport_class.csv', 1000, seed=94231)
    #
    # AIRPORTFILE = '../data/airport_class'
    # FLIGHTFILE = 'clean_no_dupe_itineraries'
    #
    # run(AIRPORTFILE + '.csv', FLIGHTFILE + '.csv')

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['datetime', 'csv', 'codecs', 'py7zr', 'network', 'flightsearcher', 'datetime'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
        'allowed-io': ['read_csv_file']
    })
