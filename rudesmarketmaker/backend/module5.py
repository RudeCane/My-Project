backend/
├── main.py
├── config.py
├── database.py
├── models.py
├── auth.py
├── uniswap_handler.py
├── websocket_handler.py
├── requirements.txt
├── Dockerfile
├── .env
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install fastapi uvicorn sqlalchemy web3 uniswap-python passlib python-dotenv
backend/main.py
from fastapi import FastAPI
from auth import router as auth_router
from database import Base, engine
import asyncio
from websocket_handler import send_price_updates

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include Authentication Routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(send_price_updates())

@app.get("/")
def read_root():
    return {"message": "Uniswap Market Maker Backend Running"}

