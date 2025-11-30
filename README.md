# Financial Data Pipeline

A comprehensive financial data analysis system with real-time data collection, K-line generation, technical indicators, and AI-powered market analysis.

## ✨ Core Features

- 📊 **K-Line Generation** - Collects tick data every 5 seconds, automatically generates 5-minute OHLC candlesticks
- 📈 **Technical Indicators** - MA7/MA30 moving averages with automatic calculation and visualization
- 🤖 **AI Market Analysis** - Integrated DeepSeek API for intelligent market commentary
- 🛡️ **Risk Engine** - Real-time market risk monitoring with rolling standard deviation anomaly detection and volatility analysis
- 🎨 **Interactive Charts** - Plotly visualization supporting 3 trading pairs (GBPUSD/EURUSD/BTCUSD)
- 🔍 **Data Quality Control** - Anomaly filtering to ensure clean, noise-free charts
- 🚀 **One-Click Launch** - Desktop shortcut for automatic system startup
- 🚨 **Risk Alert System** - Dynamic alert banners for high-risk scenarios with real-time notifications

## 📸 System Overview

**Real-Time K-Line Charts:**
- Historical trend line (blue): 300 5-minute K-line data points
- MA7 moving average (orange dashed): 7-day short-term trend
- MA30 moving average (red dotted): 30-day long-term trend
- Latest real-time point (green star): current market price

**🛡️ Risk Monitor Panel:**
- Risk level assessment: Minimal/Low/Medium/High/Critical (5-level scoring system 0-100)
- Volatility analysis: current volatility, average volatility, percentile ranking
- Anomaly detection: Z-score based detection with rolling standard deviation (threshold 2.5σ)
- Risk signals: automatic generation of risk warnings and trading recommendations
- Risk factors: real-time summary of market-impacting risk factors
- Alert banners: prominent warnings for medium, high, and critical risk levels

**Supported Trading Pairs:**
- GBP/USD (British Pound / US Dollar)
- EUR/USD (Euro / US Dollar)
- BTC/USD (Bitcoin / US Dollar)

## 🔐 Security - API Key Setup

### ⚠️ Important: Never commit your API keys to Git!

1. For AI summary we currently use DeepSeek. **Get your DeepSeek API Key** from https://platform.deepseek.com
2. **Set it as an environment variable** (Windows):
  ```powershell
  setx DEEPSEEK_API_KEY "sk-your-deepseek-key"
  ```
3. **Restart PowerShell** for changes to take effect
4. **Verify** the key is set:
  ```powershell
  echo $env:DEEPSEEK_API_KEY
  ```

Alternatively, use a `.env` file:
1. Copy `.env.example` to `.env`
2. Edit `.env` with your actual API key
3. `.env` is in `.gitignore` and will never be committed

## 🎯 Technical Architecture

**Data Flow:**
```
Tick Data Collection (every 5s) → K-line Generation (5-min OHLC) → SQLite Storage → Flask API → Dash Visualization
```

**Core Modules:**
- `kline_generator.py` - K-line generator, collects ticks and generates OHLC data
- `risk_engine.py` - Risk engine, volatility analysis and anomaly detection
- `api.py` - Flask REST API, provides historical data and real-time price queries
- `dashboard/app.py` - Dash interactive frontend, charts display, AI analysis, and risk monitoring
- `database.py` - SQLite database operations with anomaly filtering
- `fetch_data.py` - yfinance data source interface (with simulated data fallback)
- `ai_summary.py` - AI market analysis, calls DeepSeek API
- `ai_usage.py` - API usage rate control (daily limit + cooldown)

## 📂 Project Structure

