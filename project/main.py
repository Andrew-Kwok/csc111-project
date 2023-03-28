"""The main file that will be run by the grader.
"""
from __future__ import annotations

import csv
import codecs
from py7zr import SevenZipFile

from network import Network, Airport, Flight, Ticket

from python_ta.contracts import check_contracts

# AIRPORTFILE = 'clean_no_dupe_itineraries'
# FLIGHTFILE = 'clean_no_dupe_itineraries'

AIRPORTFILE = '../data/clean_no_dupe_small'
FLIGHTFILE = '../data/clean_no_dupe_small'


def unpack_csv() -> None:
    """Unpack /data/clean_no_dupe_itineraries.7z to /data/clean_no_dupe_itineraries.csv
    """

    with SevenZipFile('../data/' + FLIGHTFILE + '.7z', mode='r') as z:
        z.extractall()

    print('Finished extracting.')


def read_csv_file() -> Network:
    res_network = Network()

    with open(AIRPORTFILE + '.csv') as csv_file:
        reader = csv.DictReader(csv_file)
        header = [
            'startingAirport'
        ]

        for row in reader:
            airport = Airport(
                    iata=row['startingAirport'],
                    name=row['startingAirport'],
                    city=row['startingAirport']
                )
            res_network.add_airport(airport)
            airport = Airport(      
                    iata=row['destinationAirport'],
                    name=row['destinationAirport'],
                    city=row['destinationAirport']
                )
            res_network.add_airport(airport)


            departure = row['segmentsDepartureAirportCode'].split('||')
            for iata in departure:
                airport = Airport(
                        iata=iata,
                        name=iata,
                        city=iata
                    )
                res_network.add_airport(airport)



    with open(FLIGHTFILE + '.csv') as csv_file:
        reader = csv.DictReader(csv_file)
        header = [
            'legId',
            'startingAirport',
            'destinationAirport',
            'isNonStop',
            'totalFare',
            'segmentsArrivalAirportCode',
            'segmentsDepartureAirportCode',
            'segmentsAirlineName',
            'segmentsDepartureWeekday',
            'segmentsDepartureTimeOfDay',
            'segmentsArrivalWeekday',
            'segmentsArrivalTimeOfDay'
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
            departure = [res_network.get_airport_from_iata(airport) for airport in departure]

            departure_weekday = list(map(int, row['segmentsDepartureWeekday'].split('||')))
            departure_timeday = row['segmentsDepartureTimeOfDay'].split('||')
            departure_timeday = [tuple(map(int, timeday.split(':'))) for timeday in departure_timeday]

            arrival = row['segmentsArrivalAirportCode'].split('||')
            arrival = [res_network.get_airport_from_iata(airport) for airport in arrival]

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
                    departure_time=(departure_weekday[0], departure_timeday[i][0], departure_timeday[i][1]),
                    arrival_time=(arrival_weekday[0], arrival_timeday[i][0], arrival_timeday[i][1])
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


if __name__ == '__main__':
    # extract the 7z file
    # unpack_csv()

    read_csv_file()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['datetime'],
    #     'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
    # })