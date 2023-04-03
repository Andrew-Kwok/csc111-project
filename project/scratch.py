from __future__ import annotations

import random
import timeit
from typing import Optional

from queue import PriorityQueue
from datetime import datetime

from python_ta.contracts import check_contracts

from network import IATACode, DayHourMinute
from network import MIN_LAYOVER_TIME, MAX_LAYOVER_TIME, MAX_LAYOVER, TOP_K_RESULTS
from network import Network, Airport, Flight, Ticket
from plotly.express import scatter

import main

from flightsearcher import NaiveFlightSearcher

import csv
import datetime


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

    Preconditions:
        - source in self.flight_network.airports
        - destination in self.flight_network.airports
        - departure_time.hour == 0 and departure_time.minute == 0
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

    Preconditions:
        - source in self.flight_network.airports
        - destination in self.flight_network.airports
        - departure_time.hour == 0 and departure_time.minute == 0
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

###############################################################################
# Timing experiments and visualization for break_diffie_hellman
###############################################################################
def time_naive_search_shortest(source: IATACode, destination: IATACode, departure_time: datetime) -> float:
    """"Return the time taken to run search_shortest_flight on the given arguments source, destination, departure time

    number is the number of times to execute the statement, and should be passed into timeit.timeit.

    IMPORTANT NOTE:
        you must pass in an additional argument "globals=globals()" to the timing function:

        timeit.timeit(..., number=..., globals=globals()),

        otherwise you'll get a NameError when calling timeit.timeit.

    Remember, the first argument of `timeit.timeit` is a *string* that represents the code
    to execute; it is up to you to construct the correct string expressing a call to
    break_diffie_hellman.
    """
    time = timeit.timeit(f'{NaiveFlightSearcher.search_shortest_flight(source, destination, departure_time)}', \
                         number=1, globals=globals())
    return time


def time_naive_shortest_flight(airport_file: str, flight_file: str) -> list[tuple[int, float]]:
    """Return the time taken to run Naive search shortest flight contained in the given file.

    The return value is a *list of tuples:
        - the first element of the tuple is the total possibe path for the flight
        - the second element of the tuple is the time taken by time_naive_search_shortest
          to run on the corresponding row

    Preconditions:
        - filename refers to a CSV file in the given data
    """
    network = main.read_csv_file(airport_file, flight_file)
    list_iata = list(network.airports.keys())
    num_run = 1
    list_so_far = []
    while num_run != 1000:
        source = random.choice(list_iata)
        destination = random.choice(list_iata)
        while destination == source:
            destination = random.choice(list_iata)

        today = datetime.date.today()
        add_day = random.randint(1, 8)
        depart_time = today + datetime.timedelta(days=add_day)
        call_time = time_naive_search_shortest(source, destination, depart_time)
        list_so_far.append((num_run, call_time))
        num_run += 1

    return list_so_far


def graph_naive_search_shortest(timing_data: list[tuple[int, float]]) -> None:
    """Visualize the results of the timing experiments completed by naive_search_shortest

    Use a plotly scatterplot to visualize the data.

    The x-axis should represent the number of call in the timing data
    The y-axis should represent the time taken
    """
    num_call = [time[0] for time in timing_data]
    times = [time[1] for time in timing_data]

    figure = scatter(
        x=num_call,
        y=times,
        title='Naive search shortest flight time ',  # The graph title
        labels={
            'x': 'Number of call',
            'y': 'Time'
        }
    )

    # Show the figure in the browser
    figure.show()
    # figure.write_html('my_figure.html')
    # This will create a new file called 'my_figure.html', which you can manually open in your web browser.
