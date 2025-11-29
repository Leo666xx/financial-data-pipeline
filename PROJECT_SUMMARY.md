# Financial Data Analysis System - Project Summary

## 📋 Resume Version (3-4 lines)

**Financial Data Analysis System | Python, Flask, Dash, SQLite**
• Built real-time financial dashboard with automated K-line generation (OHLC candlesticks) from Yahoo Finance API, processing tick data every 5 seconds and generating 5-minute interval charts with MA7/MA30 technical indicators
• Implemented AI-powered market analysis using DeepSeek API with rate limiting and caching, and developed risk engine with rolling standard deviation anomaly detection (Z-score threshold 2.5σ) for volatility monitoring
• Designed comprehensive risk alert system with 5-level scoring (0-100), real-time anomaly detection, and dynamic alert banners for high-risk scenarios (GBPUSD, EURUSD, BTCUSD trading pairs)

---

## 🎯 Project Overview

A production-ready financial data pipeline featuring:
- **Real-time data collection** from Yahoo Finance API
- **Automated K-line generation** with OHLC candlestick charts
- **AI-powered market analysis** using DeepSeek large language model
- **Advanced risk engine** with statistical anomaly detection
- **Interactive dashboard** with Plotly visualizations
- **Alert system** for high-risk market conditions

---

## 💻 Technical Stack

**Backend:**
- Python 3.x
- Flask 2.3+ (REST API)
- SQLite3 (embedded database)
- yfinance (market data source)

**Frontend:**
- Dash 2.15+ (interactive UI framework)
- Plotly (data visualization)
- HTML/CSS with custom animations

**AI/ML:**
- DeepSeek API (LLM integration)
- NumPy (statistical computations)
- Custom risk engine with rolling statistics

**DevOps:**
- PowerShell automation scripts
- Environment variable management
- One-click deployment

---

## 🔥 Key Technical Achievements

### 1. **Real-Time K-Line Generation**
- Collects tick data every 5 seconds
- Aggregates into 5-minute OHLC candlesticks
- Implements data quality filters (anomaly detection at ingestion)
- Stores 300+ historical data points per symbol

### 2. **Risk Engine with Statistical Analysis**
- Rolling standard deviation (20-period window)
- Z-score anomaly detection (2.5σ threshold)
- Volatility percentile ranking
- 5-level risk classification (Minimal → Critical)
- Real-time risk signal generation

### 3. **AI Market Commentary**
- DeepSeek API integration with error handling
- Rate limiting (20 calls/day, 5-min cooldown)
- Smart caching (30-minute TTL)
- Graceful degradation on API failures

### 4. **Dynamic Alert System**
- Real-time risk level monitoring
- Color-coded alert banners
- CSS animations for critical warnings
- Prioritized signal display (top 3 alerts)

### 5. **Production-Ready Features**
- Comprehensive error handling
- Database connection pooling
- API retry logic with exponential backoff
- Environment-based configuration
- Automated service management scripts

---

## 📊 Data Flow Architecture

```
┌─────────────────┐
│  Yahoo Finance  │
│      API        │
└────────┬────────┘
         │ (tick data every 5s)
         ▼
┌─────────────────┐
│ K-line Generator│
│   (OHLC calc)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SQLite DB     │
│  (market.db)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask API     │
│  (port 5000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│        Dash Dashboard            │
│  ┌──────────────────────────┐  │
│  │  Price Chart (Plotly)    │  │
│  │  - MA7/MA30 indicators   │  │
│  │  - Real-time updates     │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  AI Market Analysis      │  │
│  │  - DeepSeek API          │  │
│  │  - Smart caching         │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  Risk Monitor Panel      │  │
│  │  - Alert banners         │  │
│  │  - Risk signals          │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
         (port 8050)
```

---

## 🛠️ Implementation Highlights

### Data Quality Control
```python
def is_valid_price(price, symbol):
    """Validates price ranges per symbol to filter anomalies"""
    if 'GBPUSD' in symbol or 'EURUSD' in symbol:
        return 0.5 < price < 3.0  # Forex pairs
    elif 'BTCUSD' in symbol:
        return 1000 < price < 1000000  # Crypto
    return price > 0
```

### Risk Detection Algorithm
```python
# Rolling standard deviation with Z-score
z_score = (current_price - rolling_mean) / rolling_std
is_anomaly = abs(z_score) > 2.5  # 2.5σ threshold

# Risk scoring (0-100)
risk_score = (
    volatility_percentile * 0.4 +
    anomaly_penalty * 0.3 +
    z_score_penalty * 0.3
)
```

### AI Rate Limiting
```python
# Daily quota + cooldown period
can_call(max_calls_per_day=20, cooldown_sec=300)
# Returns: (allowed, reason, wait_seconds)
```

---

## 📈 Supported Trading Pairs

| Symbol | Full Name | Asset Class |
|--------|-----------|-------------|
| GBPUSD | British Pound / US Dollar | Forex |
| EURUSD | Euro / US Dollar | Forex |
| BTCUSD | Bitcoin / US Dollar | Cryptocurrency |

---

## 🚀 Quick Start

```powershell
# Clone repository
git clone https://github.com/Leo666xx/financial-data-pipeline.git
cd financial-data-pipeline

# Set up environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure API key
setx DEEPSEEK_API_KEY "your-api-key-here"

# Launch all services
.\start_all.ps1

# Access dashboard
# http://localhost:8050
```

---

## 📊 Performance Metrics

- **Data Collection**: 5-second intervals, 12 ticks/minute
- **K-line Generation**: 5-minute OHLC aggregation
- **API Response Time**: <100ms (historical data queries)
- **Dashboard Refresh**: Manual refresh (optimized for API usage)
- **Database Size**: ~1MB per 10,000 data points
- **Risk Analysis**: Real-time processing (<50ms)

---

## 🔐 Security & Best Practices

- ✅ Environment variables for sensitive data (no hardcoded API keys)
- ✅ .env file support with .gitignore protection
- ✅ API rate limiting to prevent quota exhaustion
- ✅ Input validation on all data ingestion points
- ✅ SQL injection prevention (parameterized queries)
- ✅ Error handling with graceful degradation
- ✅ Comprehensive logging for debugging

---

## 📚 Learning Outcomes

**Technical Skills:**
- Real-time data pipeline architecture
- RESTful API design and implementation
- Time-series data processing
- Statistical analysis for anomaly detection
- LLM API integration
- Interactive data visualization
- Production deployment practices

**Problem-Solving:**
- Handling API rate limits and failures
- Data quality control and anomaly filtering
- Real-time performance optimization
- State management in dashboards
- Cross-module integration

---

## 🎓 Suitable For

- **Resume/Portfolio**: Demonstrates full-stack development, API integration, data engineering
- **Interview Discussions**: Rich technical depth across multiple domains
- **Further Development**: Extensible architecture for additional features
- **Learning Reference**: Well-documented codebase with clear patterns

---

## 🔗 Repository

**GitHub**: https://github.com/Leo666xx/financial-data-pipeline
**License**: MIT
**Status**: Production-ready, actively maintained

---

## 📞 Contact

For questions or collaboration opportunities regarding this project, please refer to the GitHub repository or contact through GitHub profile.
