import dash
from dash import dcc, html, Output, Input, State
import requests
import datetime
import plotly.graph_objs as go
import json

app = dash.Dash(__name__)

# Simple UI: symbol input, graph, and hidden store for collected points
app.layout = html.Div([
    html.H1("Financial Dashboard"),
    html.Div([
        html.Label("Symbol:"),
        dcc.Input(id='symbol-input', type='text', value='GBPUSD')
    ], style={'marginBottom': '12px'}),

    dcc.Graph(id='price-graph', config={'displayModeBar': False}),

    # store holds list of {ts: ..., price: ...}
    dcc.Store(id='price-store', data=[]),

    # poll every 5 seconds
    dcc.Interval(id='interval', interval=5*1000, n_intervals=0),

    html.Div(id='status', style={'marginTop': '8px', 'color': '#666'})
])


def fetch_price(symbol: str):
    """Call Flask API to get latest price for symbol. Returns dict or None."""
    # simple retry logic
    attempts = 2
    backoff = 0.5
    for i in range(attempts):
        try:
            resp = requests.get(f'http://127.0.0.1:5000/price', params={'symbol': symbol}, timeout=2.0)
            if resp.status_code == 200:
                return resp.json()
            else:
                # non-200 -> try again
                pass
        except Exception:
            pass
        try:
            # small backoff
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


@app.callback(
    Output('price-store', 'data'),
    Output('status', 'children'),
    Input('interval', 'n_intervals'),
    State('symbol-input', 'value'),
    State('price-store', 'data')
)
def poll_price(n_intervals, symbol, stored):
    symbol = (symbol or 'GBPUSD').strip()
    stored = stored or []
    # On first interval, try to load history if store empty
    if n_intervals == 0 and (not stored or len(stored) == 0):
        hist = fetch_history(symbol, limit=500)
        if hist:
            # hist is list of {timestamp, price}
            stored = [{'ts': h['timestamp'], 'price': float(h['price'])} for h in hist]
            return stored, f'Loaded history: {len(stored)} points.'

    data = fetch_price(symbol)
    if not data or 'price' not in data:
        return stored, f'Last poll: {datetime.datetime.utcnow().isoformat()} - failed to fetch.'

    # normalize timestamp
    ts = data.get('timestamp') or datetime.datetime.utcnow().isoformat()
    try:
        parsed = ts
    except Exception:
        parsed = datetime.datetime.utcnow().isoformat()

    entry = {'ts': parsed, 'price': float(data['price'])}
    # append but keep only last 500 points
    stored.append(entry)
    if len(stored) > 500:
        stored = stored[-500:]
    return stored, f'Last poll: {datetime.datetime.utcnow().isoformat()} - price {entry["price"]} ({symbol})'


@app.callback(
    Output('price-graph', 'figure'),
    Input('price-store', 'data'),
    State('symbol-input', 'value')
)
def update_graph(data, symbol):
    symbol = (symbol or 'GBPUSD').strip()
    data = data or []
    if not data:
        fig = go.Figure()
        fig.update_layout(title=f'{symbol} - no data yet')
        return fig

    # convert to lists
    x = [d['ts'] for d in data]
    y = [d['price'] for d in data]

    fig = go.Figure(data=[go.Scatter(x=x, y=y, mode='lines+markers', name=symbol)])
    fig.update_layout(title=f'{symbol} - Live Price', xaxis_title='Timestamp', yaxis_title='Price')
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
