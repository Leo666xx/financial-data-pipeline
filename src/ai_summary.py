"""
AI Summary Module
————————————————————————
Generate market analysis summaries using OpenAI GPT API.
Reads 7-day data from database and returns English market summary.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "market.db")


def get_7day_data_from_db(symbol: str) -> list:
    """
    Read 7-day price data from SQLite database.
    
    Args:
        symbol: Trading symbol (e.g., 'GBPUSD=X')
    
    Returns:
        List of dicts with 'timestamp', 'symbol', 'price' keys
    """
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return []
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Calculate 7 days ago timestamp
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        # Query: Get all prices for symbol from last 7 days
        query = """
        SELECT timestamp, symbol, price 
        FROM prices 
        WHERE symbol = ? AND timestamp >= ?
        ORDER BY timestamp ASC
        """
        
        cursor.execute(query, (symbol, seven_days_ago))
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        data = [
            {
                'timestamp': row['timestamp'],
                'symbol': row['symbol'],
                'price': float(row['price'])
            }
            for row in rows
        ]
        
        print(f"✓ Retrieved {len(data)} data points for {symbol} from last 7 days")
        return data
    
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []


def calculate_statistics(prices: list) -> dict:
    """
    Calculate price statistics from 7-day data.
    
    Args:
        prices: List of price values
    
    Returns:
        Dict with statistics
    """
    if not prices or len(prices) < 2:
        return {}
    
    current = prices[-1]
    previous = prices[0]
    price_change = current - previous
    change_pct = (price_change / previous * 100) if previous != 0 else 0
    
    return {
        'current_price': current,
        'previous_price': previous,
        'min_price': min(prices),
        'max_price': max(prices),
        'price_change': price_change,
        'change_pct': change_pct,
        'data_points': len(prices)
    }


def generate_gpt_prompt(symbol: str, stats: dict) -> str:
    """
    Generate a detailed prompt for GPT analysis.
    
    Args:
        symbol: Trading symbol
        stats: Statistics dict from calculate_statistics()
    
    Returns:
        Formatted prompt string
    """
    
    data_summary = f"""
Symbol: {symbol}
Current Price: ${stats['current_price']:.6f}
7-Day Change: {stats['price_change']:+.6f} ({stats['change_pct']:+.2f}%)
7-Day High: ${stats['max_price']:.6f}
7-Day Low: ${stats['min_price']:.6f}
Data Points: {stats['data_points']}
"""
    
    prompt = f"""You are a professional financial analyst. Based on the following 7-day trading data, 
generate a brief market analysis summary in English (120-150 words).

{data_summary}

Please analyze:
1. Price trend (uptrend/downtrend/consolidation)
2. Support and resistance levels
3. Market volatility assessment
4. Key market signals
5. Brief trading outlook

Format: Provide a concise analysis without numbering or bullet points. Write as a professional market summary."""
    
    return prompt


def call_gpt_api(prompt: str) -> str:
    """
    Call OpenAI GPT API to generate market analysis.
    
    Args:
        prompt: Analysis prompt
    
    Returns:
        Generated summary or error message
    """
    if not client or not OPENAI_API_KEY:
        return "❌ OpenAI API not configured. Please set OPENAI_API_KEY environment variable."
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert financial market analyst with deep knowledge of forex, crypto, and commodity markets."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=250,
            timeout=10.0
        )
        
        summary = response.choices[0].message.content.strip()
        print(f"✓ GPT API call successful ({len(summary)} characters)")
        return summary
    
    except Exception as e:
        error_msg = f"❌ GPT API error: {str(e)}"
        print(error_msg)
        return error_msg


def generate_ai_summary(symbol: str) -> dict:
    """
    Complete workflow: Read 7-day data → Generate prompt → Call GPT → Return English summary.
    
    Args:
        symbol: Trading symbol (e.g., 'GBPUSD=X')
    
    Returns:
        Dict with 'success', 'summary', 'stats', 'timestamp' keys
    """
    
    print(f"\n📊 Starting AI Summary generation for {symbol}...")
    print("=" * 60)
    
    # Step 1: Read 7-day data from database
    print("Step 1️⃣ : Reading 7-day data from database...")
    data = get_7day_data_from_db(symbol)
    
    if not data or len(data) < 2:
        return {
            'success': False,
            'summary': f'⚠️ Insufficient data: {len(data)} points (need at least 2)',
            'stats': {},
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # Step 2: Calculate statistics
    print("Step 2️⃣ : Calculating price statistics...")
    prices = [d['price'] for d in data]
    stats = calculate_statistics(prices)
    print(f"   Current: ${stats['current_price']:.6f}")
    print(f"   Range: ${stats['min_price']:.6f} - ${stats['max_price']:.6f}")
    print(f"   Change: {stats['change_pct']:+.2f}%")
    
    # Step 3: Generate GPT prompt
    print("Step 3️⃣ : Generating GPT prompt...")
    prompt = generate_gpt_prompt(symbol, stats)
    print(f"   Prompt length: {len(prompt)} characters")
    
    # Step 4: Call GPT API
    print("Step 4️⃣ : Calling OpenAI GPT API...")
    summary = call_gpt_api(prompt)
    
    # Step 5: Return result
    result = {
        'success': not summary.startswith('❌'),
        'summary': summary,
        'stats': stats,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    print("=" * 60)
    print("✅ AI Summary generation complete!\n")
    
    return result


# Example usage and testing
if __name__ == "__main__":
    # Test the module
    print("Testing AI Summary Module")
    print("=" * 60)
    
    # Ensure API key is set
    if not OPENAI_API_KEY:
        print("⚠️ OPENAI_API_KEY not set. Please configure it first.")
        print("   Run: setx OPENAI_API_KEY 'your-key-here'")
        exit(1)
    
    # Generate summaries for different symbols
    symbols = ['GBPUSD=X', 'EURUSD=X', 'BTCUSD=X']
    
    for symbol in symbols:
        result = generate_ai_summary(symbol)
        
        if result['success']:
            print(f"\n📈 Market Summary for {symbol}")
            print("-" * 60)
            print(result['summary'])
            print("-" * 60)
            print(f"Stats: {result['stats']}")
        else:
            print(f"\n⚠️ Could not generate summary for {symbol}")
            print(f"   Reason: {result['summary']}")
        
        print()
