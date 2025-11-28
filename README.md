# Financial Data Pipeline

一个用 Flask 构建的金融数据 API，用于获取和管理金融市场数据（如外汇汇率）。

## 功能特性

- 📊 **价格查询接口** - 通过 symbol 查询最新的金融资产价格
- 🗄️ **SQLite 数据库** - 使用 SQLite 存储价格数据
- 🚀 **Flask REST API** - 简洁的 RESTful 接口设计
- 🔄 **自动符号映射** - 支持多种符号格式（如 `GBPUSD` 自动映射到 `GBPUSD=X`）

## 项目结构

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
│   └── market.db           # SQLite 数据库
├── requirements.txt        # Python 依赖
└── README.md              # 项目文档
```

## 安装

### 前置要求

- Python 3.10+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用

### 启动 API 服务器

```bash
python src/api.py
```

服务器将在 `http://localhost:5000` 启动。

### API 端点

#### 1. 根路由 - 检查 API 状态

```
GET http://localhost:5000/
```

**响应示例：**
```json
{
  "message": "Hello — Flask API is running!",
  "status": "ok"
}
```

#### 2. 价格查询接口

```
GET http://localhost:5000/price?symbol=GBPUSD
```

**参数：**
- `symbol` (可选) - 金融资产代码，默认为 `GBPUSD`

**响应示例：**
```json
{
  "symbol": "GBPUSD",
  "timestamp": "2025-11-28T14:08:31.784065",
  "price": 1.3228038549423218
}
```

**错误响应：**
```json
{
  "error": "No data found"
}
```

## 支持的符号

目前数据库中支持的符号：
- `GBPUSD` - 英镑/美元汇率

## 开发

### 项目依赖

- **Flask** - Web 框架
- **sqlite3** - 数据库（Python 标准库）

### 调试模式

API 默认以调试模式运行，支持热重载。修改代码后自动重启服务器。

## 数据库架构

### prices 表

```sql
CREATE TABLE prices (
    timestamp TEXT,
    symbol TEXT,
    price REAL
);
```

- `timestamp` - ISO 8601 格式的时间戳
- `symbol` - 金融资产代码
- `price` - 价格值

## 许可证

MIT

## 作者

Leo666xx

---

**快速开始：**

1. 安装依赖：`pip install flask`
2. 启动服务器：`python src/api.py`
3. 访问接口：`http://localhost:5000/price?symbol=GBPUSD`
