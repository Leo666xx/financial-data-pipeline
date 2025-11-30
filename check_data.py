import sqlite3

conn = sqlite3.connect('data/market.db')
cursor = conn.cursor()
cursor.execute('SELECT symbol, COUNT(*) FROM prices GROUP BY symbol')
rows = cursor.fetchall()

print('Database Summary:')
print('='*40)
for row in rows:
    print(f'  {row[0]}: {row[1]} records')
conn.close()
