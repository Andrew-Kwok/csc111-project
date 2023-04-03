"""The main file that will be run by the grader.
"""
from __future__ import annotations

from typing import Optional
import os
import sys
import csv
from datetime import datetime
from py7zr import SevenZipFile

from python_ta.contracts import check_contracts

from network import IATACode, DayHourMinute
from network import MIN_LAYOVER_TIME, MAX_LAYOVER_TIME, MAX_LAYOVER, TOP_K_RESULTS
from network import Network, Airport, Flight, Ticket
from flightsearcher import AbstractFlightSearcher, NaiveFlightSearcher, DijkstraFlightSearcher

sys.path.append(os.path.join(os.getcwd(), '..', 'data'))
sys.path.append(os.path.join(os.getcwd(), '..', 'skysearcher'))

import airport_data_cleaner
import flight_data_cleaner
import testcase_generator

ALWAYS_NO = False


def unpack_csv() -> None:
    """Unpack /data/clean_no_dupe_itineraries.7z to /data/clean_no_dupe_itineraries.csv
    """
    prev_path = os.getcwd()
    os.chdir(os.path.join(os.getcwd(), '..', 'data'))
    with SevenZipFile('clean_no_dupe_itineraries.7z', mode='r') as z:
        z.extractall()

    os.chdir(prev_path)


def read_csv_file(airport_file: str, flight_file: str) -> Network:
    """
    Read and load the CSV file into a network

    Preconditions:
        - airport_file.endswith('.csv')
        - flight_file.endswith('.csv')

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


def generate_data_from_scratch() -> None:
    """Generate the data from scratch.
    WARNING: might take up to 8GB of disk space and 8GB of RAM!
    """
    if not ask_yes_no(
            """Downloading this file (~6GB) from python is currently very slow (~30 minutes),
please download the file yourself through this link (also available on the report file):
https://utoronto-my.sharepoint.com/:u:/g/personal/nagata_aptana_mail_utoronto_ca/EQWH6C9UxMJOlVTzVXfPelkB3-ZA7N7VOBF9Naih_i5jng?download=1

Put the file in the data/ directory.
Press y if you have finished.
If you still want to use python to download the file, press n.""", default=None):
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
        elif len(choice) > 0 and choice[0] == 'y':
            print('Yes selected')
            return True
        elif len(choice) > 0 and choice[0] == 'n':
            print('No selected')
            return False
        else:
            sys.stdout.write('Invalid response, please respond with \'y\' (yes) or \'n\' (no) .\n')


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


def django_helper(airport_file: str, flight_file: str) -> tuple[AbstractFlightSearcher, AbstractFlightSearcher, list[Airport]]:
    """
    """
    # os.chdir('../data')
    flight_network = read_csv_file(airport_file, flight_file)

    return (
        NaiveFlightSearcher(flight_network=flight_network),
        DijkstraFlightSearcher(flight_network=flight_network),
        list(sorted(flight_network.airports.values(), key=lambda x: x.city))
    )


def run_django_project(airport_file: str, flight_file: str) -> None:
    import subprocess, webbrowser, requests

    # Move the directory and Start the Django server using subprocess
    os.chdir('../skysearcher')
    subprocess.Popen(['python', 'manage.py', 'runserver'])

    # Wait for the server to start up
    url = 'http://localhost:8000'
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            pass

    # Overwrite the variable in views.py using a POST request
    data = {
        'airport_file': airport_file,
        'flight_file': flight_file
    }
    response = requests.post(url, data=data)

    print(response)

    # Open the project in a web browser
    webbrowser.open(url)


if __name__ == '__main__':
    # AIRPORTFILE = 'clean_no_dupe_itineraries'
    # FLIGHTFILE = 'clean_no_dupe_itineraries'
    AIRPORTFILE = '../data/airport_class_1000.csv'
    FLIGHTFILE = '../data/clean_no_dupe_itineraries_1000.csv'

#     if not ALWAYS_NO and ask_yes_no(
#             """Do you want to download and construct the data from scratch,
# instead of using the precomputed data?

# WARNING: This action will use ~16GB of memory, ~16GB of disk space, and ~6GB of internet data,
# as well as around 5 to 40 minutes depending on the computer's processing power and download speed.
# Proceed with caution.""", default=False):
#         generate_data_from_scratch()
#     else:
#         unpack_csv()

    testcase_generator.generate_testcase_general(
        '../data/clean_no_dupe_itineraries.csv', '../data/airport_class.csv', 1000, seed=65537)
    # testcase_generator.generate_testcase_direct_flight(
    #     '../data/clean_no_dupe_itineraries.csv', '../data/airport_class.csv', 1000, seed=94231)
    #
    # run(AIRPORTFILE, FLIGHTFILE, 'naive')
    run_django_project(AIRPORTFILE, FLIGHTFILE)

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['datetime', 'csv', 'codecs', 'py7zr', 'network', 'flightsearcher', 'datetime'],
    #     'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
    #     'allowed-io': ['read_csv_file', 'run', '_get_iata_input']
    # })
