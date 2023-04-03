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

###############################################################################
# Timing experiments and visualization for break_diffie_hellman
###############################################################################
def time_naive_shortest_flight(airport_file: str, flight_file: str) -> list[tuple[int, float]]:
    """Return the time taken to run Naive search shortest flight contained in the given file.

    The return value is a *list of tuples:
        - the first element of the tuple is the total possibe path for the flight
        - the second element of the tuple is the time taken by time_naive_search_shortest
          to run on the corresponding row

    Preconditions:
        - filename refers to a CSV file in the given data
    """
    network = main.read_csv_file(airport_file, flight_file)  # doesn't create edge (tickets)
    naive_network = NaiveFlightSearcher(network)
    list_iata = list(network.airports.keys())
    num_run = 0
    list_so_far = []
    while num_run != 15:
        source = random.choice(list_iata)
        destination = random.choice(list_iata)
        while destination == source:
            destination = random.choice(list_iata)
        year = random.randint(2000, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        depart_time = datetime.datetime(year, month, day, hour, minute, second)
        # add_day = random.randint(1, 8)
        # depart_time = today + datetime.timedelta(days=add_day)
        # depart_time = datetime.datetime.now()
        print(naive_network.search_shortest_flight(source, destination, depart_time))
        call_time = timeit.timeit(f'{naive_network.search_shortest_flight(source, destination, depart_time)}', \
                         number=1, globals=globals())
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
            'y': 'Time run (s)'
        }
    )

    # Show the figure in the browser
    figure.show()
    # figure.write_html('my_figure.html')
    # This will create a new file called 'my_figure.html', which you can manually open in your web browser.
