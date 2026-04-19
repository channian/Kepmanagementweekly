"""Offline demo data — mirrors the same interface as queries.py.

Use with:  python generate_report.py --demo
No database connection required.
"""

from datetime import date, datetime, timedelta
from typing import Any

# ── Reference anchor: "today" for demo is fixed so the report looks realistic ──
_TODAY = date(2026, 4, 4)
_WEEK_START = _TODAY - timedelta(days=_TODAY.weekday())   # 2026-03-30 (Mon)


def _dt(d: date, hour: int = 9, minute: int = 0) -> datetime:
    return datetime(d.year, d.month, d.day, hour, minute)


# ── New tags added during demo "week" ──────────────────────────────────────────
_NEW_TAGS_ROWS = [
    {
        "tagname": "Factory-A.Line1.PLC01.Tank01_Level",
        "description": "1號槽液位",
        "node_name": "SCADA-A",
        "site": "Factory-A", "bu": "製造部", "zone": "1F", "floor": "1F",
        "driver_type": "Allen-Bradley", "data_type": "float",
        "owner": "王志明", "department": "電氣課",
        "created_date": _dt(_WEEK_START, 9, 15),
    },
    {
        "tagname": "Factory-A.Line1.PLC01.Tank02_Level",
        "description": "2號槽液位",
        "node_name": "SCADA-A",
        "site": "Factory-A", "bu": "製造部", "zone": "1F", "floor": "1F",
        "driver_type": "Allen-Bradley", "data_type": "float",
        "owner": "王志明", "department": "電氣課",
        "created_date": _dt(_WEEK_START, 9, 16),
    },
    {
        "tagname": "Factory-A.Line1.PLC01.Pump01_Speed",
        "description": "泵浦01 轉速",
        "node_name": "SCADA-A",
        "site": "Factory-A", "bu": "製造部", "zone": "1F", "floor": "1F",
        "driver_type": "Allen-Bradley", "data_type": "float",
        "owner": "李淑華", "department": "儀控課",
        "created_date": _dt(_WEEK_START, 10, 5),
    },
    {
        "tagname": "Factory-A.Line2.PLC02.Conveyor_Speed",
        "description": "輸送帶速度",
        "node_name": "SCADA-A",
        "site": "Factory-A", "bu": "製造部", "zone": "2F", "floor": "2F",
        "driver_type": "Allen-Bradley", "data_type": "float",
        "owner": "李淑華", "department": "儀控課",
        "created_date": _dt(_WEEK_START + timedelta(days=1), 8, 30),
    },
    {
        "tagname": "Factory-B.Utility.PLC10.Chiller01_Temp",
        "description": "冰水機01 出水溫",
        "node_name": "SCADA-B",
        "site": "Factory-B", "bu": "設備部", "zone": "B1", "floor": "B1",
        "driver_type": "Siemens", "data_type": "float",
        "owner": "陳建國", "department": "動力課",
        "created_date": _dt(_WEEK_START + timedelta(days=1), 11, 0),
    },
    {
        "tagname": "Factory-B.Utility.PLC10.Chiller01_Power",
        "description": "冰水機01 耗電",
        "node_name": "SCADA-B",
        "site": "Factory-B", "bu": "設備部", "zone": "B1", "floor": "B1",
        "driver_type": "Siemens", "data_type": "float",
        "owner": "陳建國", "department": "動力課",
        "created_date": _dt(_WEEK_START + timedelta(days=1), 11, 2),
    },
    {
        "tagname": "Factory-B.Utility.PLC10.AHU01_Temp",
        "description": "AHU01 回風溫度",
        "node_name": "SCADA-B",
        "site": "Factory-B", "bu": "設備部", "zone": "3F", "floor": "3F",
        "driver_type": "Modbus TCP", "data_type": "float",
        "owner": "林俊傑", "department": "動力課",
        "created_date": _dt(_WEEK_START + timedelta(days=2), 9, 45),
    },
    {
        "tagname": "Factory-B.Utility.PLC10.AHU01_Humidity",
        "description": "AHU01 回風濕度",
        "node_name": "SCADA-B",
        "site": "Factory-B", "bu": "設備部", "zone": "3F", "floor": "3F",
        "driver_type": "Modbus TCP", "data_type": "float",
        "owner": "林俊傑", "department": "動力課",
        "created_date": _dt(_WEEK_START + timedelta(days=2), 9, 47),
    },
    {
        "tagname": "Factory-C.Process.PLC20.Reactor01_Temp",
        "description": "反應槽01 溫度",
        "node_name": "SCADA-C",
        "site": "Factory-C", "bu": "製造部", "zone": "2F", "floor": "2F",
        "driver_type": "OPC-UA", "data_type": "float",
        "owner": "張美玲", "department": "製程課",
        "created_date": _dt(_WEEK_START + timedelta(days=2), 14, 0),
    },
    {
        "tagname": "Factory-C.Process.PLC20.Reactor01_Pressure",
        "description": "反應槽01 壓力",
        "node_name": "SCADA-C",
        "site": "Factory-C", "bu": "製造部", "zone": "2F", "floor": "2F",
        "driver_type": "OPC-UA", "data_type": "float",
        "owner": "張美玲", "department": "製程課",
        "created_date": _dt(_WEEK_START + timedelta(days=2), 14, 3),
    },
    {
        "tagname": "Factory-C.Process.PLC20.Mixer01_Torque",
        "description": "攪拌機01 扭力",
        "node_name": "SCADA-C",
        "site": "Factory-C", "bu": "製造部", "zone": "2F", "floor": "2F",
        "driver_type": "OPC-UA", "data_type": "float",
        "owner": "張美玲", "department": "製程課",
        "created_date": _dt(_WEEK_START + timedelta(days=3), 10, 20),
    },
    {
        "tagname": "Factory-A.Energy.PLC05.MainBreaker_kW",
        "description": "主電錶 功率",
        "node_name": "SCADA-A",
        "site": "Factory-A", "bu": "設備部", "zone": "B1", "floor": "B1",
        "driver_type": "Modbus TCP", "data_type": "float",
        "owner": "吳建志", "department": "電氣課",
        "created_date": _dt(_WEEK_START + timedelta(days=3), 15, 30),
    },
    {
        "tagname": "Factory-A.Energy.PLC05.MainBreaker_kWh",
        "description": "主電錶 累積用電",
        "node_name": "SCADA-A",
        "site": "Factory-A", "bu": "設備部", "zone": "B1", "floor": "B1",
        "driver_type": "Modbus TCP", "data_type": "float",
        "owner": "吳建志", "department": "電氣課",
        "created_date": _dt(_WEEK_START + timedelta(days=3), 15, 32),
    },
    {
        "tagname": "Factory-B.Safety.PLC30.GasDetector01_PPM",
        "description": "氣體偵測器01",
        "node_name": "SCADA-B",
        "site": "Factory-B", "bu": "製造部", "zone": "1F", "floor": "1F",
        "driver_type": "Modbus TCP", "data_type": "float",
        "owner": "黃靜宜", "department": "儀控課",
        "created_date": _dt(_WEEK_START + timedelta(days=4), 9, 0),
    },
    {
        "tagname": "Factory-C.Env.PLC35.Boiler01_FlueGas_Temp",
        "description": "鍋爐01 煙道氣溫",
        "node_name": "SCADA-C",
        "site": "Factory-C", "bu": "能源部", "zone": "RF", "floor": "RF",
        "driver_type": "Siemens", "data_type": "float",
        "owner": "蔡宗翰", "department": "動力課",
        "created_date": _dt(_WEEK_START + timedelta(days=4), 11, 15),
    },
]

