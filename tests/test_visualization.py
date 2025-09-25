import pytest
import plotly.graph_objects as go
from src.visualization.visualizer import create_orderbook_visualization, create_trade_flow_diagram

class TestVisualization:
    def test_create_orderbook_visualization(self):
        """Test order book visualization creation"""
        bids = [(49000.0, 1.0), (48000.0, 2.0)]
        asks = [(51000.0, 1.5), (52000.0, 1.0)]
        
        fig = create_orderbook_visualization(bids, asks)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2  # One trace for bids, one for asks

    def test_create_orderbook_visualization_with_trades(self):
        """Test order book visualization with trades"""
        bids = [(49000.0, 1.0)]
        asks = [(51000.0, 1.5)]
        trades = [
            {
                "price": 50000.0,
                "quantity": 1.0,
                "aggressor_side": "buy",
                "timestamp": "2025-09-24T10:00:00Z"
            }
        ]
        
        fig = create_orderbook_visualization(bids, asks, trades)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3  # Bids, asks, and trades

    def test_create_trade_flow_diagram(self):
        """Test trade flow diagram creation"""
        trades = [
            {
                "timestamp": "2025-09-24T10:00:00Z",
                "price": 50000.0,
                "quantity": 1.0,
                "aggressor_side": "buy"
            },
            {
                "timestamp": "2025-09-24T10:01:00Z",
                "price": 50100.0,
                "quantity": 2.0,
                "aggressor_side": "sell"
            }
        ]
        
        fig = create_trade_flow_diagram(trades)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1  # One trace for all trades