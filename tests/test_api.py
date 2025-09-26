import pytest
from fastapi.testclient import TestClient
from src.api.main import app

# Initialize test client with default settings
# FastAPI's TestClient automatically uses the correct transport
client = TestClient(app)

def test_create_order_limit_buy():
    """Test creating a limit buy order"""
    response = client.post("/api/v1/orders", params={
        "symbol": "BTC-USDT",
        "side": "buy",
        "order_type": "limit",
        "quantity": 1.0,
        "price": 50000.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "order" in data
    assert "trades" in data
    assert data["order"]["symbol"] == "BTC-USDT"
    assert data["order"]["side"] == "buy"
    assert data["order"]["order_type"] == "limit"

def test_create_order_market_sell():
    """Test creating a market sell order"""
    response = client.post("/api/v1/orders", params={
        "symbol": "BTC-USDT",
        "side": "sell",
        "order_type": "market",
        "quantity": 1.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["order"]["order_type"] == "market"
    assert data["order"]["price"] is None

def test_create_order_invalid_symbol():
    """Test creating an order with invalid symbol"""
    response = client.post("/api/v1/orders", params={
        "symbol": "INVALID-PAIR",
        "side": "buy",
        "order_type": "limit",
        "quantity": 1.0,
        "price": 50000.0
    })
    
    assert response.status_code == 404

def test_create_limit_order_without_price():
    """Test creating a limit order without price"""
    response = client.post("/api/v1/orders", params={
        "symbol": "BTC-USDT",
        "side": "buy",
        "order_type": "limit",
        "quantity": 1.0
    })
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_orderbook_websocket():
    """Test order book WebSocket connection and updates"""
    import asyncio
    from fastapi.websockets import WebSocketDisconnect
    
    with client.websocket_connect("/ws/orderbook/BTC-USDT") as websocket:
        # Get initial snapshot
        data = websocket.receive_json()
        assert "timestamp" in data
        assert "symbol" in data
        assert "bids" in data
        assert "asks" in data

        # Create an order to trigger an update
        response = client.post("/api/v1/orders", params={
            "symbol": "BTC-USDT",
            "side": "buy",
            "order_type": "limit",
            "quantity": 1.0,
            "price": 50000.0
        })
        assert response.status_code == 200

        # Get the update
        data = websocket.receive_json()
        assert "bids" in data
        assert len(data["bids"]) > 0
        await asyncio.sleep(0.1) # Add a small delay
    websocket.close() # Explicitly close the websocket