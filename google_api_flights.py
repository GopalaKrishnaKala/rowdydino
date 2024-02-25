from serpapi import GoogleSearch
import json
from datetime import datetime

params = {
  "engine": "google_flights",
  "departure_id": "FLL",
  "arrival_id": "SAT",
  "outbound_date": "2024-02-28",
  "currency": "USD",
  "hl": "en",
  "api_key": "9c33b6d3138a844039b1f7eb0d24ae02f93a03b72c0110f14742dad2ae801512",
  "gl": "us",
  "adults": "1",
  "type": "2"
}

search = GoogleSearch(params)
results = search.get_dict()
price_insights = results["price_insights"]

import pandas as pd

# Assuming the `results` dictionary is already obtained from the Google Flights API
price_insights = results["price_insights"]
best_flights_json = results["best_flights"]

# Convert timestamp for price_history
def convert_timestamp(ts):
    return pd.to_datetime(ts, unit='s')

# Prepare the Price History DataFrame
price_history_data = [[convert_timestamp(item[0]), item[1]] for item in price_insights['price_history']]
price_history_df = pd.DataFrame(price_history_data, columns=['Date', 'Price'])
# Adding metadata as a separate DataFrame
metadata_df = pd.DataFrame({
    'Metadata': ['Lowest Price', 'Price Level', 'Typical Price Range'],
    'Value': [
        price_insights['lowest_price'],
        price_insights['price_level'],
        f"{price_insights['typical_price_range'][0]}-{price_insights['typical_price_range'][1]}"
    ]
})

# Prepare the Best Flights DataFrame
flights_data = []
for flight_option in best_flights_json:
    for flight in flight_option['flights']:
        flight_details = {
            'Departure Airport Name': flight['departure_airport']['name'],
            'Departure Airport ID': flight['departure_airport']['id'],
            'Departure Time': flight['departure_airport']['time'],
            'Arrival Airport Name': flight['arrival_airport']['name'],
            'Arrival Airport ID': flight['arrival_airport']['id'],
            'Arrival Time': flight['arrival_airport']['time'],
            'Duration (minutes)': flight['duration'],
            'Airplane': flight['airplane'],
            'Airline': flight['airline'],
            'Flight Number': flight['flight_number'],
            'Legroom': flight['legroom'],
            'Extensions': ', '.join(flight['extensions']),
            'Total Duration': flight_option['total_duration'],
            'Carbon Emissions (this flight)': flight_option['carbon_emissions']['this_flight'],
            'Typical Carbon Emissions for this Route': flight_option['carbon_emissions']['typical_for_this_route'],
            'Difference Percent in Carbon Emissions': flight_option['carbon_emissions']['difference_percent'],
            'Price': flight_option['price'],
            'Type': flight_option['type'],
            'Airline Logo URL': flight['airline_logo'],
        }
        # Handle layovers if present
        layovers = flight_option.get('layovers', [])
        layover_details = '; '.join([f"{layover['name']} ({layover['duration']} min)" for layover in layovers])
        flight_details['Layovers'] = layover_details
        
        flights_data.append(flight_details)
flights_df = pd.DataFrame(flights_data)

# Writing to an Excel file with multiple sheets
with pd.ExcelWriter('C:/Users/Gopala Kala/OneDrive/Desktop/Flight History/flight_data_and_price_history_FLL_to_SAT.xlsx', engine='openpyxl') as writer:
    price_history_df.to_excel(writer, sheet_name='Price History', index=False)
    metadata_df.to_excel(writer, startrow=len(price_history_df)+2, sheet_name='Price History', index=False)
    flights_df.to_excel(writer, sheet_name='Best Flights', index=False)
