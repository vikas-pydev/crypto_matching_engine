# Crypto Matching Engine

This project implements a high-performance cryptocurrency matching engine, designed to facilitate real-time trading of digital assets. It features a robust backend for order matching and market data dissemination, coupled with an interactive frontend for order submission and visualization.

## Project Goal

The primary goal is to develop a reliable, efficient, and scalable matching engine that can handle a high throughput of orders and provide accurate market data updates. The system aims to demonstrate best practices in concurrent programming, real-time data processing, and responsive web development.

## Initial Setup

To get the project up and running, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd crypto_matching_engine
    ```

2.  **Set up Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    ./venv/Scripts/activate  # On Windows
    source venv/bin/activate # On macOS/Linux
    ```

3.  **Install Dependencies:**
    Install the required Python packages for both the backend and frontend.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Backend Server:**
    The backend is built with FastAPI and Uvicorn. Navigate to the project root and run:
    ```bash
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    ```
    This will start the WebSocket server, handling order submissions and market data.

5.  **Run the Frontend Server:**
    The frontend is a simple HTML/CSS/JavaScript application. You can serve it using a basic Python HTTP server:
    ```bash
    python -m http.server 8080
    ```

6.  **Access the Frontend UI:**
    Open your web browser and navigate to `http://localhost:8080`.

## Core Matching Engine Logic

The heart of the system is the matching engine, implemented in Python, which processes and matches buy and sell orders.

### Best Bid and Offer (BBO) Calculation

The BBO represents the best available buy (bid) and sell (offer) prices in the order book. It is continuously updated as orders are placed, cancelled, or matched. The engine efficiently tracks the highest bid and lowest ask to provide real-time market depth.

### Internal Order Protection

To prevent self-trading (an order matching against another order from the same user), the matching engine incorporates internal order protection. This ensures that a user's buy order will not execute against their own sell order, maintaining fair and logical trading.

### Price-Time Priority

Orders are matched based on a strict price-time priority algorithm:

*   **Price Priority:** Buy orders with higher prices have priority, and sell orders with lower prices have priority.
*   **Time Priority:** Among orders at the same price level, the order that was submitted earlier in time has priority.

This ensures a fair and transparent matching process.

### Order Type Handling

The engine supports various order types to cater to different trading strategies:

*   **Limit Orders:** Orders to buy or sell at a specified price or better. These orders enter the order book if they are not immediately matched.
*   **Market Orders:** Orders to buy or sell immediately at the best available current market price. Market orders are guaranteed to execute but not at a guaranteed price.
*   **Stop Orders:** (Planned/Future Enhancement) Orders that become market orders once a specified stop price is reached.
*   **Stop-Limit Orders:** (Planned/Future Enhancement) Orders that become limit orders once a specified stop price is reached.

## Data Generation and API Specifications

### Order Submission

Orders are submitted to the backend via WebSocket connections. The API expects order messages to contain:

*   `symbol`: The trading pair (e.g., "BTC/USD").
*   `type`: Order type (e.g., "limit", "market").
*   `side`: "buy" or "sell".
*   `price`: (For limit orders) The desired price.
*   `quantity`: The amount to trade.

### Market Data Dissemination

The backend continuously disseminates real-time market data to connected clients via WebSockets. This includes:

*   **Order Book Snapshots:** Updates on the current state of bids and asks, typically showing aggregated price levels and quantities.
*   **Trade Executions:** Notifications of executed trades, including price, quantity, and timestamp.

### Trade Execution Data

When trades occur, the system generates and broadcasts trade execution reports, providing details such as:

*   `trade_id`: Unique identifier for the trade.
*   `symbol`: Trading pair.
*   `price`: Execution price.
*   `quantity`: Executed quantity.
*   `timestamp`: Time of execution.

## Technical Requirements

### Implementation in Python

The entire matching engine and API are implemented in Python, leveraging its rich ecosystem for asynchronous programming and data structures.

### High Performance

Optimizations are applied to ensure low-latency order processing and high throughput. This includes efficient data structures for the order book and asynchronous handling of WebSocket connections.

### Error Handling

Robust error handling mechanisms are in place to manage invalid order submissions, network issues, and unexpected system states, ensuring the stability and reliability of the engine.

### Logging

Comprehensive logging is implemented across the system to monitor order flow, trade executions, and system health. This aids in debugging, auditing, and performance analysis.

### Testing

Unit and integration tests are developed to ensure the correctness of the matching logic, API endpoints, and overall system behavior.

### Documentation

This `README.md` serves as a primary documentation source, complemented by inline code comments and potentially more detailed design documents.

## Bonus: Interactive Frontend

The project includes a simple yet interactive frontend built with HTML, CSS, and JavaScript. It connects to the backend via WebSockets to:

*   **Submit Orders:** Users can place buy/sell orders through a user-friendly interface.
*   **Visualize Order Book:** Real-time updates of the order book (bids and asks) are displayed dynamically.
*   **View Trade History:** Executed trades are shown as they occur, providing immediate feedback on market activity.

This frontend demonstrates the real-time capabilities of the matching engine and provides a practical way to interact with the system.