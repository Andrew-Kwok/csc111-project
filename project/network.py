""" network.py """

from __future__ import annotations
from typing import Any

from datetime import datetime


from python_ta.contracts import check_contracts


@check_contracts
class Network:
    """
    A graph representing the cities and airports.
    Each node is an airport.
    Each edge is a flight connecting two airports.

    Instance Attributes:
        - cities: A list of all the cities in the network.
        - airports: A dictionary that maps a city to a list of all the airports in the city.

    Representation Invariants:
        - all(city in self.airports for city in self.cities)
    """
    cities: set[str]
    airports: dict[str, set[Airport]]

    def __init__(self) -> None:
        """Initialize an empty network. """
        self.cities = set()
        self.airports = {}

    def add_airport(self, airport: Airport) -> None:
        """Add an airport to this network and adds its corresponding city to this network
         if the city is not in this network.
        """
        if airport.city not in self.cities:
            self.cities.add(airport.city)
            self.airports[airport.city] = set()
        self.airports[airport.city].add(airport)


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
        - all(ticket.origin == self for ticket in tickets)
        - all(ticket[i].departure_time <= ticket[i + 1].departure_time for i in range(len(tickets) - 1))
    """
    iata: str
    name: str
    city: str
    tickets: list[Ticket]

    def __init__(self, iata: str, name: str, city: str) -> None:
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
        - self.departure_time <= self.arrival_time
    """
    airline: str
    flight_id: str
    origin: Airport
    destination: Airport
    departure_time: tuple[int, int, int]  # Day of the week, hour, minute
    arrival_time: tuple[int, int, int]

    def __init__(self, airline: str, flight_id: str, origin: Airport, destination: Airport,
                 departure_time: tuple[int, int, int], arrival_time: tuple[int, int, int]) -> None:
        """Initialise a flight with the given airline, flight id, origin, destination, departure time and
        arrival time. """
        self.airline = airline
        self.flight_id = flight_id
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time


@check_contracts
class Ticket:
    """
    A ticket containing a list of flights and its total price.

    Instance Attributes:
        - flights: A list of the flights on the ticket.
        - price: The total price of all the flights on the ticket.

    Representation Invariants:
        - self.flights != []
        - all(self.flights[i].arrival_time <= self.flights[i+1].departure_time for i in range(len(self.flights) - 1))
        - len(flights) + 1 == \
        len({flight.origin flight for flight in flights} + {flight.destination flight for flight in flights})
        - self.price > 0
    """
    flights: list[Flight]
    price: float

    def __init__(self, flights: list[Flight], price: float) -> None:
        self.flights = flights
        self.price = price


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['datetime'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
    })
