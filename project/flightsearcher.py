""" flight searcher """
from __future__ import annotations
from typing import Optional

import math
from queue import PriorityQueue
from datetime import datetime

from python_ta.contracts import check_contracts

from network import IATACode, DayHourMinute
from network import MIN_LAYOVER_TIME, MAX_LAYOVER_TIME, MAX_LAYOVER, TOP_K_RESULTS
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

    def _merge_ticket(self, tickets: list[Ticket]) -> Ticket:
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
    def _get_day_of_week(self, date: datetime) -> DayHourMinute:
        """A function that return the day and in a week and specific time of a given date
        """
        return DayHourMinute(date.weekday() + 1, date.hour, date.minute)

    def _get_datetime_other(self, pivot_date: datetime, other_time: DayHourMinute) -> datetime:
        """ Get the next possible datetime interpretation for other_time.

        Preconditions:
            - 1 <= other_time.day <= 7
            - 0 <= other_time.hour <= 23
            - 0 <= other_time.minute <= 60
        """
        pass

    def _minute_diff(self, before: DayHourMinute, after: DayHourMinute) -> int:
        """Return the difference of time between before and after (in minutes).
        """
        if before.day > after.day:
            after = DayHourMinute(after.day + 7, after.hour, after.minute)
        elif before.day == after.day and before.hour > after.hour:
            after = DayHourMinute(after.day + 7, after.hour, after.minute)
        elif before.day == after.day and before.hour == after.hour and before.minute > after.minute:
            after = DayHourMinute(after.day + 7, after.hour, after.minute)

        return (after.day * 1440 + after.hour * 60 + after.minute) - \
            (before.day * 1440 + before.hour * 60 + before.minute)


    def _day_hour_minute_diff(self, before: DayHourMinute, after: DayHourMinute) -> DayHourMinute:
        """Return the difference of time between before and after.
        """
        minute_diff = self._minute_diff(before, after)
        return DayHourMinute(day=minute_diff // 1440, hour=(minute_diff % 1440) // 60, minute=minute_diff % 60)


    def search_shortest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        raise NotImplementedError

    def search_cheapest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
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

    def _search_all_flight(self, source: Airport, destination: Airport, departure_time: DayHourMinute, visited: set[Airport]) -> list[Optional[Ticket]]:
        """ TODO DOCSTRING
        """
        if source == destination:
            return [None]
        
        paths = []
        for ticket in source.tickets:
            minute_diff = self._minute_diff(departure_time, ticket.departure_time)
            if all(flight.destination not in visited for flight in ticket.flights) and \
                (MIN_LAYOVER_TIME <= minute_diff <= MAX_LAYOVER_TIME or \
                 (len(visited) == 1 and minute_diff < 2 * MAX_LAYOVER_TIME)):  # 24 hour gap for first flight.
                next_visited = visited.union(flight.destination for flight in ticket.flights)
                if len(next_visited) > MAX_LAYOVER + 1:
                    continue
                next_paths = self._search_all_flight(source=ticket.destination, 
                                                     destination=destination, 
                                                     departure_time=ticket.arrival_time, 
                                                     visited=next_visited)
                for path in next_paths:
                    if path is None:
                        paths.append(ticket)
                    else:
                        paths.append(self._merge_ticket(ticket, path))
        return paths

    def search_shortest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        source_airport = self.flight_network.airports[source]
        destination_airport = self.flight_network.airports[destination]
        departure_weektime = self._get_day_of_week(departure_time)
        visited = {source_airport}

        tickets = self._search_all_flight(source=source_airport,
                                          destination=destination_airport,
                                          departure_time=departure_weektime,
                                          visited=visited)
        tickets.sort(key=lambda x: self._minute_diff(x.departure_time, x.arrival_time))
        return tickets[:TOP_K_RESULTS]

    def search_cheapest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        source_airport = self.flight_network.airports[source]
        destination_airport = self.flight_network.airports[destination]
        departure_weektime = self._get_day_of_week(departure_time)
        visited = {source_airport}

        tickets = self._search_all_flight(source=source_airport,
                                          destination=destination_airport,
                                          departure_time=departure_weektime,
                                          visited=visited)
        tickets.sort(key=lambda x: x.price)
        return tickets[:TOP_K_RESULTS]


# @check_contracts
class PrunedLandmarkLabeling(AbstractFlightSearcher):
    """ DOCSTRING
    """
    flight_network: Network
    label_in: list[tuple[str, float]]
    label_out: list[tuple[str, float]]

    # def _query(self, source: str, destination: str, label: dict[str, list[tuple[str, float]]]) -> float:
    #     """
    #     """
    #     s_label = label_out[source]
    #     t_label = label_in[destination]

    #     i, j = 0, 0
    #     res = math.inf
    #     while i < s_label and j < t_label:
    #         if s_label[i][0] == t_label[j][0]:
    #             res = min(res, s_label[i] + t_label[j])
    #         elif s_labe[i] < t_label[j]:
    #             j += 1
    #         else:
    #             i += 1
    #     return res

    # def _pruned_dijkstra(self):
    #     """
    #     """
    #     airports_iata = sorted(self.flight_network.airports.keys())
    #     label = [{iata: [] for iata in airports_iata} for _ in range(2)]
        
    #     for i in range(len(airports_iata)):
    #         pq = PriorityQueue()
    #         pq.put(airports_iata[i])

    #         P = [math.inf] * len(airports_iata)
    #         P[i] = 0
    #         for j in range(len(airports_iata)):
    #             label[i][j]

    # def _construct_label(self, label: dict[str, list[tuple[str, float]]]):
    #     for airport in flight_network.airports:
    #         label_in[airport] = []

    #     self._pruned_dijkstra()

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
