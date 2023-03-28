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
        """
        """
        self.flight_network = flight_network

    def _merge_ticket(self, tickets: list[Ticket]) -> Ticket:
        """
        """

    def _get_day_of_week(self, date: datetime) -> tuple[int, int, int]:
        """
        """

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