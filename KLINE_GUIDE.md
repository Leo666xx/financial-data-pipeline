# K-Line Generator 使用指南

## 🎯 功能概述

完整的 K 线数据收集系统，包含：
- ✅ **Tick 数据收集**：每 5 秒获取一次实时价格
- ✅ **OHLC 生成**：5 分钟 K 线（开盘/最高/最低/收盘）
- ✅ **异常值过滤**：自动过滤错误价格
- ✅ **数据清理**：支持清空旧数据或只删除异常值

---

## 📊 K 线生成原理

### 正确的做法
```
5 分钟内连续收集 tick：
  14:30:05 → 1.2345
  14:30:12 → 1.2346
  14:31:23 → 1.2347
  14:33:45 → 1.2344
  14:34:56 → 1.2348  ← 最后一个

生成 K 线：
  Open  = 1.2345  (第一个 tick)
  High  = 1.2348  (最大 tick)
  Low   = 1.2344  (最小 tick)
  Close = 1.2348  (最后一个 tick)
  Time  = 14:34:56

存入数据库 ✓
```

---

## 🛡️ 异常值过滤

### 过滤规则
```python
# GBPUSD / EURUSD
if price < 0.5 or price > 3.0:
    ⛔ 拒绝（超出合理范围）

# BTCUSD
if price < 1000 or price > 1000000:
    ⛔ 拒绝

# 通用
if price is None or price <= 0:
    ⛔ 拒绝
```

### 自动过滤
- ❌ 0.02 → 拒绝
- ❌ 0.01 → 拒绝
- ❌ 0 → 拒绝
- ❌ None → 拒绝
- ✅ 1.2345 → 接受

---

## 🚀 使用方法

### 方法 1：清空并重新开始（推荐）

```powershell
# 1. 清空所有旧数据并启动 K 线生成器
.\start_kline_generator.ps1

# 这会：
# - 删除所有旧的价格数据
# - 启动 5 分钟 K 线生成器
# - 每 5 秒收集一次 tick
# - 每 5 分钟生成一个 OHLC K 线
```

### 方法 2：只清理异常数据

```powershell
# 保留有效数据，只删除异常值
.\clean_database.ps1
# 选择选项 2: Remove only INVALID prices
```

### 方法 3：手动控制

```powershell
# 只清空数据
python src/database.py clear

# 只删除异常值
python src/database.py clean

# 启动 K 线生成器（不清空）
python src/kline_generator.py
```

---

## ⚙️ 配置选项

### 修改采集间隔

```powershell
# 每 10 秒采集一次 tick，生成 10 分钟 K 线
python src/kline_generator.py --tick-interval 10 --kline-interval 600

# 只采集 GBPUSD
python src/kline_generator.py --symbols GBPUSD=X

# 采集多个品种
python src/kline_generator.py --symbols GBPUSD=X EURUSD=X BTCUSD=X
```

---

## 📈 Dashboard 集成

K 线生成器运行后，Dashboard 会自动：
1. 读取 5 分钟 K 线历史数据
2. 计算 MA7/MA30 技术指标
3. 显示平滑的趋势曲线（无噪音）
4. 叠加最新实时报价

---

## 🔄 完整工作流

```
启动 K 线生成器
    ↓
每 5 秒获取 tick
    ↓
验证价格有效性 → ❌ 无效：丢弃
    ↓              ✅ 有效：保存
累积到 5 分钟桶
    ↓
生成 OHLC K 线
    ↓
存入数据库
    ↓
Dashboard 读取并显示
```

---

## 🐛 故障排查

### 问题：图表出现断崖/暴跌

**原因**：旧数据中有异常值（0.02, 0.01 等）

**解决**：
```powershell
.\start_kline_generator.ps1  # 清空并重新开始
```

### 问题：没有新数据

**检查**：
1. K 线生成器是否在运行？
2. 网络连接是否正常？
3. 查看终端输出是否有错误

### 问题：价格仍然有噪音

**原因**：可能在用旧的采集脚本

**解决**：
- 停止旧的 `ingest_loop.py`
- 使用新的 `kline_generator.py`

---

## 📝 数据库表结构

当前使用 `prices` 表存储收盘价：
```sql
CREATE TABLE prices (
    timestamp TEXT,  -- K 线结束时间
    symbol TEXT,     -- 交易对
    price REAL       -- 收盘价 (Close)
);
```

**未来扩展**：可创建完整 OHLC 表
```sql
CREATE TABLE klines (
    timestamp TEXT,
    symbol TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL
);
```

---

## ✨ 优势

| 特性 | 旧方式 | 新方式（K线生成器） |
|------|--------|-------------------|
| 数据质量 | ❌ 有噪音、有异常值 | ✅ 过滤异常、平滑稳定 |
| K线准确性 | ❌ 简单采样 | ✅ 真实 OHLC |
| 图表显示 | ❌ 跳动、断崖 | ✅ 平滑、专业 |
| 数据验证 | ❌ 无验证 | ✅ 自动过滤 |
| 技术指标 | ❌ 不稳定 | ✅ 可靠准确 |

---

## 🎯 推荐配置

**开发/测试**：
- Tick 间隔：5 秒
- K 线间隔：5 分钟
- 品种：GBPUSD=X, EURUSD=X

**生产环境**：
- Tick 间隔：1-3 秒（更密集）
- K 线间隔：5 分钟（标准）
- 品种：根据需求

---

## 📞 快速命令参考

```powershell
# 清空并重启（推荐用于解决数据问题）
.\start_kline_generator.ps1

# 清理数据库（交互式）
.\clean_database.ps1

# 启动 Dashboard
.\start_all.ps1

# 停止所有服务
.\stop_all.ps1
```
