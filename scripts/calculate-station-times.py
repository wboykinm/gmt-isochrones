import os
import zipfile
import requests
import pandas as pd

def calculate_travel_time(gtfs_path, origin_stop_id, destination_stop_id):
    trips_df = pd.read_csv(os.path.join(gtfs_path, "trips.txt"))
    stop_times_df = pd.read_csv(os.path.join(gtfs_path, "stop_times.txt"))

    # Filter stop times for the specified origin and destination stop IDs
    origin_stop_times = stop_times_df[stop_times_df["stop_id"] == origin_stop_id]
    destination_stop_times = stop_times_df[stop_times_df["stop_id"] == destination_stop_id]

    # Merge origin and destination stop times based on trip ID
    merged_df = pd.merge(origin_stop_times, destination_stop_times, on="trip_id")

    # Filter trips that have both origin and destination stops
    valid_trips = merged_df["trip_id"].unique()

    # Filter trips dataframe for valid trips
    valid_trips_df = trips_df[trips_df["trip_id"].isin(valid_trips)]

    # Get the minimum start time and maximum end time for each trip
    min_start_times = merged_df.groupby("trip_id")["departure_time_x"].min().reset_index()
    max_end_times = merged_df.groupby("trip_id")["arrival_time_y"].max().reset_index()

    # Merge minimum start times and maximum end times with valid trips dataframe
    valid_trips_df = pd.merge(valid_trips_df, min_start_times, on="trip_id")
    valid_trips_df = pd.merge(valid_trips_df, max_end_times, on="trip_id")

    # Calculate travel times as the difference between maximum end time and minimum start time
    valid_trips_df["travel_time"] = (
        pd.to_datetime(valid_trips_df["arrival_time_y"], format="%H:%M:%S") -
        pd.to_datetime(valid_trips_df["departure_time_x"], format="%H:%M:%S")
    ).dt.total_seconds()

    # Find the minimum travel time among valid trips
    min_travel_time = valid_trips_df["travel_time"].min()

    return min_travel_time

# URL for GTFS data download
gtfs_url = "https://data.trilliumtransit.com/gtfs/ccta-vt-us/ccta-vt-us.zip"

# Download and extract GTFS data
response = requests.get(gtfs_url)
with open("gtfs.zip", "wb") as f:
    f.write(response.content)
with zipfile.ZipFile("gtfs.zip", "r") as zip_ref:
    zip_ref.extractall("gtfs_data")

# Load GTFS data into dataframes
gtfs_path = "gtfs_data"
stops_df = pd.read_csv(os.path.join(gtfs_path, "stops.txt"))
stop_ids = stops_df["stop_id"].tolist()

# Calculate travel times for each stop
for stop_id in stop_ids:
    # Create an empty dataframe to store travel times
    travel_times_df = pd.DataFrame(columns=["destination_stop_id", "travel_time"])

    for destination_stop_id in stop_ids:
        # Calculate travel time from stop_id to destination_stop_id
        travel_time = calculate_travel_time(gtfs_path, stop_id, destination_stop_id)

        # Append travel time to the dataframe
        travel_times_df = travel_times_df.append({
            "destination_stop_id": destination_stop_id,
            "travel_time": travel_time
        }, ignore_index=True)

    # Save travel times dataframe to a CSV file
    output_filename = f"{stop_id}.csv"
    travel_times_df.to_csv(output_filename, index=False)

# Clean up downloaded files
os.remove("gtfs.zip")
os.rmdir("gtfs_data")
