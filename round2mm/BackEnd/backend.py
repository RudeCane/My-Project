backend/
│── main.py                # FastAPI entry point
from fastapi import FastAPI
from auth import router as auth_router
from routes.trades import router as trade_router
from routes.liquidity import router as liquidity_router
from routes.pnl import router as pnl_router
from routes.websocket import router as websocket_router
from database import Base, engine
import asyncio
from websocket_handler import send_price_updates

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(trade_router, prefix="/trade", tags=["Trading"])
app.include_router(liquidity_router, prefix="/liquidity", tags=["Liquidity"])
app.include_router(pnl_router, prefix="/pnl", tags=["PnL"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSockets"])

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(send_price_updates())

@app.get("/")
def read_root():
    return {"message": "Uniswap Market Maker Backend Running"}

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
FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

│── docker-compose.yml     # Orchestrates database & backend services
│── .env                   # Environment variables (PRIVATE KEYS, API URLs)
│── .gitignore             # Ignore unnecessary files (venv, logs, DB)
