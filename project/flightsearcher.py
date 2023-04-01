""" flight searcher """

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
        """ TODO DOCSTRING
        """

    def search_shortest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        raise NotImplementedError

    def search_cheapest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ TODO DOCSTRING
        """
        raise NotImplementedError


@check_contracts
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


@check_contracts
class PrunedLandmarkLabeling(AbstractFlightSearcher):
    """ DOCSTRING
    """
    flight_network: Network
    label_in: list[tuple[str, float]]
    label_out: list[tuple[str, float]]

    def _query(source: str, destination: str, label: dict[str, list[tuple[str, float]]]) -> float:
        """
        """
        s_label = label_out[source]
        t_label = label_in[destination]

        i, j = 0, 0
        res = math.inf
        while i < s_label and j < t_label:
            if s_label[i][0] == t_label[j][0]:
                res = min(res, s_label[i] + t_label[j])
            elif s_labe[i] < t_label[j]:
                j += 1
            else:
                i += 1
        return res

    def _pruned_dijkstra(self):
        """
        """
        airports_iata = sorted(self.flight_network.airports.keys())
        label = [{iata: [] for iata in airports_iata} for _ in range(2)]
        
        for i in range(len(airports_iata)):
            pq = PriorityQueue()
            pq.put(airports_iata[i])

            P = [math.inf] * len(airports_iata)
            P[i] = 0
            for j in range(len(airports_iata)):
                label[i][j]




    def _construct_label(self, label: dict[str, list[tuple[str, float]]]):
        for airport in flight_network.airports:
            label_in[airport] = []

        self._pruned_dijkstra()


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


if __name__ == '__main__':

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['network', 'datetime'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports'],
        'allowed-io': []
    })
