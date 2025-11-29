import dash
from dash import dcc, html, Output, Input, State, callback
import requests
import datetime
import plotly.graph_objs as go
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import sys

# import helper for usage control and risk engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
try:
    from ai_usage import can_call, record_call
    from risk_engine import RiskEngine
except Exception:
    can_call = None
    record_call = None
    RiskEngine = None

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

app = dash.Dash(__name__)

# Initialize DeepSeek client (compatible with OpenAI SDK)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
) if DEEPSEEK_API_KEY else None

# AI usage controls (environment-configurable)
try:
    MAX_CALLS_PER_DAY = int(os.getenv('MAX_CALLS_PER_DAY', '20'))
except Exception:
    MAX_CALLS_PER_DAY = 20
try:
    SUMMARY_COOLDOWN_SEC = int(os.getenv('SUMMARY_COOLDOWN_SEC', '300'))
except Exception:
    SUMMARY_COOLDOWN_SEC = 300

# UI: symbol dropdown, graph, status, AI summary
app.layout = html.Div([
    html.H1("Financial Dashboard"),
    
    html.Div([
        html.Label("Symbol:"),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[
                {'label': 'GBP/USD', 'value': 'GBPUSD'},
                {'label': 'EUR/USD', 'value': 'EURUSD'},
                {'label': 'BTC/USD', 'value': 'BTCUSD'}
            ],
            value='GBPUSD'
        )
    ], style={'marginBottom': '12px', 'width': '200px'}),

    dcc.Graph(id='price-graph', config={'displayModeBar': False}),

    # store holds list of {ts: ..., price: ...}
    dcc.Store(id='price-store', data=[]),

    # store for AI summary
    dcc.Store(id='summary-store', data=''),

    # store for risk data
    dcc.Store(id='risk-store', data={}),

    # Disabled auto-refresh for cleaner display
    # dcc.Interval(id='interval', interval=5*1000, n_intervals=0),

    html.Div(id='status', style={'marginTop': '8px', 'color': '#666', 'fontSize': '12px'}),

    # Manual refresh button for data
    html.Button(
        '🔄 刷新数据',
        id='refresh-data-btn',
        n_clicks=0,
        style={
            'marginTop': '10px',
            'padding': '8px 16px',
            'backgroundColor': '#2196F3',
            'color': 'white',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'fontSize': '14px'
        }
    ),

    html.Div([
        html.Div([
            html.H3("AI 市场点评", style={'marginTop': '24px', 'display': 'inline-block', 'marginRight': '10px'}),
            html.Button(
                '🔄 刷新分析',
                id='refresh-summary-btn',
                n_clicks=0,
                style={
                    'padding': '8px 16px',
                    'backgroundColor': '#4CAF50',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer',
                    'fontSize': '14px'
                }
            )
        ]),
        html.Div(
            id='ai-summary',
            style={
                'backgroundColor': '#f0f0f0',
                'padding': '16px',
                'borderRadius': '8px',
                'lineHeight': '1.6',
                'color': '#333',
                'minHeight': '100px',
                'marginTop': '10px'
            }
        )
    ], style={'marginTop': '20px'}),

    # Risk Engine Panel
    html.Div([
        html.H3("🛡️ 风险监控", style={'marginTop': '24px', 'color': '#d32f2f'}),
        html.Div(id='risk-panel', style={'marginTop': '10px'})
    ], style={'marginTop': '20px'})
])


