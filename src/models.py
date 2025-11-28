from datetime import datetime

def build_price_record(symbol, price):
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "price": price
    }

if __name__ == "__main__":
    r = build_price_record("GBPUSD", 1.2663)
    print(r)
