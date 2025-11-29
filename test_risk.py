"""
风险分析测试工具
================
演示风险引擎的各项功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from risk_engine import RiskEngine, analyze_risk
import numpy as np
import sqlite3


def test_with_database_data(symbol='GBPUSD', limit=300):
    """使用数据库中的真实数据测试风险引擎"""
    print("=" * 70)
    print(f"📊 风险分析报告 - {symbol}")
    print("=" * 70)
    
    # 连接数据库
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'market.db')
    if not os.path.exists(db_path):
        print("❌ 数据库不存在，请先填充历史数据")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询历史数据
    cursor.execute(
        "SELECT timestamp, price FROM prices WHERE symbol=? ORDER BY timestamp DESC LIMIT ?",
        (symbol, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"❌ 未找到 {symbol} 的数据")
        return
    
    # 反转为时间正序
    rows = list(reversed(rows))
    prices = [float(row[1]) for row in rows]
    
    print(f"\n数据概况:")
    print(f"  时间范围: {rows[0][0]} 至 {rows[-1][0]}")
    print(f"  数据点数: {len(prices)}")
    print(f"  价格范围: {min(prices):.6f} - {max(prices):.6f}")
    
    # 运行风险分析
    engine = RiskEngine(
        volatility_window=20,
        anomaly_threshold=2.5,
        high_volatility_threshold=0.015
    )
    
    report = engine.get_risk_report(prices)
    
    if report['status'] != 'OK':
        print(f"\n⚠️ {report['message']}")
        return
    
    # 打印详细报告
    summary = report['summary']
    volatility = report['volatility']
    anomalies = report['anomalies']
    signals = report['signals']
    
    print("\n" + "=" * 70)
    print("📋 风险摘要")
    print("=" * 70)
    
    risk_level_emoji = {
        'MINIMAL': '🟢',
        'LOW': '🟡',
        'MEDIUM': '🟠',
        'HIGH': '🔴',
        'CRITICAL': '🚨'
    }
    
    risk_level_zh = {
        'MINIMAL': '极低',
        'LOW': '低',
        'MEDIUM': '中',
        'HIGH': '高',
        'CRITICAL': '严重'
    }
    
    risk_level = summary['risk_level']
    emoji = risk_level_emoji.get(risk_level, '⚪')
    level_zh = risk_level_zh.get(risk_level, risk_level)
    
    print(f"\n{emoji} 风险等级: {level_zh} ({risk_level})")
    print(f"📊 风险评分: {summary['risk_score']}/100")
    print(f"💰 当前价格: {summary['current_price']:.6f}")
    print(f"📈 价格变化: {summary['price_change_pct']:+.2f}%")
    
    print("\n" + "=" * 70)
    print("📊 波动率分析")
    print("=" * 70)
    print(f"\n当前波动率: {volatility['current_volatility']:.6f}")
    print(f"平均波动率: {volatility['avg_volatility']:.6f}")
    print(f"波动率百分位: {volatility['volatility_percentile']:.1f}%")
    print(f"状态: {'⚠️  高波动率' if volatility['is_high_volatility'] else '✅ 正常波动'}")
    
    # 波动率趋势图（简单文本版）
    print("\n波动率趋势:")
    percentile = volatility['volatility_percentile']
    bar_length = int(percentile / 2)  # 0-50个字符
    bar = '█' * bar_length + '░' * (50 - bar_length)
    print(f"  0% {bar} 100%")
    print(f"      {'↑' * (bar_length // 2) if bar_length > 25 else ' ' * (25 - bar_length // 2) + '↑'}")
    
    print("\n" + "=" * 70)
    print("🔍 异常检测")
    print("=" * 70)
    print(f"\n检测到异常: {'是 🚨' if anomalies['detected'] else '否 ✅'}")
    print(f"异常点数量: {anomalies['count']}")
    print(f"最新Z-score: {anomalies['latest_z_score']:.2f}")
    
    z_score = anomalies['latest_z_score']
    if abs(z_score) > 3.0:
        z_status = "🔴 极端异常"
    elif abs(z_score) > 2.5:
        z_status = "🟠 显著异常"
    elif abs(z_score) > 2.0:
        z_status = "🟡 轻微异常"
    else:
        z_status = "🟢 正常范围"
    print(f"Z-score状态: {z_status}")
    
    print("\n" + "=" * 70)
    print(f"⚠️  风险信号 ({len(signals)} 个)")
    print("=" * 70)
    
    if signals:
        for i, signal in enumerate(signals, 1):
            severity_emoji = {
                'CRITICAL': '🔴',
                'WARNING': '🟡',
                'INFO': '🔵'
            }
            print(f"\n{severity_emoji.get(signal['severity'], '⚪')} 信号 {i}: [{signal['severity']}] {signal['type']}")
            print(f"   描述: {signal['message']}")
            print(f"   💡 建议: {signal['recommendation']}")
    else:
        print("\n✅ 无风险信号，市场状况良好")
    
    print("\n" + "=" * 70)
    print("📋 风险因素汇总")
    print("=" * 70)
    
    if report['risk_factors']:
        for factor in report['risk_factors']:
            print(f"  • {factor}")
    else:
        print("  ✅ 未发现显著风险因素")
    
    print("\n" + "=" * 70)
    print("💡 综合建议")
    print("=" * 70)
    
    if summary['risk_score'] >= 70:
        print("\n🚨 风险严重，建议立即采取行动：")
        print("  1. 立即减少或平仓现有头寸")
        print("  2. 暂停新开仓，等待市场稳定")
        print("  3. 设置严格的止损和止盈")
        print("  4. 密切监控市场动态")
    elif summary['risk_score'] >= 50:
        print("\n⚠️  风险较高，建议谨慎操作：")
        print("  1. 减少仓位至正常水平的50%")
        print("  2. 收紧止损设置")
        print("  3. 避免逆势操作")
        print("  4. 增加监控频率")
    elif summary['risk_score'] >= 30:
        print("\n🟡 风险中等，建议注意以下事项：")
        print("  1. 保持正常仓位")
        print("  2. 设置合理的止损")
        print("  3. 关注市场变化")
        print("  4. 做好风险预案")
    else:
        print("\n✅ 风险较低，可正常交易：")
        print("  1. 可以按计划执行交易策略")
        print("  2. 保持常规风险管理")
        print("  3. 持续监控市场状况")
    
    print("\n" + "=" * 70)
    print(f"⏰ 报告生成时间: {report['timestamp']}")
    print("=" * 70 + "\n")


def compare_symbols():
    """比较多个交易品种的风险"""
    symbols = ['GBPUSD', 'EURUSD', 'BTCUSD']
    
    print("\n" + "=" * 70)
    print("📊 多品种风险对比")
    print("=" * 70 + "\n")
    
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'market.db')
    if not os.path.exists(db_path):
        print("❌ 数据库不存在")
        return
    
    results = []
    
    for symbol in symbols:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT price FROM prices WHERE symbol=? ORDER BY timestamp DESC LIMIT 100",
            (symbol,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            continue
        
        prices = [float(row[0]) for row in reversed(rows)]
        report = analyze_risk(prices, symbol)
        
        if report['status'] == 'OK':
            results.append({
                'symbol': symbol,
                'risk_level': report['summary']['risk_level'],
                'risk_score': report['summary']['risk_score'],
                'volatility': report['volatility']['current_volatility'],
                'anomalies': report['anomalies']['count']
            })
    
    if not results:
        print("❌ 没有可用数据")
        return
    
    # 排序（风险评分从高到低）
    results.sort(key=lambda x: x['risk_score'], reverse=True)
    
    print(f"{'品种':<10} {'风险等级':<12} {'评分':<8} {'波动率':<12} {'异常点'}")
    print("-" * 70)
    
    for r in results:
        risk_emoji = {
            'MINIMAL': '🟢', 'LOW': '🟡', 'MEDIUM': '🟠',
            'HIGH': '🔴', 'CRITICAL': '🚨'
        }
        emoji = risk_emoji.get(r['risk_level'], '⚪')
        
        print(f"{r['symbol']:<10} {emoji} {r['risk_level']:<10} "
              f"{r['risk_score']:<8} {r['volatility']:<12.6f} {r['anomalies']}")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='风险分析测试工具')
    parser.add_argument('--symbol', default='GBPUSD', choices=['GBPUSD', 'EURUSD', 'BTCUSD'],
                       help='交易品种')
    parser.add_argument('--compare', action='store_true',
                       help='对比多个品种的风险')
    parser.add_argument('--limit', type=int, default=300,
                       help='数据点数量')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_symbols()
    else:
        test_with_database_data(args.symbol, args.limit)
