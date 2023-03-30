""" naive search """

from .network import Network, Airport, Flight, Ticket, AbstractFlightSearch


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

        """A function that merge a list of tickets on a transit route
        """
        origin = ticket[0].origin
        destination = ticket[-1].destination
        price_so_far = 0
        flights_so_far = []
        for ticket in tickets:
            flights_so_far.extend(ticket.flights)
            price_so_far += ticket.price

        return Ticket(origin, destination, flights_so_far, price_so_far)

    def _get_day_of_week(date: datetime) -> tuple[int, int, int]:
        """A function that return the day and in a week and specific time of a given date
        """
        return (date.weekday(), date.hour, date.minute)

    def _get_datetime_other(self, pivot_date: datetime, other_time: tuple[int, int, int]) -> datetime:
        """
        """

    def search_shortest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """
        """
        raise NotImplementedError

    def search_cheapest_flight(self, source: str, destination: str, departure_time: datetime) -> list[Ticket]:
        """
        """
        raise NotImplementedError


class NaiveFlightSearcher(AbstractFlightSearch):
    # Make more helper functions

    def __init__(self, flight_network: Network):
        AbstractFlightSearch.__init__(self, flight_network)

    def search_shortest_flight(source: str, destination: str, departure_time: datetime): 
        """
        """
        pass

    def search_cheapest_flight(source: str, destination: str, departure_time: datetime):
        """
        """
        pass


class PrunedLandmarkLabeling(AbstractFlightSearch):
    # TODO: description + helper functions

    def __init__(self, flight_network: Network):
        AbstractFlightSearch.__init__(self, flight_network)

    def search_shortest_flight(source: str, destination: str, departure_time: datetime): 
        """
        """
        pass

    def search_cheapest_flight(source: str, destination: str, departure_time: datetime):
        """
        """
        pass