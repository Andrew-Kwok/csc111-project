"""Script for generating testcases"""

import os
from typing import Optional

import polars as pl


def generate_testcase_general(itineraries: str, airports: str, size: int, seed: Optional[int]) -> None:
    """Generate general testcase, using seed for reproducibility."""
    itn = pl.scan_csv(source=itineraries).collect().sample(n=size, seed=seed)
    itn_explode = itn.with_columns([
        pl.col('segmentsArrivalAirportCode').str.split('||'),
        pl.col('segmentsDepartureAirportCode').str.split('||'),
        pl.col('segmentsAirlineName').str.split('||'),
        pl.col('segmentsDepartureWeekday').str.split('||'),
        pl.col('segmentsDepartureTimeOfDay').str.split('||'),
        pl.col('segmentsArrivalWeekday').str.split('||'),
        pl.col('segmentsArrivalTimeOfDay').str.split('||'),
    ]).explode([
        'segmentsArrivalAirportCode', 'segmentsDepartureAirportCode', 'segmentsAirlineName',
        'segmentsDepartureWeekday', 'segmentsDepartureTimeOfDay', 'segmentsArrivalWeekday', 'segmentsArrivalTimeOfDay'
    ])
    air = pl.scan_csv(source=airports).filter(
        pl.col('iata_code').is_in(itn_explode.get_column('segmentsDepartureAirportCode')) |
        pl.col('iata_code').is_in(itn_explode.get_column('segmentsArrivalAirportCode'))
    ).collect()

    itn.write_csv(os.path.join(os.getcwd(), '..', 'data', f'clean_no_dupe_itineraries_{size}.csv'))
    air.write_csv(os.path.join(os.getcwd(), '..', 'data', f'airport_class_{size}.csv'))


def generate_testcase_direct_flight(itineraries: str, airports: str, size: int, seed: Optional[int]) -> None:
    """Generate direct flight testcase, using seed for reproducibility."""
    itn = pl.scan_csv(source=itineraries).filter(pl.col('isNonStop')).collect().sample(n=size, seed=seed)
    air = pl.scan_csv(source=airports).filter(
        pl.col('iata_code').is_in(itn.get_column('startingAirport')) |
        pl.col('iata_code').is_in(itn.get_column('destinationAirport'))
    ).collect()

    itn.write_csv(os.path.join(os.getcwd(), '..', 'data', f'clean_no_dupe_itineraries_direct_{size}.csv'))
    air.write_csv(os.path.join(os.getcwd(), '..', 'data', f'airport_class_direct_{size}.csv'))
