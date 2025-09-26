from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal
from collections import defaultdict
from sortedcontainers import SortedDict
from loguru import logger
from .order import Order, OrderSide, OrderStatus, OrderType

class OrderBook:
    def __init__(self, symbol: str):
        """Initialize a new order book"""
        self.symbol = symbol
        self.bids = SortedDict(lambda x: -x)  # Price levels for bids, sorted descending
        self.asks = SortedDict()  # Price levels for asks, sorted ascending
        self.orders = {}  # Map order_id to Order
        self.bid_queues = defaultdict(list)  # Orders at each bid price level
        self.ask_queues = defaultdict(list)  # Orders at each ask price level

    @property
    def best_bid(self) -> Optional[float]:
        """Returns the highest bid price"""
        return self.bids.keys()[0] if self.bids else None

    @property
    def best_ask(self) -> Optional[float]:
        """Returns the lowest ask price"""
        return self.asks.keys()[0] if self.asks else None

    def add_order(self, order: Order) -> List[dict]:
        """Add a new order to the book and process any immediate matches"""
        self.orders[order.order_id] = order

        if order.order_type == OrderType.MARKET:
            return self._process_market_order(order)
        elif order.order_type in [OrderType.IOC, OrderType.FOK]:
            return self._process_immediate_order(order)
        return self._process_limit_order(order)

    def _process_market_order(self, order: Order) -> List[dict]:
        """Process a market order"""
        trades = []
        opposite_side = self.asks if order.side == OrderSide.BUY else self.bids

        if not opposite_side:
            order.status = OrderStatus.CANCELLED
            return trades

        while order.remaining_quantity > 0 and opposite_side:
            best_price = opposite_side.keys()[0]
            trades.extend(self._match_at_price_level(order, best_price))

            if order.remaining_quantity > 0:
                if not opposite_side:
                    order.status = OrderStatus.PARTIAL if order.filled_quantity > 0 else OrderStatus.CANCELLED
                    break
                elif order.order_type == OrderType.FOK:
                    order.status = OrderStatus.CANCELLED
                    trades = []  # Clear trades for FOK orders that can't be fully filled
                    break

        if order.remaining_quantity == 0:
            order.status = OrderStatus.FILLED

        return trades

    def _process_limit_order(self, order: Order) -> List[dict]:
        """Process a limit order"""
        trades = []

        # Try to match against existing orders
        if order.side == OrderSide.BUY and self.asks and order.price >= self.best_ask:
            while order.remaining_quantity > 0 and self.asks and order.price >= self.best_ask:
                trades.extend(self._match_at_price_level(order, self.best_ask))
        elif order.side == OrderSide.SELL and self.bids and order.price <= self.best_bid:
            while order.remaining_quantity > 0 and self.bids and order.price <= self.best_bid:
                trades.extend(self._match_at_price_level(order, self.best_bid))

        # Add any remaining quantity to the book
        if order.remaining_quantity > 0:
            self._add_to_book(order)

        return trades

    def _process_immediate_order(self, order: Order) -> List[dict]:
        """Process IOC or FOK orders"""
        if order.order_type == OrderType.FOK:
            # For FOK, check if we can fill the entire quantity first
            opposite_side = self.asks if order.side == OrderSide.BUY else self.bids
            if not opposite_side:
                order.status = OrderStatus.CANCELLED
                return []

            total_available = 0
            for price in opposite_side.keys():
                if (order.side == OrderSide.BUY and price > order.price) or \
                   (order.side == OrderSide.SELL and price < order.price):
                    break
                total_available += opposite_side[price]
                if total_available >= order.quantity:
                    break

            if total_available < order.quantity:
                order.status = OrderStatus.CANCELLED
                return []

        # Process like a market order
        return self._process_market_order(order)

    def _match_at_price_level(self, incoming_order: Order, price_level: float) -> List[dict]:
        """Match incoming order against resting orders at a price level"""
        trades = []
        queue = self.ask_queues[price_level] if incoming_order.side == OrderSide.BUY else self.bid_queues[price_level]

        while queue and incoming_order.remaining_quantity > 0:
            resting_order = queue[0]
            traded_quantity = min(incoming_order.remaining_quantity, resting_order.remaining_quantity)

            trade = {
                "timestamp": datetime.utcnow(),
                "symbol": self.symbol,
                "trade_id": f"trade_{datetime.utcnow().timestamp()}",
                "price": price_level,
                "quantity": traded_quantity,
                "aggressor_side": incoming_order.side.value,
                "maker_order_id": resting_order.order_id,
                "taker_order_id": incoming_order.order_id
            }
            trades.append(trade)

            # Update quantities
            incoming_order.filled_quantity += traded_quantity
            incoming_order.remaining_quantity -= traded_quantity
            resting_order.filled_quantity += traded_quantity
            resting_order.remaining_quantity -= traded_quantity

            if resting_order.remaining_quantity == 0:
                resting_order.status = OrderStatus.FILLED
                queue.pop(0)
                if not queue:
                    self._remove_price_level(price_level, resting_order.side)

            if incoming_order.remaining_quantity == 0:
                incoming_order.status = OrderStatus.FILLED
            elif incoming_order.filled_quantity > 0:
                incoming_order.status = OrderStatus.PARTIAL

        return trades

    def get_all_bids(self) -> List[Dict[str, float]]:
        """Returns all bid orders aggregated by price level."""
        return [{
            "price": float(price),
            "quantity": sum(order.remaining_quantity for order in self.bid_queues[price])
        } for price in self.bids.keys()]

    def get_all_asks(self) -> List[Dict[str, float]]:
        """Returns all ask orders aggregated by price level."""
        return [{
            "price": float(price),
            "quantity": sum(order.remaining_quantity for order in self.ask_queues[price])
        } for price in self.asks.keys()]

    def _add_to_book(self, order: Order) -> None:
        """Add an order to the order book"""
        if order.side == OrderSide.BUY:
            if order.price not in self.bids:
                self.bids[order.price] = order.remaining_quantity
            else:
                self.bids[order.price] += order.remaining_quantity
            self.bid_queues[order.price].append(order)
        else:
            if order.price not in self.asks:
                self.asks[order.price] = order.remaining_quantity
            else:
                self.asks[order.price] += order.remaining_quantity
            self.ask_queues[order.price].append(order)

    def _remove_price_level(self, price: float, side: OrderSide) -> None:
        """Remove a price level from the order book"""
        if side == OrderSide.BUY:
            if price in self.bids:
                del self.bids[price]
                del self.bid_queues[price]
        else:
            if price in self.asks:
                del self.asks[price]
                del self.ask_queues[price]

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order in the book"""
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return False

        if order.side == OrderSide.BUY:
            self.bids[order.price] -= order.remaining_quantity
            if self.bids[order.price] <= 0:
                del self.bids[order.price]
            queue = self.bid_queues[order.price]
        else:
            self.asks[order.price] -= order.remaining_quantity
            if self.asks[order.price] <= 0:
                del self.asks[order.price]
            queue = self.ask_queues[order.price]

        queue.remove(order)
        if not queue:
            self._remove_price_level(order.price, order.side)

        del self.orders[order_id]
        order.status = OrderStatus.CANCELLED
        return True

    def get_order_book_snapshot(self, depth: int = 10) -> dict:
        """Get current order book state up to specified depth"""
        bids = []
        asks = []
        
        # Get top bids (highest prices)
        bid_prices = list(reversed(list(self.bids.keys())))[:depth]
        for price in bid_prices:
            bids.append([float(price), float(self.bids[price])])
        
        # Get top asks (lowest prices)
        ask_prices = list(self.asks.keys())[:depth]
        for price in ask_prices:
            asks.append([float(price), float(self.asks[price])])
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": self.symbol,
            "bids": bids,
            "asks": asks
        }