from fetch_data import fetch_price
from models import build_price_record
from database import init_db, insert_price

def ingest_once(symbol="GBPUSD=X"):
    init_db()
    price = fetch_price(symbol)
    record = build_price_record(symbol, price)
    insert_price(record)
    print("Inserted:", record)

if __name__ == "__main__":
    ingest_once()
