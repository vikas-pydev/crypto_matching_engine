import pytest
from src.engine.order import Order, OrderType, OrderSide, OrderStatus
from src.engine.orderbook import OrderBook

def test_order_book_initialization(empty_order_book):
    """Test order book initialization"""
    assert empty_order_book.symbol == "BTC-USDT"
    assert len(empty_order_book.bids) == 0
    assert len(empty_order_book.asks) == 0

def test_limit_order_addition(empty_order_book, limit_buy_order):
    """Test adding a limit order to the book"""
    trades = empty_order_book.add_order(limit_buy_order)
    
    assert len(trades) == 0  # No trades should be generated
    assert limit_buy_order.order_id in empty_order_book.orders
    assert len(empty_order_book.bids) == 1
    assert empty_order_book.best_bid == limit_buy_order.price

def test_market_order_matching(populated_order_book, market_buy_order):
    """Test matching of a market order"""
    initial_ask_size = len(populated_order_book.asks)
    trades = populated_order_book.add_order(market_buy_order)
    
    assert len(trades) > 0  # Should generate at least one trade
    assert market_buy_order.status == OrderStatus.FILLED
    assert len(populated_order_book.asks) < initial_ask_size  # Ask should be removed

def test_price_time_priority(empty_order_book):
    """Test price-time priority matching"""
    # Add two buy orders at the same price
    order1 = Order(
        order_id="buy1",
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=1.0,
        price=50000.0,
        remaining_quantity=1.0
    )
    order2 = Order(
        order_id="buy2",
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=1.0,
        price=50000.0,
        remaining_quantity=1.0
    )
    empty_order_book.add_order(order1)
    empty_order_book.add_order(order2)
    
    # Add matching sell order
    sell_order = Order(
        order_id="sell1",
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=1.0,
        price=50000.0,
        remaining_quantity=1.0
    )
    trades = empty_order_book.add_order(sell_order)
    
    assert len(trades) == 1
    assert trades[0]["maker_order_id"] == "buy1"  # First order should be matched first

def test_ioc_order_partial_fill(empty_order_book):
    """Test IOC order with partial fill"""
    # Add a small limit order
    limit_order = Order(
        order_id="limit1",
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=1.0,
        price=50000.0,
        remaining_quantity=1.0
    )
    empty_order_book.add_order(limit_order)
    
    # Add larger IOC order
    ioc_order = Order(
        order_id="ioc1",
        symbol="BTC-USDT",
        order_type=OrderType.IOC,
        side=OrderSide.BUY,
        quantity=2.0,
        price=50000.0,
        remaining_quantity=2.0
    )
    trades = empty_order_book.add_order(ioc_order)
    
    assert len(trades) == 1
    assert trades[0]["quantity"] == 1.0  # Should fill only available quantity
    assert ioc_order.status == OrderStatus.PARTIAL  # Should be partially filled
    assert ioc_order.remaining_quantity == 1.0  # Remaining quantity should be cancelled

def test_fok_order_no_fill(empty_order_book):
    """Test FOK order with no fill (should be cancelled)"""
    # Add a small limit order
    limit_order = Order(
        order_id="limit1",
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=1.0,
        price=50000.0,
        remaining_quantity=1.0
    )
    empty_order_book.add_order(limit_order)
    
    # Add larger FOK order
    fok_order = Order(
        order_id="fok1",
        symbol="BTC-USDT",
        order_type=OrderType.FOK,
        side=OrderSide.BUY,
        quantity=2.0,
        price=50000.0,
        remaining_quantity=2.0
    )
    trades = empty_order_book.add_order(fok_order)
    
    assert len(trades) == 0  # Should not generate any trades
    assert fok_order.status == OrderStatus.CANCELLED  # Should be cancelled

def test_order_cancellation(populated_order_book, limit_buy_order):
    """Test order cancellation"""
    assert populated_order_book.cancel_order(limit_buy_order.order_id) == True
    assert limit_buy_order.status == OrderStatus.CANCELLED
    assert limit_buy_order.order_id not in populated_order_book.bid_queues[limit_buy_order.price]

def test_order_book_snapshot(populated_order_book):
    """Test order book snapshot generation"""
    snapshot = populated_order_book.get_order_book_snapshot()
    
    assert "timestamp" in snapshot
    assert "symbol" in snapshot
    assert "bids" in snapshot
    assert "asks" in snapshot
    assert len(snapshot["bids"]) > 0
    assert len(snapshot["asks"]) > 0