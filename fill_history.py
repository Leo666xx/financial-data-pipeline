"""
Fill historical K-line data (300 bars, 5-minute interval)
Fetches historical data from yfinance and generates proper OHLC K-lines
"""

import sys
import os
from datetime import datetime, timedelta
import random
import yfinance as yf

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import init_db, insert_price, is_valid_price

# Symbol mapping (same as in api.py)
SYMBOL_MAP = {
    'GBPUSD': 'GBPUSD=X',
    'EURUSD': 'EURUSD=X',
    'BTCUSD': 'BTC-USD'
}

# Base prices for simulation
BASE_PRICES = {
    'GBPUSD': 1.27,
    'EURUSD': 1.05,
    'BTCUSD': 95000.0
}

def generate_simulated_kline_data(symbol, bars, interval_minutes=5):
    """
    Generate simulated K-line data with realistic price movements
    
    Args:
        symbol: Trading symbol
        bars: Number of K-line bars
        interval_minutes: Interval in minutes (default: 5)
    
    Returns:
        List of (timestamp, price) tuples
    """
    base_price = BASE_PRICES.get(symbol, 1.0)
    
    # Generate timestamps (going backwards from now)
    now = datetime.now()
    timestamps = []
    for i in range(bars):
        ts = now - timedelta(minutes=interval_minutes * (bars - i))
        timestamps.append(ts)
    
    # Generate realistic price movements
    prices = []
    current_price = base_price
    
    for i in range(bars):
        # Random walk with drift
        if symbol == 'BTCUSD':
            # Bitcoin: larger volatility
            change_pct = random.uniform(-0.01, 0.01)  # ±1%
        else:
            # Forex: smaller volatility
            change_pct = random.uniform(-0.002, 0.002)  # ±0.2%
        
        current_price = current_price * (1 + change_pct)
        
        # Add some trend
        if i % 50 < 25:  # Uptrend for first half
            current_price *= 1.0001
        else:  # Downtrend for second half
            current_price *= 0.9999
        
        prices.append((timestamps[i], current_price))
    
    return prices

def fetch_and_fill_history(symbol='GBPUSD', bars=300, interval='5m', use_simulated=False):
    """
    Fetch historical data and fill database with K-line close prices
    
    Args:
        symbol: Trading symbol (GBPUSD, EURUSD, BTCUSD)
        bars: Number of K-line bars to fetch (default: 300)
        interval: Time interval (default: 5m)
    """
    print(f"========================================")
    print(f"  Fill Historical K-line Data")
    print(f"========================================")
    print(f"Symbol: {symbol}")
    print(f"Bars: {bars}")
    print(f"Interval: {interval}")
    print()
    
    # Initialize database
    init_db()
    
    data_points = []
    
    if use_simulated:
        # Use simulated data
        print(f"[1/3] Generating simulated data...")
        interval_minutes = int(interval.replace('m', '').replace('h', '60' if 'h' in interval else ''))
        data_points = generate_simulated_kline_data(symbol, bars, interval_minutes)
        print(f"[OK] Generated {len(data_points)} simulated K-line bars")
        print(f"  -> Date range: {data_points[0][0]} to {data_points[-1][0]}")
        print()
        
    else:
        # Try to fetch from yfinance
        yf_symbol = SYMBOL_MAP.get(symbol, symbol)
        print(f"[1/3] Fetching data from yfinance ({yf_symbol})...")
        
        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period='7d', interval=interval)
            
            if df.empty:
                print(f"[WARN] No data from yfinance, switching to simulated data...")
                use_simulated = True
            else:
                print(f"[OK] Fetched {len(df)} data points from yfinance")
                print(f"  -> Date range: {df.index[0]} to {df.index[-1]}")
                
                # Convert to list of tuples
                for timestamp, row in df.iterrows():
                    data_points.append((timestamp, float(row['Close'])))
                
                # Take last N bars
                if len(data_points) > bars:
                    data_points = data_points[-bars:]
                
                print()
                
        except Exception as e:
            print(f"[WARN] yfinance error: {e}")
            print(f"[INFO] Switching to simulated data...")
            use_simulated = True
        
        # Fallback to simulated data
        if use_simulated and not data_points:
            interval_minutes = int(interval.replace('m', '').replace('h', '60' if 'h' in interval else ''))
            data_points = generate_simulated_kline_data(symbol, bars, interval_minutes)
            print(f"[OK] Generated {len(data_points)} simulated K-line bars")
            print(f"  -> Date range: {data_points[0][0]} to {data_points[-1][0]}")
            print()
    
    print(f"[2/3] Using {len(data_points)} bars...")
    print()
    
    # Insert into database
    print(f"[3/3] Inserting into database...")
    inserted = 0
    skipped = 0
    
    for timestamp, price in data_points:
        # Validate price
        if not is_valid_price(price, symbol):
            skipped += 1
            continue
        
        # Convert timestamp to ISO format
        if hasattr(timestamp, 'isoformat'):
            ts_str = timestamp.isoformat()
        else:
            ts_str = timestamp
        
        # Insert into database
        record = {
            'timestamp': ts_str,
            'symbol': symbol,
            'price': price
        }
        
        try:
            insert_price(record)
            inserted += 1
            
            # Progress indicator
            if inserted % 50 == 0:
                print(f"  -> Inserted {inserted}/{len(data_points)} records...")
                
        except Exception as e:
            skipped += 1
            continue
    
    print()
    print(f"========================================")
    print(f"  ✓ Historical Data Filled")
    print(f"========================================")
    print(f"Inserted: {inserted} records")
    print(f"Skipped:  {skipped} records (invalid/duplicate)")
    print(f"Symbol:   {symbol}")
    print()
    
    return inserted


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fill historical K-line data')
    parser.add_argument('--symbol', default='GBPUSD', 
                       choices=['GBPUSD', 'EURUSD', 'BTCUSD'],
                       help='Symbol to fill (default: GBPUSD)')
    parser.add_argument('--bars', type=int, default=300,
                       help='Number of K-line bars (default: 300)')
    parser.add_argument('--interval', default='5m',
                       choices=['1m', '5m', '15m', '30m', '1h'],
                       help='K-line interval (default: 5m)')
    parser.add_argument('--simulated', action='store_true',
                       help='Use simulated data (bypass yfinance)')
    
    args = parser.parse_args()
    
    # Fill data for specified symbol
    inserted = fetch_and_fill_history(
        symbol=args.symbol,
        bars=args.bars,
        interval=args.interval,
        use_simulated=args.simulated
    )
    
    if inserted > 0:
        print(f"Success! You can now view the chart in Dashboard:")
        print(f"  http://localhost:8050")
        print()
        print(f"To fill other symbols, run:")
        print(f"  python fill_history.py --symbol EURUSD")
        print(f"  python fill_history.py --symbol BTCUSD")
    else:
        print(f"[WARN] No data inserted. Please check yfinance connection.")
    
    print()


if __name__ == '__main__':
    main()
