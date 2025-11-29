"""
5-Minute K-Line (Candlestick) Generator
==========================================
Collects tick data and generates proper OHLC (Open, High, Low, Close) candlesticks.

Workflow:
1. Continuously fetch tick prices (every few seconds)
2. Accumulate ticks within 5-minute intervals
3. At interval end, generate OHLC from accumulated ticks
4. Validate and save to database
"""

import time
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import signal
import sys

# Import existing modules
from fetch_data import fetch_price
from database import init_db, is_valid_price

DB_PATH = "data/market.db"

# Global state
running = True
tick_buffer = defaultdict(list)  # {symbol: [(timestamp, price), ...]}


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global running
    print("\n\n⏹️  Stopping K-line generator...")
    running = False


def get_5min_bucket(dt):
    """
    Get the 5-minute bucket start time for a given datetime.
    Example: 14:32:47 -> 14:30:00
    """
    minutes = (dt.minute // 5) * 5
    return dt.replace(minute=minutes, second=0, microsecond=0)


def generate_kline_from_ticks(ticks):
    """
    Generate OHLC candlestick from tick data.
    
    Args:
        ticks: List of (timestamp, price) tuples
    
    Returns:
        dict with 'open', 'high', 'low', 'close', 'timestamp'
    """
    if not ticks:
        return None
    
    # Sort by timestamp
    ticks.sort(key=lambda x: x[0])
    
    prices = [p for _, p in ticks]
    
    return {
        'open': prices[0],      # First tick
        'high': max(prices),    # Highest tick
        'low': min(prices),     # Lowest tick
        'close': prices[-1],    # Last tick
        'timestamp': ticks[-1][0]  # Use last tick's timestamp
    }


def insert_kline(symbol, kline):
    """
    Insert a K-line (candlestick) into database.
    Stores as a single close price for now (can expand to OHLC table later).
    """
    # Validate the close price
    if not is_valid_price(kline['close'], symbol):
        print(f"⚠️  Invalid K-line close price: {kline['close']} for {symbol}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # For now, store as regular price (close)
    # TODO: Create separate OHLC table for full candlestick data
    c.execute("""
        INSERT INTO prices (timestamp, symbol, price)
        VALUES (?, ?, ?)
    """, (kline['timestamp'], symbol, kline['close']))
    
    conn.commit()
    conn.close()
    
    print(f"✓ K-line saved: {symbol} @ {kline['timestamp'][:19]} | "
          f"O:{kline['open']:.6f} H:{kline['high']:.6f} "
          f"L:{kline['low']:.6f} C:{kline['close']:.6f}")
    
    return True


def collect_and_generate_klines(symbols=['GBPUSD', 'EURUSD', 'BTCUSD'], 
                                  tick_interval=5, 
                                  kline_interval=300):
    """
    Main loop: collect ticks and generate K-lines.
    
    Args:
        symbols: List of symbols to track
        tick_interval: Seconds between tick fetches (default 5)
        kline_interval: Seconds per K-line (default 300 = 5 minutes)
    """
    global running, tick_buffer
    
    init_db()
    print(f"\n🚀 Starting K-line generator...")
    print(f"📊 Symbols: {', '.join(symbols)}")
    print(f"⏱️  Tick interval: {tick_interval}s")
    print(f"📈 K-line interval: {kline_interval}s ({kline_interval//60}min)")
    print(f"\nPress Ctrl+C to stop.\n")
    
    last_bucket = {}  # Track last processed bucket per symbol
    
    while running:
        now = datetime.utcnow()
        current_bucket = get_5min_bucket(now)
        
        # Fetch ticks for all symbols
        for symbol in symbols:
            try:
                # Fetch current price (tick)
                price = fetch_price(symbol)
                
                # Validate before adding to buffer
                if is_valid_price(price, symbol):
                    timestamp = now.isoformat()
                    tick_buffer[symbol].append((timestamp, price))
                    print(f"📍 Tick: {symbol} = {price:.6f} @ {timestamp[:19]}")
                else:
                    print(f"⚠️  Filtered invalid tick: {symbol} = {price}")
                
            except Exception as e:
                print(f"❌ Error fetching {symbol}: {e}")
        
        # Check if we need to close K-lines for any symbol
        for symbol in symbols:
            if symbol not in last_bucket:
                last_bucket[symbol] = current_bucket
                continue
            
            # If bucket has changed, generate K-line for previous bucket
            if current_bucket > last_bucket[symbol]:
                ticks = tick_buffer[symbol]
                
                if ticks:
                    kline = generate_kline_from_ticks(ticks)
                    if kline:
                        insert_kline(symbol, kline)
                    
                    # Clear buffer for this symbol
                    tick_buffer[symbol] = []
                
                last_bucket[symbol] = current_bucket
        
        # Wait before next tick
        time.sleep(tick_interval)
    
    print("\n✓ K-line generator stopped.")


if __name__ == "__main__":
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='5-Minute K-Line Generator')
    parser.add_argument('--symbols', nargs='+', default=['GBPUSD=X', 'EURUSD=X', 'BTCUSD=X'],
                        help='Symbols to track (default: GBPUSD=X EURUSD=X BTCUSD=X)')
    parser.add_argument('--tick-interval', type=int, default=5,
                        help='Seconds between ticks (default: 5)')
    parser.add_argument('--kline-interval', type=int, default=300,
                        help='Seconds per K-line (default: 300 = 5min)')
    
    args = parser.parse_args()
    
    # Start the K-line generator
    collect_and_generate_klines(
        symbols=args.symbols,
        tick_interval=args.tick_interval,
        kline_interval=args.kline_interval
    )
