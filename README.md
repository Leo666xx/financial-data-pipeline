# Financial Data Pipeline

A Flask-based financial data API for fetching and managing financial market data (such as forex exchange rates).

## 🔐 Security - API Key Setup

### ⚠️ Important: Never commit your API keys to Git!

1. **Get your OpenAI API Key** from https://platform.openai.com/api/keys
2. **Set it as an environment variable** (Windows):
   ```powershell
   setx OPENAI_API_KEY "sk-proj-your-actual-key"
   ```
3. **Restart PowerShell** for changes to take effect
4. **Verify** the key is set:
   ```powershell
   echo $env:OPENAI_API_KEY
   ```

Alternatively, use `.env` file:
1. Copy `.env.example` to `.env`
2. Edit `.env` with your actual API key
3. `.env` is in `.gitignore` and will never be committed

## 🎯 Features

- 📊 **Price Query Interface** - Query the latest prices of financial assets by symbol
- 🗄️ **SQLite Database** - Store price data using SQLite
- 🚀 **Flask REST API** - Clean and simple RESTful API design
- 🔄 **Automatic Symbol Mapping** - Support multiple symbol formats (e.g., `GBPUSD` automatically maps to `GBPUSD=X`)
- 🔍 **Real-time Queries** - Support real-time queries for the latest price data
- 📈 **Extensible Architecture** - Easy to add new data sources and interfaces
- 🤖 **AI Market Analysis** - Automatic market summary using OpenAI GPT
- 📉 **Technical Indicators** - 7-day and 30-day moving averages

## 📂 Project Structure

```
financial-data-pipeline/
├── src/
│   ├── api.py              # Flask API main file
│   ├── database.py         # Database operations
│   ├── fetch_data.py       # Data collection module
│   ├── ingest.py           # Data import module
│   ├── models.py           # Data models
│   └── hello.py            # Test script
├── data/
│   └── (Databases and CSV files will be stored here)
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore file
├── LICENSE                # MIT License
└── README.md              # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start API Server

```bash
python src/api.py
```

The server will start at `http://localhost:5000`.

## 📡 API Documentation

### 1. Health Check - Root Route

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

**cURL Example:**
```bash
curl http://localhost:5000/
```

---

### 2. Price Query Interface

```http
GET http://localhost:5000/price?symbol=GBPUSD
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | No | GBPUSD | Financial asset code |

**Success Response (200):**
```json
{
  "symbol": "GBPUSD",
  "timestamp": "2025-11-28T14:08:31.784065",
  "price": 1.3228038549423218
}
```

**Error Response (404):**
```json
{
  "error": "No data found"
}
```

**cURL Examples:**
```bash
# Query GBPUSD exchange rate
curl "http://localhost:5000/price?symbol=GBPUSD"

# Using Python requests
python -c "import requests; print(requests.get('http://localhost:5000/price?symbol=GBPUSD').json())"
```

---

## 🗄️ Database Architecture

### prices Table

```sql
CREATE TABLE prices (
    timestamp TEXT NOT NULL,      -- ISO 8601 timestamp
    symbol TEXT NOT NULL,         -- Financial asset code (e.g., GBPUSD=X)
    price REAL NOT NULL           -- Price value
);
```

**Field Descriptions:**
- **timestamp** - ISO 8601 formatted timestamp (UTC), precise to milliseconds. Example: `2025-11-28T14:08:31.784065`
- **symbol** - Financial asset code. Stored in the database as `GBPUSD=X` format, but API supports `GBPUSD` alias query
- **price** - Asset price, floating point number. Example: `1.3228038549423218`

### Supported Symbols

| Symbol | Database Storage | API Query | Description |
|--------|-----------------|-----------|-------------|
| GBP/USD | `GBPUSD=X` | `GBPUSD` | British Pound to US Dollar exchange rate |

## 🛠️ Developer Guide

### Project Dependencies

- **Flask** - Lightweight web framework
- **yfinance** - Financial data from Yahoo Finance
- **pandas** - Data manipulation and analysis
- **requests** - HTTP client library
- **sqlite3** - Embedded database (Python standard library)

### Debug Mode

The API runs in debug mode by default, supporting hot reload. The server automatically restarts when code changes.

```bash
# Enable debug mode
python src/api.py
```

### Project Architecture

- `api.py` - Flask application entry point, defines API routes and business logic
- `database.py` - Database connections and query operations
- `fetch_data.py` - Data source integration (e.g., yfinance)
- `models.py` - Data models and ORM
- `ingest.py` - Data import and initialization

## 📈 Roadmap

### Phase 1: Core Features ✅
- [x] Flask API basic framework
- [x] SQLite database integration
- [x] Single symbol price query
- [x] Project documentation

### Phase 2: Feature Extensions (Planned)
- [ ] Support multiple symbol batch queries
- [ ] Support historical data queries (time range)
- [ ] Automatic scheduled task: fetch latest prices every hour
- [ ] Support more asset types (cryptocurrencies, stocks, futures, etc.)
- [ ] Data caching and performance optimization
- [ ] Error handling and logging

### Phase 3: Application Layer (Later)
- [ ] Frontend Web UI (React/Vue)
- [ ] Data visualization and charts
- [ ] Price alert functionality
- [ ] User authentication and API keys
- [ ] Deploy to cloud (AWS/Azure/Heroku)
- [ ] Docker containerization

### Phase 4: Operations and Monitoring (Long-term)
- [ ] Database backup and recovery
- [ ] Monitoring dashboard
- [ ] Performance optimization and load testing
- [ ] Microservices separation

## 🔧 Configuration and Environment Variables

To customize settings, create a `.env` file (already ignored in `.gitignore`):

```bash
# .env file example
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_PATH=data/market.db
API_PORT=5000
API_HOST=0.0.0.0
```

## ❓ FAQ

### Q: How do I initialize the database?
A: Run the `src/ingest.py` script to initialize the database and import sample data.

### Q: Which symbols are supported?
A: Currently `GBPUSD` is supported. You can add more data sources by modifying `fetch_data.py`.

### Q: How do I query historical data?
A: The current version only supports querying the latest price. Historical data query functionality is planned for Phase 2 roadmap.

### Q: What is the data update frequency?
A: Currently, you need to manually run `fetch_data.py` to update. Automatic scheduled updates are planned for Phase 2.

## 🚀 Deployment

### Local Development

```bash
python src/api.py
```

### Production Environment (Using Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app
```

### Docker Deployment (Planned)

```dockerfile
# Dockerfile will be added in the future
```

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👤 Author

**Leo666xx**

- GitHub: [@Leo666xx](https://github.com/Leo666xx)
- Email: (optional)

## 🤝 Contributing

We welcome issues and pull requests!

## 📞 Support

If you have any questions, please submit an issue on GitHub.

---

**Last Updated:** 2025-11-28  
**Version:** 1.0.0
