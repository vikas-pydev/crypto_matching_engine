from src.engine.order import Order, OrderType, OrderSide
from src.engine.orderbook import OrderBook

def print_header(text):
    print(f"\n{'='*20} {text} {'='*20}")

def print_trades(trades):
    if not trades:
        print("No trades executed")
        return
    print("\nTrades executed:")
    for trade in trades:
        print(f"MATCH: {trade['quantity']} BTC @ ${trade['price']}")
        print(f"Buyer: {trade['taker_order_id']}, Seller: {trade['maker_order_id']}")

def print_book_state(book):
    snapshot = book.get_order_book_snapshot()
    print("\nOrder Book State:")
    
    print("Bids (Buy Orders):")
    for price, quantity in snapshot['bids']:
        print(f"  ${price:.2f}: {quantity:.8f} BTC")
    
    print("\nAsks (Sell Orders):")
    for price, quantity in snapshot['asks']:
        print(f"  ${price:.2f}: {quantity:.8f} BTC")

def main():
    # Initialize
    print_header("Initializing Order Book")
    book = OrderBook("BTC-USD")
    
    # Test 1: Add Limit Buy Order
    print_header("Test 1: Adding Limit Buy Order")
    buy_order = Order(
        order_id="buy1",
        symbol="BTC-USD",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=1.0,
        price=50000.0,
        remaining_quantity=1.0
    )
    trades = book.add_order(buy_order)
    print(f"Added: Buy 1.0 BTC @ $50,000")
    print_trades(trades)
    print_book_state(book)
    
    # Test 2: Add Matching Sell Order
    print_header("Test 2: Adding Matching Sell Order")
    sell_order = Order(
        order_id="sell1",
        symbol="BTC-USD",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=0.5,
        price=50000.0,
        remaining_quantity=0.5
    )
    trades = book.add_order(sell_order)
    print(f"Added: Sell 0.5 BTC @ $50,000")
    print_trades(trades)
    print_book_state(book)
    
    # Test 3: Add Non-matching Order
    print_header("Test 3: Adding Non-matching Order")
    sell_order2 = Order(
        order_id="sell2",
        symbol="BTC-USD",
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        quantity=1.0,
        price=51000.0,
        remaining_quantity=1.0
    )
    trades = book.add_order(sell_order2)
    print(f"Added: Sell 1.0 BTC @ $51,000")
    print_trades(trades)
    print_book_state(book)
    
    # Test 4: Add Market Buy Order
    print_header("Test 4: Adding Market Buy Order")
    market_buy = Order(
        order_id="market_buy1",
        symbol="BTC-USD",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=0.8,
        price=None,
        remaining_quantity=0.8
    )
    trades = book.add_order(market_buy)
    print(f"Added: Market Buy 0.8 BTC")
    print_trades(trades)
    print_book_state(book)

if __name__ == "__main__":
    main()