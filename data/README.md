# How to get the .csv file
In the `/data` directory, unpack `clean_no_dupe_itineraries.7z` archive by calling the `unpack_data()` function in `main.py`. The `clean_no_dupe_itineraries.csv` file will be written to the same directory as the `main.py` file.

# Data sourcing
In this program, we'll use the data provided from file `clean_no_dupe_itineraries.csv`. The raw data is obtained from _Flight Prices: One-way flights found on Expedia between 2022-04-16 and 2022-10-05_ on Kaggle and processed using the `flight_data_cleaner.py`, `airport_data_cleaner.py`, and `testcase_generator.py` scripts (Wong D., 2022).

# Data specification
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

# What to do with the data
Each row of the CSV (except the header) represents an itinerary of 1-4 flights. Parse it and convert each subsequence into valid `Ticket` instances. For example, an itinerary that passes Miami - Atlanta - Nevada - Seattle will be broken into three `Ticket`s, namely:
+ Miami - Atlanta
+ Atlanta - Nevada
+ Nevada - Seattle

# Raw data processing
If you wish to replicate our raw data processing, please follow these steps.
**WARNING: These operations are extremely resource-intensive for a laptop to run. These operations require at least 17GB of available disk storage and up to 30GB of RAM. You can reduce the RAM usage by reducing the `RSTP` constant in `flight_data_cleaner.py` (~550,000 rows/GB).**

## Datasets
The flight data was obtained from: https://github.com/dilwong/FlightPrices and the airport data
from https://github.com/datasets/airport-codes.

### Flight Data Description
The flight data that we use is a list of 965188 flight tickets (itineraries) in and around the United States of America, stored in the ‘clean no dupe itineraries.csv’ file which contains 12 columns:
1. legID: Unique string identifier for each ticket
2. isNonStop: Starting airport of the ticket
3. totalFare: The total fare that will be charged to passengers
4. segmentsDepartureAirportCode: The departure airport for each flight on the ticket, separated by the string ‘||’
5. segmentsArrivalAirportCode: The arrival airport for each flight on the ticket, separated by the string ’||’
6. segmentsAirlineName: The airline name for each flight on the ticket, separated by the string ’||’
7. segmentsDepartureWeekday: The departure weekday (1: Monday to 7: Sunday) for each flight on the ticket, separated by the string ’||’
8. segmentsDepartureTimeOfDay: The departure time of day rounded to the nearest 15 minutes for each flight on the ticket, separated by the string ’||’
9. segmentsArrivalWeekday: The arrival weekday (1: Monday to 7: Sunday) for each flight on the ticket, separated by the string ’||’
10. segmentsArrivalTimeOfDay: The arrival time of day rounded to the nearest 15 minutes for each flight on the ticket, separated by the string ’||’
11. startingAirport: Starting airport of the ticket
12. destinationAirport: Destination airport of the ticket

### Flight Data Processing
For the flight dataset, the data-cleaning process is divided into 5 steps, namely:

1. Getting the data. Since the actual data is located either in Kaggle or Dropbox and requires an API key to download from Python, we downloaded the data from Dropbox and reuploaded it to UofT’s OneDrive. This way, the data can be accessed by Python’s requests library. However, downloading the file using Python’s requests library took too much time, so we provided the direct link to the file in UofT OneDrive so that the user could download the file themselves. The data itself is contained in the Apache Parquet file format in the ‘itineraries_gzip.parquet’ file. From now on, we will use the Polars library to work on the data.
2. Selecting useful columns of the dataset. First, we read the ‘itineraries_gzip.parquet’ file using `polars.scan_csv` function. Then we select only 8 of the 26 columns, which are all the columns listed above except ‘startingAirport’, ‘destinationAirport’, as well as the departure and arrival times which are encoded in UNIX time instead of weekday and time of day. Finally, we write the selected columns to the ‘cleaned_itineraries.csv’ file.
3. Select unique flights and drop the duplicates. For simplicity, we assume that flights repeat weekly, so if there is a weekly repeating flights in the dataset, we only use it once. Since the dataset contains around 82 million lines, we will process the dataset in batches of 9.2 million so that our laptop can still run it. For every batch,
- Scan 9.2 million rows
- Select only the ‘legId’, ‘segmentsDepartureTimeEpochSeconds’, ‘segmentsArrivalTimeEpochSeconds’, ‘segmentsDepartureAirportCode’, ‘segmentsArrivalAirportCode’, and ‘segmentsAirlineName’ columns to process
- Split the segments columns into a column of a list of strings
- “Explode” the segments columns so that every row (itinerary) only contains one flight. For example, a row with legID 123 and flight from ATL-JFK and JFK-BOS will be exploded into two rows with the same legID but different flights.
- Convert the epochs columns to weekday and time of day columns. Round the time of day to the nearest 15-minute mark to keep the flight number low (we assume 8:43 and 8:40 are roughly the same time). Drop the epochs columns since they are no longer useful.
- Take unique flights by considering only the airport codes, departure and arrival times, and airline names.
- Write the data to a temporary file.
Then we combine the temporary files and filter by uniqueness once again, and write it to the ‘no dupe flights.parquet’ file.
4. Filter unique itineraries by the legId of the unique flights.
5. Convert the time in epochs to time in weekday and time of day. Construct the starting and destination airport columns.

### Airport Data
The airport data that we use is a list of 229 airports that are in the ‘clean no dupe itineraries.csv’ file, which
contains 3 columns:
1. iata code: The code of the airport assigned by the International Air Transport Association (IATA)
2. name: The name of the airport
3. municipality: The municipal/city area that is being served by the airport

### Airport Data Processing
We processed the airport data in two steps:
1. Getting the airport data. We used the requests library to download the dataset from GitHub. Since the size is small enough, we do this directly using Python.
2. Select the ‘iata code’, ‘name’, ‘municipality’, and ‘type’ columns. Filter the data so that the ‘iata code’ appears on the ‘clean no dupe itineraries.csv’, and the ‘type’ value is not “closed”.
