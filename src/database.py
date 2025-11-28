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
    conn.close()


def insert_price(record):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO prices (timestamp, symbol, price)
        VALUES (?, ?, ?)
    """, (record["timestamp"], record["symbol"], record["price"]))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("数据库初始化完成！market.db 已创建。")
