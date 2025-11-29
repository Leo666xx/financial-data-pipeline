# Financial Data Pipeline

一个完整的金融数据分析系统，包含实时数据采集、K线生成、技术指标计算和AI市场分析。

## ✨ 核心特性

- 📊 **K线数据生成** - 每5秒采集tick数据，自动生成5分钟K线（OHLC）
- 📈 **技术指标** - MA7/MA30移动平均线，自动计算并可视化
- 🤖 **AI市场分析** - 集成DeepSeek API，生成中文市场点评
- 🎨 **交互式图表** - Plotly可视化，支持3个交易品种（GBPUSD/EURUSD/BTCUSD）
- 🛡️ **数据质量控制** - 异常值过滤，确保图表清晰无噪音
- 🚀 **一键启动** - 桌面快捷方式，自动启动完整系统

## 📸 系统展示

**实时K线图表：**
- 历史趋势线（蓝色）：300条5分钟K线数据
- MA7移动平均（橙色虚线）：7日短期趋势
- MA30移动平均（红色点线）：30日长期趋势
- 最新实时点（绿色星标）：当前市场价格

**支持的交易品种：**
- GBP/USD（英镑/美元）
- EUR/USD（欧元/美元）
- BTC/USD（比特币/美元）

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

## 🎯 技术架构

**数据流：**
```
Tick数据采集(5秒/次) → K线生成(5分钟/根) → SQLite存储 → Flask API → Dash可视化
```

**核心模块：**
- `kline_generator.py` - K线生成器，采集tick并生成OHLC数据
- `api.py` - Flask REST API，提供历史数据和实时价格查询
- `dashboard/app.py` - Dash交互式前端，图表展示和AI分析
- `database.py` - SQLite数据库操作，包含异常值过滤
- `fetch_data.py` - yfinance数据源接口（支持模拟数据备选）
- `ai_summary.py` - AI市场分析，调用DeepSeek API
- `ai_usage.py` - API使用率控制（每日限额+冷却时间）

## 📂 项目结构

```
financial-data-pipeline/
├── src/
│   ├── kline_generator.py   # K线生成器（核心模块）
│   ├── api.py               # Flask REST API
│   ├── database.py          # SQLite数据库操作 + 异常值过滤
│   ├── fetch_data.py        # yfinance数据源（含模拟数据备选）
│   ├── ai_summary.py        # AI市场分析
│   └── ai_usage.py          # API使用率控制
├── dashboard/
│   └── app.py               # Dash交互式前端
├── data/
│   ├── market.db            # SQLite数据库
│   └── ai_usage.json        # AI API使用记录
├── fill_history.py          # 历史数据填充工具
├── fill_history.ps1         # 批量填充脚本
├── start_all.ps1            # 一键启动脚本
├── stop_all.ps1             # 停止所有服务
├── clean_database.ps1       # 数据库清理工具
├── create_desktop_shortcuts.ps1  # 创建桌面快捷方式
├── requirements.txt         # Python依赖
├── .env                     # 环境变量（本地配置，已忽略）
└── KLINE_GUIDE.md          # K线生成器详细文档
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Windows PowerShell（推荐）
- 网络连接（用于获取市场数据）

### 1. 安装依赖

```powershell
# 克隆仓库
git clone https://github.com/Leo666xx/financial-data-pipeline.git
cd financial-data-pipeline

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（或使用 setx 命令）：

```bash
# DeepSeek API Key（用于AI市场分析）
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# 可选：API使用限制（不设置则使用默认值）
MAX_CALLS_PER_DAY=20        # 每日最大调用次数
SUMMARY_COOLDOWN_SEC=300    # 两次调用间隔（秒）
```

**获取API Key：** https://platform.deepseek.com

### 3. 填充历史数据（推荐）

```powershell
# 一键填充所有品种（每个300条K线）
.\fill_history.ps1

# 或单独填充某个品种
python fill_history.py --symbol GBPUSD --bars 300
```

### 4. 创建桌面快捷方式

```powershell
.\create_desktop_shortcuts.ps1
```

### 5. 启动系统

**方式1：桌面快捷方式（推荐）**
- 双击桌面上的 "Financial Dashboard" 快捷方式

**方式2：命令行启动**
```powershell
.\start_all.ps1
```

系统将自动：
1. 清空旧数据
2. 启动K线生成器（实时采集）
3. 启动Flask API（后台）
4. 启动Dashboard（后台）
5. 打开浏览器（http://localhost:8050）

### 6. 停止系统

