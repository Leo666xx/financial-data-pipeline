import dash
from dash import dcc, html, Output, Input, State, callback
import requests
import datetime
import plotly.graph_objs as go
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

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

    # poll every 5 seconds
    dcc.Interval(id='interval', interval=5*1000, n_intervals=0),

    html.Div(id='status', style={'marginTop': '8px', 'color': '#666', 'fontSize': '12px'}),

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
        
        # Build data summary
        data_summary = f"""
交易对: {symbol}
当前价格: {current_price:.6f}
7天变化: {price_change:+.6f} ({change_pct:+.2f}%)
7天最高: {max_price:.6f}
7天最低: {min_price:.6f}
7日MA: {last_ma7:.6f if last_ma7 else 'N/A'}
30日MA: {last_ma30:.6f if last_ma30 else 'N/A'}
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
        return f"❌ AI 总结生成失败: {str(e)}"


@app.callback(
    Output('price-store', 'data'),
    Output('status', 'children'),
    Input('interval', 'n_intervals'),
    State('symbol-dropdown', 'value'),
    State('price-store', 'data')
)
def poll_price(n_intervals, symbol, stored):
    symbol = (symbol or 'GBPUSD').strip()
    stored = stored or []
    
    # On first interval, try to load history if store empty
    if n_intervals == 0 and (not stored or len(stored) == 0):
        hist = fetch_history(symbol, limit=500)
        if hist:
            stored = [{'ts': h['timestamp'], 'price': float(h['price'])} for h in hist]
            return stored, f'Loaded history: {len(stored)} points.'

    data = fetch_price(symbol)
    if not data or 'price' not in data:
        return stored, f'Last poll: {datetime.datetime.utcnow().isoformat()} - failed to fetch.'

    ts = data.get('timestamp') or datetime.datetime.utcnow().isoformat()
    entry = {'ts': ts, 'price': float(data['price'])}
    stored.append(entry)
    if len(stored) > 500:
        stored = stored[-500:]
    return stored, f'Last poll: {datetime.datetime.utcnow().isoformat()} - price {entry["price"]:.6f} ({symbol})'


@app.callback(
    Output('price-graph', 'figure'),
    Input('price-store', 'data'),
    State('symbol-dropdown', 'value')
)
def update_graph(data, symbol):
    symbol = (symbol or 'GBPUSD').strip()
    data = data or []
    if not data:
        fig = go.Figure()
        fig.update_layout(title=f'{symbol} - no data yet')
        return fig

    x = [d['ts'] for d in data]
    y = [d['price'] for d in data]

    # Calculate moving averages
    ma7 = calculate_ma(y, 7)
    ma30 = calculate_ma(y, 30)

    # Create figure with price, MA7, MA30
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=symbol, line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=x, y=ma7, mode='lines', name='MA7', line=dict(color='orange', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=x, y=ma30, mode='lines', name='MA30', line=dict(color='red', width=1, dash='dot')))

    fig.update_layout(
        title=f'{symbol} - Live Price with Moving Averages',
        xaxis_title='Timestamp',
        yaxis_title='Price',
        hovermode='x unified',
        template='plotly_white'
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
    
    # Generate AI summary (only when button clicked or cache expired)
    summary = generate_ai_summary(symbol, seven_day_data)
    
    # Update cache
    ai_summary_cache[symbol] = summary
    ai_summary_last_update[symbol] = current_time
    
    return f"{summary}\n\n🕐 刚刚更新"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