```
financial-data-pipeline/
├── src/
│   ├── kline_generator.py   # K-line generator (core module)
│   ├── risk_engine.py       # Risk engine (volatility + anomaly detection)
│   ├── api.py               # Flask REST API
│   ├── database.py          # SQLite database operations + anomaly filtering
│   ├── fetch_data.py        # yfinance data source (with simulated data fallback)
│   ├── ai_summary.py        # AI market analysis
│   └── ai_usage.py          # API usage rate control
├── dashboard/
│   └── app.py               # Dash interactive frontend
├── data/
│   ├── market.db            # SQLite database
│   └── ai_usage.json        # AI API usage tracking
├── fill_history.py          # Historical data fill tool
├── fill_history.ps1         # Batch fill script
├── test_risk.py             # Risk analysis testing tool
├── start_all.ps1            # One-click startup script
├── stop_all.ps1             # Stop all services
├── clean_database.ps1       # Database cleanup tool
├── backup_database.ps1      # Database backup utility
├── check_database.ps1       # Database health check
├── create_desktop_shortcuts.ps1  # Create desktop shortcuts
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (local config, gitignored)
├── DATABASE_GUIDE.md        # Database management guide
├── KLINE_GUIDE.md          # K-line generator detailed documentation
└── QUICK_REFERENCE.md      # Quick reference card
```

## 🚀 Quick Start

### Requirements

- Python 3.10+
- Windows PowerShell (recommended)
- Network connection (for fetching market data)

### 1. Install Dependencies

```powershell
# Clone repository
git clone https://github.com/Leo666xx/financial-data-pipeline.git
cd financial-data-pipeline

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file (or use setx command):

```bash
# DeepSeek API Key (for AI market analysis)
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# Optional: API usage limits (defaults will be used if not set)
MAX_CALLS_PER_DAY=20        # Maximum daily API calls
SUMMARY_COOLDOWN_SEC=300    # Cooldown between calls (seconds)
```

**Get API Key:** https://platform.deepseek.com

### 3. Fill Historical Data (Recommended)

```powershell
# Fill all symbols with one command (300 K-lines each)
.\fill_history.ps1

# Or fill a specific symbol
python fill_history.py --symbol GBPUSD --bars 300
```

### 4. Create Desktop Shortcuts

```powershell
.\create_desktop_shortcuts.ps1
```

### 5. Start System

**Method 1: Desktop Shortcut (Recommended)**
- Double-click the "Financial Dashboard" shortcut on desktop

**Method 2: Command Line**
```powershell
.\start_all.ps1
```

The system will automatically:
1. Check database status
2. Start K-line generator (real-time collection)
3. Start Flask API (background)
4. Start Dashboard (background)
5. Open browser (http://localhost:8050)

### 6. Stop System

```powershell
.\stop_all.ps1
```

## 📊 Usage Guide

### Dashboard Features

After accessing http://localhost:8050, you can:

1. **Select Trading Pair**
   - Use dropdown menu: GBPUSD / EURUSD / BTCUSD

2. **View Real-Time Charts**
   - Blue line: Historical K-line data (5-minute interval, latest 300 bars)
   - Orange dashed: MA7 moving average (7-day short-term trend)
   - Red dotted: MA30 moving average (30-day long-term trend)
   - Green star: Latest real-time price

3. **Refresh Data**
   - Click "Refresh Data" button to fetch latest K-line data

4. **AI Market Analysis**
   - Click "Refresh Analysis" button to generate AI market commentary
   - Automatically analyzes recent 7-day price trends
   - Output in English, approximately 150-200 words

### Data Quality Assurance

System automatically filters anomalous data:
- **GBPUSD/EURUSD**: Only accepts prices in range 0.5-3.0
- **BTCUSD**: Only accepts prices in range 1000-1000000
- **All symbols**: Rejects None, 0, negative values

### K-Line Generation Logic

**Collection Process:**
```
Collect tick every 5 seconds → Accumulate into 5-minute bucket → Generate OHLC
```

**OHLC Calculation:**
- Open: First tick in the 5-minute period
- High: Maximum tick in the 5-minute period
- Low: Minimum tick in the 5-minute period
- Close: Last tick in the 5-minute period

For detailed explanation, see [KLINE_GUIDE.md](KLINE_GUIDE.md)

### 🛡️ 风险引擎 (Risk Engine)

**核心功能：**
1. **滚动标准差异常检测** - 基于20周期滚动窗口，检测价格异常波动
2. **波动率分析** - 计算当前波动率、平均波动率、百分位排名
3. **Z-score异常检测** - 标准化价格偏离度，阈值2.5倍标准差
4. **风险等级评估** - 5级评分系统（极低/低/中/高/严重）
5. **风险信号生成** - 自动生成风险警告和操作建议

**风险指标：**
- **风险评分**：0-100分综合评分
  - 0-10: 极低风险 🟢
  - 10-30: 低风险 🟡
  - 30-50: 中等风险 🟠
  - 50-70: 高风险 🔴
  - 70+: 严重风险 🚨

- **波动率分析**：
  - 当前波动率（基于收益率标准差）
  - 历史平均波动率
  - 波动率百分位（在历史分布中的位置）
  - 高波动率警告（阈值：1.5%）

- **异常检测**：
  - Z-score偏离度（标准化偏离指标）
  - 异常点计数（超过2.5倍标准差）
  - 异常价格列表

**Using Risk Engine:**

```python
# Method 1: Use command-line tool
python test_risk.py --symbol GBPUSD

