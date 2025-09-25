# Order Types and Behavior

## Overview
The matching engine supports multiple order types to accommodate different trading strategies. Each order type has specific behavior and execution rules.

## Supported Order Types

### 1. Market Orders
- **Definition**: Execute immediately at best available price
- **Use Case**: When immediate execution is priority over price
- **Behavior**:
  - Takes best available price from opposite side
  - Can result in multiple trades at different prices
  - No price specified - takes whatever is available
- **Example**:
```python
market_order = Order(
    order_id="market1",
    symbol="BTC-USD",
    order_type=OrderType.MARKET,
    side=OrderSide.BUY,
    quantity=1.0,
    remaining_quantity=1.0
)
```

### 2. Limit Orders
- **Definition**: Execute at specified price or better
- **Use Case**: When price is priority over immediate execution
- **Behavior**:
  - Can execute immediately if matching price available
  - Otherwise stays in order book
  - Guarantees price but not execution
- **Example**:
```python
limit_order = Order(
    order_id="limit1",
    symbol="BTC-USD",
    order_type=OrderType.LIMIT,
    side=OrderSide.BUY,
    quantity=1.0,
    price=50000.0,
    remaining_quantity=1.0
)
```

### 3. IOC (Immediate-or-Cancel)
- **Definition**: Fill what's possible immediately, cancel rest
- **Use Case**: When wanting immediate partial fills without waiting
- **Behavior**:
  - Attempts to fill immediately
  - Cancels any unfilled portion
  - Never enters order book
- **Example**:
```python
ioc_order = Order(
    order_id="ioc1",
    symbol="BTC-USD",
    order_type=OrderType.IOC,
    side=OrderSide.BUY,
    quantity=1.0,
    price=50000.0,
    remaining_quantity=1.0
)
```

### 4. FOK (Fill-or-Kill)
- **Definition**: Fill entire order immediately or cancel
- **Use Case**: When needing complete fill or nothing
- **Behavior**:
  - Must fill entire quantity to execute
  - Cancels if complete fill not possible
  - No partial fills allowed
- **Example**:
```python
fok_order = Order(
    order_id="fok1",
    symbol="BTC-USD",
    order_type=OrderType.FOK,
    side=OrderSide.BUY,
    quantity=1.0,
    price=50000.0,
    remaining_quantity=1.0
)
```

## Order States

1. **NEW**
   - Initial state when order is created
   - No trades executed yet

2. **PARTIAL**
   - Some quantity has been filled
   - Remaining quantity still available

3. **FILLED**
   - Entire quantity has been executed
   - Order is complete

4. **CANCELLED**
   - Order has been cancelled
   - No further execution possible

## Order Properties

### Required Properties
- `order_id`: Unique identifier
- `symbol`: Trading pair (e.g., "BTC-USD")
- `side`: BUY or SELL
- `quantity`: Amount to trade
- `remaining_quantity`: Amount left to fill

### Optional Properties
- `price`: Required for LIMIT, IOC, FOK; optional for MARKET
- `timestamp`: Automatically set on creation

## Error Handling
The system validates orders and handles common errors:

1. Invalid Quantity
```python
# Raises ValueError
Order(
    order_id="invalid1",
    symbol="BTC-USD",
    order_type=OrderType.LIMIT,
    side=OrderSide.BUY,
    quantity=-1.0,  # Invalid: negative quantity
    price=50000.0,
    remaining_quantity=-1.0
)
```

2. Missing Price for Limit Orders
```python
# Raises ValueError
Order(
    order_id="invalid2",
    symbol="BTC-USD",
    order_type=OrderType.LIMIT,
    side=OrderSide.BUY,
    quantity=1.0,
    price=None,  # Invalid: price required for limit orders
    remaining_quantity=1.0
)
```