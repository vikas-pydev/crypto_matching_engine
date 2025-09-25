import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Tuple
import pandas as pd

def create_orderbook_visualization(
    bids: List[Tuple[float, float]],
    asks: List[Tuple[float, float]],
    trades: List[dict] = None,
    title: str = "Order Book Depth"
):
    """
    Create an interactive order book visualization using Plotly
    
    Args:
        bids: List of (price, quantity) tuples for bid orders
        asks: List of (price, quantity) tuples for ask orders
        trades: Optional list of recent trades to display
        title: Title for the visualization
    """
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bid bars
    bid_prices, bid_quantities = zip(*bids) if bids else ([], [])
    fig.add_trace(
        go.Bar(
            x=bid_prices,
            y=bid_quantities,
            name="Bids",
            marker_color="rgba(0, 255, 0, 0.5)"
        ),
        secondary_y=False,
    )
    
    # Add ask bars
    ask_prices, ask_quantities = zip(*asks) if asks else ([], [])
    fig.add_trace(
        go.Bar(
            x=ask_prices,
            y=ask_quantities,
            name="Asks",
            marker_color="rgba(255, 0, 0, 0.5)"
        ),
        secondary_y=False,
    )
    
    # Add trades if provided
    if trades:
        trade_prices = [t["price"] for t in trades]
        trade_quantities = [t["quantity"] for t in trades]
        trade_sides = [t["aggressor_side"] for t in trades]
        
        # Different colors for buy/sell trades
        colors = ["blue" if side == "buy" else "red" for side in trade_sides]
        
        fig.add_trace(
            go.Scatter(
                x=trade_prices,
                y=trade_quantities,
                mode="markers",
                name="Trades",
                marker=dict(color=colors, size=10),
                hovertext=[f"Price: {p}<br>Quantity: {q}<br>Side: {s}" 
                          for p, q, s in zip(trade_prices, trade_quantities, trade_sides)]
            ),
            secondary_y=True,
        )
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Price",
        yaxis_title="Quantity",
        hovermode="x unified",
        showlegend=True,
        template="plotly_dark"
    )
    
    return fig

def create_trade_flow_diagram(trades: List[dict]):
    """
    Create a visualization of trade flow showing price levels and matched orders
    """
    fig = go.Figure()
    
    # Extract trade data
    timestamps = [t["timestamp"] for t in trades]
    prices = [t["price"] for t in trades]
    quantities = [t["quantity"] for t in trades]
    sides = [t["aggressor_side"] for t in trades]
    
    # Create scatter plot for trades
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=prices,
            mode="markers+lines",
            marker=dict(
                size=quantities,
                sizemode="area",
                sizeref=2.*max(quantities)/(40.**2),
                sizemin=4,
                color=[("green" if s == "buy" else "red") for s in sides]
            ),
            text=[f"Quantity: {q}<br>Side: {s}" for q, s in zip(quantities, sides)],
            name="Trades"
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Trade Flow Visualization",
        xaxis_title="Time",
        yaxis_title="Price",
        showlegend=True,
        template="plotly_dark",
        hovermode="closest"
    )
    
    return fig