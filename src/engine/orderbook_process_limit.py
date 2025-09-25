def _process_limit_order(self, order: Order) -> List[dict]:
        """Process a limit order"""
        trades = []
        
        # If the order is marketable, try to match it first
        if order.is_marketable:
            opposite_side = self.asks if order.side == OrderSide.BUY else self.bids
            best_price = opposite_side.keys()[0] if opposite_side else None
            
            if best_price and (
                (order.side == OrderSide.BUY and order.price >= best_price) or
                (order.side == OrderSide.SELL and order.price <= best_price)
            ):
                trades.extend(self._match_at_price_level(order, best_price))
        
        # If order still has remaining quantity, add it to the book
        if order.remaining_quantity > 0:
            if order.side == OrderSide.BUY:
                if order.price not in self.bids:
                    self.bids[order.price] = order.remaining_quantity
                else:
                    self.bids[order.price] += order.remaining_quantity
                self.bid_queues[order.price].append(order)
            else:  # SELL
                if order.price not in self.asks:
                    self.asks[order.price] = order.remaining_quantity
                else:
                    self.asks[order.price] += order.remaining_quantity
                self.ask_queues[order.price].append(order)
            
            self.orders[order.order_id] = order
        
        return trades