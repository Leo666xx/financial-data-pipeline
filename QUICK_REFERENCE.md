# 🚀 Quick Reference Card

## Daily Operations

```powershell
# Start System (Safe - keeps data)
.\start_all.ps1

# Stop System
.\stop_all.ps1

# Check Database Health
.\check_database.ps1

# Create Backup
.\backup_database.ps1
```

## Common Tasks

### Add More Historical Data
```powershell
python fill_history.py --symbol GBPUSD
python fill_history.py --symbol EURUSD
python fill_history.py --symbol BTCUSD
```

### View Risk Analysis
```powershell
python test_risk.py --symbol GBPUSD
python test_risk.py --compare
```

### Access Dashboard
- http://localhost:8050
- Refresh with Ctrl+F5 if data doesn't show

## ⚠️ Warning

**NEVER run these unless you know what you're doing:**
- ❌ `.\clean_database.ps1` → Option 1 (deletes ALL data)
- ❌ Manual deletion of `data/market.db`

## 🛟 Emergency Recovery

```powershell
# 1. Stop everything
Get-Process python | Where-Object { $_.Path -like "*financial-data-pipeline*" } | Stop-Process -Force

# 2. Check backups
Get-ChildItem "data\backups\*.db"

# 3. Restore latest backup
$latest = Get-ChildItem "data\backups\*.db" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $latest.FullName "data\market.db" -Force

# 4. Restart
.\start_all.ps1
```

## 📁 Important Files

- `data/market.db` - Main database (DO NOT DELETE)
- `data/backups/` - Automatic backups (keeps 10 recent)
- `DATABASE_GUIDE.md` - Full documentation

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| No data in Dashboard | Run `.\check_database.ps1` then `python fill_history.py` |
| "Database locked" | Stop all processes and restart |
| Lost data | Restore from `data/backups/` |
| Services not starting | Check if ports 5000/8050 are free |

See `DATABASE_GUIDE.md` for detailed documentation.
