# KPM 月報專案

## Reporting / Pipeline Conventions

- 撰寫任何報告產生程式碼前，**必須先向使用者確認資料庫 schema 結構**（欄位名稱、資料型別），確認後才開始寫 SQL 或 Python 程式碼。
- 要求「產生報告」或「建立頁面」時，預設建立 Python data pipeline（讀取 PostgreSQL → 用 Jinja2 渲染 HTML），**不可產生靜態 HTML 檔案**，除非使用者明確要求。
- 任何連接 PostgreSQL 的腳本，一律用 `python-dotenv` 自動載入 `.env` 檔（`load_dotenv()`），不可把連線資訊寫死在程式碼裡。

## Environment

- DB 連線設定統一放在 `.env`，範本參考 `.env.example`
- Python 套件需求記錄在 `requirements.txt`