```powershell
.\stop_all.ps1
```

## 📊 使用说明

### Dashboard 功能

访问 http://localhost:8050 后，您可以：

1. **选择交易品种**
   - 下拉菜单选择：GBPUSD / EURUSD / BTCUSD

2. **查看实时图表**
   - 蓝色线：历史K线数据（5分钟间隔，最近300条）
   - 橙色虚线：MA7移动平均（7日短期趋势）
   - 红色点线：MA30移动平均（30日长期趋势）
   - 绿色星标：最新实时价格

3. **刷新数据**
   - 点击 "🔄 刷新数据" 按钮获取最新K线数据

4. **AI市场分析**
   - 点击 "🔄 刷新分析" 按钮生成AI市场点评
   - 自动分析最近7天价格趋势
   - 中文输出，约150-200字

### 数据质量保证

系统自动过滤异常数据：
- **GBPUSD/EURUSD**: 只接受 0.5-3.0 范围内的价格
- **BTCUSD**: 只接受 1000-1000000 范围内的价格
- **所有品种**: 拒绝 None、0、负数

### K线生成逻辑

**采集流程：**
```
每5秒采集一次tick → 累积到5分钟桶中 → 生成OHLC
```

**OHLC计算：**
- Open（开盘价）: 该5分钟内第一个tick
- High（最高价）: 该5分钟内最大tick
- Low（最低价）: 该5分钟内最小tick
- Close（收盘价）: 该5分钟内最后一个tick

详细说明请参考 [KLINE_GUIDE.md](KLINE_GUIDE.md)

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

## 🗄️ 数据库结构

### prices 表

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

**支持的交易品种:**

| 品种 | 符号 | 描述 |
|------|------|------|
| GBP/USD | `GBPUSD` | 英镑/美元 |
| EUR/USD | `EURUSD` | 欧元/美元 |
| BTC/USD | `BTCUSD` | 比特币/美元 |

## 🛠️ 开发指南

### 技术栈

- **Flask 2.3+** - 轻量级Web框架
- **Dash >=2.15** - 交互式数据可视化
- **Plotly** - 图表库
- **yfinance** - Yahoo Finance数据源
- **SQLite3** - 嵌入式数据库
- **OpenAI SDK** - DeepSeek API客户端
- **python-dotenv** - 环境变量管理

### 核心模块

**1. K线生成器 (`kline_generator.py`)**
```python
# 启动K线生成器
python src/kline_generator.py

# 自定义参数
python src/kline_generator.py --symbols GBPUSD EURUSD --tick-interval 5 --kline-interval 300
```

**2. Flask API (`api.py`)**
```python
# 启动API服务器（默认端口5000）
python src/api.py
```

**3. Dashboard (`dashboard/app.py`)**
```python
# 启动Dashboard（默认端口8050）
python dashboard/app.py
```

**4. 数据库工具 (`database.py`)**
```python
# 清空所有数据
python src/database.py clear

# 清理异常数据（保留正常数据）
python src/database.py clean
```

**5. 历史数据填充 (`fill_history.py`)**
```python
# 填充300条历史K线
python fill_history.py --symbol GBPUSD --bars 300

# 使用模拟数据
python fill_history.py --symbol GBPUSD --bars 300 --simulated
```

## 🎯 已完成功能

### ✅ 核心功能
- [x] K线生成器（tick采集 → OHLC生成）
- [x] 异常值过滤（数据质量控制）
- [x] Flask REST API（/price, /history端点）
- [x] Dash交互式Dashboard
- [x] Plotly图表可视化
- [x] MA7/MA30技术指标
- [x] AI市场分析（DeepSeek集成）
- [x] API使用率控制（每日限额+冷却时间）
- [x] SQLite数据持久化
- [x] 历史数据填充工具
- [x] 一键启动脚本
- [x] 桌面快捷方式

### 🔄 可扩展功能
- [ ] 支持更多K线周期（1分钟、15分钟、1小时）
- [ ] 完整OHLC表（单独存储开高低收）
- [ ] 更多技术指标（MACD、RSI、布林带）
- [ ] 价格预警功能
- [ ] 历史回测功能
- [ ] Docker容器化部署
- [ ] Web端用户认证

## ⚙️ 配置说明

### 环境变量

在项目根目录创建 `.env` 文件：

```bash
# DeepSeek API Key（必需）
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# AI使用限制（可选）
MAX_CALLS_PER_DAY=20           # 每日最大调用次数（默认20）
SUMMARY_COOLDOWN_SEC=300       # 两次调用间隔秒数（默认300=5分钟）
```

