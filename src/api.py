from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# ---------------------
# 1. 得到 api.py 的绝对路径
# ---------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------
# 2. 拼接数据库的真实路径
#    ../data/market.db
# ---------------------
DB_PATH = os.path.join(BASE_DIR, "..", "data", "market.db")
DB_PATH = os.path.abspath(DB_PATH)

print(">>> DB PATH =", DB_PATH)    # 调试用：看到 Flask 真的会找这个文件

# ---------------------
# 3. API 路由
# ---------------------
@app.get("/")
def hello():
    return jsonify({"message": "Hello — Flask API is running!", "status": "ok"})

@app.get("/price")
def get_price():
    # 获取 symbol 参数，并且去除空格
    symbol = request.args.get("symbol", "GBPUSD")
    symbol = symbol.strip()   # ← 关键步骤
    print(">>> symbol from request =", repr(symbol))  # 调试
    print(">>> API 收到的 symbol =", symbol)
    
    # 如果用户输入的是 GBPUSD，则映射到数据库中的 GBPUSD=X
    db_symbol = symbol
    if symbol == "GBPUSD":
        db_symbol = "GBPUSD=X"
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 查询最新的价格记录
    c.execute(
        "SELECT timestamp, price FROM prices WHERE symbol=? ORDER BY timestamp DESC LIMIT 1",
        (db_symbol,)
    )
    row = c.fetchone()
    conn.close()

    # 数据存在 → 返回 JSON
    if row:
        return jsonify({
            "symbol": symbol,
            "timestamp": row[0],
            "price": row[1]
        })

    # 数据不存在 → 返回错误
    return jsonify({"error": "No data found"})


# ---------------------
# 4. 启动 Flask
# ---------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
