"""The main file that will be run by the grader.
"""
from __future__ import annotations

import csv
import codecs
import datetime

from py7zr import SevenZipFile

from python_ta.contracts import check_contracts

from network import Network, Airport, Flight, Ticket, IATACode, DayHourMinute
from flightsearcher import NaiveFlightSearcher, PrunedLandmarkLabeling, Dijkstra


def unpack_csv() -> None:
    """Unpack /data/clean_no_dupe_itineraries.7z to /data/clean_no_dupe_itineraries.csv
    """

    with SevenZipFile('../data/' + FLIGHTFILE + '.7z', mode='r') as z:
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
        header = [
            'iata_code',
            'name',
            'municipality'
        ]
        assert reader.fieldnames == header

        for row in reader:
            airport = Airport(
                iata=row['iata_code'],
                name=row['name'],
                city=row['municipality']
            )
            res_network.add_airport(airport)

    with open(flight_file) as csv_file:
        reader = csv.DictReader(csv_file)
        header = [
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
            'destinationAirport',
        ]
        assert reader.fieldnames == header

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
                    arrival_time=DayHourMinute(arrival_weekday[0], arrival_timeday[i][0], arrival_timeday[i][1])
                )
                flights.append(flight)

            ticket = Ticket(
                origin=origin,
                destination=destination,
                flights=flights,
                price=price
            )

            if origin not in airport_ticket:
                airport_ticket[origin] = []
            airport_ticket[origin].append(ticket)

        for origin in airport_ticket:
            tickets = airport_ticket[origin]
            tickets.sort(key=lambda x: x.flights[0].departure_time)

            for ticket in tickets:
                origin.add_ticket(ticket)

    return res_network


def run(airport_file: str, flight_file: str) -> None:
    """ Docstring here
    """
    flight_network = read_csv_file(airport_file, flight_file)
    dijkstra_searcher = Dijkstra(flight_network)

    # do some operations with naive searcher
    tickets = dijkstra_searcher.search_shortest_flight('LGA', 'ORD', datetime.datetime(2023, 4, 1))

    for x in flight_network.city_airport:
        print(x, flight_network.city_airport[x])

    # for x in flight_network.airports:
    #     print(x, flight_network.airports[x])
    #     for ticket in flight_network.airports[x].tickets:
    #         print(ticket)
    #         for flight in ticket.flights:
    #             print(flight)
    #     print()

    print('tickets:')
    for ticket in tickets:
        print(ticket)


if __name__ == '__main__':
    # AIRPORTFILE = 'clean_no_dupe_itineraries'
    # FLIGHTFILE = 'clean_no_dupe_itineraries'

    AIRPORTFILE = '../data/airport_class_direct_1000.csv'
    FLIGHTFILE = '../data/clean_no_dupe_itineraries_direct_1000.csv'

    run(AIRPORTFILE, FLIGHTFILE)

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['datetime', 'csv', 'codecs', 'py7zr', 'network', 'flightsearcher'],
    #     'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
    #     'allowed-io': ['read_csv_file']
    # })