# ── Modified tags during demo "week" ──────────────────────────────────────────
_MODIFIED_TAGS_ROWS = [
    {
        "tagname": "Factory-A.Line1.PLC01.Tank03_Level",
        "description": "3號槽液位（量程修正）",
        "site": "Factory-A", "bu": "製造部", "zone": "1F",
        "driver_type": "Allen-Bradley",
        "owner": "王志明", "department": "電氣課",
        "created_date": _dt(date(2026, 2, 10), 14, 0),
        "updated_date": _dt(_WEEK_START, 16, 30),
    },
    {
        "tagname": "Factory-B.Utility.PLC10.Chiller02_Temp",
        "description": "冰水機02 出水溫（換機型）",
        "site": "Factory-B", "bu": "設備部", "zone": "B1",
        "driver_type": "Siemens",
        "owner": "陳建國", "department": "動力課",
        "created_date": _dt(date(2026, 1, 5), 9, 0),
        "updated_date": _dt(_WEEK_START + timedelta(days=1), 10, 0),
    },
    {
        "tagname": "Factory-C.Process.PLC20.Reactor02_Temp",
        "description": "反應槽02 溫度（描述更新）",
        "site": "Factory-C", "bu": "製造部", "zone": "2F",
        "driver_type": "OPC-UA",
        "owner": "張美玲", "department": "製程課",
        "created_date": _dt(date(2026, 3, 1), 11, 0),
        "updated_date": _dt(_WEEK_START + timedelta(days=2), 9, 0),
    },
    {
        "tagname": "Factory-A.Energy.PLC05.SubBreaker02_kW",
        "description": "副電錶02 功率（地址修正）",
        "site": "Factory-A", "bu": "設備部", "zone": "2F",
        "driver_type": "Modbus TCP",
        "owner": "吳建志", "department": "電氣課",
        "created_date": _dt(date(2026, 2, 20), 10, 0),
        "updated_date": _dt(_WEEK_START + timedelta(days=3), 14, 0),
    },
    {
        "tagname": "Factory-B.Safety.PLC30.FireDetector03_Status",
        "description": "火警偵測器03（更換點位）",
        "site": "Factory-B", "bu": "設備部", "zone": "3F",
        "driver_type": "Allen-Bradley",
        "owner": "黃靜宜", "department": "儀控課",
        "created_date": _dt(date(2026, 3, 15), 9, 0),
        "updated_date": _dt(_WEEK_START + timedelta(days=3), 17, 0),
    },
    {
        "tagname": "Factory-C.Env.PLC35.Boiler01_SteamFlow",
        "description": "鍋爐01 蒸汽流量（單位修正）",
        "site": "Factory-C", "bu": "能源部", "zone": "RF",
        "driver_type": "Siemens",
        "owner": "蔡宗翰", "department": "動力課",
        "created_date": _dt(date(2026, 1, 20), 8, 0),
        "updated_date": _dt(_WEEK_START + timedelta(days=4), 13, 0),
    },
]

