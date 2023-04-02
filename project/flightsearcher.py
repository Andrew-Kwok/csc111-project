""" flight searcher """
from __future__ import annotations

import math
from datetime import datetime, timedelta

from python_ta.contracts import check_contracts

from network import Network, Airport, Flight, Ticket, IATACode, DayHourMinute
import queue


# @check_contracts
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
        k = 5
        dep_time_simpl = DayHourMinute(departure_time.isoweekday(), departure_time.hour, departure_time.minute)
        pq = queue.PriorityQueue()
        pq.put((dep_time_simpl, source, None, 0))
        distance: dict[IATACode, list[DayHourMinute]] = {iata: [] for iata in self.flight_network.airports}
        previous: dict[IATACode, list[tuple[Ticket, int]]] = {iata: [] for iata in self.flight_network.airports}
        first_flight = True
        first_path = True

        while not pq.empty():
            curr_time, curr_pos, prev_ticket, prev_k = pq.get()

            if len(distance[curr_pos]) == k:
                continue

            print(curr_time, curr_pos)
            print(prev_ticket, prev_k)
            distance[curr_pos].append(curr_time)

            if not first_flight:
                previous[curr_pos].append((prev_ticket, prev_k))

            if curr_pos == destination:
                first_path = False
                continue

            for ticket in self.flight_network.airports[curr_pos].tickets:
                depart_time = ticket.flights[0].departure_time

                if not first_flight:
                    time_to_depart = self._day_hour_minute_diff(curr_time, depart_time)
                    if not DayHourMinute(0, 1, 30) < time_to_depart < DayHourMinute(0, 12, 0):
                        continue
                if first_path and depart_time.day != dep_time_simpl.day:
                    continue

                pq.put((ticket.flights[-1].arrival_time, ticket.destination.iata, ticket, len(distance[curr_pos]) - 1))

            first_flight = False

        results = []
        for i in range(len(distance[destination])):
            path = []
            now_pos = destination
            prev_tuple = (None, i)
            while now_pos != source:
                prev_tuple = previous[now_pos][prev_tuple[1]]
                path.append(prev_tuple[0])
                now_pos = prev_tuple[0].origin.iata

            assert now_pos == source
            path.reverse()
            results.append(self._merge_ticket(path))

        return results

    def search_cheapest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """Compare based on price; should be easier.
        """
        k = 5
        dep_time_simpl = DayHourMinute(departure_time.isoweekday(), departure_time.hour, departure_time.minute)
        pq = queue.PriorityQueue()
        pq.put((0.0, source, None, 0))
        cheapest: dict[IATACode, list[float]] = {iata: [] for iata in self.flight_network.airports}
        previous: dict[IATACode, list[tuple[Ticket, int]]] = {iata: [] for iata in self.flight_network.airports}
        first_flight = True
        first_path = True

        while not pq.empty():
            curr_price, curr_pos, prev_ticket, prev_k = pq.get()

            if len(cheapest[curr_pos]) == k:
                continue

            print(curr_price, curr_pos)
            print(prev_ticket, prev_k)
            cheapest[curr_pos].append(curr_price)

            if not first_flight:
                previous[curr_pos].append((prev_ticket, prev_k))

            if curr_pos == destination:
                first_path = False
                continue

            for ticket in self.flight_network.airports[curr_pos].tickets:
                depart_time = ticket.flights[0].departure_time

                if not first_flight:
                    time_to_depart = self._day_hour_minute_diff(prev_ticket.flights[-1].arrival_time, depart_time)
                    if not DayHourMinute(0, 1, 30) < time_to_depart < DayHourMinute(0, 12, 0):
                        continue
                if first_path and depart_time.day != dep_time_simpl.day:
                    continue

                pq.put((curr_price + ticket.price, ticket.destination.iata, ticket, len(cheapest[curr_pos]) - 1))

            first_flight = False

        results = []
        for i in range(len(cheapest[destination])):
            print(cheapest[destination][i])
            path = []
            now_pos = destination
            prev_tuple = (None, i)
            while now_pos != source:
                prev_tuple = previous[now_pos][prev_tuple[1]]
                path.append(prev_tuple[0])
                now_pos = prev_tuple[0].origin.iata

            assert now_pos == source
            path.reverse()
            results.append(self._merge_ticket(path))

        return results


if __name__ == '__main__':

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['network', 'datetime'],
    #     'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
    #     'allowed-io': []
    # })
    pass
