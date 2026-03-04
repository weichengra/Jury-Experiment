# Jury Experiment - FRAND 費率評估研究

陪審團決策研究：標準必要專利（SEP）FRAND費率評估

## 專案概述

2×2 實驗設計：Study (Study 1 vs. Study 2) × Treatment (Simple vs. Complex)

- **oTree 6.0** | **Python 3.11.4** | **部署平台: Heroku**
- **參與者自動分配**: 每4人循環 (S1-Simple → S1-Complex → S2-Simple → S2-Complex)
- **Study 1**: 3次費率評估 + 滑鼠追蹤
- **Study 2**: 2次費率評估 + reCAPTCHA驗證

## 快速部署至 Heroku

```bash
# 1. 創建應用程式
heroku login
heroku create your-app-name

# 2. 設定環境變數（必須）
heroku config:set OTREE_ADMIN_PASSWORD=your_password
heroku config:set OTREE_PRODUCTION=1
heroku config:set RECAPTCHA_SECRET_KEY=your_secret_key

# 3. 部署
git push heroku main
heroku ps:scale web=4 worker=2
heroku open
```

### 推薦配置

**100人實驗**: 4台Web + 2台Worker = $410/月  
**800人實驗**: 8台Web + 2台Worker = $610/月

```bash
# 擴展至800人配置
heroku ps:scale web=8
```

## 本地開發

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 啟動開發伺服器

```bash
otree devserver
```

訪問 http://localhost:8000 查看實驗

### 重置數據庫

```bash
otree resetdb
```

## 數據收集

### 下載實驗數據

1. 訪問管理後台：`https://your-app.herokuapp.com/`
2. 使用管理員帳號登入（用戶名：admin）
3. 進入 "Data" 頁面
4. 選擇 "All apps (wide)" 下載完整數據
5. 或分別下載 jury1 和 jury2 的數據

### 主要測量變數

- **FRAND費率評估**: `frand_rate_initial`, `frand_rate_post_germany`, `frand_rate_final`
- **證據選擇**: `evidence_e1` ~ `evidence_e8`
- **人口統計**: `demographic_q1` ~ `demographic_q9`
- **時間追蹤**: `duration_*` 系列欄位
## 資料下載

1. 登入 `https://your-app.herokuapp.com/`
2. 點擊 **Data** → 選擇 **jury1** 或 **jury2** → **Download**
3. 分別下載兩個CSV檔案進行分析

**重要欄位**:
- `inst`: Treatment (0=Simple, 1=Complex)
- Study 1: `frand_rate_initial`, `frand_rate_final`, `prolific_ID`
- Study 2: `frand_rate_0`, `frand_rate_revised`, `prolific_id`
- `comprehension_passed`: 是否通過理解測驗

完整欄位說明請參考 [專案說明與CSV欄位指南.md](專案說明與CSV欄位指南.md)

## 監控與除錯

```bash
# 即時日誌
heroku logs --tail

# 檢查dyno狀態
heroku ps

# 檢查環境變數
heroku config

# 重啟應用
heroku restart
```

## 文檔

- [專案說明與CSV欄位指南.md](專案說明與CSV欄位指南.md) - 詳細欄位說明
- [部署與操作指南.md](部署與操作指南.md) - 完整部署教程
- [reCAPTCHA設定指南.md](reCAPTCHA設定指南.md) - reCAPTCHA配置
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - 部署檢查清單

---

**版本**: 2.0 | **更新**: 2026年3月1日 | **oTree**: 6.0.0
