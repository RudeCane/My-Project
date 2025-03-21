backend/
│── main.py                # FastAPI entry point
│── config.py              # Configuration settings (API keys, DB URL)
│── database.py            # Database setup (SQLAlchemy)
│── models.py              # Defines database tables (Users, Trades, PnL)
│── auth.py                # User authentication (Google OAuth & Email/Password)
│── uniswap_handler.py     # Uniswap trade execution & liquidity functions
│── websocket_handler.py   # WebSocket live updates
│── routes/
│   ├── users.py           # Authentication routes
│   ├── trades.py          # Trade execution API
│   ├── liquidity.py       # Liquidity management API
│   ├── pnl.py             # PnL tracking API
│   ├── websocket.py       # WebSocket connection API
│── requirements.txt       # List of Python dependencies
│── Dockerfile             # Docker setup for backend deployment
│── docker-compose.yml     # Orchestrates database & backend services
│── .env                   # Environment variables (PRIVATE KEYS, API URLs)
│── .gitignore             # Ignore unnecessary files (venv, logs, DB)


