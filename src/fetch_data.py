import yfinance as yf

def fetch_price(symbol="GBPUSD=X"):
    # 下载最近一天，1分钟级别数据
    data = yf.download(symbol, period="1d", interval="1m")

    # 取最后一条收盘价
    latest_price = data["Close"].iloc[-1]

    return float(latest_price)

if __name__ == "__main__":
    price = fetch_price()
    print("Latest GBP/USD:", price)
