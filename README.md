# Kepmanagementweekly

管理週報系統

## 目錄

- [環境需求](#環境需求)
- [專案設定](#專案設定)
- [環境變數說明](#環境變數說明)
- [切換正式環境（資料庫設定）](#切換正式環境資料庫設定)
  - [Django 專案](#django-專案)
  - [Flask 專案](#flask-專案)
- [資料庫遷移](#資料庫遷移)
- [正式環境注意事項](#正式環境注意事項)

---

## 環境需求

- Python 3.9+
- pip / virtualenv
- 資料庫：開發環境使用 SQLite，正式環境建議使用 PostgreSQL 或 MySQL

---

## 專案設定

```bash
# 1. 建立並啟動虛擬環境
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 2. 安裝套件
pip install -r requirements.txt

# 3. 複製環境變數範本
cp .env.example .env
```

---

## 環境變數說明

在專案根目錄建立 `.env` 檔案，並依環境填入對應值：

```
# ==============================
# 通用設定
# ==============================
SECRET_KEY=your-secret-key-here
DEBUG=True                        # 正式環境請改為 False

# ==============================
# 資料庫設定
# ==============================

# 開發環境（SQLite，預設值，不需額外安裝）
DATABASE_URL=sqlite:///db.sqlite3

# --- 正式環境請改用以下其中一種 ---

# PostgreSQL
# DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DB_NAME

# MySQL
# DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/DB_NAME

# ==============================
# 其他設定（視需求填寫）
# ==============================
ALLOWED_HOSTS=localhost,127.0.0.1   # 正式環境請加上實際網域
```

> `.env` 檔案含有機敏資訊，**請勿提交至 Git**。確認 `.gitignore` 已包含 `.env`。

---

## 切換正式環境（資料庫設定）

### Django 專案

**1. 安裝 PostgreSQL 或 MySQL 驅動套件**

```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install mysqlclient
```

**2. 修改 `settings.py`（建議以環境變數控制，不硬寫連線字串）**

```python
import os
import dj_database_url

# 讀取 .env 或系統環境變數中的 DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
    )
}
```

> 需安裝 `dj-database-url`：`pip install dj-database-url`

**3. 正式環境的 `settings.py` 關鍵設定**

```python
# 正式環境務必關閉 DEBUG
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# 設定允許的主機
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# 從環境變數讀取 Secret Key
SECRET_KEY = os.environ.get('SECRET_KEY')
```

---

### Flask 專案

**1. 安裝 SQLAlchemy 與對應驅動**

```bash
pip install flask-sqlalchemy psycopg2-binary   # PostgreSQL
pip install flask-sqlalchemy mysqlclient        # MySQL
```

**2. 修改 `config.py` 或 `app.py`**

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

# 依環境變數自動選擇設定
config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
}
```

**3. 在應用程式入口讀取設定**

```python
app_env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[app_env])
```

**4. 切換方式：設定環境變數**

```bash
# Linux / macOS
export FLASK_ENV=production
export DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DB_NAME

# Windows
set FLASK_ENV=production
set DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DB_NAME
```

---

## 資料庫遷移

切換資料庫後，務必執行遷移指令同步資料表結構：

```bash
# Django
python manage.py migrate

# Flask（使用 Flask-Migrate）
flask db upgrade
```

---

## 正式環境注意事項

| 項目 | 開發環境 | 正式環境 |
|------|---------|---------|
| `DEBUG` | `True` | `False` |
| 資料庫 | SQLite（本機檔案） | PostgreSQL / MySQL |
| `SECRET_KEY` | 任意字串 | 隨機高強度字串，從環境變數讀取 |
| `ALLOWED_HOSTS` | `localhost` | 實際網域（如 `example.com`） |
| 靜態檔案 | Django/Flask 自動服務 | 透過 Nginx / CDN 服務 |

**產生安全的 SECRET_KEY：**

```bash
python -c "import secrets; print(secrets.token_hex(50))"
```

**部署前檢查清單：**

- [ ] `.env` 已設定正式資料庫連線字串
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` 已更換為高強度隨機字串
- [ ] `ALLOWED_HOSTS` 已設定正確網域
- [ ] 已執行 `migrate` 確認資料表建立完成
- [ ] `.env` 已加入 `.gitignore`，未被提交至版控

---

## 授權

本專案採用 [MIT License](LICENSE)。
