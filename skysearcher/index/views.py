from django.shortcuts import render

import sys
sys.path.insert(1, '../project/')

from main import get_naive_searcher, get_pruned_landmark_labelling

import json


NAIVE_FLIGHT_SEARCHER = None
PRUNED_FLIGHT_SEARCHER = None
AIRPORT_OPTIONS = None

def search(request):
    global NAIVE_FLIGHT_SEARCHER
    global PRUNED_FLIGHT_SEARCHER
    global AIRPORT_OPTIONS

    if NAIVE_FLIGHT_SEARCHER is None:
        NAIVE_FLIGHT_SEARCHER = get_naive_searcher()
    if PRUNED_FLIGHT_SEARCHER is None:
        PRUNED_FLIGHT_SEARCHER = get_pruned_landmark_labelling()
    if AIRPORT_OPTIONS is None:
        AIRPORT_OPTIONS = list(sorted(NAIVE_FLIGHT_SEARCHER.flight_network.airports.values(), key=lambda x: x.city))


    # if request.method == 'POST':
    #     if 'naive_clicked' in request.POST:
    #         FLIGHT_SEARCHER_STATUS = 1
    #         FLIGHT_SEARCHER_MESSAGE = 'Naive Flight Searcher Selected'
    #         FLIGHT_SEARCHER = get_naive_searcher()
    #         AIRPORT_OPTIONS = list(sorted(FLIGHT_SEARCHER.flight_network.airports.values(), key=lambda x: x.city))

    #     elif 'prune_clicked' in request.POST:
    #         FLIGHT_SEARCHER_STATUS = 2
    #         FLIGHT_SEARCHER_MESSAGE = 'Pruned Landmark Labelling Selected'
    #         FLIGHT_SEARCHER = get_pruned_landmark_labelling()
    #         AIRPORT_OPTIONS = list(sorted(FLIGHT_SEARCHER.flight_network.airports.values(), key=lambda x: x.city))

    context = {}
    data = {}
    
    if request.method == 'GET':
        print(request.GET)

        flight_searcher_type = request.GET.get('button_input')
        origin = request.GET.get('from_input')
        destination = request.GET.get('to_input')
        date = request.GET.get('date_input')

        data['flight_searcher_type'] = flight_searcher_type
        data['origin'] = origin
        data['destination'] = destination
        data['date'] = date

        print(flight_searcher_type, origin, destination, date)

    context['airport_options'] = AIRPORT_OPTIONS
    context['json_data'] = json.dumps(data)

    return render(request, 'index.html', context)