from polygon_handler import PolygonDataHandler

class Backtester:
    def __init__(self, polygon_handler: PolygonDataHandler):
        self.polygon_handler = polygon_handler

    def run_backtest(self, symbol, start_date, end_date, strategy):
        # Fetch historical data
        historical_data = self.polygon_handler.get_aggs(symbol, 1, 'day', start_date, end_date)

        # Initialize backtest variables
        portfolio_value = 10000  # Starting with $10,000
        position = 0
        trades = []

        # Run the backtest
        for bar in historical_data:
            date = bar['t']
            open_price = bar['o']
            high_price = bar['h']
            low_price = bar['l']
            close_price = bar['c']

            # Apply strategy
            action = strategy(open_price, high_price, low_price, close_price)

            if action == 'buy' and position <= 0:
                # Buy logic
                shares_to_buy = int(portfolio_value / close_price)
                position += shares_to_buy
                portfolio_value -= shares_to_buy * close_price
                trades.append(('buy', date, close_price, shares_to_buy))

            elif action == 'sell' and position >= 0:
                # Sell logic
                shares_to_sell = abs(position)
                position -= shares_to_sell
                portfolio_value += shares_to_sell * close_price
                trades.append(('sell', date, close_price, shares_to_sell))

        # Calculate final portfolio value
        final_portfolio_value = portfolio_value + position * historical_data[-1]['c']

        return {
            'initial_value': 10000,
            'final_value': final_portfolio_value,
            'return': (final_portfolio_value - 10000) / 10000 * 100,
            'trades': trades
        }