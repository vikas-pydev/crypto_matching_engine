import pytest
from datetime import datetime
from src.engine.order import Order, OrderType, OrderSide, OrderStatus

def test_order_initialization(sample_order_params):
    """Test basic order initialization"""
    order = Order(**sample_order_params)
    
    assert order.order_id == sample_order_params["order_id"]
    assert order.symbol == sample_order_params["symbol"]
    assert order.order_type == sample_order_params["order_type"]
    assert order.side == sample_order_params["side"]
    assert order.quantity == sample_order_params["quantity"]
    assert order.price == sample_order_params["price"]
    assert order.status == OrderStatus.NEW
    assert order.filled_quantity == 0.0
    assert order.remaining_quantity == sample_order_params["quantity"]

def test_market_order_initialization():
    """Test market order initialization without price"""
    order = Order(
        order_id="test_market",
        symbol="BTC-USDT",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=1.0,
        remaining_quantity=1.0
    )
    
    assert order.price is None
    assert order.is_marketable == True

def test_limit_order_is_marketable(limit_buy_order):
    """Test limit order marketable property"""
    assert limit_buy_order.is_marketable == True

def test_order_fill_update():
    """Test order state updates after partial and full fills"""
    order = Order(
        order_id="test_fill",
        symbol="BTC-USDT",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=2.0,
        price=50000.0,
        remaining_quantity=2.0
    )
    
    # Test partial fill
    order.filled_quantity = 1.0
    order.remaining_quantity = 1.0
    order._update_status()
    assert order.status == OrderStatus.PARTIAL
    
    # Test complete fill
    order.filled_quantity = 2.0
    order.remaining_quantity = 0.0
    order._update_status()
    assert order.status == OrderStatus.FILLED

def test_ioc_order_initialization():
    """Test IOC order initialization and marketable property"""
    order = Order(
        order_id="test_ioc",
        symbol="BTC-USDT",
        order_type=OrderType.IOC,
        side=OrderSide.BUY,
        quantity=1.0,
        price=50000.0,
        remaining_quantity=1.0
    )
    
    assert order.is_marketable == True
    assert order.order_type == OrderType.IOC

def test_fok_order_initialization():
    """Test FOK order initialization and marketable property"""
    order = Order(
        order_id="test_fok",
        symbol="BTC-USDT",
        order_type=OrderType.FOK,
        side=OrderSide.SELL,
        quantity=1.0,
        price=50000.0,
        remaining_quantity=1.0
    )
    
    assert order.is_marketable == True
    assert order.order_type == OrderType.FOK

def test_invalid_quantity():
    """Test order initialization with invalid quantity"""
    with pytest.raises(ValueError):
        Order(
            order_id="test_invalid",
            symbol="BTC-USDT",
            order_type=OrderType.LIMIT,
            side=OrderSide.BUY,
            quantity=-1.0,
            price=50000.0,
            remaining_quantity=-1.0
        )