# Method 2: Compare multiple symbols
python test_risk.py --compare

# Method 3: Use in code
from src.risk_engine import RiskEngine, analyze_risk

prices = [1.27, 1.271, 1.269, ...]  # Price series
report = analyze_risk(prices, symbol='GBPUSD')

print(f"Risk Level: {report['summary']['risk_level']}")
print(f"Risk Score: {report['summary']['risk_score']}/100")
```

**Dashboard Integration:**
- Dashboard automatically displays risk monitoring panel in real-time
- Risk analysis updates automatically on data refresh
- Color coding: Green (safe) → Yellow (caution) → Orange (warning) → Red (danger)
- Risk signals automatically suggest trading recommendations

## 📡 API Documentation

### 1. 健康检查

```http
GET http://localhost:5000/
```

**返回示例:**
```json
{
  "message": "Hello — Flask API is running!",
  "status": "ok"
}
```

### 2. 获取最新价格

```http
GET http://localhost:5000/price?symbol=GBPUSD
```

**返回示例:**
```json
{
  "symbol": "GBPUSD",
  "timestamp": "2025-11-29T15:23:33.036512",
  "price": 1.2697
}
```

### 3. 获取历史数据

```http
GET http://localhost:5000/history?symbol=GBPUSD&limit=300
```

**参数:**
- `symbol`: 交易品种（GBPUSD/EURUSD/BTCUSD）
- `limit`: 返回数据条数（可选，默认500）

**返回示例:**
```json
{
  "symbol": "GBPUSD",
  "data": [
    {"timestamp": "2025-11-29T14:30:00", "price": 1.2695},
    {"timestamp": "2025-11-29T14:35:00", "price": 1.2697},
    ...
  ]
}
```

## 🗄️ Database Structure

### prices Table

```sql
CREATE TABLE prices (
    timestamp TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    PRIMARY KEY (timestamp, symbol)
);

CREATE INDEX idx_prices_symbol_timestamp 
ON prices(symbol, timestamp);
```

**Supported Trading Pairs:**

| Pair | Symbol | Description |
|------|--------|-------------|
| GBP/USD | `GBPUSD` | British Pound / US Dollar |
| EUR/USD | `EURUSD` | Euro / US Dollar |
| BTC/USD | `BTCUSD` | Bitcoin / US Dollar |

## 🛠️ Development Guide

### Tech Stack

- **Flask 2.3+** - 轻量级Web框架
- **Dash >=2.15** - 交互式数据可视化
- **Plotly** - 图表库
- **yfinance** - Yahoo Finance数据源
- **SQLite3** - 嵌入式数据库
- **OpenAI SDK** - DeepSeek API客户端
- **python-dotenv** - 环境变量管理

### Core Modules

**1. K-line Generator (`kline_generator.py`)**
```python
# Start K-line generator
python src/kline_generator.py

# Custom parameters
python src/kline_generator.py --symbols GBPUSD EURUSD --tick-interval 5 --kline-interval 300
```

**2. Flask API (`api.py`)**
```python
# Start API server (default port 5000)
python src/api.py
```

**3. Dashboard (`dashboard/app.py`)**
```python
# Start Dashboard (default port 8050)
python dashboard/app.py
```

**4. Database Tools (`database.py`)**
```python
# Clear all data
python src/database.py clear

# Clean anomalous data (keep valid data)
python src/database.py clean
```

**5. Historical Data Fill (`fill_history.py`)**
```python
# Fill 300 historical K-lines
python fill_history.py --symbol GBPUSD --bars 300

