import os
from dotenv import load_dotenv
from polygon_handler import PolygonDataHandler
from strategy_analyzer import StrategyAnalyzer
from ai_engine import AIEngine
from backtester import Backtester

load_dotenv()

def main():
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    polygon_handler = PolygonDataHandler(polygon_api_key)
    ai_engine = AIEngine()
    backtester = Backtester(polygon_handler)

    # Example usage
    symbol = "AAPL"
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    # Define a simple strategy
    def simple_strategy(open_price, high_price, low_price, close_price):
        if close_price > open_price:
            return 'buy'
        else:
            return 'sell'

    # Run backtest
    backtest_results = backtester.run_backtest(symbol, start_date, end_date, simple_strategy)

    # Analyze strategy
    analyzer = StrategyAnalyzer(polygon_handler, ai_engine)
    analysis = analyzer.analyze_strategy(symbol, start_date, end_date, backtest_results)

    print("Backtest Results:")
    print(backtest_results)
    print("\nStrategy Analysis:")
    print(analysis)

if __name__ == "__main__":
    main()