"""Script for downloading and cleaning the airport data."""

import os
import requests

import polars as pl


def download_airport_data() -> None:
    """Download and write the airport data file."""
    if os.path.exists(os.path.join(os.getcwd(), '..', 'data', 'airport_data.csv')):
        print('Step 1 skipped, file airport_data.csv exists.')
        return

    print('Step 1: Downloading airport data (~5.7 MB).')

    r = requests.get('https://raw.githubusercontent.com/datasets/airport-codes/master/data/airport-codes.csv')
    with open(os.path.join(os.getcwd(), '..', 'data', 'airport_data.csv'), 'wb') as f:
        f.write(r.content)

    print('Step 1 finished.')


def airport_class_file() -> None:
    """Construct the file required for the creation of the Airport class"""
    if os.path.exists(os.path.join(os.getcwd(), '..', 'data', 'airport_class.csv')):
        print('Step 2 skipped, file airport_class.csv exists.')
        return

    print('Step 2: construct the file required for the creation of the Airport class.')

    departures = pl.scan_parquet(source=os.path.join(os.getcwd(), '..', 'data', 'no_dupe_flights.parquet'))\
        .select('segmentsDepartureAirportCode').unique().collect()
    arrivals = pl.scan_parquet(source=os.path.join(os.getcwd(), '..', 'data', 'no_dupe_flights.parquet'))\
        .select('segmentsArrivalAirportCode').unique().collect()
    airports = (
        pl.scan_csv(os.path.join(os.getcwd(), '..', 'data', 'airport_data.csv'))
        .select(['iata_code', 'name', 'municipality', 'type'])
        .filter((pl.col('type') != 'closed') &
                (pl.col('iata_code').is_in(departures.get_column('segmentsDepartureAirportCode')) |
                pl.col('iata_code').is_in(arrivals.get_column('segmentsArrivalAirportCode'))))
        .drop('type')
    )

    airports.collect().write_csv(os.path.join(os.getcwd(), '..', 'data', 'airport_class.csv'))
    print('Step 2 finshed.')
