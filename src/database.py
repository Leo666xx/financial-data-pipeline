import sqlite3

DB_PATH = "data/market.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            timestamp TEXT,
            symbol TEXT,
            price REAL
        );
    """)

    conn.commit()
    
    # Create index for faster queries on symbol and timestamp
    try:
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_prices_symbol_ts 
            ON prices(symbol, timestamp)
        """)
        conn.commit()
    except Exception as e:
        print(f"Index creation skipped or already exists: {e}")
    
    conn.close()


def is_valid_price(price, symbol):
    """
    Validate price to filter out anomalies.
    
    Args:
        price: Price value to validate
        symbol: Trading symbol (for symbol-specific validation)
    
    Returns:
        bool: True if price is valid, False otherwise
    """
    if price is None:
        return False
    
    try:
        price = float(price)
    except (ValueError, TypeError):
        return False
    
    # Filter out clearly invalid prices
    if price <= 0:
        return False
    
    # Symbol-specific validation
    if 'GBPUSD' in symbol or 'EURUSD' in symbol:
        # Forex pairs should be in reasonable range (0.5 - 3.0)
        if price < 0.5 or price > 3.0:
            return False
    elif 'BTCUSD' in symbol or 'BTC' in symbol:
        # BTC should be reasonable (1000 - 1000000)
        if price < 1000 or price > 1000000:
            return False
    
    return True


def insert_price(record):
    """
    Insert price record into database with validation.
    Filters out anomalies before insertion.
    """
    # Validate price before insertion
    if not is_valid_price(record.get("price"), record.get("symbol", "")):
        print(f"⚠️  Filtered out invalid price: {record.get('price')} for {record.get('symbol')}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO prices (timestamp, symbol, price)
        VALUES (?, ?, ?)
    """, (record["timestamp"], record["symbol"], record["price"]))

    conn.commit()
    conn.close()
    return True


def clear_all_prices():
    """Clear all price data from database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM prices")
    conn.commit()
    count = c.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
    conn.close()
    print(f"✓ Cleared all price data. Remaining records: {count}")


def remove_invalid_prices():
    """Remove invalid/anomaly prices from database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get all records
    c.execute("SELECT rowid, timestamp, symbol, price FROM prices")
    rows = c.fetchall()
    
    removed_count = 0
    for rowid, timestamp, symbol, price in rows:
        if not is_valid_price(price, symbol):
            c.execute("DELETE FROM prices WHERE rowid = ?", (rowid,))
            removed_count += 1
            print(f"Removed invalid: {symbol} @ {timestamp} = {price}")
    
    conn.commit()
    conn.close()
    print(f"✓ Removed {removed_count} invalid price records")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "clear":
            print("Clearing all price data...")
            clear_all_prices()
        elif sys.argv[1] == "clean":
            print("Removing invalid prices...")
            remove_invalid_prices()
    else:
        init_db()
        print("数据库初始化完成！market.db 已创建。")
