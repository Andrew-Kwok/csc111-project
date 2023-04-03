""" network.py """

from __future__ import annotations

from collections import namedtuple
from typing import Any, TypeAlias
from datetime import datetime

from python_ta.contracts import check_contracts


IATACode: TypeAlias = str
DayHourMinute: TypeAlias = namedtuple('DayHourMinute', ['day', 'hour', 'minute'])

MIN_LAYOVER_TIME = 90   # minutes
MAX_LAYOVER_TIME = 720  # minutes
MAX_LAYOVER = 3         # stops
TOP_K_RESULTS = 10


# @check_contracts
class Network:
    """
    A graph representing the cities and airports.
    Each node is an airport.
    Each edge is a flight connecting two airports.

    Instance Attributes:
        - city_airport: A dictionary that maps a city to a set of all the airports' iata code in the city.
        - airports: A dictionary that maps an airport's IATA code to its airport object.

    Representation Invariants:
        - all(iata in self.airports for iata in iatas for iatas in self.city_airport.values())
    """
    city_airport: dict[str, set[IATACode]]
    airports: dict[IATACode, Airport]

    def __init__(self) -> None:
        """Initialize an empty network. """
        self.city_airport = {}
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


# @check_contracts
class Airport:
    """
    A node in the graph that represents a single airport.

    Instance Attributes:
        - iata: A three-character IATA airport code.
        - name: The name of the airport.
        - city: The city in which this airport is located in.
        - tickets: A list of tickets which represents the possible flight paths from this airport,
         sorted in non-decreasing departure time.


    Representation Invariants:
        - len(self.iata) == 3
        - all(ticket.origin == self for ticket in tickets)
        - all(ticket[i].departure_time <= ticket[i + 1].departure_time for i in range(len(tickets) - 1))
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
        """Return a string representing the iata code, name and location(city) of the airport.
        """
        return f'{self.iata} - {self.name} - {self.city}'


# @check_contracts
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
        """Return a string representing the flight_id, airline, iata code of the origin airport, departure time, iata
        code of the destination airport, and arrival time of the flight.
        """
        return f'{self.flight_id} | {self.airline} | {self.origin.iata} ({str(self.departure_time)})' \
               f' to {self.destination.iata} ({str(self.arrival_time)})'


# @check_contracts
class Ticket:
    """
    A ticket containing a list of flights and its total price.

    Instance Attributes:
        - origin: The departure airport of the flight.
        - destination: The destination airport of the flight.
        - departure_time: A tuple representing the day of the week, hour and minute of the departure time of the first
        flight in the ticket.
        - arrival_time: A tuple representing the day of the week, hour and minute of the arrival time of the last flight
        in the ticket.
        - flights: A list of the flights on the ticket.
        - price: The total price of all the flights on the ticket.

    Representation Invariants:
        - self.flights != []
        - len(flights) + 1 == \
        len({flight.origin for flight in self.flights} + {flight.destination for flight in self.flights})
        - self.origin != self.destination
        - self.origin == self.flights[0].origin
        - self.destination == self.flights[-1].destination
        - self.price > 0
        - self.departure_time == self.flights[0].departure_time
        - self.arrival_time == self.flights[-1].arrival_time
    """
    origin: Airport
    destination: Airport
    departure_time: DayHourMinute
    arrival_time: DayHourMinute
    flights: list[Flight]
    price: float

    def __init__(self, origin: Airport, destination: Airport, departure_time: DayHourMinute,
                 arrival_time: DayHourMinute, flights: list[Flight], price: float) -> None:
        """Initialize a ticket with the fiven origin airport, destination airport, departure time, arrival time, flights
        and price.
        """
        self.origin = origin
        self.destination = destination
        self.departure_time = DayHourMinute(*departure_time)
        self.arrival_time = DayHourMinute(*arrival_time)
        self.flights = flights
        self.price = price

    def __str__(self) -> str:
        """Return a string representing the iata code of the origin airport, the iata of the destination airport, the
        price of the ticket and the flight information for each flight on the ticket. Each flight information consists
        of the airline and flight_id of the flight.
        """
        flight_info = "\n\t".join(f'{flight}' for flight in self.flights)
        return f'{self.origin.iata} to {self.destination.iata} | {self.price} \n\t{flight_info}'

    def __lt__(self, other: Ticket) -> bool:
        """placeholder for less than"""
        if self.flights[-1].arrival_time < other.flights[-1].arrival_time:
            return True
        elif self.flights[0].departure_time < other.flights[0].departure_time:
            return True
        return False


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['datetime', 'collections'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports', 'E9992', 'E9997', 'too-many-arguments'],
    })
