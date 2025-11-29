import yfinance as yf
import random

# Symbol mapping: internal symbol -> yfinance symbol
SYMBOL_MAP = {
    'GBPUSD': 'GBPUSD=X',
    'EURUSD': 'EURUSD=X',
    'BTCUSD': 'BTC-USD'
}

# Base prices for simulation fallback
BASE_PRICES = {
    'GBPUSD': 1.27,
    'EURUSD': 1.05,
    'BTCUSD': 95000.0
}

def fetch_price(symbol="GBPUSD"):
    """
    Fetch latest price for a symbol.
    
    Args:
        symbol: Internal symbol (GBPUSD, EURUSD, BTCUSD)
    
    Returns:
        float: Latest price, or simulated price if yfinance fails
    """
    # Map to yfinance symbol
    yf_symbol = SYMBOL_MAP.get(symbol, symbol)
    
    try:
        # 下载最近一天，1分钟级别数据
        data = yf.download(yf_symbol, period="1d", interval="1m", progress=False)
        
        if not data.empty:
            # 取最后一条收盘价
            latest_price = data["Close"].iloc[-1]
            return float(latest_price)
    except Exception:
        pass
    
    # Fallback: generate simulated price with random walk
    base = BASE_PRICES.get(symbol, 1.0)
    if symbol == 'BTCUSD':
        variation = random.uniform(-500, 500)
    else:
        variation = random.uniform(-0.002, 0.002) * base
    
    return base + variation

if __name__ == "__main__":
    price = fetch_price("GBPUSD")
    print("Latest GBP/USD:", price)
