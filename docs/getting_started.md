# Getting Started with Cryptocurrency Matching Engine

## Introduction
A cryptocurrency matching engine is the core component of a trading system that matches buy and sell orders. This document will help you understand how our matching engine works and how to use it.

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone [repository-url]

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage Example
```python
from src.engine.order import Order, OrderType, OrderSide
from src.engine.orderbook import OrderBook

# Create an order book for BTC-USD
book = OrderBook("BTC-USD")

# Create a limit buy order
buy_order = Order(
    order_id="buy1",
    symbol="BTC-USD",
    order_type=OrderType.LIMIT,
    side=OrderSide.BUY,
    quantity=1.0,
    price=50000.0,
    remaining_quantity=1.0
)

# Add the buy order to the book
book.add_order(buy_order)

# Create a matching sell order
sell_order = Order(
    order_id="sell1",
    symbol="BTC-USD",
    order_type=OrderType.LIMIT,
    side=OrderSide.SELL,
    quantity=1.0,
    price=50000.0,
    remaining_quantity=1.0
)

# Process the sell order and get trades
trades = book.add_order(sell_order)

# Check trade details
for trade in trades:
    print(f"Trade executed: {trade['quantity']} BTC at ${trade['price']}")
```

## Running Tests
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_order.py -v
```

## Project Structure
```
crypto_matching_engine/
├── src/
│   └── engine/
│       ├── __init__.py    # Package exports
│       ├── order.py       # Order management
│       └── orderbook.py   # Order book and matching
├── tests/
│   ├── test_order.py     # Order tests
│   └── test_orderbook.py # Order book tests
├── docs/                 # Documentation
└── requirements.txt     # Dependencies
```

## Key Features
- Price-Time Priority Matching
- Multiple Order Types Support
- Efficient Order Book Management
- Trade Generation
- Comprehensive Test Coverage

## Dependencies
- pydantic (2.3.0): Data validation
- sortedcontainers (2.4.0): Order book implementation

## Next Steps
- Check out [order_types.md](order_types.md) for details on supported order types
- See [matching_logic.md](matching_logic.md) for understanding the matching algorithm
- Review [architecture.md](architecture.md) for system design details