### 配置参数说明

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `DEEPSEEK_API_KEY` | ✅ 是 | - | DeepSeek API密钥，从 https://platform.deepseek.com 获取 |
| `MAX_CALLS_PER_DAY` | ⚪ 否 | `20` | 每日AI调用上限，UTC午夜重置 |
| `SUMMARY_COOLDOWN_SEC` | ⚪ 否 | `300` | 连续调用最小间隔（秒），防止过度使用 |

## 🤖 AI市场分析

### 技术实现

使用 **DeepSeek API**（通过OpenAI兼容SDK）：
- **API端点**: `https://api.deepseek.com/v1`
- **模型**: `deepseek-reasoner`
- **数据来源**: SQLite数据库中最近7天的价格历史
- **输出格式**: 中文市场点评（150-200字），包含趋势分析、技术指标解读和投资建议

### 使用率控制

为降低API成本并防止配额耗尽，实现了**三层保护机制**：

#### 1️⃣ 客户端缓存（30分钟）
- AI分析结果在Dashboard中缓存30分钟
- 自动刷新页面时使用缓存，无需调用API
- 需手动点击"刷新分析"按钮绕过缓存

#### 2️⃣ 每日配额限制
- 通过 `MAX_CALLS_PER_DAY` 配置（默认：20次/天）
- 计数器在UTC午夜重置
- 达到限制时：显示缓存内容 + 等待时间估算
- 使用数据持久化到 `data/ai_usage.json`

#### 3️⃣ 冷却时间
- 通过 `SUMMARY_COOLDOWN_SEC` 配置（默认：300秒 = 5分钟）
- 强制连续调用之间的最小间隔
- 冷却期间：显示缓存内容 + 剩余等待时间

### 用户体验

**允许调用时**: 生成并显示最新AI分析  
**限流时**:
- ✅ 有缓存：显示缓存分析 + 友好提示（如 "冷却中，约 3 分钟后可再刷新"）
- ❌ 无缓存：显示等待提示（如 "今日 AI 调用次数已用完，请约 5 小时后再试"）

**手动控制**: 用户需明确点击"🔄 刷新分析"按钮触发AI调用，防止意外使用。

## ❓ 常见问题

### Q: Dashboard显示"无历史数据"？
**A:** 需要先填充历史数据：
```powershell
.\fill_history.ps1
```
或手动填充：
```powershell
python fill_history.py --symbol GBPUSD --bars 300
```

### Q: 支持哪些交易品种？
**A:** 当前支持3个品种：
- GBPUSD（英镑/美元）
- EURUSD（欧元/美元）  
- BTCUSD（比特币/美元）

可通过修改 `fetch_data.py` 中的 `SYMBOL_MAP` 添加更多品种。

### Q: 如何修改K线周期？
**A:** 编辑 `kline_generator.py` 中的启动参数：
```python
# 将5分钟改为15分钟
python src/kline_generator.py --kline-interval 900
```
同时需修改 `dashboard/app.py` 中的 `resample_to_low_frequency` 函数。

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

## 🚀 部署

### 本地开发环境
```powershell
.\start_all.ps1
```

### 生产环境（Linux/云服务器）
```bash
# 安装依赖
pip install -r requirements.txt

# 启动API
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app &

# 启动Dashboard
gunicorn -w 2 -b 0.0.0.0:8050 dashboard.app:server &

# 启动K线生成器
nohup python src/kline_generator.py &
```

### Docker部署（未来计划）
待添加 Dockerfile 和 docker-compose.yml

## 📝 更新日志

**v1.0.0** (2025-11-29)
- ✅ 完整的K线生成系统（tick采集 → OHLC生成）
- ✅ 异常值过滤机制
- ✅ Dash可视化Dashboard
- ✅ MA7/MA30技术指标
- ✅ DeepSeek AI市场分析
- ✅ API使用率控制
- ✅ 历史数据填充工具
- ✅ 一键启动脚本
- ✅ 桌面快捷方式

## 📜 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 👤 作者

**Leo666xx**

- GitHub: [@Leo666xx](https://github.com/Leo666xx)
- 项目地址: https://github.com/Leo666xx/financial-data-pipeline

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请在 GitHub 上提交 Issue。

## 🙏 致谢

- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance数据源
- [Dash](https://dash.plotly.com/) - 交互式可视化框架
- [DeepSeek](https://platform.deepseek.com) - AI API服务

---

**最后更新:** 2025-11-29  
**版本:** 1.0.0
