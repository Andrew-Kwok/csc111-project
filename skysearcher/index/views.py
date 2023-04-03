""" views.py controller for Django
"""
import sys
import json
from datetime import datetime

from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

sys.path.insert(1, '../project/')
from main import django_helper

AIRPORT_FILE = None
FLIGHT_FILE = None
NAIVE_FLIGHT_SEARCHER = None
DIJKSTRA_FLIGHT_SEARCHER = None
AIRPORT_OPTIONS = None

@csrf_exempt
def search(request):
    """ Function Based View for index.html
    """
    global AIRPORT_FILE
    global FLIGHT_FILE
    global NAIVE_FLIGHT_SEARCHER
    global DIJKSTRA_FLIGHT_SEARCHER
    global AIRPORT_OPTIONS

    # assert NAIVE_FLIGHT_SEARCHER is not None
    # assert DIJKSTRA_FLIGHT_SEARCHER is not None
    # assert AIRPORT_OPTIONS is not None

    # if NAIVE_FLIGHT_SEARCHER is None:
    #     NAIVE_FLIGHT_SEARCHER = get_naive_searcher()
    # if PRUNED_FLIGHT_SEARCHER is None:
    #     PRUNED_FLIGHT_SEARCHER = get_pruned_landmark_labelling()
    # if AIRPORT_OPTIONS is None:
    #     AIRPORT_OPTIONS = list(sorted(NAIVE_FLIGHT_SEARCHER.flight_network.airports.values(), key=lambda x: x.city))

    # print(request)
    if request.method == 'POST':
        AIRPORT_FILE = request.POST.get('airport_file')
        FLIGHT_FILE = request.POST.get('flight_file')
        NAIVE_FLIGHT_SEARCHER, DIJKSTRA_FLIGHT_SEARCHER, AIRPORT_OPTIONS = django_helper(AIRPORT_FILE, FLIGHT_FILE)

    context = {}
    data = {}

    if request.method == 'GET':
        if NAIVE_FLIGHT_SEARCHER is None and AIRPORT_FILE is not None:
            NAIVE_FLIGHT_SEARCHER, DIJKSTRA_FLIGHT_SEARCHER, AIRPORT_OPTIONS = django_helper(AIRPORT_FILE, FLIGHT_FILE)

        flight_searcher_type = request.GET.get('searcher_input')
        sort_type = request.GET.get('filter_input')
        origin = request.GET.get('from_input')
        destination = request.GET.get('to_input')
        date = request.GET.get('date_input')

        data['flight_searcher_type'] = flight_searcher_type
        data['sort_type'] = sort_type
        data['origin'] = origin
        data['destination'] = destination
        data['date'] = date
        context['date'] = date

        empty_count = 0
        if origin is None or len(origin) == 0:
            empty_count += 1
        if destination is None or len(destination) == 0:
            empty_count += 1
        if date is None or len(date) == 0:
            empty_count += 1

        if empty_count == 3:
            pass
        elif empty_count > 0:
            messages.error(request, 'empty input')
        elif len(origin) < 4 or origin[-4:-1] not in NAIVE_FLIGHT_SEARCHER.flight_network.airports:
            messages.error(request, 'invalid origin')
        elif len(destination) < 4 or destination[-4:-1] not in NAIVE_FLIGHT_SEARCHER.flight_network.airports:
            messages.error(request, 'invalid destination')
        else:
            tickets = []
            origin_iata = origin[-4:-1]
            destination_iata = destination[-4:-1]
            date = date.split('-')
            departure_time = datetime(int(date[0]), int(date[1]), int(date[2]))

            if flight_searcher_type == 'naive' and sort_type == 'duration':
                tickets = NAIVE_FLIGHT_SEARCHER.search_shortest_flight(source=origin_iata,
                                                                       destination=destination_iata,
                                                                       departure_time=departure_time)
            elif flight_searcher_type == 'naive' and sort_type == 'price':
                tickets = NAIVE_FLIGHT_SEARCHER.search_cheapest_flight(source=origin_iata,
                                                                       destination=destination_iata,
                                                                       departure_time=departure_time)
            elif flight_searcher_type == 'dijkstra' and sort_type == 'duration':
                tickets = DIJKSTRA_FLIGHT_SEARCHER.search_shortest_flight(source=origin_iata,
                                                                          destination=destination_iata,
                                                                          departure_time=departure_time)
            elif flight_searcher_type == 'dijkstra' and sort_type == 'price':
                tickets = DIJKSTRA_FLIGHT_SEARCHER.search_cheapest_flight(source=origin_iata,
                                                                          destination=destination_iata,
                                                                          departure_time=departure_time)
            context['tickets'] = tickets
            messages.success(request, 'scroll to view the generated tickets')

    context['airport_options'] = AIRPORT_OPTIONS
    context['json_data'] = json.dumps(data)

    return render(request, 'index.html', context)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['django', 'json', 'sys', 'datetime'],
        'disable': ['unused-import', 'too-many-branches', 'extra-imports', 'too-many-locals', 'too-many-nested-blocks'],
        'allowed-io': []
    })