def fetch_price(symbol: str):
    """Call Flask API to get latest price for symbol. Returns dict or None."""
    attempts = 2
    backoff = 0.5
    for i in range(attempts):
        try:
            resp = requests.get(f'http://127.0.0.1:5000/price', params={'symbol': symbol}, timeout=2.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        try:
            import time
            time.sleep(backoff * (i + 1))
        except Exception:
            pass
    return None


def fetch_history(symbol: str, limit: int = 500):
    """Call Flask API /history to get recent points. Returns list of dicts or None."""
    try:
        resp = requests.get(f'http://127.0.0.1:5000/history', params={'symbol': symbol, 'limit': limit}, timeout=5.0)
        if resp.status_code == 200:
            j = resp.json()
            return j.get('data', [])
    except Exception:
        return None
    return None


def resample_to_low_frequency(data: list, interval_minutes: int = 5):
    """
    Resample high-frequency data to low-frequency K-line (candlestick) data.
    
    模拟真实 K 线生成逻辑：
    1. 按固定时间间隔（如 5 分钟）划分区间
    2. 每个区间内不断更新价格
    3. 取该区间最后一个价格作为收盘价 (close)
    
    Args:
        data: List of dicts with 'timestamp' and 'price' keys
        interval_minutes: Interval in minutes (default 5)
    
    Returns:
        List of resampled K-line data (close price of each interval)
    """
    if not data or len(data) < 2:
        return data
    
    from datetime import datetime, timedelta
    
    try:
        # Step 1: Parse and sort all data points by timestamp
        time_price_pairs = []
        for d in data:
            ts_str = d['timestamp']
            if 'Z' in ts_str:
                ts_str = ts_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(ts_str)
            time_price_pairs.append((dt, float(d['price'])))
        
        time_price_pairs.sort(key=lambda x: x[0])
        
        if not time_price_pairs:
            return data
        
        # Step 2: Align to K-line intervals (floor to nearest interval)
        first_dt = time_price_pairs[0][0]
        interval_delta = timedelta(minutes=interval_minutes)
        
        # Floor the first timestamp to interval boundary
        # Example: 14:32:15 with 5-min interval -> 14:30:00
        minutes_offset = first_dt.minute % interval_minutes
        seconds_offset = first_dt.second
        microseconds_offset = first_dt.microsecond
        
        bucket_start = first_dt - timedelta(
            minutes=minutes_offset,
            seconds=seconds_offset,
            microseconds=microseconds_offset
        )
        
        # Step 3: Group data into K-line buckets and extract close price
        klines = []
        current_bucket_start = bucket_start
        current_bucket_data = []
        
        for dt, price in time_price_pairs:
            # Calculate which bucket this data point belongs to
            while dt >= current_bucket_start + interval_delta:
                # Close current bucket if it has data
                if current_bucket_data:
                    # Take the LAST price in this interval as close price
                    close_time, close_price = current_bucket_data[-1]
                    klines.append({
                        'timestamp': close_time.isoformat(),
                        'price': close_price
                    })
                
                # Move to next bucket
                current_bucket_start += interval_delta
                current_bucket_data = []
            
            # Add data point to current bucket
            current_bucket_data.append((dt, price))
        
        # Don't forget to close the last bucket
        if current_bucket_data:
            close_time, close_price = current_bucket_data[-1]
            klines.append({
                'timestamp': close_time.isoformat(),
                'price': close_price
            })
        
        return klines if klines else data
    
    except Exception as e:
        print(f"K-line resample error: {e}")
        return data


def calculate_ma(prices, window):
    """Calculate simple moving average."""
    if len(prices) < window:
        return [None] * len(prices)
    ma = [None] * (window - 1)
    for i in range(window - 1, len(prices)):
        ma.append(sum(prices[i - window + 1:i + 1]) / window)
    return ma


def get_7day_data(data):
    """Extract 7-day data from price store. Returns list of dicts or empty list."""
    if not data:
        return []
    
    # Get the last 7 days worth of data
    # Assuming ~144 data points per day (86400 seconds / 600 seconds per point if polling every 10 min)
    # But with 5-second intervals, it's much denser. Let's use a time-based approach instead.
    now = datetime.datetime.utcnow()
    seven_days_ago = now - datetime.timedelta(days=7)
    
    result = []
    for d in data:
        try:
            ts = datetime.datetime.fromisoformat(d['ts'].replace('Z', '+00:00'))
            if ts >= seven_days_ago:
                result.append(d)
        except Exception:
            pass
    
    return result


def generate_ai_summary(symbol: str, data: list) -> str:
    """
    Generate AI summary for the given symbol using 7-day data.
    
    Args:
        symbol: Trading symbol (e.g., 'GBPUSD')
        data: List of price data points with 'ts' and 'price' keys
    
    Returns:
        Summary string or error message
    """
    if not client or not DEEPSEEK_API_KEY:
        return "⚠️ DeepSeek API 未配置。请设置 DEEPSEEK_API_KEY 环境变量。"
    
    if not data or len(data) < 2:
        return "⚠️ 数据不足，无法生成总结。"
    
    try:
        # Extract prices
        prices = [d['price'] for d in data]
        
        # Calculate basic stats
        current_price = prices[-1]
        prev_price = prices[0]
        min_price = min(prices)
        max_price = max(prices)
        price_change = current_price - prev_price
        change_pct = (price_change / prev_price * 100) if prev_price != 0 else 0
        
        # Get MA values
        ma7 = calculate_ma(prices, 7)
        ma30 = calculate_ma(prices, 30)
        
        # Extract last valid MA values
        last_ma7 = next((x for x in reversed(ma7) if x is not None), None)
        last_ma30 = next((x for x in reversed(ma30) if x is not None), None)
        
        # Format MA values safely
        ma7_str = f"{last_ma7:.6f}" if last_ma7 is not None else "N/A"
        ma30_str = f"{last_ma30:.6f}" if last_ma30 is not None else "N/A"
        
        # Build data summary
        data_summary = f"""
交易对: {symbol}
当前价格: {current_price:.6f}
7天变化: {price_change:+.6f} ({change_pct:+.2f}%)
7天最高: {max_price:.6f}
7天最低: {min_price:.6f}
7日MA: {ma7_str}
30日MA: {ma30_str}
数据点数: {len(data)}
"""
        
        # Create prompt for GPT
        prompt = f"""作为一位专业的金融分析师，请根据以下7天的交易数据，用中文生成一份市场点评（150-200字）。
        
{data_summary}

请分析：
1. 价格趋势（上升/下降/震荡）
2. 与移动平均线的关系
3. 可能的市场信号
4. 简短的投资建议

格式：直接输出分析意见，无需标题或编号。"""
        
        # Call DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "你是一位专业的金融分析师。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            timeout=10.0
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
    
    except Exception as e:
        error_msg = str(e)
        
        # Provide user-friendly error messages
        if "402" in error_msg or "Insufficient Balance" in error_msg:
            return "💳 DeepSeek 账户余额不足。请访问 https://platform.deepseek.com 充值后再试。"
        elif "401" in error_msg or "Unauthorized" in error_msg:
            return "🔑 API 密钥无效。请检查 DEEPSEEK_API_KEY 环境变量配置。"
        elif "429" in error_msg or "rate" in error_msg.lower():
            return "⏱️ API 调用频率过高，请稍后再试。"
        elif "timeout" in error_msg.lower():
            return "⏰ API 请求超时，请检查网络连接后重试。"
        else:
            return f"❌ AI 总结生成失败: {error_msg}"


@app.callback(
    Output('price-store', 'data'),
    Output('status', 'children'),
    Input('refresh-data-btn', 'n_clicks'),
    Input('symbol-dropdown', 'value'),
    prevent_initial_call=False
)
def load_data(n_clicks, symbol):
    """Load historical data + latest real-time point separately."""
    symbol = (symbol or 'GBPUSD').strip()
    
    # Load raw historical data (more points to ensure good resampling)
    hist = fetch_history(symbol, limit=2000)
    if not hist:
        return {'historical': [], 'latest': None}, f'无法加载 {symbol} 的历史数据'
    
    # Resample to low-frequency (5-minute candles) for clean trends
    resampled = resample_to_low_frequency(hist, interval_minutes=5)
    
    # Keep only the most recent 300 resampled points for display
    if len(resampled) > 300:
        resampled = resampled[-300:]
    
    # Convert historical data to internal format
    historical = [{'ts': h['timestamp'], 'price': float(h['price'])} for h in resampled]
    
    # Fetch the latest single real-time point
    latest_point = None
    latest = fetch_price(symbol)
    if latest and 'price' in latest:
        latest_ts = latest.get('timestamp') or datetime.datetime.utcnow().isoformat()
        latest_price = float(latest['price'])
        
        # Only use if it's newer than the last historical point
        if historical and latest_ts > historical[-1]['ts']:
            latest_point = {'ts': latest_ts, 'price': latest_price}
    
    update_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    status_msg = f'✓ 历史: {len(historical)} 点 (5分钟K线)'
    if latest_point:
        status_msg += f' | 最新实时: {latest_point["price"]:.6f}'
    status_msg += f' | 更新: {update_time} | {symbol}'
    
    return {'historical': historical, 'latest': latest_point}, status_msg


@app.callback(
    Output('price-graph', 'figure'),
    Input('price-store', 'data'),
    State('symbol-dropdown', 'value')
)
def update_graph(data, symbol):
    symbol = (symbol or 'GBPUSD').strip()
    
    # Handle new data structure
    if not data or not isinstance(data, dict):
        fig = go.Figure()
        fig.update_layout(title=f'{symbol} - 等待数据加载...')
        return fig
    
    historical = data.get('historical', [])
    latest_point = data.get('latest')
    
    if not historical:
        fig = go.Figure()
        fig.update_layout(title=f'{symbol} - 无历史数据')
        return fig
    
    # Extract historical data for plotting and MA calculation
    hist_x = [d['ts'] for d in historical]
    hist_y = [d['price'] for d in historical]
    
    # Calculate moving averages on historical data only
    ma7 = calculate_ma(hist_y, 7)
    ma30 = calculate_ma(hist_y, 30)
    
    # Create figure
    fig = go.Figure()
    
    # Plot 1: Historical price line (smooth, no noise)
    fig.add_trace(go.Scatter(
        x=hist_x, 
        y=hist_y, 
        mode='lines', 
        name=f'{symbol} (历史)',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='%{y:.6f}<extra></extra>'
    ))
    
    # Plot 2: MA7 (calculated from historical data)
    fig.add_trace(go.Scatter(
        x=hist_x, 
        y=ma7, 
        mode='lines', 
        name='MA7',
        line=dict(color='#ff7f0e', width=1.5, dash='dash'),
        hovertemplate='MA7: %{y:.6f}<extra></extra>'
    ))
    
    # Plot 3: MA30 (calculated from historical data)
    fig.add_trace(go.Scatter(
        x=hist_x, 
        y=ma30, 
        mode='lines', 
        name='MA30',
        line=dict(color='#d62728', width=1.5, dash='dot'),
        hovertemplate='MA30: %{y:.6f}<extra></extra>'
    ))
    
    # Plot 4: Latest real-time point (highlighted)
    if latest_point:
        fig.add_trace(go.Scatter(
            x=[latest_point['ts']], 
            y=[latest_point['price']], 
            mode='markers+text',
            name='最新报价',
            marker=dict(color='#2ca02c', size=12, symbol='star'),
            text=[f"{latest_point['price']:.6f}"],
            textposition="top center",
            textfont=dict(size=10, color='#2ca02c', family='Arial Black'),
            hovertemplate='最新: %{y:.6f}<extra></extra>'
        ))
        title_suffix = f' + 最新点'
    else:
        title_suffix = ''
    
    fig.update_layout(
        title=f'{symbol} - 5分钟K线趋势 ({len(historical)} 点) + MA7/MA30{title_suffix}',
        xaxis_title='时间',
        yaxis_title='价格',
        hovermode='x unified',
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


# Cache for AI summaries to avoid excessive API calls
ai_summary_cache = {}
ai_summary_last_update = {}

@app.callback(
    Output('ai-summary', 'children'),
    Input('refresh-summary-btn', 'n_clicks'),
    Input('price-store', 'data'),
    State('symbol-dropdown', 'value'),
    prevent_initial_call=False
)
def update_ai_summary(n_clicks, data, symbol):
    """Update AI summary. Only calls API when refresh button is clicked or cache is old."""
    symbol = (symbol or 'GBPUSD').strip()
    data = data or []
    
    if not data:
        return "⏳ 等待数据加载...（点击【🔄 刷新分析】生成 AI 点评）"
    
    # Check if we have cached summary
    import time
    current_time = time.time()
    
    # If button never clicked and no cache, show prompt
    if n_clicks == 0 and symbol not in ai_summary_cache:
        return "💡 点击【🔄 刷新分析】按钮生成 AI 市场点评（节省 API 用量）"
    
    # Check cache (30 minutes = 1800 seconds)
    cache_duration = 1800  # 30 minutes
    
    if symbol in ai_summary_cache and n_clicks == 0:
        last_update = ai_summary_last_update.get(symbol, 0)
        if current_time - last_update < cache_duration:
            # Return cached summary with timestamp
            minutes_ago = int((current_time - last_update) / 60)
            return f"{ai_summary_cache[symbol]}\n\n🕐 缓存分析（{minutes_ago} 分钟前生成）· 点击【🔄 刷新分析】更新"
    
    # Extract 7-day data
    seven_day_data = get_7day_data(data)
    
    if len(seven_day_data) < 2:
        return f"⏳ 数据点不足 ({len(seven_day_data)}/2)，正在收集..."
    
    # Rate-limiting: check allowance before calling API
    allowed, reason, wait = (True, "ok", 0)
    if can_call:
        try:
            allowed, reason, wait = can_call(MAX_CALLS_PER_DAY, SUMMARY_COOLDOWN_SEC)
        except Exception:
            allowed, reason, wait = True, "ok", 0

    if not allowed:
        # If blocked, prefer serving cached summary if available
        if symbol in ai_summary_cache:
            if reason == "daily_cap":
                hrs = max(1, wait // 3600)
                return f"{ai_summary_cache[symbol]}\n\n⛔ 今日 AI 次数已达上限。约 {hrs} 小时后可再刷新。"
            else:
                mins = max(1, wait // 60)
                return f"{ai_summary_cache[symbol]}\n\n⏳ 冷却中（约 {mins} 分钟后可再刷新）。"
        else:
            if reason == "daily_cap":
                hrs = max(1, wait // 3600)
                return f"⛔ 今日 AI 调用次数已用完。请约 {hrs} 小时后再试。"
            else:
                mins = max(1, wait // 60)
                return f"⏳ 冷却中，请约 {mins} 分钟后再试。"

    # Generate AI summary (only when button clicked or cache expired)
    summary = generate_ai_summary(symbol, seven_day_data)

    # Record usage after a real API attempt
    if record_call and client and DEEPSEEK_API_KEY:
        try:
            record_call()
        except Exception:
            pass
    
    # Update cache
    ai_summary_cache[symbol] = summary
    ai_summary_last_update[symbol] = current_time
    
    return f"{summary}\n\n🕐 刚刚更新"


@app.callback(
    Output('risk-store', 'data'),
    Output('risk-panel', 'children'),
    Input('price-store', 'data'),
    State('symbol-dropdown', 'value')
)
def update_risk_analysis(data, symbol):
    """实时风险分析和监控"""
    symbol = (symbol or 'GBPUSD').strip()
    
    # 检查数据
    if not data or not isinstance(data, dict):
        return {}, html.Div("等待数据加载...", style={'color': '#999'})
    
    historical = data.get('historical', [])
    if not historical or len(historical) < 20:
        return {}, html.Div("数据不足，需要至少20个数据点进行风险分析", style={'color': '#999'})
    
    # 检查风险引擎是否可用
    if not RiskEngine:
        return {}, html.Div("⚠️ 风险引擎模块未加载", style={'color': '#f44336'})
    
    # 提取价格序列
    prices = [float(d['price']) for d in historical]
    
    # 初始化风险引擎
    engine = RiskEngine(
        volatility_window=20,
        anomaly_threshold=2.5,
        high_volatility_threshold=0.015
    )
    
    # 生成风险报告
    try:
        report = engine.get_risk_report(prices)
    except Exception as e:
        return {}, html.Div(f"❌ 风险分析失败: {str(e)}", style={'color': '#f44336'})
    
    if report.get('status') != 'OK':
        return report, html.Div(
            f"⚠️ {report.get('message', '无法生成风险报告')}",
            style={'color': '#ff9800'}
        )
    
    # 构建风险面板UI
    summary = report['summary']
    volatility = report['volatility']
    anomalies = report['anomalies']
    signals = report['signals']
    
    # 风险等级颜色
    risk_colors = {
        'MINIMAL': '#4caf50',
        'LOW': '#8bc34a',
        'MEDIUM': '#ff9800',
        'HIGH': '#ff5722',
        'CRITICAL': '#d32f2f'
    }
    
    risk_level = summary['risk_level']
    risk_color = risk_colors.get(risk_level, '#999')
    
    # 风险等级中文
    risk_level_zh = {
        'MINIMAL': '极低',
        'LOW': '低',
        'MEDIUM': '中',
        'HIGH': '高',
        'CRITICAL': '严重'
    }
    
    panel_children = [
        # 风险摘要卡片
        html.Div([
            html.Div([
                html.Div([
                    html.H4(f"风险等级: {risk_level_zh.get(risk_level, risk_level)}", 
                           style={'margin': '0', 'color': risk_color}),
                    html.P(f"评分: {summary['risk_score']}/100", 
                          style={'margin': '5px 0 0 0', 'fontSize': '14px', 'color': '#666'})
                ], style={'flex': '1'}),
                html.Div([
                    html.Div(
                        f"{summary['risk_score']}",
                        style={
                            'fontSize': '36px',
                            'fontWeight': 'bold',
                            'color': risk_color,
                            'lineHeight': '1'
                        }
                    )
                ], style={'textAlign': 'right'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'padding': '16px',
                'backgroundColor': '#fff',
                'border': f'2px solid {risk_color}',
                'borderRadius': '8px',
                'marginBottom': '16px'
            })
        ]),
        
        # 波动率指标
        html.Div([
            html.H4("📊 波动率分析", style={'margin': '0 0 12px 0', 'fontSize': '16px'}),
            html.Div([
                html.Div([
                    html.Span("当前波动率: ", style={'color': '#666'}),
                    html.Span(f"{volatility['current_volatility']:.4f}", 
                             style={'fontWeight': 'bold', 'color': '#ff5722' if volatility['is_high_volatility'] else '#333'})
                ], style={'marginBottom': '8px'}),
                html.Div([
                    html.Span("平均波动率: ", style={'color': '#666'}),
                    html.Span(f"{volatility['avg_volatility']:.4f}", style={'fontWeight': 'bold'})
                ], style={'marginBottom': '8px'}),
                html.Div([
                    html.Span("波动率百分位: ", style={'color': '#666'}),
                    html.Span(f"{volatility['volatility_percentile']:.1f}%", style={'fontWeight': 'bold'}),
                    html.Span(
                        " 🔥 高波动" if volatility['volatility_percentile'] > 80 else "",
                        style={'color': '#f44336', 'marginLeft': '8px'}
                    )
                ], style={'marginBottom': '8px'}),
                html.Div([
                    html.Span("状态: ", style={'color': '#666'}),
                    html.Span(
                        "⚠️ 高波动率" if volatility['is_high_volatility'] else "✅ 正常",
                        style={'fontWeight': 'bold', 'color': '#f44336' if volatility['is_high_volatility'] else '#4caf50'}
                    )
                ])
            ], style={
                'padding': '12px',
                'backgroundColor': '#f5f5f5',
                'borderRadius': '6px',
                'fontSize': '14px'
            })
        ], style={'marginBottom': '16px'}),
        
        # 异常检测
        html.Div([
            html.H4("🔍 异常检测", style={'margin': '0 0 12px 0', 'fontSize': '16px'}),
            html.Div([
                html.Div([
                    html.Span("异常点数量: ", style={'color': '#666'}),
                    html.Span(
                        f"{anomalies['count']}", 
                        style={'fontWeight': 'bold', 'color': '#f44336' if anomalies['count'] > 0 else '#4caf50'}
                    )
                ], style={'marginBottom': '8px'}),
                html.Div([
                    html.Span("最新Z-score: ", style={'color': '#666'}),
                    html.Span(f"{anomalies['latest_z_score']:.2f}", style={'fontWeight': 'bold'}),
                    html.Span(
                        " ⚠️ 异常" if abs(anomalies['latest_z_score']) > 2.5 else " ✅ 正常",
                        style={'marginLeft': '8px', 'color': '#f44336' if abs(anomalies['latest_z_score']) > 2.5 else '#4caf50'}
                    )
                ], style={'marginBottom': '8px'}),
                html.Div([
                    html.Span("状态: ", style={'color': '#666'}),
                    html.Span(
                        "🚨 检测到异常" if anomalies['detected'] else "✅ 无异常",
                        style={'fontWeight': 'bold', 'color': '#f44336' if anomalies['detected'] else '#4caf50'}
                    )
                ])
            ], style={
                'padding': '12px',
                'backgroundColor': '#f5f5f5',
                'borderRadius': '6px',
                'fontSize': '14px'
            })
        ], style={'marginBottom': '16px'}),
        
        # 风险信号
        html.Div([
            html.H4(f"⚠️ 风险信号 ({len(signals)} 个)", style={'margin': '0 0 12px 0', 'fontSize': '16px'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(
                            "🔴 " if s['severity'] == 'CRITICAL' else "🟡 " if s['severity'] == 'WARNING' else "🔵 ",
                            style={'fontSize': '18px'}
                        ),
                        html.Span(f"{s['type']}", style={'fontWeight': 'bold', 'fontSize': '14px'})
                    ], style={'marginBottom': '6px'}),
                    html.Div(s['message'], style={'marginBottom': '6px', 'color': '#666', 'fontSize': '13px'}),
                    html.Div([
                        html.Span("💡 ", style={'fontSize': '14px'}),
                        html.Span(s['recommendation'], style={'fontSize': '13px', 'fontStyle': 'italic', 'color': '#555'})
                    ])
                ], style={
                    'padding': '12px',
                    'backgroundColor': '#fff3e0' if s['severity'] == 'WARNING' else '#ffebee' if s['severity'] == 'CRITICAL' else '#e3f2fd',
                    'borderLeft': f"4px solid {'#ff9800' if s['severity'] == 'WARNING' else '#f44336' if s['severity'] == 'CRITICAL' else '#2196f3'}",
                    'borderRadius': '4px',
                    'marginBottom': '12px'
                })
                for s in signals
            ]) if signals else html.Div(
                "✅ 无风险信号，市场状况良好",
                style={'padding': '12px', 'backgroundColor': '#e8f5e9', 'borderRadius': '4px', 'color': '#4caf50'}
            )
        ], style={'marginBottom': '16px'}),
        
        # 风险因素
        html.Div([
            html.H4("📋 风险因素", style={'margin': '0 0 12px 0', 'fontSize': '16px'}),
            html.Div([
                html.Div(f"• {factor}", style={'marginBottom': '6px', 'fontSize': '14px'})
                for factor in report['risk_factors']
            ]) if report['risk_factors'] else html.Div(
                "✅ 未发现显著风险因素",
                style={'color': '#4caf50', 'fontSize': '14px'}
            )
        ], style={
            'padding': '12px',
            'backgroundColor': '#f5f5f5',
            'borderRadius': '6px'
        })
    ]
    
    return report, html.Div(panel_children)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
