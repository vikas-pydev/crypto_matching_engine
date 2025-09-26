document.addEventListener('DOMContentLoaded', () => {
    const buyList = document.getElementById('buy-list');
    const sellList = document.getElementById('sell-list');
    const tradesList = document.getElementById('trades-list');
    const orderForm = document.getElementById('order-form');
    const orderTypeSelect = document.getElementById('order-type');
    const priceInput = document.getElementById('price');

    // Function to render orders (bids/asks)
    function renderOrders(orderListElement, orders) {
        orderListElement.innerHTML = '';
        if (orders.length === 0) {
            orderListElement.innerHTML = '<li>No orders</li>';
            return;
        }
        orders.forEach(order => {
            const [price, quantity] = order; // Orders from WebSocket are [price, quantity]
            const listItem = document.createElement('li');
            listItem.textContent = `Price: ${price}, Quantity: ${quantity}`;
            orderListElement.appendChild(listItem);
        });
    }

    // Function to render trades
    function renderTrades(trades) {
        if (trades.length === 0) {
            tradesList.innerHTML = '<li>No trades yet</li>';
            return;
        }
        // Clear only if there are actual trades to display
        if (tradesList.innerHTML === '<li>No trades yet</li>') {
            tradesList.innerHTML = '';
        }
        trades.forEach(trade => {
            const listItem = document.createElement('li');
            listItem.textContent = `Trade: ${trade.quantity} @ ${trade.price} (Side: ${trade.aggressor_side})`;
            tradesList.prepend(listItem); // Add new trades to the top
        });
    }

    // WebSocket connection for market data and trades
    const symbol = "BTC-USDT";
    const ws = new WebSocket(`ws://localhost:8000/ws/orderbook/${symbol}`);

    ws.onopen = () => {
        console.log("WebSocket connected!");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("WebSocket message received:", data);

        if (data.bids && data.asks) {
            // This is an order book update
            renderOrders(buyList, data.bids);
            renderOrders(sellList, data.asks);
        } else if (data.trades) {
            // This is a trade execution update
            renderTrades(data.trades);
        }
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
        console.log("WebSocket closed.");
    };

    // Handle order type change for price input
    orderTypeSelect.addEventListener('change', (event) => {
        if (event.target.value === 'MARKET' || event.target.value === 'IOC' || event.target.value === 'FOK') {
            priceInput.disabled = true;
            priceInput.value = '';
        } else {
            priceInput.disabled = false;
        }
    });

    // Handle order form submission
    orderForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const orderData = {
            symbol: document.getElementById('symbol').value,
            side: document.getElementById('side').value.toLowerCase(),
            order_type: orderTypeSelect.value.toLowerCase(),
            quantity: parseFloat(document.getElementById('quantity').value),
            price: priceInput.disabled ? null : parseFloat(priceInput.value)
        };

        try {
            const response = await fetch('http://localhost:8000/api/v1/orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(`Error placing order: ${JSON.stringify(errorData, null, 2)}`);
                return;
            }

            const result = await response.json();
            console.log('Order placed successfully:', result);
            alert('Order placed successfully!');
            orderForm.reset();
        } catch (error) {
            console.error('Error placing order:', error);
            alert(`Error placing order: ${error.message || 'Unknown error'}`);
        }
    });
});