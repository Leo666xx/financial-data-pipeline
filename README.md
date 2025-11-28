# Financial Data Pipeline

一个用 Flask 构建的金融数据 API，用于获取和管理金融市场数据（如外汇汇率）。

## 🎯 功能特性

- 📊 **价格查询接口** - 通过 symbol 查询最新的金融资产价格
- 🗄️ **SQLite 数据库** - 使用 SQLite 存储价格数据
- 🚀 **Flask REST API** - 简洁的 RESTful 接口设计
- 🔄 **自动符号映射** - 支持多种符号格式（如 `GBPUSD` 自动映射到 `GBPUSD=X`）
- 🔍 **实时查询** - 支持实时查询最新价格数据
- 📈 **可扩展架构** - 易于添加新的数据源和接口

## 📂 项目结构

```
financial-data-pipeline/
├── src/
│   ├── api.py              # Flask API 主文件
│   ├── database.py         # 数据库操作
│   ├── fetch_data.py       # 数据采集模块
│   ├── ingest.py           # 数据导入模块
│   ├── models.py           # 数据模型
│   └── hello.py            # 测试脚本
├── data/
│   └── (数据库和 CSV 文件将存放在这里)
├── requirements.txt        # Python 依赖
├── .gitignore             # Git 忽略文件
├── LICENSE                # MIT 许可证
└── README.md              # 项目文档
```

## 🚀 快速开始

### 前置要求

- Python 3.10+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动 API 服务器

```bash
python src/api.py
```

服务器将在 `http://localhost:5000` 启动。

## 📡 API 文档

### 1. 健康检查 - 根路由

```http
GET http://localhost:5000/
```

**响应示例：**
```json
{
  "message": "Hello — Flask API is running!",
  "status": "ok"
}
```

**cURL 示例：**
```bash
curl http://localhost:5000/
```

---

### 2. 价格查询接口

```http
GET http://localhost:5000/price?symbol=GBPUSD
```

**参数：**
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `symbol` | string | 否 | GBPUSD | 金融资产代码 |

**响应成功示例 (200)：**
```json
{
  "symbol": "GBPUSD",
  "timestamp": "2025-11-28T14:08:31.784065",
  "price": 1.3228038549423218
}
```

**响应错误示例 (404)：**
```json
{
  "error": "No data found"
}
```

**cURL 示例：**
```bash
# 查询 GBPUSD 汇率
curl "http://localhost:5000/price?symbol=GBPUSD"

# 使用 Python requests
python -c "import requests; print(requests.get('http://localhost:5000/price?symbol=GBPUSD').json())"
```

---

## 🗄️ 数据库架构

### prices 表

```sql
CREATE TABLE prices (
    timestamp TEXT NOT NULL,      -- ISO 8601 时间戳
    symbol TEXT NOT NULL,         -- 金融资产代码 (如 GBPUSD=X)
    price REAL NOT NULL           -- 价格值
);
```

**字段说明：**
- **timestamp** - ISO 8601 格式的时间戳（UTC），精确到毫秒。例如：`2025-11-28T14:08:31.784065`
- **symbol** - 金融资产代码。数据库中存储为 `GBPUSD=X` 格式，但 API 支持 `GBPUSD` 别名查询
- **price** - 资产价格，浮点数。例如：`1.3228038549423218`

### 支持的符号

| 符号 | 数据库存储 | API 查询 | 说明 |
|------|----------|---------|------|
| 英镑/美元 | `GBPUSD=X` | `GBPUSD` | 英镑对美元汇率 |

## 🛠️ 开发指南

### 项目依赖

- **Flask** - 轻量级 Web 框架
- **sqlite3** - 嵌入式数据库（Python 标准库）

### 调试模式

API 默认以调试模式运行，支持热重载。修改代码后自动重启服务器。

```bash
# 启用调试模式
python src/api.py
```

### 项目架构

- `api.py` - Flask 应用主入口，定义 API 路由和业务逻辑
- `database.py` - 数据库连接和查询操作
- `fetch_data.py` - 数据源集成（如 yfinance）
- `models.py` - 数据模型和 ORM
- `ingest.py` - 数据导入和初始化

## 📈 未来计划 (Roadmap)

### Phase 1: 核心功能 ✅
- [x] Flask API 基础框架
- [x] SQLite 数据库集成
- [x] 单个 symbol 价格查询
- [x] 项目文档完善

### Phase 2: 功能扩展（计划中）
- [ ] 支持多个 symbol 批量查询
- [ ] 支持历史数据接询（时间范围）
- [ ] 自动定时任务：每小时自动抓取最新价格
- [ ] 支持更多交易品种（加密货币、股票、期货等）
- [ ] 数据缓存和性能优化
- [ ] 错误处理和日志记录

### Phase 3: 应用层面（后期）
- [ ] 前端 Web UI（React/Vue）
- [ ] 数据可视化和图表
- [ ] 价格告警功能
- [ ] 用户认证和 API Key
- [ ] 部署到云端（AWS/Azure/Heroku）
- [ ] Docker 容器化

### Phase 4: 运维和监控（长期）
- [ ] 数据库备份和恢复
- [ ] 监控仪表板
- [ ] 性能优化和压力测试
- [ ] 微服务拆分

## 📝 配置和环境变量

如需自定义配置，可创建 `.env` 文件（已在 `.gitignore` 中忽略）：

```bash
# .env 文件示例
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_PATH=data/market.db
API_PORT=5000
API_HOST=0.0.0.0
```

## 🐛 常见问题

### Q: 如何初始化数据库？
A: 运行 `src/ingest.py` 脚本来初始化数据库和导入样本数据。

### Q: 支持哪些 symbol？
A: 目前支持 `GBPUSD`。可通过修改 `fetch_data.py` 添加更多数据源。

### Q: 如何查询历史数据？
A: 当前版本只支持查询最新价格。历史数据查询功能在 Phase 2 roadmap 中。

### Q: 数据更新频率是多少？
A: 目前需要手动运行 `fetch_data.py` 更新。自动定时更新在 Phase 2 中规划。

## 📦 部署

### 本地开发

```bash
python src/api.py
```

### 生产环境（使用 Gunicorn）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api:app
```

### Docker 部署（计划中）

```dockerfile
# Dockerfile 将在未来添加
```

## 📜 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 👤 作者

**Leo666xx**

- GitHub: [@Leo666xx](https://github.com/Leo666xx)
- Email: (可选)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请在 GitHub 上提交 Issue。

---

**最后更新：** 2025-11-28  
**版本：** 1.0.0
