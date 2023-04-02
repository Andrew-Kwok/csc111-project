""" network.py """

from __future__ import annotations

from collections import namedtuple
from typing import Any, TypeAlias
from datetime import datetime

from python_ta.contracts import check_contracts


IATACode: TypeAlias = str
DayHourMinute: TypeAlias = namedtuple('DayHourMinute', ['day', 'hour', 'minute'])


@check_contracts
class Network:
    """
    A graph representing the cities and airports.
    Each node is an airport.
    Each edge is a flight connecting two airports.

    Instance Attributes:
        - city_airport: A dictionary that maps a city to a set of all the airports' iata code in the city.
        - airports: A dictionary that maps an airport's IATA code to its airport object.

    Representation Invariants:
        - pass
    """
    city_airport: dict[str, set[IATACode]]
    airports: dict[IATACode, Airport]

    def __init__(self) -> None:
        """Initialize an empty network. """
        self.city_airport: dict[str, set[IATACode]] = {}
        self.airports = {}

    def add_airport(self, airport: Airport) -> None:
        """Add an airport to this network and adds its corresponding city to this network
         if the city is not in this network.
        """
        if airport.city not in self.city_airport:
            self.city_airport[airport.city] = set()
        self.city_airport[airport.city].add(airport.iata)
        self.airports[airport.iata] = airport

    def get_airport_from_iata(self, iata: IATACode) -> Airport:
        """Return the airport corresponding to the given three-character iata code.

        Preconditions:
            - iata in self.airports
        """
        return self.airports[iata]

    def get_airport_from_city(self, city: str) -> set[Airport]:
        """Return a set of all airports in the given city.

        Preconditions:
            - city in self.city_airport
            - all(iata in self.airports for iata in self.city_airport[city])
        """
        return {self.get_airport_from_iata(iata) for iata in self.city_airport[city]}


@check_contracts
class Airport:
    """
    A node in the graph that represents a single airport.

    Instance Attributes:
        - iata: A three-character IATA airport code.
        - name: The name of the airport
        - city: The city in which this airport is located in.
        - tickets: A list of tickets which represents the possible flight paths from this airport,
         sorted in non-decreasing departure time


    Representation Invariants:
        - len(self.iata) == 3
        - all(ticket.origin == self for ticket in tickets)
        # - all(ticket[i].departure_time <= ticket[i + 1].departure_time for i in range(len(tickets) - 1))
        # TODO: check for timezone
    """
    iata: IATACode
    name: str
    city: str
    tickets: list[Ticket]

    def __init__(self, iata: IATACode, name: str, city: str) -> None:
        """Initialize an airport with the given IATA code, name and city with no flights.
        """
        self.iata = iata
        self.name = name
        self.city = city
        self.tickets = []

    def add_ticket(self, ticket: Ticket) -> None:
        """Add a ticket to the list of flights in this airport.
        """
        self.tickets.append(ticket)

    def __str__(self) -> str:
        """return some details about the airport
        """
        return f'{self.iata} - {self.name} - {self.city}'


@check_contracts
class Flight:
    """
    An edge in the graph that represents a flight between two airports.

    Instance Attributes:
        - airline: The airline operating the flight.
        - flight_id: The unique identifier of the flight.
        - origin: The departure airport of the flight.
        - destination: The destination airport of the flight.
        - departure_time: A tuple representing the day of the week, hour and minute of the departure time.
        - arrival_time: A tuple representing the day of the week, hour and minute of the arrival time.

    Representation Invariants:
        - self.origin != self.destination
        # - self.departure_time <= self.arrival_time
    """
    airline: str
    flight_id: str
    origin: Airport
    destination: Airport
    departure_time: DayHourMinute  # Day of the week, hour, minute
    arrival_time: DayHourMinute

    def __init__(self, airline: str, flight_id: str, origin: Airport, destination: Airport,
                 departure_time: DayHourMinute, arrival_time: DayHourMinute) -> None:
        """Initialise a flight with the given airline, flight id, origin, destination, departure time and
        arrival time. """
        self.airline = airline
        self.flight_id = flight_id
        self.origin = origin
        self.destination = destination
        self.departure_time = DayHourMinute(*departure_time)
        self.arrival_time = DayHourMinute(*arrival_time)


    def __str__(self) -> str:
        """print some details about the flight
        """
        return f'{self.flight_id} | {self.airline} | {self.origin.iata}({str(self.departure_time)}) to {self.destination.iata}({str(self.arrival_time)})'


@check_contracts
class Ticket:
    """
    A ticket containing a list of flights and its total price.

    Instance Attributes:
        - flights: A list of the flights on the ticket.
        - price: The total price of all the flights on the ticket.
        - origin: The departure airport of the flight.
        - destination: The destination airport of the flight.

    Representation Invariants:
        - self.flights != []
        # - all(self.flights[i].arrival_time <= self.flights[i+1].departure_time for i in range(len(self.flights) - 1))
        - len(flights) + 1 == \
        len({flight.origin flight for flight in flights} + {flight.destination flight for flight in flights})
        - self.origin != self.destination
        - self.origin == self.flights[0].origin
        - self.destination == self.flights[-1].destination
        - self.price > 0
    """
    origin: Airport
    destination: Airport
    flights: list[Flight]
    price: float

    def __init__(self, origin: Airport, destination: Airport, flights: list[Flight], price: float) -> None:
        self.origin = origin
        self.destination = destination
        self.flights = flights
        self.price = price

    def __str__(self) -> str:
        """print some details about the ticket
        """
        flight_info = " - ".join(f'{flight.airline}({flight.flight_id})' for flight in self.flights)
        return f'{self.origin.iata} to {self.destination.iata} | {self.price} | {flight_info}'


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['datetime'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
    })
