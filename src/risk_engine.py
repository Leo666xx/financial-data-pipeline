"""
Risk Engine - 风险引擎
======================
实时监控市场风险，提供异常检测和风险信号

功能：
1. 滚动标准差（Rolling Std）异常检测
2. 波动率分析（Volatility Analysis）
3. 风险等级评估（Risk Level Assessment）
4. 异常价格检测（Anomaly Detection）
5. 风险信号生成（Risk Signal Generation）
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional


class RiskEngine:
    """
    风险引擎：监控市场异常和风险信号
    """
    
    def __init__(self, 
                 volatility_window: int = 20,
                 anomaly_threshold: float = 2.5,
                 high_volatility_threshold: float = 0.02):
        """
        初始化风险引擎
        
        Args:
            volatility_window: 波动率计算窗口（默认20个周期）
            anomaly_threshold: 异常检测阈值（标准差倍数，默认2.5）
            high_volatility_threshold: 高波动率阈值（默认2%）
        """
        self.volatility_window = volatility_window
        self.anomaly_threshold = anomaly_threshold
        self.high_volatility_threshold = high_volatility_threshold
    
    def calculate_returns(self, prices: List[float]) -> np.ndarray:
        """
        计算收益率序列
        
        Args:
            prices: 价格列表
            
        Returns:
            收益率数组
        """
        if len(prices) < 2:
            return np.array([])
        
        prices_array = np.array(prices)
        returns = np.diff(prices_array) / prices_array[:-1]
        return returns
    
    def calculate_rolling_std(self, prices: List[float], window: int = None) -> np.ndarray:
        """
        计算滚动标准差
        
        Args:
            prices: 价格列表
            window: 滚动窗口大小（默认使用初始化时的窗口）
            
        Returns:
            滚动标准差数组
        """
        if window is None:
            window = self.volatility_window
        
        if len(prices) < window:
            return np.array([np.nan] * len(prices))
        
        prices_array = np.array(prices)
        rolling_std = np.full(len(prices), np.nan)
        
        for i in range(window - 1, len(prices)):
            window_data = prices_array[i - window + 1:i + 1]
            rolling_std[i] = np.std(window_data, ddof=1)
        
        return rolling_std
    
    def calculate_volatility(self, prices: List[float]) -> Dict[str, float]:
        """
        计算波动率指标
        
        Args:
            prices: 价格列表
            
        Returns:
            波动率指标字典
        """
        if len(prices) < 2:
            return {
                'current_volatility': 0.0,
                'avg_volatility': 0.0,
                'volatility_percentile': 0.0,
                'is_high_volatility': False
            }
        
        # 计算收益率
        returns = self.calculate_returns(prices)
        
        if len(returns) < self.volatility_window:
            current_vol = np.std(returns, ddof=1) if len(returns) > 1 else 0.0
            return {
                'current_volatility': float(current_vol),
                'avg_volatility': float(current_vol),
                'volatility_percentile': 50.0,
                'is_high_volatility': current_vol > self.high_volatility_threshold
            }
        
        # 滚动窗口波动率
        rolling_vols = []
        for i in range(self.volatility_window - 1, len(returns)):
            window_returns = returns[i - self.volatility_window + 1:i + 1]
            vol = np.std(window_returns, ddof=1)
            rolling_vols.append(vol)
        
        rolling_vols = np.array(rolling_vols)
        current_vol = rolling_vols[-1]
        avg_vol = np.mean(rolling_vols)
        
        # 计算当前波动率在历史分布中的百分位
        percentile = (rolling_vols < current_vol).sum() / len(rolling_vols) * 100
        
        return {
            'current_volatility': float(current_vol),
            'avg_volatility': float(avg_vol),
            'volatility_percentile': float(percentile),
            'is_high_volatility': current_vol > self.high_volatility_threshold
        }
    
    def detect_anomalies(self, prices: List[float]) -> Dict[str, any]:
        """
        异常检测（基于滚动标准差）
        
        Args:
            prices: 价格列表
            
        Returns:
            异常检测结果
        """
        if len(prices) < self.volatility_window:
            return {
                'has_anomaly': False,
                'anomaly_indices': [],
                'anomaly_prices': [],
                'z_scores': [],
                'latest_z_score': 0.0
            }
        
        prices_array = np.array(prices)
        anomalies = []
        anomaly_indices = []
        z_scores = []
        
        # 计算滚动均值和标准差
        for i in range(self.volatility_window - 1, len(prices)):
            window_data = prices_array[i - self.volatility_window + 1:i + 1]
            mean = np.mean(window_data)
            std = np.std(window_data, ddof=1)
            
            if std > 0:
                z_score = (prices_array[i] - mean) / std
                z_scores.append(z_score)
                
                # 检测异常（超过阈值）
                if abs(z_score) > self.anomaly_threshold:
                    anomalies.append(prices_array[i])
                    anomaly_indices.append(i)
        
        return {
            'has_anomaly': len(anomalies) > 0,
            'anomaly_count': len(anomalies),
            'anomaly_indices': anomaly_indices,
            'anomaly_prices': anomalies,
            'z_scores': z_scores,
            'latest_z_score': float(z_scores[-1]) if z_scores else 0.0
        }
    
    def assess_risk_level(self, prices: List[float]) -> Dict[str, any]:
        """
        评估风险等级
        
        Args:
            prices: 价格列表
            
        Returns:
            风险评估结果
        """
        if len(prices) < 2:
            return {
                'risk_level': 'UNKNOWN',
                'risk_score': 0,
                'risk_factors': []
            }
        
        # 计算各项指标
        volatility = self.calculate_volatility(prices)
        anomalies = self.detect_anomalies(prices)
        
        # 风险评分（0-100）
        risk_score = 0
        risk_factors = []
        
        # 因素1：波动率水平（0-40分）
        vol_score = min(40, volatility['volatility_percentile'] * 0.4)
        risk_score += vol_score
        if volatility['is_high_volatility']:
            risk_factors.append(f"高波动率 ({volatility['current_volatility']:.4f})")
        
        # 因素2：异常值存在（0-30分）
        if anomalies['has_anomaly']:
            anomaly_score = min(30, anomalies['anomaly_count'] * 10)
            risk_score += anomaly_score
            risk_factors.append(f"检测到 {anomalies['anomaly_count']} 个异常点")
        
        # 因素3：最新Z-score（0-30分）
        z_score = abs(anomalies['latest_z_score'])
        if z_score > 2.0:
            z_score_penalty = min(30, (z_score - 2.0) * 15)
            risk_score += z_score_penalty
            risk_factors.append(f"最新价格偏离度高 (Z={z_score:.2f})")
        
        # 确定风险等级
        if risk_score >= 70:
            risk_level = 'CRITICAL'  # 严重
        elif risk_score >= 50:
            risk_level = 'HIGH'      # 高
        elif risk_score >= 30:
            risk_level = 'MEDIUM'    # 中
        elif risk_score >= 10:
            risk_level = 'LOW'       # 低
        else:
            risk_level = 'MINIMAL'   # 极低
        
        return {
            'risk_level': risk_level,
            'risk_score': int(risk_score),
            'risk_factors': risk_factors,
            'volatility': volatility,
            'anomalies': anomalies
        }
    
    def generate_risk_signals(self, prices: List[float]) -> List[Dict[str, any]]:
        """
        生成风险信号
        
        Args:
            prices: 价格列表
            
        Returns:
            风险信号列表
        """
        signals = []
        
        if len(prices) < self.volatility_window:
            return signals
        
        # 评估风险
        risk_assessment = self.assess_risk_level(prices)
        volatility = risk_assessment['volatility']
        anomalies = risk_assessment['anomalies']
        
        # 信号1：高波动率警告
        if volatility['is_high_volatility']:
            signals.append({
                'type': 'HIGH_VOLATILITY',
                'severity': 'WARNING',
                'message': f"当前波动率 {volatility['current_volatility']:.4f} 超过阈值 {self.high_volatility_threshold:.4f}",
                'recommendation': '建议降低仓位或设置更严格的止损'
            })
        
        # 信号2：异常价格警告
        if anomalies['has_anomaly']:
            latest_z = anomalies['latest_z_score']
            if abs(latest_z) > self.anomaly_threshold:
                signals.append({
                    'type': 'PRICE_ANOMALY',
                    'severity': 'ALERT',
                    'message': f"检测到价格异常，Z-score = {latest_z:.2f}",
                    'recommendation': '谨慎交易，可能存在剧烈波动或数据异常'
                })
        
        # 信号3：风险等级变化
        risk_level = risk_assessment['risk_level']
        if risk_level in ['HIGH', 'CRITICAL']:
            signals.append({
                'type': 'RISK_LEVEL_CHANGE',
                'severity': 'CRITICAL' if risk_level == 'CRITICAL' else 'WARNING',
                'message': f"风险等级: {risk_level}（评分: {risk_assessment['risk_score']}/100）",
                'recommendation': '市场风险较高，建议减少暴露或暂停交易'
            })
        
        # 信号4：波动率趋势
        if volatility['volatility_percentile'] > 90:
            signals.append({
                'type': 'VOLATILITY_SPIKE',
                'severity': 'WARNING',
                'message': f"波动率处于历史高位（第 {volatility['volatility_percentile']:.1f} 百分位）",
                'recommendation': '市场不确定性增加，注意风险控制'
            })
        
        return signals
    
    def get_risk_report(self, prices: List[float], timestamps: List[str] = None) -> Dict[str, any]:
        """
        生成完整的风险报告
        
        Args:
            prices: 价格列表
            timestamps: 时间戳列表（可选）
            
        Returns:
            完整风险报告
        """
        if len(prices) < 2:
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': '数据不足，无法生成风险报告',
                'data_points': len(prices),
                'required_points': self.volatility_window
            }
        
        # 风险评估
        risk_assessment = self.assess_risk_level(prices)
        
        # 风险信号
        signals = self.generate_risk_signals(prices)
        
        # 统计信息
        current_price = prices[-1]
        price_change = ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] != 0 else 0
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'OK',
            'summary': {
                'risk_level': risk_assessment['risk_level'],
                'risk_score': risk_assessment['risk_score'],
                'current_price': current_price,
                'price_change_pct': float(price_change),
                'data_points': len(prices)
            },
            'volatility': risk_assessment['volatility'],
            'anomalies': {
                'detected': risk_assessment['anomalies']['has_anomaly'],
                'count': risk_assessment['anomalies']['anomaly_count'],
                'latest_z_score': risk_assessment['anomalies']['latest_z_score']
            },
            'signals': signals,
            'risk_factors': risk_assessment['risk_factors'],
            'recommendations': [s['recommendation'] for s in signals]
        }
        
        return report


def analyze_risk(prices: List[float], symbol: str = 'UNKNOWN') -> Dict[str, any]:
    """
    便捷函数：分析价格序列的风险
    
    Args:
        prices: 价格列表
        symbol: 交易品种名称
        
    Returns:
        风险分析报告
    """
    engine = RiskEngine()
    report = engine.get_risk_report(prices)
    report['symbol'] = symbol
    return report


if __name__ == '__main__':
    # 测试示例
    print("=" * 60)
    print("风险引擎测试")
    print("=" * 60)
    
    # 生成测试数据：正常价格 + 突然波动
    np.random.seed(42)
    base_price = 1.27
    normal_prices = base_price + np.random.normal(0, 0.002, 100)
    
    # 添加异常点
    test_prices = list(normal_prices)
    test_prices[80] = base_price + 0.05  # 异常高点
    test_prices[85] = base_price - 0.04  # 异常低点
    
    # 运行风险分析
    engine = RiskEngine(
        volatility_window=20,
        anomaly_threshold=2.5,
        high_volatility_threshold=0.015
    )
    
    report = engine.get_risk_report(test_prices)
    
    # 打印报告
    print(f"\n📊 风险报告")
    print(f"状态: {report['status']}")
    print(f"\n摘要:")
    print(f"  风险等级: {report['summary']['risk_level']}")
    print(f"  风险评分: {report['summary']['risk_score']}/100")
    print(f"  当前价格: {report['summary']['current_price']:.6f}")
    print(f"  价格变化: {report['summary']['price_change_pct']:.2f}%")
    print(f"  数据点数: {report['summary']['data_points']}")
    
    print(f"\n波动率:")
    print(f"  当前波动率: {report['volatility']['current_volatility']:.6f}")
    print(f"  平均波动率: {report['volatility']['avg_volatility']:.6f}")
    print(f"  波动率百分位: {report['volatility']['volatility_percentile']:.1f}%")
    print(f"  高波动率: {'是' if report['volatility']['is_high_volatility'] else '否'}")
    
    print(f"\n异常检测:")
    print(f"  检测到异常: {'是' if report['anomalies']['detected'] else '否'}")
    print(f"  异常点数量: {report['anomalies']['count']}")
    print(f"  最新Z-score: {report['anomalies']['latest_z_score']:.2f}")
    
    print(f"\n⚠️  风险信号 ({len(report['signals'])} 个):")
    for i, signal in enumerate(report['signals'], 1):
        print(f"  {i}. [{signal['severity']}] {signal['type']}")
        print(f"     {signal['message']}")
        print(f"     💡 {signal['recommendation']}")
    
    print(f"\n风险因素:")
    for factor in report['risk_factors']:
        print(f"  • {factor}")
    
    print("\n" + "=" * 60)