# Use simulated data
python fill_history.py --symbol GBPUSD --bars 300 --simulated
```

**6. Risk Engine (`test_risk.py`)**
```python
# Analyze single symbol risk
python test_risk.py --symbol GBPUSD

# Compare all symbol risks
python test_risk.py --compare

# Limit data points (faster analysis)
python test_risk.py --symbol EURUSD --limit 100
```

**Risk Engine Output Example:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Risk Analysis Report - GBPUSD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛡️ Risk Summary:
  • Risk Level: MEDIUM
  • Risk Score: 39/100
  • Analysis Time: 2025-01-16 10:30:45

📈 Volatility Analysis:
  • Current Volatility: 0.0011 (0.11%)
  • Average Volatility: 0.0010 (0.10%)
  • Volatility Percentile: 55% (historical mid-level)
  • High Volatility Alert: No

🔍 Anomaly Detection:
  • Z-score Deviation: 1.23 standard deviations
  • Anomaly Count: 5 points (1.67%)
  • Anomalies Detected: Yes

⚠️ Risk Signals:
  1. [PRICE_ANOMALY] Price deviation: Z-score=1.23 → Advice: Monitor price movement
  2. [HIGH_VOLATILITY] Volatility increase → Advice: Reduce position size

🎯 Overall Recommendation:
  • Medium risk level, trade with caution
  • Volatility at normal levels
  • Detected 5 anomalous price points, recommend monitoring
```

## 🎯 Features Implemented

### ✅ Core Features
- [x] K-line generator (tick collection → OHLC generation)
- [x] Anomaly filtering (data quality control)
- [x] Flask REST API (/price, /history endpoints)
- [x] Dash interactive Dashboard
- [x] Plotly chart visualization
- [x] MA7/MA30 technical indicators
- [x] AI market analysis (DeepSeek integration)
- [x] API usage rate control (daily quota + cooldown)
- [x] SQLite data persistence
- [x] Historical data fill tool
- [x] One-click startup script
- [x] Desktop shortcuts
- [x] Risk engine with volatility analysis
- [x] Real-time risk monitoring dashboard
- [x] Database backup and health check utilities

### 🔄 Potential Extensions
- [ ] Support more K-line periods (1min, 15min, 1hour)
- [ ] Complete OHLC table (separate storage for OHLC)
- [ ] More technical indicators (MACD, RSI, Bollinger Bands)
- [ ] Price alert functionality
- [ ] Historical backtesting
- [ ] Docker containerized deployment
- [ ] Web user authentication

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# DeepSeek API Key (required)
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# AI usage limits (optional)
MAX_CALLS_PER_DAY=20           # Maximum daily API calls (default 20)
SUMMARY_COOLDOWN_SEC=300       # Cooldown between calls in seconds (default 300=5min)
```

### Configuration Parameters

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | ✅ Yes | - | DeepSeek API key from https://platform.deepseek.com |
| `MAX_CALLS_PER_DAY` | ⚪ No | `20` | Daily AI call limit, resets at UTC midnight |
| `SUMMARY_COOLDOWN_SEC` | ⚪ No | `300` | Minimum interval between consecutive calls (seconds) to prevent overuse |

## 🤖 AI Market Analysis

### Technical Implementation

Using **DeepSeek API** (via OpenAI-compatible SDK):
- **API Endpoint**: `https://api.deepseek.com/v1`
- **Model**: `deepseek-reasoner`
- **Data Source**: Recent 7-day price history from SQLite database
- **Output Format**: Market commentary (150-200 words) with trend analysis, technical indicator interpretation, and trading recommendations

### 使用率控制

为降低API成本并防止配额耗尽，实现了**三层保护机制**：

#### 1️⃣ 客户端缓存（30分钟）
- AI分析结果在Dashboard中缓存30分钟
- 自动刷新页面时使用缓存，无需调用API
- 需手动点击"刷新分析"按钮绕过缓存

#### 2️⃣ 每日配额限制
- 通过 `MAX_CALLS_PER_DAY` 配置（默认：20次/天）
- 计数器在UTC午夜重置
- When limit reached: display cached content + estimated wait time
- Usage data persisted to `data/ai_usage.json`

