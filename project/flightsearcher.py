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
        """ Return the corresponding datetime object based on the pivot_date and information of other_time in
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

    def search_all_flight(self, source: str, destination: str, departure_time: datetime) -> list[list[Ticket]]:
        """ Return a list of tickets for a shortest path between a given source and destination
        """
        source_airports = self.flight_network.get_airport_from_city(source)
        destination_airports = self.flight_network.get_airport_from_city(destination)
        tickets_so_far = []
        #for source_airport in source_airports:

        source_airport = self.flight_network.get_airport_from_iata(source)
        destination_airport = self.flight_network.get_airport_from_iata(destination)
        for ticket in source_airport.tickets:
            # if ticket.destination in destination_airports:
            if ticket.destination == destination_airport:
                tickets_so_far.append([ticket])
            else:
                current_ticket = [ticket]
                other_destination = ticket.destination
                # rec_value = self.search_shortest_flight(other_destination, destination, departure_time)
                rec_value = self.search_shortest_flight(other_destination.iata, destination, departure_time)
                for value in rec_value:
                    value.append(current_ticket)
                    tickets_so_far.append(current_ticket)

        return tickets_so_far


    def search_shortest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """ Return a list of tickets for a shortest path between a given source and destination
        """
        all_path = self.search_all_flight(source, destination, departure_time)
        shortest_so_far = all_path[0]
        for i in range(1, len(all_path)):
            if len(all_path[i]) < len(shortest_so_far):
                shortest_so_far =  all_path[i]
        return shortest_so_far

    def search_cheapest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """Return a list of tickets for a cheapeast path between a given source and destination
        """
        all_path = self.search_all_flight(source, destination, departure_time)
        cheapest_so_far = all_path[0]
        cheapest_price_so_far = sum(ticket.price for ticket in all_path[0])
        for i in range(1, len(all_path)):
            if sum(ticket.price for ticket in all_path[i]) < cheapest_price_so_far:
                cheapest_so_far = all_path[i]

        return cheapest_so_far



@check_contracts
class PrunedLandmarkLabeling(AbstractFlightSearcher):
    """ DOCSTRING
    """
    def _query(source: str, destination: str, label: dict[str, list[tuple[str, float]]]) -> float:
        """
        """

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
