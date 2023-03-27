"""The main file that will be run by the grader."""
from py7zr import SevenZipFile


def unpack_csv() -> None:
    """Unpack /data/clean_no_dupe_itineraries.7z to /data/clean_no_dupe_itineraries.csv"""

    with SevenZipFile('../data/clean_no_dupe_itineraries.7z', mode='r') as z:
        z.extractall()

    print('Finished extracting.')