#### 3️⃣ Cooldown Period
- Configured via `SUMMARY_COOLDOWN_SEC` (default: 300 seconds = 5 minutes)
- Enforces minimum interval between consecutive calls
- During cooldown: display cached content + remaining wait time

### User Experience

**When call allowed**: Generate and display latest AI analysis  
**When rate limited**:
- ✅ With cache: Show cached analysis + friendly message (e.g., "Cooling down, refresh available in ~3 minutes")
- ❌ No cache: Show wait message (e.g., "Daily AI quota reached, please try again in ~5 hours")

**Manual control**: User must explicitly click "Refresh Analysis" button to trigger AI call, preventing accidental usage.

## ❓ FAQ

### Q: Dashboard shows "No historical data"?
**A:** You need to fill historical data first:
```powershell
.\fill_history.ps1
```
Or manually fill:
```powershell
python fill_history.py --symbol GBPUSD --bars 300
```

### Q: Which trading pairs are supported?
**A:** Currently supports 3 pairs:
- GBPUSD (British Pound / US Dollar)
- EURUSD (Euro / US Dollar)  
- BTCUSD (Bitcoin / US Dollar)

You can add more pairs by modifying `SYMBOL_MAP` in `fetch_data.py`.

### Q: How to change K-line period?
**A:** Edit startup parameters in `kline_generator.py`:
```python
# Change from 5 minutes to 15 minutes
python src/kline_generator.py --kline-interval 900
```
Also need to modify `resample_to_low_frequency` function in `dashboard/app.py`.

### Q: yfinance无法获取数据怎么办？
**A:** 系统会自动切换到模拟数据生成模式，或手动指定：
```powershell
python fill_history.py --symbol GBPUSD --bars 300 --simulated
```

### Q: AI分析提示"余额不足"？
**A:** 需要为DeepSeek账户充值，或暂时关闭AI功能（Dashboard仍可正常显示图表）。

### Q: 如何清空数据库重新开始？
**A:** 使用数据库清理工具：
```powershell
# 清空所有数据
python src/database.py clear

# 或使用交互式脚本
.\clean_database.ps1
```

### Q: 数据多久更新一次？
**A:** K线生成器每5秒采集一次tick，每5分钟生成一根K线。Dashboard可手动点击"刷新数据"获取最新数据。

### Q: 可以部署到服务器吗？
**A:** 可以。推荐使用Gunicorn部署Flask API：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app
```
Dashboard同样可以用 `gunicorn dashboard.app:server` 部署。

## 🚀 Deployment

### Local Development
```powershell
.\start_all.ps1
```

### Production (Linux/Cloud Server)
```bash
# Install dependencies
pip install -r requirements.txt

# Start API
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app &

# Start Dashboard
gunicorn -w 2 -b 0.0.0.0:8050 dashboard.app:server &

# Start K-line generator
nohup python src/kline_generator.py &
```

### Docker Deployment (Future Plan)
Dockerfile and docker-compose.yml to be added

## 📝 Changelog

**v1.0.0** (2025-11-29)
- ✅ Complete K-line generation system (tick collection → OHLC generation)
- ✅ Anomaly filtering mechanism
- ✅ Dash visualization Dashboard
- ✅ MA7/MA30 technical indicators
- ✅ DeepSeek AI market analysis
- ✅ API usage rate control
- ✅ Historical data fill tool
- ✅ One-click startup script
- ✅ Desktop shortcuts
- ✅ Risk engine with volatility analysis and anomaly detection
- ✅ Real-time risk monitoring panel with alert banners
- ✅ Database backup and health check utilities

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 👤 Author

**Leo666xx**

- GitHub: [@Leo666xx](https://github.com/Leo666xx)
- Project URL: https://github.com/Leo666xx/financial-data-pipeline

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📞 Support

For questions or issues, please submit an Issue on GitHub.

## 🙏 Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance data source
- [Dash](https://dash.plotly.com/) - Interactive visualization framework
- [DeepSeek](https://platform.deepseek.com) - AI API service

---

**Last Updated:** 2025-11-30  
**Version:** 1.0.0
