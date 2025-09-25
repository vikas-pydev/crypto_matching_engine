# Matching Logic and Order Book Management

## Price-Time Priority

### Overview
The matching engine uses a price-time priority (also known as FIFO - First In, First Out) algorithm to determine which orders get matched first.

### Priority Rules
1. **Price Priority**
   - For buy orders: Higher prices get priority
   - For sell orders: Lower prices get priority
   - Example: Buy order at $50,000 matches before buy at $49,900

2. **Time Priority**
   - When prices are equal, older orders match first
   - Based on order timestamp
   - Example: Two buy orders at $50,000, first one submitted gets filled first

## Order Book Structure

### Components
```python
class OrderBook:
    def __init__(self, symbol: str):
        self.bids = SortedDict()  # Buy orders sorted high to low
        self.asks = SortedDict()  # Sell orders sorted low to high
        self.orders = {}          # Quick order lookup by ID
```

### Price Levels
- Bids (Buy Orders): Sorted in descending order (highest first)
- Asks (Sell Orders): Sorted in ascending order (lowest first)
- Each price level maintains a queue of orders

## Matching Process

### 1. New Order Arrival
```python
def add_order(self, order: Order) -> List[Trade]:
    if order.order_type == OrderType.MARKET:
        return self._process_market_order(order)
    elif order.order_type in [OrderType.IOC, OrderType.FOK]:
        return self._process_immediate_order(order)
    return self._process_limit_order(order)
```

### 2. Matching Algorithm
1. Check if order can match:
   - Buy order price >= Sell order price
   - Both orders have remaining quantity

2. Generate trades:
   ```python
   trade = {
       "timestamp": datetime.utcnow(),
       "symbol": self.symbol,
       "price": match_price,
       "quantity": traded_quantity,
       "buyer_order_id": buy_order.order_id,
       "seller_order_id": sell_order.order_id
   }
   ```

3. Update orders:
   - Subtract filled quantity
   - Update order status
   - Remove completed orders

## Examples

### 1. Market Order Matching
```python
# Order book has sell orders at:
# $50,000 - 1.0 BTC
# $50,100 - 2.0 BTC

# Incoming market buy for 1.5 BTC
market_buy = Order(
    order_id="market1",
    symbol="BTC-USD",
    order_type=OrderType.MARKET,
    side=OrderSide.BUY,
    quantity=1.5
)

# Results in:
# - Trade 1: 1.0 BTC at $50,000
# - Trade 2: 0.5 BTC at $50,100
```

### 2. Limit Order Matching
```python
# Order book has buy orders at:
# $49,900 - 1.0 BTC
# $49,800 - 2.0 BTC

# Incoming limit sell at $49,900
limit_sell = Order(
    order_id="limit1",
    symbol="BTC-USD",
    order_type=OrderType.LIMIT,
    side=OrderSide.SELL,
    quantity=1.0,
    price=49900.0
)

# Results in:
# - Trade: 1.0 BTC at $49,900
```

## Performance Considerations

### Data Structures
- `SortedDict`: O(log n) for insertions and deletions
- Hash table for order lookup: O(1)
- Queue for time priority: O(1)

### Optimizations
1. Quick order lookup by ID
2. Efficient price level management
3. Minimal data copying
4. In-memory operations

## Error Handling

### Common Scenarios
1. Insufficient quantity
2. Price mismatch
3. Invalid order status
4. Duplicate order IDs

### Resolution
```python
def _validate_order(self, order: Order) -> bool:
    if order.price <= 0 or order.quantity <= 0:
        return False
    if self._order_exists(order.order_id):
        return False
    return True
```