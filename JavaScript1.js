frontend /
├── src /
│   ├── components /
import Dashboard from "./components/Dashboard";

function App() {
    return (
        <div>
            <h1>Uniswap Market Maker</h1>
            <Dashboard />
        </div>
    );
}

export default App;
import { useEffect, useState } from "react";

const WebSocketComponent = () => {
    const [price, setPrice] = useState(null);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws");

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "price_update") {
                setPrice(data.price);
            }
        };

        return () => {
            socket.close();
        };
    }, []);

    return (
        <div>
            <h2>Live Price</h2>
            <p>{price ? `Price: ${price}` : "Fetching..."}</p>
        </div>
    );
};

export default WebSocketComponent;
│   │   ├── Dashboard.js
│   │   ├── WebSocketComponent.js
│   │   ├── TradePanel.js
│   │   ├── PnLChart.js
│   ├── App.js
│   ├── index.js
├── package.json

