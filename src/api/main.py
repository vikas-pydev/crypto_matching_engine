from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
import asyncio
from datetime import datetime
import uuid

from ..engine.order import Order, OrderType, OrderSide
from ..engine.orderbook import OrderBook

app = FastAPI(title="Crypto Matching Engine API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize order books for different trading pairs
order_books = {
    "BTC-USDT": OrderBook("BTC-USDT"),
    "ETH-USDT": OrderBook("ETH-USDT"),
}

# WebSocket connections per symbol
websocket_connections = {}

async def broadcast_orderbook_updates(symbol: str):
    """Broadcast order book updates to all connected clients"""
    if symbol not in websocket_connections or not websocket_connections[symbol]:
        return
    
    orderbook = order_books[symbol]
    snapshot = orderbook.get_order_book_snapshot()
    
    # Create a copy of the list to avoid modification during iteration
    connections = websocket_connections[symbol].copy()
    for websocket in connections:
        try:
            await websocket.send_json(snapshot)
        except Exception as e:
            try:
                websocket_connections[symbol].remove(websocket)
                await websocket.close()
            except:
                pass  # Connection might already be closed

@app.post("/api/v1/orders")
async def create_order(
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    quantity: float,
    price: Optional[float] = None
):
    """Create a new order"""
    if symbol not in order_books:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    if order_type == OrderType.LIMIT and price is None:
        raise HTTPException(status_code=400, detail="Price is required for limit orders")
    
    order = Order(
        order_id=str(uuid.uuid4()),
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        remaining_quantity=quantity
    )
    
    trades = order_books[symbol].add_order(order)
    
    # Broadcast order book updates
    await broadcast_orderbook_updates(symbol)
    
    return {
        "order": order,
        "trades": trades
    }

@app.websocket("/ws/orderbook/{symbol}")
async def orderbook_feed(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for order book updates"""
    if symbol not in order_books:
        await websocket.close(code=1000, reason="Invalid trading pair")
        return
    
    await websocket.accept()
    
    # Initialize the connection list for this symbol if it doesn't exist
    if symbol not in websocket_connections:
        websocket_connections[symbol] = []
    websocket_connections[symbol].append(websocket)
    
    try:
        # Send initial snapshot
        snapshot = order_books[symbol].get_order_book_snapshot()
        await websocket.send_json(snapshot)
        
        # Wait for client disconnect
        while True:
            try:
                # Use a small timeout to allow checking for client disconnect
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                # This is expected - continue waiting
                pass
            except Exception:
                # Client disconnected or other error
                break
            await asyncio.sleep(1)  # Update frequency
    except:
        websocket_connections.remove(websocket)
        await websocket.close()

@app.get("/order_book/{symbol}")
async def get_order_book(symbol: str):
    if symbol not in order_books:
        raise HTTPException(status_code=404, detail="Order book not found for this symbol")
    order_book = order_books[symbol]
    return {
        "buy_orders": order_book.buy_orders.get_all_orders(),
        "sell_orders": order_book.sell_orders.get_all_orders()
    }

@app.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    # Find the order in any of the order books and cancel it
    for symbol, order_book in order_books.items():
        if order_book.cancel_order(order_id):
            await manager.broadcast(f"Order {order_id} cancelled")
            return {"message": f"Order {order_id} cancelled successfully"}
    raise HTTPException(status_code=404, detail="Order not found")