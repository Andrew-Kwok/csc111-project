from __future__ import annotations

import math
from queue import PriorityQueue
from datetime import datetime

from python_ta.contracts import check_contracts

from network import Network, Airport, Flight, Ticket


@check_contracts
class AbstractFlightSearcher:
    """
    An abstract implementation of flight search.

    Instance Attributes:
        - flight_network: The network used to look-up flights.
    """
    flight_network: Network

    def __init__(self, flight_network: Network) -> None:
        """ Initializer of AbstractFlightSearch
        """
        self.flight_network = flight_network

    def _merge_ticket(tickets: list[Ticket]) -> Ticket:
        """A function that merge a list of tickets on a transit route
        """
        origin = tickets[0].origin
        destination = tickets[-1].destination
        price_so_far = 0
        flights_so_far = []
        for ticket in tickets:
            flights_so_far.extend(ticket.flights)
            price_so_far += ticket.price

        return Ticket(origin, destination, flights_so_far, price_so_far)

    def _get_day_of_week(self, date: datetime) -> tuple[int, int, int]:
        """A function that return the day and in a week and specific time of a given date
        """
        return (date.weekday(), date.hour, date.minute)

    def _get_datetime_other(self, pivot_date: datetime, other_time: tuple[int, int, int]) -> datetime:
        """ Return the correspond datetime object based on the pivot_date and information of other_time in
        weekday, hour, minute
        """
        # pivot_day = pivot_date.weekday()
        # if other_time[0] >= pivot_day:
        #     return_date = pivot_date + (other_time[0] - pivot_day) #difference in days
        # else:
        #     return_date = pivot_date + (7 - pivot_day - other_time[0]) #difference in days
        #
        # return return_date

    def search_shortest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ Return a list of tickets for a shortest path between a given source and destination
        """
        raise NotImplementedError

    def search_cheapest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ Return a list of tickets for a cheapeast path between a given source and destination"""
        raise NotImplementedError


@check_contracts
class NaiveFlightSearcher(AbstractFlightSearcher)
    """A subclass of AbstractFlightSearcher"""
    # Make more helper functions

    def __init__(self, flight_network: Network) -> None:
        """ Initializer for NaiveFlightSearcher"""

        AbstractFlightSearcher.__init__(self, flight_network)

    def search_shortest_flight(source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ Return a list of tickets for a shortest path between a given source and destination
        """
        pass
        origin = flight_network.get_airport_from_iata(source)

    def search_cheapest_flight(source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """Return a list of tickets for a cheapeast path between a given source and destination
        """
        pass

class PrunedLandmarkLabeling(AbstractFlightSearcher):
        """
        AbstractFlightSearcher.__init__(self, flight_network)

    def search_shortest_flight(source: str, destination: str, departure_time: datetime) -> list[Ticket]: 
    def search_shortest_flight(source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        pass
@ -101,11 +109,10 @@ class PrunedLandmarkLabeling(AbstractFlightSearcher):


if __name__ == '__main__':

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['network', 'datetime'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
        'allowed-io': []
    })
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['network', 'datetime'],
    #     'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
    #     'allowed-io': []
    # })
