""" network.py """

from __future__ import annotations
from datetime import datetime
from typing import Any


class Network:
    """
    """
    cities: list[str]
    airports: dict[str, list[Airport]]
    pass


class Airport:
    """
    """
    IATA: str
    name: str
    city: str
    flights: list[Ticket]
    pass


class Flight:
    """
    """
    airline: str
    origin: Airport
    destination: Airport
    departure_time: tuple[int, int, int]  # Day of the week, hour, minute
    arrival_time: tuple[int, int, int]
    pass


class Ticket:
    """
    """
    flights: list[Flight]
    price: float
    pass


class AbstractFlightSearch:
    """
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
