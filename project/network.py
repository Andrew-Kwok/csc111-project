""" network.py """

from __future__ import annotations
from datetime import datetime
from typing import Any


class Network:
    """
    A graph representing the cities and airports.
    Each node is an airport.
    Each edge is a flight connecting two airports.

    Instance Attributes:
        - cities: A list of all the cities in the network.
        - airports: A dictionary that maps a city to a list of all the airports in the city.

    Representation Invariants:
        - city in list(self.airports.keys()) for city in cities
    """
    cities: list[str]
    airports: dict[str, list[Airport]]

    def __init__(self) -> None:
        """Initialize an empty network. """
        self.cities = []
        self.airports = {}

    def add_airport(self, airport: Airport) -> None:
        """Add an airport to this network and adds its corresponding city to this network if the city is not in this
        network. """
        if airport.city not in self.cities:
            self.cities.append(airport.city)
        self.airports[airport.city].append(airport)


class Airport:
    """
    A node in the graph that represents a single airport.

    Instance Attributes:
        - IATA: A three-character IATA airport code.
        - name: The name of the airport
        - city: The city in which this airport is located in.
        - flights: A list of tickets which represents the possible flight paths from this airport.


    Representation Invariants:
        - self.flights[0].origin == self
    """
    IATA: str
    name: str
    city: str
    flights: list[Ticket]

    def __init__(self, IATA: str, name: str, city: str) -> None:
        """Initialize an airport with the given IATA code, name and city with no flights. """
        self.IATA = IATA
        self.name = name
        self.city = city
        self.flights = []

    def add_ticket(self, ticket: ticket) -> None:
        """Add a ticket to the list of flights in this airport. """
        self.flights.append(ticket)


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
        - #TODO departure_time is before arrival_time
    """
    airline: str
    flight_id: str
    origin: Airport
    destination: Airport
    departure_time: tuple[int, int, int]  # Day of the week, hour, minute
    arrival_time: tuple[int, int, int]

    def __init__(self, airline: str, flight_id: str, origin: Airport, destination: Airport,
                 departure_time: tuple[int, int, int], arrival_time: tuple[int, int, int]):
        """Initialise a flight with the given airline, flight id, origin, destination, departure time and
        arrival time. """
        self.airline = airline
        self.flight_id = flight_id
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time


class Ticket:
    """
    A ticket containing a list of flights and its total price.

    Instance Attributes:
        - flights: A list of the flights on the ticket.
        - price: The total price of all the flights on the ticket.

    Representation Invariants:
        - self.flights != []
        - self.price > 0
    """
    flights: list[Flight]
    price: float
    pass


class AbstractFlightSearch:
    """
    An abstract implementation of flight search.

    Instance Attributes:
        - flight_network: The network used to look-up flights.
    """
    flight_network: Network

    def __init__(self, flight_network: Network):
        """
        """
        self.flight_network = flight_network

    def _merge_ticket(tickets: list[Ticket]) -> Ticket:
        """
        """
        pass

    def _get_day_of_week(date: datetime) -> tuple[int, int, int]:
        """
        """
        pass

    def _get_datetime_other(pivot_date: datetime, other_time: tuple[int, int, int]) -> datetime:
        """
        """
        pass

    def search_shortest_flight(source: str, destination: str, departure_time: datetime):
        """
        """
        raise NotImplementedError

    def search_cheapest_flight(source: str, destination: str, departure_time: datetime):
        """
        """
        raise NotImplementedError
