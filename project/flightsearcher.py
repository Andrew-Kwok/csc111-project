""" flight searcher """
from __future__ import annotations
from typing import Optional

from queue import PriorityQueue
from datetime import datetime

from python_ta.contracts import check_contracts

from network import IATACode, DayHourMinute
from network import MIN_LAYOVER_TIME, MAX_LAYOVER_TIME, MAX_LAYOVER, TOP_K_RESULTS
from network import Network, Airport, Flight, Ticket


# @check_contracts
class AbstractFlightSearcher:
    """
    Abstract class for flight search.

    Instance Attributes:
        - flight_network: The network used to look-up flights.
    """
    flight_network: Network

    def __init__(self, flight_network: Network) -> None:
        """Initializes a flight network for Abstract Flight Searcher.
        """
        self.flight_network = flight_network

    def _merge_ticket(self, tickets: list[Ticket]) -> Ticket:
        """Merge a list of tickets into one ticket and return the merged ticket.
        """
        origin = tickets[0].origin
        destination = tickets[-1].destination
        departure_time = tickets[0].departure_time
        arrival_time = tickets[-1].arrival_time
        price_so_far = 0
        flights_so_far = []
        for ticket in tickets:
            flights_so_far.extend(ticket.flights)
            price_so_far += ticket.price

        return Ticket(origin=origin,
                      destination=destination,
                      departure_time=departure_time,
                      arrival_time=arrival_time,
                      flights=flights_so_far,
                      price=price_so_far)

    def _get_day_of_week(self, date: datetime) -> DayHourMinute:
        """Returns the day of the week, hour and minute of a given date.
        """
        return DayHourMinute(date.weekday() + 1, date.hour, date.minute)

    def _get_datetime_other(self, pivot_date: datetime, other_time: DayHourMinute) -> datetime:
        """Get the next possible datetime interpretation for other_time.

        Preconditions:
            - 1 <= other_time.day <= 7
            - 0 <= other_time.hour <= 23
            - 0 <= other_time.minute <= 60
        """

    def _minute_diff(self, before: DayHourMinute, after: DayHourMinute) -> int:
        """Return the difference in time between before and after (in minutes).
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

    def search_shortest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """ An abstract function that returns a list of tickets where each ticket departs from `source` and ends at
        `destination`. The flight departs on the same day as `departure_time`. The ticket is sorted in non-decreasing
        flight duration.

        Preconditions:
            - source in self.flight_network.airports
            - destination in self.flight_network.airports
            - d.hour == 0 and d.minute == 0
        """
        raise NotImplementedError

    def search_cheapest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """ An abstract function that returns a list of tickets where each ticket departs from `source` and ends at
        `destination`. The flight departs on the same day as `departure_time`. The ticket is sorted in non-decreasing
        price.

        Preconditions:
            - source in self.flight_network.airports
            - destination in self.flight_network.airports
            - d.hour == 0 and d.minute == 0
        """
        raise NotImplementedError


# @check_contracts
class NaiveFlightSearcher(AbstractFlightSearcher):
    """A naive implementation of flight searcher.
    """
    # Make more helper functions

    def __init__(self, flight_network: Network) -> None:
        """Initializes a flight network for NaiveFlightSearcher.
        """
        AbstractFlightSearcher.__init__(self, flight_network)

    def _search_all_flight(self, source: Airport, destination: Airport, departure_time: DayHourMinute,
                           visited: set[Airport]) -> list[Optional[Ticket]]:
        """Returns all possible flight paths that departs from the `source`, on the same day as departure_time to the
        given `destination`. Each ticket can only visit each airport at most once. This function also takes into
        consideration the minimum and maximum layover time, and the maximum number of layovers.
        """
        if source == destination:
            return [None]

        paths = []
        for ticket in source.tickets:
            minute_diff = self._minute_diff(departure_time, ticket.departure_time)
            if any(flight.destination in visited for flight in ticket.flights):
                continue
            if not ((MIN_LAYOVER_TIME <= minute_diff <= MAX_LAYOVER_TIME)
                    or (len(visited) == 1 and minute_diff < 2 * MAX_LAYOVER_TIME)):  # 24 hour gap for first flight.
                continue

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
                    paths.append(self._merge_ticket([ticket, path]))
        return paths

    def search_shortest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """Calls the `_search_all_flight` function to generate all possible paths. Then, returns the `TOP_K_RESULTS`
        flights with the shortest flight duration.
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
        """Calls the `_search_all_flight` function to generate all possible paths. Then, returns the `TOP_K_RESULTS`
        flights with the lowest ticket price.
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


class DijkstraFlightSearcher(AbstractFlightSearcher):
    """Use Dijkstra algorithm to find the shortest path."""

    def __init__(self, flight_network: Network) -> None:
        """ TODO DOCSTRING
        """
        AbstractFlightSearcher.__init__(self, flight_network)

    def search_shortest_flight(self, source: IATACode, destination: IATACode, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        Compare based on the times
        """
        dep_time_simpl = DayHourMinute(departure_time.isoweekday(), departure_time.hour, departure_time.minute)
        pq = PriorityQueue()
        pq.put((dep_time_simpl, source, None, 0, 0))
        distance: dict[IATACode, list[DayHourMinute]] = {iata: [] for iata in self.flight_network.airports}
        previous: dict[IATACode, list[tuple[Ticket, int]]] = {iata: [] for iata in self.flight_network.airports}
        first_flight = True  # to indicate when we should not start storing the "previous" node data
        first_path = True  # to indicate when we should search on all flights withih the departure date

        while not pq.empty():
            curr_time, curr_pos, prev_ticket, prev_k, num_flights = pq.get()

            if len(distance[curr_pos]) == TOP_K_RESULTS or num_flights > MAX_LAYOVER:
                continue

            distance[curr_pos].append(curr_time)

            if not first_flight:
                previous[curr_pos].append((prev_ticket, prev_k))

            if curr_pos == destination:
                first_path = False
                continue

            for ticket in self.flight_network.airports[curr_pos].tickets:
                if not first_flight:
                    time_to_depart = self._minute_diff(curr_time, ticket.departure_time)
                    if not MIN_LAYOVER_TIME <= time_to_depart <= MAX_LAYOVER_TIME:
                        continue
                if first_path and ticket.departure_time.day != dep_time_simpl.day:
                    continue

                pq.put((ticket.arrival_time, ticket.destination.iata,
                        ticket, len(distance[curr_pos]) - 1, num_flights + len(ticket.flights)))

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
        dep_time_simpl = DayHourMinute(departure_time.isoweekday(), departure_time.hour, departure_time.minute)
        pq = PriorityQueue()
        pq.put((0.0, source, None, 0, 0))
        cheapest: dict[IATACode, list[float]] = {iata: [] for iata in self.flight_network.airports}
        previous: dict[IATACode, list[tuple[Ticket, int]]] = {iata: [] for iata in self.flight_network.airports}
        first_flight = True     # to indicate when we should not start storing the "previous" node data
        first_path = True       # to indicate when we should search on all flights withih the departure date

        while not pq.empty():
            curr_price, curr_pos, prev_ticket, prev_k, num_flights = pq.get()

            if len(cheapest[curr_pos]) == TOP_K_RESULTS or num_flights > MAX_LAYOVER:
                continue

            cheapest[curr_pos].append(curr_price)

            if not first_flight:
                previous[curr_pos].append((prev_ticket, prev_k))

            if curr_pos == destination:
                first_path = False
                continue

            for ticket in self.flight_network.airports[curr_pos].tickets:
                if not first_flight:
                    time_to_depart = self._minute_diff(prev_ticket.arrival_time, ticket.departure_time)
                    if not MIN_LAYOVER_TIME <= time_to_depart <= MAX_LAYOVER_TIME:
                        continue
                if first_path and ticket.departure_time.day != dep_time_simpl.day:
                    continue

                pq.put((curr_price + ticket.price,
                        ticket.destination.iata, ticket,
                        len(cheapest[curr_pos]) - 1, num_flights + len(ticket.flights)))

            first_flight = False

        results = []
        for i in range(len(cheapest[destination])):
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


# @check_contracts
class PrunedLandmarkLabeling(AbstractFlightSearcher):
    """ TODO DOCSTRING
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

    def search_shortest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """

    def search_cheapest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['network', 'datetime', 'queue'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
        'allowed-io': []
    })
