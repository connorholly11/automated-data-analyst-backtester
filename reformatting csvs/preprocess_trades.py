import pandas as pd
import pytz
from polygon_handler import PolygonDataHandler
from dotenv import load_dotenv
import os
import requests
import time
from datetime import timedelta
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

def convert_symbol(symbol):
    if symbol.startswith(("MNQ", "NQ")):
        return "QQQ"
    elif symbol.startswith(("ES", "MES")):
        return "SPY"
    return symbol

def get_equity_price(symbol, timestamp, retries=3):
    etf_symbol = convert_symbol(symbol)
    start_timestamp = (timestamp - timedelta(seconds=1)).timestamp() * 1000
    end_timestamp = (timestamp + timedelta(seconds=1)).timestamp() * 1000
    url = f"https://api.polygon.io/v2/aggs/ticker/{etf_symbol}/range/1/second/{int(start_timestamp)}/{int(end_timestamp)}?adjusted=true&sort=asc&limit=3&apiKey={POLYGON_API_KEY}"

    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['resultsCount'] > 0:
                # Return the price of the middle (closest) timestamp
                return timestamp, data['results'][len(data['results'])//2]['o']
            else:
                print(f"No data available for {etf_symbol} at {timestamp}")
                return timestamp, None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {etf_symbol} at {timestamp}: {e}")
            if attempt < retries - 1:
                print("Retrying...")
                time.sleep(2)
            else:
                print("Max retries reached.")
                return timestamp, None

def calculate_converted_quantity(row):
    if row['Symbol'].startswith('MNQ'):
        return row['Qta'] * 80
    elif row['Symbol'].startswith('NQ'):
        return row['Qta'] * 800
    elif row['Symbol'].startswith('MES'):
        return row['Qta'] * 50
    elif row['Symbol'].startswith('ES'):
        return row['Qta'] * 500
    else:
        return row['Qta']

def process_trades(input_file, output_file):
    try:
        # Read the CSV file
        df = pd.read_csv(input_file, parse_dates=['DateTime'])

        # Convert UTC to EST
        eastern = pytz.timezone('US/Eastern')
        df['DateTime'] = pd.to_datetime(df['DateTime'], utc=True).dt.tz_convert(eastern)

        # Remove timezone info and milliseconds
        df['DateTime'] = df['DateTime'].dt.tz_localize(None).dt.floor('S')

        # Add converted symbol column
        df['ConvertedSymbol'] = df['Symbol'].apply(convert_symbol)

        # Calculate converted quantity
        df['ConvertedQuantity'] = df.apply(calculate_converted_quantity, axis=1)

        # Get equity prices
        unique_timestamps = df['DateTime'].unique()
        equity_prices = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_timestamp = {executor.submit(get_equity_price, 'QQQ', timestamp): timestamp for timestamp in unique_timestamps}
            future_to_timestamp.update({executor.submit(get_equity_price, 'SPY', timestamp): timestamp for timestamp in unique_timestamps})

            for future in tqdm(as_completed(future_to_timestamp), total=len(future_to_timestamp), desc="Fetching equity prices"):
                timestamp, price = future.result()
                if price is not None:
                    equity_prices.setdefault(timestamp, {})['QQQ' if 'QQQ' in str(future_to_timestamp[future]) else 'SPY'] = price

        # Add converted price column
        df['ConvertedPrice'] = df.apply(lambda row: 
            equity_prices.get(row['DateTime'], {}).get(row['ConvertedSymbol'], row['Price']), axis=1)

        # Save the updated CSV
        df.to_csv(output_file, index=False)
        print(f"Processed data saved to {output_file}")

    except Exception as e:
        print(f"Error in process_trades: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    input_file = "new_format_trades_report.csv"
    output_file = "updated_new_format_trades_report.csv"

    process_trades(input_file, output_file)