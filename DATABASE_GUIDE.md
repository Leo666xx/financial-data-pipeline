# Database Management Guide

## 📊 Database Location
- **Primary Database**: `data/market.db`
- **Backup Location**: `data/backups/`
- **DO NOT** delete or modify `data/market.db` manually

## ✅ Safe Operations

### Check Database Status
```powershell
.\check_database.ps1
```
Shows database size, last modified time, and record counts.

### Create Backup
```powershell
.\backup_database.ps1
```
- Creates timestamped backup in `data/backups/`
- Automatically keeps last 10 backups
- Safe to run anytime

### Start System (Safe)
```powershell
.\start_all.ps1
```
- ✅ **Safe**: No longer clears data automatically
- Only checks database status
- Preserves existing data

### Fill Historical Data
```powershell
python fill_history.py --symbol GBPUSD
python fill_history.py --symbol EURUSD
python fill_history.py --symbol BTCUSD
```
- Adds 300 K-line records per symbol
- Safe to run multiple times (duplicates ignored)

## ⚠️ Dangerous Operations

### Clean Database (Interactive)
```powershell
.\clean_database.ps1
```
Options:
1. **Clear ALL data** ⚠️ DESTRUCTIVE - Requires typing `DELETE`
2. Remove only invalid prices (safe)
3. Backup database before cleaning
4. Cancel

### Manual Database Reset (Advanced)
```powershell
# Stop all services first
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*financial-data-pipeline*" } | Stop-Process -Force

# Remove database
Remove-Item "data\market.db" -Force

# Restart system
.\start_all.ps1

# Fill data
python fill_history.py
python fill_history.py --symbol EURUSD
python fill_history.py --symbol BTCUSD
```

## 🔄 Recovery from Data Loss

If you accidentally lost data:

1. **Check for backups**:
   ```powershell
   Get-ChildItem "data\backups\*.db" | Sort-Object LastWriteTime -Descending
   ```

2. **Restore from backup**:
   ```powershell
   # Stop services
   Get-Process python | Where-Object { $_.Path -like "*financial-data-pipeline*" } | Stop-Process -Force
   
   # Restore (replace YYYYMMDD_HHMMSS with actual backup timestamp)
   Copy-Item "data\backups\market_YYYYMMDD_HHMMSS.db" "data\market.db" -Force
   
   # Restart
   .\start_all.ps1
   ```

3. **If no backup exists, refill data**:
   ```powershell
   python fill_history.py
   python fill_history.py --symbol EURUSD
   python fill_history.py --symbol BTCUSD
   ```

## 📋 Best Practices

1. **Regular Backups**: Run `.\backup_database.ps1` before major changes
2. **Never use** `.\clean_database.ps1` option 1 unless you want to reset completely
3. **Check status** with `.\check_database.ps1` if Dashboard shows "No data"
4. **Git ignore**: Database files are in `.gitignore` (don't commit to Git)
5. **Backup before upgrades**: Always backup before system updates

## 🛡️ Protection Measures

- ✅ `start_all.ps1` no longer auto-clears data
- ✅ `clean_database.ps1` requires typing `DELETE` for destructive operation
- ✅ Automatic backup retention (keeps 10 most recent)
- ✅ Health check script for quick diagnosis

## 📈 Expected Data Volume

- **300 records per symbol** after fill_history.py
- **Database size**: ~100-200 KB with 3 symbols (900 records)
- **Growth rate**: ~50-100 records/day per symbol (real-time collection)
- **1 month**: ~5,000 records per symbol (~500 KB)
- **6 months**: ~30,000 records per symbol (~3 MB)

## 🔍 Troubleshooting

### Dashboard shows "No historical data"
```powershell
# 1. Check database
.\check_database.ps1

# 2. If empty, fill data
python fill_history.py
python fill_history.py --symbol EURUSD
python fill_history.py --symbol BTCUSD

# 3. Refresh Dashboard (Ctrl+F5 in browser)
```

### "Database locked" error
```powershell
# Stop all services and restart
Get-Process python | Where-Object { $_.Path -like "*financial-data-pipeline*" } | Stop-Process -Force
.\start_all.ps1
```

### Wrong database path
- Always use `data/market.db` (NOT `financial_data.db` in root)
- Check `src/database.py` for `DB_PATH = "data/market.db"`
