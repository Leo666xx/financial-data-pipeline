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

## 🔄 Auto-Update

The system can automatically check for updates from GitHub and restart services.

**One-time Setup:**
```powershell
.\setup_auto_update.ps1
```

This creates a scheduled task that checks for updates every 6 hours.

**Manual Update:**
```powershell
.\auto_update.ps1
```

**Disable Auto-Update:**
```powershell
Disable-ScheduledTask -TaskName "FinancialDashboard_AutoUpdate"
```

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

### 🛡️ Risk Engine

**Core Features:**
1. **Rolling Standard Deviation Anomaly Detection** - Based on 20-period rolling window, detects abnormal price fluctuations
2. **Volatility Analysis** - Calculates current volatility, average volatility, percentile ranking
3. **Z-score Anomaly Detection** - Standardized price deviation, threshold 2.5 standard deviations
4. **Risk Level Assessment** - 5-level scoring system (Minimal/Low/Medium/High/Critical)
5. **Risk Signal Generation** - Automatically generates risk warnings and trading recommendations

**Risk Indicators:**
- **Risk Score**: 0-100 composite score
  - 0-10: Minimal Risk 🟢
  - 10-30: Low Risk 🟡
  - 30-50: Medium Risk 🟠
  - 50-70: High Risk 🔴
  - 70+: Critical Risk 🚨

- **Volatility Analysis**:
  - Current volatility (based on return standard deviation)
  - Historical average volatility
  - Volatility percentile (position in historical distribution)
  - High volatility alert (threshold: 1.5%)

- **Anomaly Detection**:
  - Z-score deviation (standardized deviation indicator)
  - Anomaly count (exceeding 2.5 standard deviations)
  - Anomalous price list

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

### 1. Health Check

```http
GET http://localhost:5000/
```

**Response Example:**
```json
{
  "message": "Hello — Flask API is running!",
  "status": "ok"
}
```

### 2. Get Latest Price

```http
GET http://localhost:5000/price?symbol=GBPUSD
```

**Response Example:**
```json
{
  "symbol": "GBPUSD",
  "timestamp": "2025-11-29T15:23:33.036512",
  "price": 1.2697
}
```

### 3. Get Historical Data

```http
GET http://localhost:5000/history?symbol=GBPUSD&limit=300
```

**Parameters:**
- `symbol`: Trading pair (GBPUSD/EURUSD/BTCUSD)
- `limit`: Number of records to return (optional, default 500)

**Response Example:**
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

- **Flask 2.3+** - Lightweight web framework
- **Dash >=2.15** - Interactive data visualization
- **Plotly** - Chart library
- **yfinance** - Yahoo Finance data source
- **SQLite3** - Embedded database
- **OpenAI SDK** - DeepSeek API client
- **python-dotenv** - Environment variable management

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

### Usage Rate Control

To reduce API costs and prevent quota exhaustion, implemented **three-layer protection**:

#### 1️⃣ Client-Side Caching (30 minutes)
- AI analysis results cached in Dashboard for 30 minutes
- Automatic page refreshes use cache without API calls
- Manual "Refresh Analysis" button required to bypass cache

#### 2️⃣ Daily Quota Limit
- Configured via `MAX_CALLS_PER_DAY` (default: 20 calls/day)
- Counter resets at UTC midnight
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

### Q: What if yfinance cannot fetch data?
**A:** System will automatically switch to simulated data generation mode, or manually specify:
```powershell
python fill_history.py --symbol GBPUSD --bars 300 --simulated
```

### Q: AI analysis shows "Insufficient balance"?
**A:** Need to top up DeepSeek account, or temporarily disable AI feature (Dashboard will still display charts normally).

### Q: How to clear database and start fresh?
**A:** Use database cleanup tool:
```powershell
# Clear all data
python src/database.py clear

# Or use interactive script
.\clean_database.ps1
```

### Q: How often does data update?
**A:** K-line generator collects ticks every 5 seconds and generates one K-line every 5 minutes. Dashboard can manually click "Refresh Data" to get latest data.

### Q: Can it be deployed to a server?
**A:** Yes. Recommended to use Gunicorn for Flask API deployment:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app
```
Dashboard can also be deployed with `gunicorn dashboard.app:server`.

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
