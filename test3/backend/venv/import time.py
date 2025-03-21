import time
import logging
from web3 import Web3
from uniswap import Uniswap

# Configure logging
logging.basicConfig(filename="arbitrage_bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Setup Uniswap (Ethereum)
INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_API_KEY"
web3_eth = Web3(Web3.HTTPProvider(INFURA_URL))
uniswap = Uniswap(address="0x2515498760d859260e81d2480c1abf9e07330ff4", private_key="a802848e3930fe3fa9f2047eafc7d73e7a9f033552b443698ba0aba1b411ad96", version=3)

# Setup PancakeSwap (BSC)
BSC_RPC = "https://bsc-dataseed.binance.org/"
web3_bsc = Web3(Web3.HTTPProvider(BSC_RPC))
PANCAKE_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"  # PancakeSwap V2 Router
PANCAKE_ROUTER_ABI = '[...]'  # Fetch from BSCScan
pancake_router = web3_bsc.eth.contract(address=PANCAKE_ROUTER_ADDRESS, abi=PANCAKE_ROUTER_ABI)

# Tokens
TOKEN_A_ETH = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606e48c"  # USDC (Ethereum)
TOKEN_B_ETH = "0xC02aaa39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH (Ethereum)
TOKEN_A_BSC = "0xe9e7cea3dedca5984780bafc599bd69add087d56"  # BUSD (BSC)
TOKEN_B_BSC = "0xbb4CdB9Cbd36B01bD1cBaEBF2De08d9173bc095c"  # WBNB (BSC)

TRADE_AMOUNT = 10  # Example amount

# Function to get Uniswap price
def get_uniswap_price(token_in, token_out, amount):
    try:
        return uniswap.get_price_input(token_in, token_out, amount)
    except Exception as e:
        logging.error(f"Uniswap price fetch error: {e}")
        return None

# Function to get PancakeSwap price
def get_pancake_price(token_in, token_out, amount):
    try:
        price = pancake_router.functions.getAmountsOut(web3_bsc.to_wei(amount, 'ether'), [token_in, token_out]).call()
        return price[-1] / 1e18  # Convert to readable value
    except Exception as e:
        logging.error(f"PancakeSwap price fetch error: {e}")
        return None

# Function to execute Uniswap trade
def trade_uniswap(token_in, token_out, amount):
    try:
        tx = uniswap.make_trade(token_in, token_out, amount)
        logging.info(f"Executed Uniswap trade: {tx}")
        return tx
    except Exception as e:
        logging.error(f"Uniswap trade failed: {e}")

# Function to execute PancakeSwap trade
def trade_pancake(token_in, token_out, amount, private_key, wallet_address):
    try:
        nonce = web3_bsc.eth.get_transaction_count(wallet_address)
        tx = pancake_router.functions.swapExactTokensForTokens(
            web3_bsc.to_wei(amount, 'ether'), 0, [token_in, token_out], wallet_address, int(time.time()) + 60
        ).build_transaction({
            'from': wallet_address,
            'gas': 250000,
            'gasPrice': web3_bsc.to_wei('5', 'gwei'),
            'nonce': nonce
        })

        signed_tx = web3_bsc.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3_bsc.eth.send_raw_transaction(signed_tx.rawTransaction)
        logging.info(f"Executed PancakeSwap trade: {web3_bsc.to_hex(tx_hash)}")
        return web3_bsc.to_hex(tx_hash)
    except Exception as e:
        logging.error(f"PancakeSwap trade failed: {e}")

# Arbitrage detection loop
while True:
    try:
        # Get prices on both chains
        uniswap_price = get_uniswap_price(TOKEN_A_ETH, TOKEN_B_ETH, TRADE_AMOUNT)
        pancake_price = get_pancake_price(TOKEN_A_BSC, TOKEN_B_BSC, TRADE_AMOUNT)

        if uniswap_price and pancake_price:
            spread = (pancake_price - uniswap_price) / uniswap_price * 100

            if spread > 1:  # Adjust threshold based on gas costs
                logging.info(f"Arbitrage found! Spread: {spread:.2f}%")
                
                # Buy on Uniswap, Sell on PancakeSwap
                trade_uniswap(TOKEN_A_ETH, TOKEN_B_ETH, TRADE_AMOUNT)
                trade_pancake(TOKEN_A_BSC, TOKEN_B_BSC, TRADE_AMOUNT, "YOUR_PRIVATE_KEY", "YOUR_WALLET_ADDRESS")

    except Exception as e:
        logging.error(f"Error in arbitrage loop: {e}")

    time.sleep(10)
