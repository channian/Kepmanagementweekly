# /html-report

產生 KPM Kepware 月報 HTML 的完整 pipeline。

## 步驟

1. **確認 schema** — 詢問使用者提供 PostgreSQL 資料表結構（或直接讀取現有 `CREATE TABLE` 定義），確認欄位對應後才繼續。
2. **確認月份** — 詢問要產生哪個年月的報告（預設為當月）。
3. **建立 / 更新 `generate_report.py`** — 包含：
   - `load_dotenv()` 載入 `.env`
   - psycopg2 連線 PostgreSQL
   - 查詢所有報告所需資料（KPI、系統分佈、BU、廠區、部門、健康度、異動明細）
   - 使用 Jinja2 渲染 `report_template.html`
   - 輸出 `report_YYYY-MM.html`
4. **建立 / 更新 `report_template.html`** — Jinja2 模板，包含完整互動式月報版面。
5. **執行腳本** — 跑 `python generate_report.py` 確認無錯誤後回報結果。

## 注意事項

- 不可產生靜態 HTML，所有數字必須來自資料庫查詢
- 連線資訊一律從 `.env` 讀取
- 如果 `requirements.txt` 缺少套件，先補上再執行
