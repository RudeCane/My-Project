pip install fastapi uvicorn sqlalchemy web3 uniswap-python passlib python-dotenv
uvicorn main:app --reload
# main.py - Single File Uniswap Market Maker Backend
import os
import json
import asyncio
import jwt
import csv
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from dotenv import load_dotenv
from web3 import Web3
from uniswap import Uniswap

# Load Environment Variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./market_maker.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
INFURA_URL = os.getenv("INFURA_URL")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
UNISWAP_V3_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

# Initialize FastAPI
app = FastAPI()

# Database Setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

class TradeHistory(Base):
    __tablename__ = "trade_history"
    id = Column(Integer, primary_key=True, index=True)
    token_in = Column(String)
    token_out = Column(String)
    amount_in = Column(Float)
    amount_out = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=func.now())

class PnL(Base):
    __tablename__ = "pnl"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=func.now(), unique=True)
    daily_pnl = Column(Float, default=0.0)
    weekly_pnl = Column(Float, default=0.0)

Base.metadata.create_all(bind=engine)

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(email: str):
    token_data = {"sub": email}
    return jwt.encode(token_data, SECRET_KEY, algorithm="HS256")

# Dependency to Get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication Routes
@app.post("/auth/register")
def register_user(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(email=email, password_hash=hash_password(password))
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/auth/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": create_access_token(email), "token_type": "bearer"}

# Uniswap Setup
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
uniswap = Uniswap(address=WALLET_ADDRESS, private_key=PRIVATE_KEY, version=3, provider=INFURA_URL)

def get_price(token_in, token_out):
    return uniswap.get_price_input(token_in, token_out, 10**6)

def execute_trade(token_in, token_out, amount):
    return uniswap.make_trade(token_in, token_out, amount)

def provide_liquidity(token_a, token_b, amount_a, amount_b):
    return uniswap.add_liquidity(token_a, token_b, amount_a, amount_b)

# Trading Routes
@app.get("/trade/price")
def fetch_price(token_in: str, token_out: str):
    return {"price": get_price(token_in, token_out)}

@app.post("/trade/trade")
def trade(token_in: str, token_out: str, amount: float):
    tx = execute_trade(token_in, token_out, amount)
    if not tx:
        raise HTTPException(status_code=500, detail="Trade execution failed")
    return {"transaction_hash": tx}

# PnL Tracking
@app.get("/pnl")
def get_pnl(db: Session = Depends(get_db)):
    pnl_entries = db.query(PnL).all()
    return [{"date": entry.date, "daily_pnl": entry.daily_pnl, "weekly_pnl": entry.weekly_pnl} for entry in pnl_entries]

@app.get("/pnl/export")
def export_pnl():
    filename = "pnl_data.csv"
    db = SessionLocal()
    pnl_entries = db.query(PnL).all()
    
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Daily PnL", "Weekly PnL"])
        for entry in pnl_entries:
            writer.writerow([entry.date, entry.daily_pnl, entry.weekly_pnl])
    
    return {"message": "PnL data exported", "file": filename}

# WebSocket for Real-Time Updates
active_connections = set()

async def send_price_updates():
    while True:
        try:
            price = get_price("USDC", "WETH")
            message = json.dumps({"type": "price_update", "price": price})
            await broadcast(message)
        except Exception as e:
            print(f"Error fetching price: {e}")

        await asyncio.sleep(3)

async def broadcast(message: str):
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except:
            active_connections.remove(connection)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
    except:
        active_connections.remove(websocket)

@app.get("/")
def read_root():
    return {"message": "Uniswap Market Maker Backend Running"}

