"""Script for cleaning the flight data. To download the flight data, please follow the instructions in the report."""

import glob
import os
import requests
import shutil
from typing import Optional, Final

import polars as pl

RSTP: Final = 9200000
REPS: Final = 9
KAGGLE_COLUMNS: Final = ['legId', 'isNonStop', 'totalFare',
                         'segmentsDepartureTimeEpochSeconds', 'segmentsArrivalTimeEpochSeconds',
                         'segmentsDepartureAirportCode', 'segmentsArrivalAirportCode',
                         'segmentsAirlineName']
KAGGLE_DATATYPES: Final = {
    'legId': pl.Utf8, 'isNonStop': pl.Boolean, 'totalFare': pl.Float32,
    'segmentsDepartureTimeEpochSeconds': pl.Utf8, 'segmentsArrivalTimeEpochSeconds': pl.Utf8,
    'segmentsDepartureAirportCode': pl.Utf8, 'segmentsArrivalAirportCode': pl.Utf8,
    'segmentsAirlineName': pl.Utf8
}


def select_useful_columns(columns: Optional[list[str]]) -> None:
    """Select only the useful columns from the raw csv file from kaggle and writes the results into a csv file."""
    if os.path.exists('cleaned_itineraries.csv'):
        print('Step 2 skipped, file cleaned_itineraries.csv exists.')
        return

    if columns is None:
        columns = []

    print('Step 2: Selecting useful column from raw file, dropping the rest.')

    pl.scan_parquet(
        source='itineraries_gzip.parquet',
        low_memory=True, cache=False
    ).select(columns).collect(streaming=True).write_csv('cleaned_itineraries.csv')

    print('Step 2 finished.')


def select_unique_flights() -> None:
    """Select only unique flights from the cleaned itineraries.

    The uniqueness criteria is based on:
    - Departure and arrival airport
    - Weekday and time of flight, rounded to the nearest 15 minutes

    This function splits the cleaned itineraries data into 8 chunks and write it into intermediate files,
    each processing uses approximately 4GB of RAM. The intermediate files the combined and checked again
    for uniqueness, and the final result is written to a parquet file.
    """
    if os.path.exists('no_dupe_flights.parquet'):
        print('Step 3 skipped, file no_dupe_flights.parquet exists.')
        return

    print('Step 3: Select unique flights based on the criteria we set.')

    for i in range(REPS):
        df = (
            pl.scan_csv(
                source='cleaned_itineraries.csv',
                dtypes=KAGGLE_DATATYPES,
                low_memory=True, rechunk=False, cache=False,
                skip_rows_after_header=(i * RSTP), n_rows=RSTP
            )
            .select(
                pl.col('legId'),
                pl.col('segmentsDepartureTimeEpochSeconds').str.split('||'),
                pl.col('segmentsArrivalTimeEpochSeconds').str.split('||'),
                pl.col('segmentsDepartureAirportCode').str.split('||'),
                pl.col('segmentsArrivalAirportCode').str.split('||'),
                pl.col('segmentsAirlineName').str.split('||'),
            )
            .explode([
                'segmentsDepartureTimeEpochSeconds', 'segmentsArrivalTimeEpochSeconds',
                'segmentsArrivalAirportCode', 'segmentsDepartureAirportCode', 'segmentsAirlineName'
            ])
            .with_columns([
                pl.from_epoch('segmentsDepartureTimeEpochSeconds')
                .dt.weekday().alias('departureWeekday'),
                pl.from_epoch('segmentsDepartureTimeEpochSeconds')
                .dt.round('15m').dt.time().alias('departureClock'),
            ])
            .drop('segmentsDepartureTimeEpochSeconds')
            .with_columns([
                pl.from_epoch('segmentsArrivalTimeEpochSeconds')
                .dt.weekday().alias('arrivalWeekday'),
                pl.from_epoch('segmentsArrivalTimeEpochSeconds')
                .dt.round('15m').dt.time().alias('arrivalClock'),
            ])
            .drop('segmentsArrivalTimeEpochSeconds')
            .unique(maintain_order=False, subset=[
                'segmentsArrivalAirportCode', 'segmentsDepartureAirportCode', 'segmentsAirlineName',
                'departureWeekday', 'departureClock', 'arrivalWeekday', 'arrivalClock'
            ])
        )

        df.collect(streaming=True).write_csv(f'no_dupe_flights_{i}.csv', time_format='%R')
        print(f'finished processing file {i}/{REPS}')

    out_filename = 'no_dupe_flights.csv'
    with open(out_filename, 'wb') as outfile:
        for i, filename in enumerate(glob.glob('no_dupe_flights_?.{}'.format('csv'))):
            if filename == out_filename:
                continue
            with open(filename, 'rb') as readfile:
                if i != 0:
                    readfile.readline()
                shutil.copyfileobj(readfile, outfile)

    for i in range(REPS):
        os.remove(f'no_dupe_flights_{i}.csv')

    print('Finished combining files. Filtering uniqueness for the last time...')

    (
        pl.scan_csv(
            source=out_filename,
            dtypes=KAGGLE_DATATYPES,
            low_memory=True, rechunk=False, cache=False
        )
        .unique(maintain_order=False, subset=[
            'segmentsArrivalAirportCode', 'segmentsDepartureAirportCode', 'segmentsAirlineName',
            'departureWeekday', 'departureClock', 'arrivalWeekday', 'arrivalClock'
        ])
    ).collect().write_parquet('no_dupe_flights.parquet')

    print('Step 3 finished. File no_dupe_flights.csv contains unique flights.')


