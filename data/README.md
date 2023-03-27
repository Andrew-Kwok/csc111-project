# Source Data for the Program
In this program, we'll use the data provided from file `clean_no_dupe_itineraries.csv`. The raw data is obtained from _Flight Prices: One-way flights found on Expedia between 2022-04-16 and 2022-10-05_ on Kaggle and processed using the `polars-cleaner.py` file (Wong D., 2022).

# Data Specification
`clean_no_dupe_itineraries.csv` is formatted from a `polars.DataFrame` object and contains these columns:
| header name | example | description |
|--|--|--|
| legId | 'f66d72ba3a526576608b8402b5720726' | Unique string identifier for each ticket |
| startingAirport | 'ATL' | Starting airport of the ticket |
| destinationAirport | 'BOS' | Destination airport of the ticket |
| isNonStop | 'False' | Whether it is a direct flight or requires transit |
| totalFare | '252.6' | The total fare that will be charged to passengers |
| segmentsArrivalAirportCode | 'ORD\|\|BOS' | The arrival airport for each flight on the ticket, separated by string '\|\|' |
| segmentsDepartureAirportCode | 'ATL\|\|ORD' | The departure airport for each flight on the ticket, separated by string '\|\|' |
| segmentsAirlineName | 'American Airlines\|\|American Airlines' | The airline name for each flight on the ticket, separated by string '\|\|' |
| segmentsDepartureWeekday | '7\|\|7' | The departure weekday (1: Monday to 7: Sunday) for each flight on the ticket, separated by string '\|\|' |
| segmentsDepartureTimeOfDay | '18:45\|\|22:00' | The departure time of day rounded to the nearest 15 minutes for each flight on the ticket, separated by string '\|\|' |
| segmentsArrivalWeekday | '7\|\|1' | The arrival weekday (1: Monday to 7: Sunday) for each flight on the ticket, separated by string '\|\|' |
| segmentsArrivalTimeOfDay | '21:00\|\|00:30' | The arrival time of day rounded to the nearest 15 minutes for each flight on the ticket, separated by string '\|\|' |

# How to get the .csv file
In the `/data` directory, unpack `clean_no_dupe_itineraries.7z` archive by calling the `unpack_data()` function in `main.py`. The `clean_no_dupe_itineraries.csv` file will be written to the `/data` directory.

# Raw data processing
If you wish to replicate our raw data processing, please follow these steps.
**WARNING: These operations are extremely resource-intensive for a laptop to run. These operations require at least 40GB of available disk storage and up to 30GB of RAM.**

_TODO_
