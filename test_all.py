import unittest
import os
import pandas as pd
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock
from polygon_handler import PolygonDataHandler
from csv_handler import CSVDataHandler
from strategy_analyzer import StrategyAnalyzer
from ai_engine import AIEngine

load_dotenv()

class TestPolygonConnection(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.handler = PolygonDataHandler(self.api_key)

    def test_polygon_connection(self):
        # Test getting trade data
        trades = self.handler.get_trades("AAPL", "2023-04-14")
        self.assertIsNotNone(trades)
        self.assertGreater(len(trades), 0)

    def test_daily_open_close(self):
        daily_data = self.handler.get_daily_open_close("AAPL", "2023-04-14")
        self.assertIsNotNone(daily_data)
        self.assertIn("results", daily_data)

    def test_quote_data_unavailable(self):
        # Test that quote data is not available
        with self.assertRaises(NotImplementedError):
            self.handler.get_quotes("AAPL", "2023-04-14")

class TestCSVHandling(unittest.TestCase):
    def setUp(self):
        self.csv_handler = CSVDataHandler("new_format_trades_report.csv")

    def test_csv_parsing(self):
        data = self.csv_handler.get_data()
        self.assertIsNotNone(data)
        self.assertGreater(len(data), 0)
        self.assertIn("DateTime", data.columns)
        self.assertIn("Account", data.columns)
        self.assertIn("Symbol", data.columns)
        self.assertIn("TradeID", data.columns)

    def test_symbol_conversion(self):
        data = self.csv_handler.get_data()
        self.assertIn("QQQ", data["Symbol"].unique())
        self.assertIn("SPY", data["Symbol"].unique())

    def test_timezone_conversion(self):
        data = self.csv_handler.get_data()
        self.assertTrue(data["DateTime"].dt.tz is None)

class TestAnthropicConnection(unittest.TestCase):
    def setUp(self):
        self.ai_engine = AIEngine()

    @patch('anthropic.Anthropic.completions.create')
    def test_anthropic_connection(self, mock_create):
        mock_create.return_value = MagicMock(completion="Yes, I can hear you.")
        response = self.ai_engine.analyze_strategy({"test": "Can you hear me?"})
        self.assertIsNotNone(response)
        self.assertIn("hear", response.lower())

class TestAIUnderstanding(unittest.TestCase):
    def setUp(self):
        self.ai_engine = AIEngine()

    @patch('anthropic.Anthropic.completions.create')
    def test_ai_understanding(self, mock_create):
        mock_create.return_value = MagicMock(completion="Analysis of win/lose streaks, balance-based strategies, and time of day effects.")
        example_findings = """
        1. Win/Lose Streaks Strategy:
        - Fading traders based on their recent performance shows consistent profitability.
        - "Strategy 1" involves fading lose streaks 2-3 and win streak 4.
        - Daily lose streaks predict low win rates, while daily win streaks predict higher win rates.

        2. Balance-Based Streaks:
        - Fading traders based on their current account balance shows promise.
        - For tryouts, fading lose streak 2, win streak 2, and win streak 0 (all trades in drawdown) stood out.

        3. Time of Day Effects:
        - First 30 minutes of trading (9:30-10:00) consistently showed the highest average profits.
        - Morning session (9:00-11:00) had the largest losses on average (-$40), twice as large as afternoon.
        """

        response = self.ai_engine.analyze_strategy({"example_findings": example_findings})
        self.assertIn("win/lose streaks", response.lower())
        self.assertIn("balance-based", response.lower())
        self.assertIn("time of day", response.lower())

class TestAIUnderstandingCSVDescription(unittest.TestCase):
    def setUp(self):
        self.ai_engine = AIEngine()

    @patch('anthropic.Anthropic.completions.create')
    def test_ai_understanding_csv_description(self, mock_create):
        mock_create.return_value = MagicMock(completion="Analysis of trading data across multiple accounts and financial instruments.")
        csv_description = """
        CSV Format Description:
        This CSV file contains detailed trading data for multiple accounts across various financial instruments. Each row represents a single trade action within a position. The data is structured as follows:

        DateTime: Eastern Time (ET) timestamp of the trade, matching market hours of 9:30 to 16:00.
        Account: Unique identifier for each trading account. Higher numbers indicate newer accounts.
        Symbol: The financial instrument traded. Examples include "MNQ 03-2024-CME" and others.
        TradeID: Unique identifier for each trade action.
        Qta: Quantity of the instrument traded in this specific action.
        Price: The price at which the trade was executed.
        Balance: The account balance after the trade.
        PL: Profit/Loss for this specific trade action.
        NetPL: Net Profit/Loss for this specific trade action.
        PositionID: Unique identifier for each position. Multiple trades can belong to the same position.
        PositionQuantity: The total quantity of the instrument held in the position after this trade action.
        Operation: Indicates the type of action on the position (Open, Close, Increase, Decrease).
        """

        response = self.ai_engine.analyze_strategy({"csv_description": csv_description})
        self.assertIn("trading data", response.lower())
        self.assertIn("multiple accounts", response.lower())
        self.assertIn("financial instruments", response.lower())

class TestAIAnalysisCapability(unittest.TestCase):
    def setUp(self):
        self.ai_engine = AIEngine()

    @patch('anthropic.Anthropic.completions.create')
    def test_ai_analysis_trade_data(self, mock_create):
        mock_create.return_value = MagicMock(completion="Analysis of win/lose streaks, balance-based strategies, and time of day effects.")
        trade_data = {
            "win_lose_streaks": {"win_streak": 3, "lose_streak": 2},
            "balance_based_streaks": {"positive_streak": 4, "negative_streak": 1},
            "time_of_day_effects": {"morning": 100, "afternoon": -50}
        }
        response = self.ai_engine.analyze_strategy({"trade_data": trade_data})
        self.assertIn("win/lose streaks", response.lower())
        self.assertIn("balance-based streaks", response.lower())
        self.assertIn("time of day", response.lower())

    @patch('anthropic.Anthropic.completions.create')
    def test_ai_analysis_polygon_data(self, mock_create):
        mock_create.return_value = MagicMock(completion="Analysis of AAPL stock data including open, close, high, low, and volume.")
        polygon_data = {
            "symbol": "AAPL",
            "date": "2023-04-14",
            "open": 100,
            "close": 105,
            "high": 106,
            "low": 99,
            "volume": 1000000
        }
        response = self.ai_engine.analyze_strategy({"polygon_data": polygon_data})
        self.assertIn("aapl", response.lower())
        self.assertIn("open", response.lower())
        self.assertIn("close", response.lower())
        self.assertIn("volume", response.lower())

if __name__ == '__main__':
    unittest.main()