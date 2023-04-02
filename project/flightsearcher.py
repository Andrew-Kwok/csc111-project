""" flight searcher """
from __future__ import annotations

import math
from datetime import datetime, timedelta

from python_ta.contracts import check_contracts

from network import Network, Airport, Flight, Ticket, IATACode, DayHourMinute
import queue


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

    def _merge_ticket(self, tickets: list[Ticket]) -> Ticket:
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

    def _get_day_of_week(self, date: datetime) -> DayHourMinute:
        """A function that return the day and in a week and specific time of a given date
        """
        return (date.weekday(), date.hour, date.minute)

    def _get_datetime_other(self, pivot_date: datetime, other_time: DayHourMinute) -> datetime:
        """ Get the next possible datetime interpretation for other_time.

        Preconditions:
            - 1 <= other_time.day <= 7
            - 0 <= other_time.hour <= 23
            - 0 <= other_time.minute <= 60
        """

    def _day_hour_minute_diff(self, before: DayHourMinute, after: DayHourMinute) -> DayHourMinute:
        """Return the difference of time between before and after.
        """
        if before.day > after.day:
            after = DayHourMinute(after.day + 7, after.hour, after.minute)
        elif before.day == after.day and before.hour > after.hour:
            after = DayHourMinute(after.day + 7, after.hour, after.minute)
        elif before.day == after.day and before.hour == after.hour and before.minute > after.minute:
            after = DayHourMinute(after.day + 7, after.hour, after.minute)

        minute_diff = (after.day * 1440 + after.hour * 60 + after.minute) - \
                      (before.day * 1440 + before.hour * 60 + before.minute)

        return DayHourMinute(day=minute_diff // 1440, hour=(minute_diff % 1440) // 60, minute=minute_diff % 60)

    def search_shortest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        raise NotImplementedError

    def search_cheapest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        raise NotImplementedError


# @check_contracts
class NaiveFlightSearcher(AbstractFlightSearcher):
    """ TODO: Docstring
    """
    # Make more helper functions

    def __init__(self, flight_network: Network) -> None:
        """ TODO DOCSTRING
        """
        AbstractFlightSearcher.__init__(self, flight_network)

    def search_shortest_flight(source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        pass

    def search_cheapest_flight(source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """
        """
        pass


# @check_contracts
class PrunedLandmarkLabeling(AbstractFlightSearcher):
    """ DOCSTRING
    """
    # TODO: description + helper functions

    def __init__(self, flight_network: Network) -> None:
        """ TODO DOCSTRING
        """
        AbstractFlightSearcher.__init__(self, flight_network)

    def search_shortest_flight(source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        pass

    def search_cheapest_flight(source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """
        """
        pass


class Dijkstra(AbstractFlightSearcher):
    """Use Dijkstra algorithm to find the shortest path."""

    def __init__(self, flight_network: Network) -> None:
        """ TODO DOCSTRING
        """
        AbstractFlightSearcher.__init__(self, flight_network)

    def search_shortest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        Compare based on the times
        """

    def search_cheapest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """Compare based on price; should be easier.
        """


if __name__ == '__main__':

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['network', 'datetime'],
    #     'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
    #     'allowed-io': []
    # })
    pass
