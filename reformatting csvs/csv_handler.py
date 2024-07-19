import pandas as pd
import pytz

class CSVDataHandler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None

    def get_data(self):
        if self.data is None:
            self.data = pd.read_csv(self.file_path, parse_dates=['DateTime'])
            self.data = self._preprocess_data(self.data)
        return self.data

    def _preprocess_data(self, df):
        # Convert futures symbols to stocks
        df['Symbol'] = df['Symbol'].apply(self._convert_symbol)

        # Convert UTC to EST
        eastern = pytz.timezone('US/Eastern')
        df['DateTime'] = pd.to_datetime(df['DateTime'], utc=True).dt.tz_convert(eastern)

        # Remove timezone info to avoid issues with some libraries
        df['DateTime'] = df['DateTime'].dt.tz_localize(None)

        return df

    def _convert_symbol(self, symbol):
        if symbol.startswith(('MNQ', 'NQ')):
            return 'QQQ'
        elif symbol.startswith(('ES', 'MES')):
            return 'SPY'
        return symbol

    def save_updated_csv(self, output_path):
        updated_data = self.get_data()
        updated_data.to_csv(output_path, index=False)

# Example usage:
# csv_handler = CSVDataHandler("new_format_trades_report.csv")
# csv_handler.save_updated_csv("updated_new_format_trades_report.csv")