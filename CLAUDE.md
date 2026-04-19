# Kepmanagementweekly — Claude 工作備忘

## 資料庫 Schema

### tags（點位主表）

| 欄位 | 型別 | 說明 |
|------|------|------|
| tag_id | INTEGER PK | 自動遞增 |
| tagname | VARCHAR UNIQUE | 點位名稱（必填） |
| description | VARCHAR | 描述 |
| node_name | VARCHAR | 節點名稱（**非專案識別碼**） |
| driver_type | VARCHAR | PLC/OPC 類型 |
| address | VARCHAR | PLC 位址 |
| tabname | VARCHAR | 頁籤名稱 |
| zone | VARCHAR | 區域 |
| bu | VARCHAR | 事業單位 |
| site | VARCHAR | 廠區 |
| floor | VARCHAR | 樓層 |
| owner | VARCHAR | 負責人 |
| department | VARCHAR | 部門 |
| data_type | VARCHAR | 資料類型 |
| created_date | TIMESTAMP | 建立時間 |
| updated_date | TIMESTAMP | 更新時間 |

### projects（專案表）

| 欄位 | 型別 | 說明 |
|------|------|------|
| project_id | INTEGER PK | 自動遞增 |
| project_name | VARCHAR UNIQUE | 專案名稱 |
| created_date | TIMESTAMP | 建立時間 |

### tag_projects（關聯表，多對多）

| 欄位 | 型別 | 說明 |
|------|------|------|
| tag_id | INTEGER FK | 關聯 tags.tag_id |
| project_id | INTEGER FK | 關聯 projects.project_id |
| date | DATE | 關聯日期 |

## 重要規則

### 專案查詢必須 JOIN 三張表
依專案統計或分類時，**不可用 `node_name`**，要透過關聯表：

```sql
SELECT p.project_name AS label, COUNT(DISTINCT tp.tag_id) AS count
FROM projects p
JOIN tag_projects tp ON tp.project_id = p.project_id
GROUP BY p.project_name
ORDER BY count DESC
```

### Jinja2 autoescape 已開啟
`renderer.py` 啟用了 `autoescape=select_autoescape(["html"])`。
在 `<script>` 區塊傳 JSON 給 Chart.js 時，**必須回傳 `Markup` 物件**，否則雙引號會被轉成 `&#34;` 導致圖表無資料：

```python
# renderer.py — tojson_filter 正確寫法
from markupsafe import Markup

def tojson_filter(value) -> Markup:
    return Markup(json.dumps(value, ensure_ascii=False, default=str))
```

## 專案結構

```
Kepmanagementweekly/
├── generate_report.py      # CLI 入口（週報 / 月報）
├── app/
│   ├── db.py               # PostgreSQL 連線（psycopg2）
│   ├── queries.py          # SQL 查詢（含 get_project_distribution）
│   ├── demo_data.py        # 離線假資料（--demo 模式）
│   └── renderer.py         # Jinja2 HTML + WeasyPrint PDF
├── templates/
│   └── report.html         # Bootstrap 5 深色主題 + Chart.js
└── reports/                # 輸出目錄
```
