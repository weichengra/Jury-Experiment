# Jury Experiment - FRAND Rate Evaluation

陪審團決策研究：標準必要專利（SEP）FRAND費率評估實驗

## 專案概述

本研究探討陪審團在評估FRAND（公平、合理、無歧視）專利授權費率時的決策過程。實驗包含兩個研究（Study 1和Study 2），每個研究有簡單版（3因素）和複雜版（8因素）兩種處理條件。

### 研究設計

- **Study 1**: 3次FRAND費率評估（初始評估、德國案例後評估、最終評估）
- **Study 2**: 2次FRAND費率評估 + reCAPTCHA驗證
- **參與者分配**: 每4人一組循環分配
  - 參與者1 → Study 1, Simple
  - 參與者2 → Study 1, Complex
  - 參與者3 → Study 2, Simple
  - 參與者4 → Study 2, Complex

## 技術架構

- **Framework**: oTree 6.0
- **Python**: 3.11.4
- **部署平台**: Heroku
- **應用程式**:
  - `router`: 自動分配參與者至不同研究
  - `jury1`: Study 1 實驗流程
  - `jury2`: Study 2 實驗流程（含reCAPTCHA）

## 部署至Heroku

### 準備工作

1. 安裝 [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. 擁有Heroku帳號

### 部署步驟

```bash
# 1. 登入Heroku
heroku login

# 2. 創建Heroku應用程式
heroku create your-app-name

# 3. 設定環境變數
heroku config:set OTREE_ADMIN_PASSWORD=your_password
heroku config:set OTREE_PRODUCTION=1
heroku config:set RECAPTCHA_SECRET_KEY=your_recaptcha_secret_key

# 4. 部署代碼
git push heroku main

# 5. 重啟應用程式
heroku restart

# 6. 開啟應用程式
heroku open
```

### 必要的環境變數

| 變數名稱 | 說明 | 必要性 |
|---------|------|--------|
| `OTREE_ADMIN_PASSWORD` | 管理後台密碼 | 必須 |
| `OTREE_PRODUCTION` | 生產環境標記（設為1） | 必須 |
| `RECAPTCHA_SECRET_KEY` | Google reCAPTCHA密鑰 | Study 2必須 |

### 檢查部署狀態

```bash
# 查看日誌
heroku logs --tail

# 檢查dyno狀態
heroku ps

# 重啟應用程式
heroku restart
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
- **滑鼠軌跡**: `mouse_tracking_*` 系列欄位

詳細欄位說明請參考 `專案說明與CSV欄位指南.md`

## 專案結構

```
Jury Experiment/
├── settings.py              # oTree主配置
├── router/                  # 參與者路由分配
│   └── __init__.py
├── jury1/                   # Study 1
│   ├── __init__.py         # 邏輯代碼
│   └── *.html              # 頁面模板
├── jury2/                   # Study 2
│   ├── __init__.py         # 邏輯代碼
│   └── *.html              # 頁面模板
├── _static/                 # 靜態資源
│   └── global/
│       ├── styles.css
│       └── slider.js
├── _templates/              # 共用模板
│   └── global/
│       └── Page.html
├── requirements.txt         # Python依賴
├── Procfile                # Heroku啟動配置
├── runtime.txt             # Python版本
└── .gitignore              # Git忽略文件
```

## 文檔

- **專案說明與CSV欄位指南.md**: 詳細的專案說明和數據欄位解釋
- **部署與操作指南.md**: Heroku和oTreeHub部署教程

## 授權

本專案使用MIT授權 - 詳見 [LICENSE](LICENSE) 文件

## 聯絡方式

如有問題，請聯繫專案負責人。

---

**最後更新**: 2026年2月2日
