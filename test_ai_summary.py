#!/usr/bin/env python3
"""
Test script for AI Summary Module
Tests all 4 steps: Read DB → Generate Prompt → Call GPT → Return Summary
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_summary import (
    generate_ai_summary,
    get_7day_data_from_db,
    calculate_statistics,
    generate_gpt_prompt,
    call_gpt_api
)


def test_individual_steps():
    """Test each step individually"""
    
    print("\n🧪 Testing Individual Steps")
    print("=" * 80)
    
    symbol = 'GBPUSD=X'
    
    # Step 1: Read from database
    print(f"\n✓ Step 1: Read 7-day data from database")
    print(f"  Symbol: {symbol}")
    data = get_7day_data_from_db(symbol)
    print(f"  Result: {len(data)} data points retrieved")
    if data:
        print(f"  Sample: {data[0]}")
    
    # Step 2: Calculate statistics
    if data and len(data) >= 2:
        print(f"\n✓ Step 2: Calculate statistics")
        prices = [d['price'] for d in data]
        stats = calculate_statistics(prices)
        print(f"  Current Price: ${stats['current_price']:.6f}")
        print(f"  7-Day Range: ${stats['min_price']:.6f} - ${stats['max_price']:.6f}")
        print(f"  Change: {stats['change_pct']:+.2f}%")
        
        # Step 3: Generate prompt
        print(f"\n✓ Step 3: Generate GPT prompt")
        prompt = generate_gpt_prompt(symbol, stats)
        print(f"  Prompt length: {len(prompt)} characters")
        print(f"  Preview: {prompt[:200]}...")
        
        # Step 4: Call GPT
        print(f"\n✓ Step 4: Call OpenAI GPT API")
        summary = call_gpt_api(prompt)
        print(f"  Summary generated: {len(summary)} characters")
        print(f"  Preview: {summary[:150]}...")
    else:
        print(f"\n⚠️ Cannot continue: insufficient data ({len(data)} points)")


def test_complete_workflow():
    """Test the complete workflow"""
    
    print("\n\n🚀 Testing Complete Workflow")
    print("=" * 80)
    
    symbols = ['GBPUSD=X', 'EURUSD=X', 'BTCUSD=X']
    
    for symbol in symbols:
        print(f"\n📊 Generating summary for {symbol}...")
        result = generate_ai_summary(symbol)
        
        if result['success']:
            print(f"\n✅ SUCCESS - {symbol}")
            print(f"Summary:\n{result['summary']}")
            print(f"\nPrice Stats:")
            print(f"  Current: ${result['stats']['current_price']:.6f}")
            print(f"  7-Day Change: {result['stats']['change_pct']:+.2f}%")
        else:
            print(f"\n❌ FAILED - {symbol}")
            print(f"Reason: {result['summary']}")


if __name__ == "__main__":
    print("=" * 80)
    print("AI SUMMARY MODULE - COMPREHENSIVE TEST")
    print("=" * 80)
    
    # Test individual steps
    test_individual_steps()
    
    # Test complete workflow
    test_complete_workflow()
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)
