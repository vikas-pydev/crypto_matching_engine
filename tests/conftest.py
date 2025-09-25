import pytest
from datetime import datetime
from src.engine.order import Order, OrderType, OrderSide, OrderStatus
from src.engine.orderbook import OrderBook

@pytest.fixture
def sample_order_params():
    """Fixture providing sample order parameters"""
    return {
        "order_id": "test_order_1",
        "symbol": "BTC-USDT",
        "order_type": OrderType.LIMIT,
        "side": OrderSide.BUY,
        "quantity": 1.0,
        "price": 50000.0,
        "remaining_quantity": 1.0
    }

@pytest.fixture
def limit_buy_order(sample_order_params):
    """Fixture providing a sample limit buy order"""
    return Order(**sample_order_params)

@pytest.fixture
def limit_sell_order(sample_order_params):
    """Fixture providing a sample limit sell order"""
    params = sample_order_params.copy()
    params.update({
        "order_id": "test_order_2",
        "side": OrderSide.SELL,
        "price": 50100.0
    })
    return Order(**params)

@pytest.fixture
def market_buy_order():
    """Fixture providing a sample market buy order"""
    return Order(
        order_id="test_market_1",
        symbol="BTC-USDT",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=1.0,
        remaining_quantity=1.0
    )

@pytest.fixture
def empty_order_book():
    """Fixture providing an empty order book"""
    return OrderBook("BTC-USDT")

@pytest.fixture
def populated_order_book(empty_order_book, limit_buy_order, limit_sell_order):
    """Fixture providing an order book with some initial orders"""
    order_book = empty_order_book
    order_book.add_order(limit_buy_order)
    order_book.add_order(limit_sell_order)
    return order_book