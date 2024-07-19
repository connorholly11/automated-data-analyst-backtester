from polygon_handler import PolygonDataHandler
from ai_engine import AIEngine

class StrategyAnalyzer:
    def __init__(self, polygon_handler: PolygonDataHandler, ai_engine: AIEngine):
        self.polygon_handler = polygon_handler
        self.ai_engine = ai_engine

    def analyze_strategy(self, symbol, start_date, end_date, backtest_results):
        # Fetch additional market data if needed
        market_data = self.polygon_handler.get_aggs(symbol, 1, 'day', start_date, end_date)

        # Prepare data for AI analysis
        analysis_data = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "backtest_results": backtest_results,
            "market_data": market_data
        }

        # Use AI to analyze the strategy
        ai_analysis, cost = self.ai_engine.analyze_strategy(analysis_data)

        return ai_analysis, cost