def unique_itineraries() -> None:
    """Return unique itineraries based on the unique flight's ID."""
    if os.path.exists('no_dupe_itineraries.parquet'):
        print('Step 4 skipped, file no_dupe_itineraries.parquet exists.')
        return

    print('Step 4: Select unique itineraries based on the unique flight\'s ID.')

    filts = pl.scan_parquet(source='no_dupe_flights.parquet', cache=False, low_memory=True).select('legId').collect()
    print('filtering itineraries...')
    (
        pl.scan_csv(source='cleaned_itineraries.csv', rechunk=False, low_memory=True)
        .filter(pl.col('legId').is_in(filts.get_column('legId')))
        .unique(maintain_order=False)
    ).collect(streaming=True).write_parquet('no_dupe_itineraries.parquet')

    print('Step 4 finished.')


def epoch_to_weekday_time_itineraries() -> None:
    """Convert itineraries with epoch to weekday ISO and time of day rounded to 15 minutes."""
    if os.path.exists('clean_no_dupe_itineraries.csv'):
        print('Step 5 skipped, file clean_no_dupe_itineraries.csv exists.')
        return

    print('Step 5: Convert itineraries with epoch to weekday ISO and time of day rounded to 15 minutes.')

    df = (
        pl.scan_parquet(
            source='no_dupe_itineraries.parquet', cache=False, low_memory=True,
        )
        .unique(maintain_order=False)
        .with_columns([
            pl.col('segmentsDepartureTimeEpochSeconds').str.split('||')
            .arr.eval(pl.from_epoch(pl.element()).dt.weekday()).cast(pl.List(pl.Utf8))
            .arr.join('||').alias('segmentsDepartureWeekday'),
            pl.col('segmentsDepartureTimeEpochSeconds').str.split('||')
            .arr.eval(pl.from_epoch(pl.element()).dt.round('15m').dt.strftime('%H:%M'))
            .arr.join('||').alias('segmentsDepartureTimeOfDay')
        ])
        .drop('segmentsDepartureTimeEpochSeconds')
        .with_columns([
            pl.col('segmentsArrivalTimeEpochSeconds').str.split('||')
            .arr.eval(pl.from_epoch(pl.element()).dt.weekday()).cast(pl.List(pl.Utf8))
            .arr.join('||').alias('segmentsArrivalWeekday'),
            pl.col('segmentsArrivalTimeEpochSeconds').str.split('||')
            .arr.eval(pl.from_epoch(pl.element()).dt.round('15m').dt.strftime('%H:%M')).cast(pl.List(pl.Utf8))
            .arr.join('||').alias('segmentsArrivalTimeOfDay')
        ])
        .drop('segmentsArrivalTimeEpochSeconds')
        .with_columns([
            pl.col('segmentsDepartureAirportCode').str.slice(0, length=3).alias('startingAirport'),
            pl.col('segmentsArrivalAirportCode').str.slice(-3).alias('destinationAirport')
        ])
    )

    df.collect(streaming=True).write_csv('clean_no_dupe_itineraries.csv')
    print('Step 5 finished.')
