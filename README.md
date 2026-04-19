# Kepmanagementweekly

Kepware 點位管理週報／月報產生器。  
連接與 [ThingsBoradAPIWebUI](https://github.com/channian/ThingsBoradAPIWebUI) 相同的 PostgreSQL 資料庫，查詢 `tags` 資料表後輸出 HTML（可列印成 PDF）報表。

---

## 報表內容

| 區塊 | 說明 |
|------|------|
| KPI 摘要 | 總點位數 / 本期新增 / 本期修改 |
| 圓餅圖 × 4 | 依 Site / BU / Zone / 專案分佈 |
| 橫條圖 | 依部門分佈 |
| 新增點位清單 | 含 tagname、描述、site/bu/zone、負責人、建立時間 |
| 修改點位清單 | 同上 + 修改時間 |

---

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

> PDF 轉換為選用功能，需要額外安裝 WeasyPrint（見下方說明）。

---

## 模式切換：Demo vs 真實資料庫

### Demo 模式（免資料庫，預覽報表樣式）

不需要任何設定，直接執行：

```bash
python generate_report.py --demo
python generate_report.py --demo --mode monthly
```

輸出：`reports/report_YYYY-MM-DD_demo_weekly.html`

資料來自 `app/demo_data.py` 的內建假資料（3 個廠區、6 個專案、1,247 點）。

---

### 真實資料庫模式

#### Step 1：建立 `.env` 設定檔

```bash
cp .env.example .env
```

然後用任何編輯器開啟 `.env`，填入連線資訊：

```env
# PostgreSQL 連線（與 ThingsBoradAPIWebUI 使用同一個 DB）
PG_HOST=192.168.1.100      # 資料庫主機 IP
PG_PORT=5432               # 預設 5432
PG_DB=kepware              # 資料庫名稱
PG_USER=postgres           # 帳號
PG_PASSWORD=your_password  # 密碼

# 報告設定（選填）
SITE_NAME=我的工廠
REPORT_OUTPUT_DIR=reports
```

#### Step 2：執行（去掉 `--demo`）

```bash
# 本週報告
python generate_report.py --mode weekly

# 本月報告
python generate_report.py --mode monthly

# 自訂期間
python generate_report.py --start 2026-03-01 --end 2026-04-01
```

輸出：`reports/report_YYYY-MM-DD_weekly.html`

---

## 指令速查

```bash
# Demo 模式（無需 DB）
python generate_report.py --demo
python generate_report.py --demo --mode monthly

# 真實 DB 模式
python generate_report.py --mode weekly
python generate_report.py --mode monthly
python generate_report.py --start 2026-03-01 --end 2026-04-01

# 同時產生 PDF（需安裝 WeasyPrint）
python generate_report.py --mode weekly --pdf
python generate_report.py --demo --pdf

# 指定輸出目錄
python generate_report.py --mode weekly --output-dir /tmp/reports
```

---

## PDF 輸出（選用）

加上 `--pdf` 旗標時，會使用 [WeasyPrint](https://weasyprint.org/) 將 HTML 轉成 PDF。

```bash
pip install weasyprint

# Linux 需要額外的系統套件
apt install libpango-1.0-0 libpangoft2-1.0-0
```

不安裝 WeasyPrint 時去掉 `--pdf` 即可，直接用瀏覽器「列印 → 儲存為 PDF」也可以。

---

## 專案結構

```
Kepmanagementweekly/
├── generate_report.py   # CLI 入口
├── app/
│   ├── db.py            # PostgreSQL 連線（psycopg2）
│   ├── queries.py       # SQL 查詢（tags 資料表）
│   ├── demo_data.py     # 離線假資料（--demo 模式用）
│   └── renderer.py      # Jinja2 HTML + WeasyPrint PDF
├── templates/
│   └── report.html      # 報表模板（Bootstrap 5 深色主題 + Chart.js）
├── reports/             # 輸出目錄（.gitignore 排除 html/pdf）
├── .env.example         # 環境變數範本
└── requirements.txt
```

---

## 資料來源

查詢 ThingsBoradAPIWebUI 專案的 PostgreSQL `tags` 資料表：

| 欄位 | 說明 |
|------|------|
| `tagname` | 點位唯一名稱 |
| `site` | 廠區 |
| `bu` | Business Unit |
| `zone` | 區域 |
| `node_name` | 專案（SCADA 節點） |
| `driver_type` | Kepware 驅動類型 |
| `department` | 部門 |
| `owner` | 負責人 |
| `created_date` | 建立時間（用於統計新增） |
| `updated_date` | 修改時間（用於統計修改） |

> **注意**：`tags` 資料表沒有刪除記錄，因此報表只統計「新增」與「修改」，不含刪除數量。