# ── Distribution data (current totals, period-independent) ────────────────────
_DIST = {
    "site": [
        {"label": "Factory-C", "count": 485},
        {"label": "Factory-A", "count": 450},
        {"label": "Factory-B", "count": 312},
    ],
    "bu": [
        {"label": "製造部", "count": 620},
        {"label": "設備部", "count": 380},
        {"label": "能源部", "count": 247},
    ],
    "zone": [
        {"label": "3F", "count": 509},
        {"label": "2F", "count": 418},
        {"label": "1F", "count": 320},
    ],
    "node_name": [
        {"label": "PRJ-C-製程控制",    "count": 375},
        {"label": "PRJ-A-製造線",      "count": 320},
        {"label": "PRJ-A-能源管理",    "count": 200},
        {"label": "PRJ-B-公用系統",    "count": 195},
        {"label": "PRJ-B-安全監控",    "count": 100},
        {"label": "PRJ-C-環境監測",    "count":  57},
    ],
    "driver_type": [
        {"label": "Allen-Bradley", "count": 540},
        {"label": "Siemens",       "count": 380},
        {"label": "Modbus TCP",    "count": 210},
        {"label": "OPC-UA",        "count": 117},
    ],
    "department": [
        {"label": "電氣課", "count": 405},
        {"label": "儀控課", "count": 312},
        {"label": "動力課", "count": 245},
        {"label": "製程課", "count": 185},
        {"label": "其他",   "count": 100},
    ],
    "data_type": [
        {"label": "float",   "count": 1150},
        {"label": "boolean", "count":   65},
        {"label": "integer", "count":   32},
    ],
    "floor": [
        {"label": "3F",  "count": 420},
        {"label": "2F",  "count": 390},
        {"label": "1F",  "count": 295},
        {"label": "B1",  "count": 112},
        {"label": "RF",  "count":  30},
    ],
}


# ── Public interface (matches queries.py exactly) ─────────────────────────────

def get_summary(start: date, end: date) -> dict[str, Any]:
    return {"total_tags": 1_247, "new_tags": 38, "modified_tags": 12}


def get_new_tags(start: date, end: date) -> list[dict]:
    return list(_NEW_TAGS_ROWS)


def get_modified_tags(start: date, end: date) -> list[dict]:
    return list(_MODIFIED_TAGS_ROWS)


def get_distribution(field: str) -> list[dict]:
    allowed = {"site", "bu", "zone", "driver_type", "department", "data_type", "floor", "node_name"}
    if field not in allowed:
        raise ValueError(f"Field '{field}' is not allowed for distribution query.")
    return list(_DIST.get(field, []))


def get_project_distribution() -> list[dict]:
    return list(_DIST.get("node_name", []))


def get_top_new_by_site(start: date, end: date) -> list[dict]:
    counts: dict[str, int] = {}
    for row in _NEW_TAGS_ROWS:
        counts[row["site"]] = counts.get(row["site"], 0) + 1
    return [{"label": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])]
