# Cryptocurrency Matching Engine

A basic cryptocurrency order matching engine with price-time priority.

## Features
- Price-Time Priority Matching
- Market & Limit Orders
- Real-time Order Book Management

## Quick Start
```python
from src.engine.order import Order, OrderType, OrderSide
from src.engine.orderbook import OrderBook

# Create order book
book = OrderBook("BTC-USD")

# Create and add a buy order
buy_order = Order(
    order_id="buy1",
    symbol="BTC-USD",
    order_type=OrderType.LIMIT,
    side=OrderSide.BUY,
    quantity=1.0,
    price=50000.0,
    remaining_quantity=1.0
)
book.add_order(buy_order)

# Create and add a matching sell order
sell_order = Order(
    order_id="sell1",
    symbol="BTC-USD",
    order_type=OrderType.LIMIT,
    side=OrderSide.SELL,
    quantity=1.0,
    price=50000.0,
    remaining_quantity=1.0
)
trades = book.add_order(sell_order)
```

## Project Structure

## Test the Engine
Run the demonstration:
```bash
python working_demo.py
```

This will show:
1. Adding limit orders
2. Order matching
3. Trade generation
4. Order book state

## Project Structure
```
crypto_matching_engine/
├── src/engine/         # Core engine
├── tests/             # Test suite
├── working_demo.py    # Demo script
└── requirements.txt   # Dependencies
```
```

## Installation

1. Create and activate virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

## Usage Example

```python
from engine import Order, OrderBook

# Create an order book
book = OrderBook(symbol="BTC-USD")

# Create some orders
buy_order = Order(
    order_id="buy1",
    side="buy",
    order_type="limit",
    price=50000.0,
    quantity=1.0,
    symbol="BTC-USD"
)

sell_order = Order(
    order_id="sell1",
    side="sell",
    order_type="limit",
    price=50000.0,
    quantity=1.0,
    symbol="BTC-USD"
)

# Process orders
book.add_order(buy_order)   # Added to book
trades = book.add_order(sell_order)  # Matches with buy_order

print(f"Trades: {trades}")
```

## Running Tests

```bash
python -m pytest tests/
```

## API Reference

### REST API Endpoints

#### Submit Order
```http
POST /api/v1/orders
```

Parameters:
```json
{
    "symbol": "BTC-USDT",
    "side": "buy",
    "order_type": "limit",
    "quantity": 1.0,
    "price": 25000.0
}
```

Order Types:
- `market`: Market order (price optional)
- `limit`: Limit order (price required)
- `ioc`: Immediate-or-Cancel
- `fok`: Fill-or-Kill

### WebSocket API

#### Order Book Updates
```
ws://localhost:8000/ws/orderbook/{symbol}
```

Example response:
```json
{
    "timestamp": "2025-09-25T10:00:00.000Z",
    "symbol": "BTC-USDT",
    "bids": [[50000.0, 1.5], [49900.0, 2.0]],
    "asks": [[50100.0, 1.0], [50200.0, 2.5]]
}
```

## Implementation Details

### Order Book
- SortedDict-based implementation for O(log n) operations
- Price-time priority queues at each price level
- Efficient order matching and execution
- Real-time market data updates

### Order Types
1. **Market Orders**
   - Immediate execution at best available prices
   - Can result in partial fills

2. **Limit Orders**
   - Price-protected execution
   - Added to book if not immediately matched

3. **IOC (Immediate-or-Cancel)**
   - Attempt immediate execution
   - Cancel any unfilled quantity

4. **FOK (Fill-or-Kill)**
   - Execute entirely or cancel
   - No partial fills allowed

### Test Coverage
- **Order Tests**: Creation, validation, status updates
- **OrderBook Tests**: 
  - Price-time priority matching
  - Market/Limit order execution
  - IOC/FOK handling
  - Order cancellation
  - Book snapshot generation
- **API Tests**:
  - REST endpoint validation
  - WebSocket streaming
  - Error handling
- **Visualization Tests**:
  - Order book depth charts
  - Trade flow diagrams

## Performance Considerations

- Optimized data structures for order book operations
- Efficient order matching algorithm
- Real-time market data updates
- WebSocket-based streaming for low latency

## License

MIT License