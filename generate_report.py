"""
KPM Monthly Report Generator
Usage:
  python generate_report.py               # current month
  python generate_report.py 2026 3        # specific year/month
"""

import sys
import os
import json
import math
from datetime import datetime, date
from pathlib import Path

import psycopg2
import psycopg2.extras
from jinja2 import Environment, FileSystemLoader

# ── DB connection ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("PG_HOST",     "localhost"),
    "port":     int(os.getenv("PG_PORT", 5432)),
    "dbname":   os.getenv("PG_DB",       "kepware"),
    "user":     os.getenv("PG_USER",     "postgres"),
    "password": os.getenv("PG_PASSWORD", ""),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
PALETTE = ["#22d3ee","#3b82f6","#a855f7","#f59e0b","#22c55e","#60a5fa","#f43f5e","#84cc16"]

def color(i): return PALETTE[i % len(PALETTE)]

def pct(a, b): return round(a / b * 100, 1) if b else 0

def health_pct(conn, field, total, month_start, month_end):
    """% of rows where field IS NOT NULL and != ''."""
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT COUNT(*) FROM tags
            WHERE ({field} IS NOT NULL AND TRIM({field}::text) <> '')
              AND created_date < %s
        """, (month_end,))
        filled = cur.fetchone()[0]
    return round(filled / total * 100, 1) if total else 0


def fetch_all(conn, sql, params=()):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def fetchone(conn, sql, params=()):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return row[0] if row else 0


# ── Main ──────────────────────────────────────────────────────────────────────
def generate(year: int, month: int):
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, month + 1, 1)

    # Previous month boundaries
    if month == 1:
        prev_start = date(year - 1, 12, 1)
        prev_end   = date(year, 1, 1)
    else:
        prev_start = date(year, month - 1, 1)
        prev_end   = date(year, month, 1)

    label = f"{year}-{month:02d}"
    print(f"[KPM] Generating report for {label} ...")

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        # ── KPI ───────────────────────────────────────────────────────────────
        total_now  = fetchone(conn, "SELECT COUNT(*) FROM tags WHERE created_date < %s", (month_end,))
        total_prev = fetchone(conn, "SELECT COUNT(*) FROM tags WHERE created_date < %s", (prev_end,))
        new_this   = fetchone(conn,
            "SELECT COUNT(*) FROM tags WHERE created_date >= %s AND created_date < %s",
            (month_start, month_end))
        new_prev   = fetchone(conn,
            "SELECT COUNT(*) FROM tags WHERE created_date >= %s AND created_date < %s",
            (prev_start, prev_end))
        mod_this   = fetchone(conn,
            """SELECT COUNT(*) FROM tags
               WHERE updated_date >= %s AND updated_date < %s
                 AND created_date < %s""",
            (month_start, month_end, month_start))
        mod_prev   = fetchone(conn,
            """SELECT COUNT(*) FROM tags
               WHERE updated_date >= %s AND updated_date < %s
                 AND created_date < %s""",
            (prev_start, prev_end, prev_start))

        delta_total = total_now - total_prev
        delta_total_pct = round(delta_total / total_prev * 100, 1) if total_prev else 0
        new_delta_pct   = round((new_this - new_prev) / new_prev * 100, 1) if new_prev else 0
        mod_delta_pct   = round((mod_this - mod_prev) / mod_prev * 100, 1) if mod_prev else 0

        # ── Health ────────────────────────────────────────────────────────────
        health_fields = [
            ("設有描述",   "description"),
            ("指定負責人", "owner"),
            ("設有區域",   "zone"),
            ("指定 BU",    "bu"),
            ("Driver Type","driver_type"),
            ("部門設定",   "department"),
        ]
        health_bars = []
        for lbl, col_name in health_fields:
            p = health_pct(conn, col_name, total_now, month_start, month_end)
            filled = math.floor(p / 100 * total_now)
            health_bars.append({"label": lbl, "pct": p, "filled": filled, "total": total_now})

        overall_health = round(sum(h["pct"] for h in health_bars) / len(health_bars), 1)

        # ── System (driver_type) dist ─────────────────────────────────────────
        rows = fetch_all(conn, """
            SELECT driver_type AS label, COUNT(*) AS cnt
            FROM tags WHERE created_date < %s AND driver_type IS NOT NULL
            GROUP BY driver_type ORDER BY cnt DESC
        """, (month_end,))
        sys_dist = [{"label": r["label"], "count": int(r["cnt"]), "color": color(i)}
                    for i, r in enumerate(rows)]

        rows_new = fetch_all(conn, """
            SELECT driver_type AS label, COUNT(*) AS cnt
            FROM tags WHERE created_date >= %s AND created_date < %s AND driver_type IS NOT NULL
            GROUP BY driver_type ORDER BY cnt DESC
        """, (month_start, month_end))
        sys_new = [{"label": r["label"], "count": int(r["cnt"]), "color": color(i)}
                   for i, r in enumerate(rows_new)]

        # System × BU matrix
        sys_labels  = [r["label"] for r in sys_dist]
        bu_labels_m = fetch_all(conn, """
            SELECT DISTINCT bu FROM tags WHERE created_date < %s AND bu IS NOT NULL ORDER BY bu
        """, (month_end,))
        bu_labels_m = [r["bu"] for r in bu_labels_m]

        sys_bu_matrix = []
        for sys_lbl in sys_labels:
            row_vals = []
            row_total = 0
            for bu_lbl in bu_labels_m:
                cnt = fetchone(conn, """
                    SELECT COUNT(*) FROM tags
                    WHERE driver_type=%s AND bu=%s AND created_date < %s
                """, (sys_lbl, bu_lbl, month_end))
                row_vals.append(int(cnt))
                row_total += int(cnt)
            sys_bu_matrix.append({"sys": sys_lbl, "vals": row_vals, "total": row_total})
        sys_bu_totals = [sum(r["vals"][i] for r in sys_bu_matrix) for i in range(len(bu_labels_m))]

        # ── BU dist ───────────────────────────────────────────────────────────
        rows = fetch_all(conn, """
            SELECT bu AS label, COUNT(*) AS cnt
            FROM tags WHERE created_date < %s AND bu IS NOT NULL
            GROUP BY bu ORDER BY cnt DESC
        """, (month_end,))
        bu_dist = [{"label": r["label"], "count": int(r["cnt"]), "color": color(i)}
                   for i, r in enumerate(rows)]

        rows_new = fetch_all(conn, """
            SELECT bu AS label, COUNT(*) AS cnt
            FROM tags WHERE created_date >= %s AND created_date < %s AND bu IS NOT NULL
            GROUP BY bu ORDER BY cnt DESC
        """, (month_start, month_end))
        bu_new = [{"label": r["label"], "count": int(r["cnt"]), "color": color(i)}
                  for i, r in enumerate(rows_new)]

        # BU trend — past 6 months
        bu_trend_months = []
        bu_trend_data   = {b["label"]: [] for b in bu_dist}
        for i in range(5, -1, -1):
            # month offset
            m = month - i
            y = year
            while m <= 0:
                m += 12; y -= 1
            end_of = date(y, m + 1, 1) if m < 12 else date(y + 1, 1, 1)
            bu_trend_months.append(f"{y}-{m:02d}")
            for b in bu_dist:
                cnt = fetchone(conn, """
                    SELECT COUNT(*) FROM tags WHERE bu=%s AND created_date < %s
                """, (b["label"], end_of))
                bu_trend_data[b["label"]].append(int(cnt))

        # ── Project (node_name) dist ──────────────────────────────────────────
        rows = fetch_all(conn, """
            SELECT node_name AS label, site, bu, COUNT(*) AS cnt,
                   SUM(CASE WHEN created_date >= %s AND created_date < %s THEN 1 ELSE 0 END) AS new_cnt
            FROM tags WHERE created_date < %s AND node_name IS NOT NULL
            GROUP BY node_name, site, bu ORDER BY cnt DESC
        """, (month_start, month_end, month_end))
        proj_dist = [{"label": r["label"], "count": int(r["cnt"]),
                      "site": r["site"] or "", "bu": r["bu"] or "",
                      "new_cnt": int(r["new_cnt"]), "color": color(i)}
                     for i, r in enumerate(rows)]

        # ── Site dist ─────────────────────────────────────────────────────────
        rows = fetch_all(conn, """
            SELECT site AS label, COUNT(*) AS cnt,
                   SUM(CASE WHEN created_date >= %s AND created_date < %s THEN 1 ELSE 0 END) AS new_cnt
            FROM tags WHERE created_date < %s AND site IS NOT NULL
            GROUP BY site ORDER BY cnt DESC
        """, (month_start, month_end, month_end))
        site_dist = [{"label": r["label"], "count": int(r["cnt"]),
                      "new_cnt": int(r["new_cnt"]), "color": color(i)}
                     for i, r in enumerate(rows)]

        # Site trend — past 6 months
        site_trend_data = {s["label"]: [] for s in site_dist}
        for mo_lbl in bu_trend_months:
            y_t, m_t = int(mo_lbl[:4]), int(mo_lbl[5:])
            end_of = date(y_t, m_t + 1, 1) if m_t < 12 else date(y_t + 1, 1, 1)
            for s in site_dist:
                cnt = fetchone(conn,
                    "SELECT COUNT(*) FROM tags WHERE site=%s AND created_date < %s",
                    (s["label"], end_of))
                site_trend_data[s["label"]].append(int(cnt))

        # Site × BU matrix
        site_bu_matrix = []
        for s in site_dist:
            row_vals = []
            for bu_lbl in bu_labels_m:
                cnt = fetchone(conn, """
                    SELECT COUNT(*) FROM tags
                    WHERE site=%s AND bu=%s AND created_date < %s
                """, (s["label"], bu_lbl, month_end))
                row_vals.append(int(cnt))
            site_bu_matrix.append({"site": s["label"], "vals": row_vals,
                                    "total": s["count"], "color": s["color"]})
        site_bu_totals = [sum(r["vals"][i] for r in site_bu_matrix) for i in range(len(bu_labels_m))]

        # ── Department dist ───────────────────────────────────────────────────
        rows = fetch_all(conn, """
            SELECT department AS label, COUNT(*) AS cnt
            FROM tags WHERE created_date < %s AND department IS NOT NULL
            GROUP BY department ORDER BY cnt DESC
        """, (month_end,))
        dept_dist = [{"label": r["label"], "count": int(r["cnt"]), "color": color(i)}
                     for i, r in enumerate(rows)]

        # ── Overall trend — past 6 months ─────────────────────────────────────
        trend_total, trend_new, trend_mod = [], [], []
        for mo_lbl in bu_trend_months:
            y_t, m_t = int(mo_lbl[:4]), int(mo_lbl[5:])
            ms = date(y_t, m_t, 1)
            me = date(y_t, m_t + 1, 1) if m_t < 12 else date(y_t + 1, 1, 1)
            trend_total.append(fetchone(conn,
                "SELECT COUNT(*) FROM tags WHERE created_date < %s", (me,)))
            trend_new.append(fetchone(conn,
                "SELECT COUNT(*) FROM tags WHERE created_date >= %s AND created_date < %s", (ms, me)))
            trend_mod.append(fetchone(conn, """
                SELECT COUNT(*) FROM tags
                WHERE updated_date >= %s AND updated_date < %s AND created_date < %s
            """, (ms, me, ms)))

        # ── Change log — new tags this month ─────────────────────────────────
        new_tags = fetch_all(conn, """
            SELECT tagname, description, site, bu, zone, driver_type, owner,
                   created_date
            FROM tags
            WHERE created_date >= %s AND created_date < %s
            ORDER BY created_date
        """, (month_start, month_end))

        mod_tags = fetch_all(conn, """
            SELECT tagname, description, site, bu, driver_type, owner,
                   created_date, updated_date
            FROM tags
            WHERE updated_date >= %s AND updated_date < %s
              AND created_date < %s
            ORDER BY updated_date
        """, (month_start, month_end, month_start))

    finally:
        conn.close()

    # ── Compute heatmap class ─────────────────────────────────────────────────
    def hm_class(val, max_val):
        if val == 0 or max_val == 0: return "hm0"
        r = val / max_val
        if r < 0.15: return "hm1"
        if r < 0.35: return "hm2"
        if r < 0.65: return "hm3"
        return "hm4"

    all_sys_bu_vals = [v for r in sys_bu_matrix for v in r["vals"]]
    sys_bu_max = max(all_sys_bu_vals) if all_sys_bu_vals else 1

    all_site_bu_vals = [v for r in site_bu_matrix for v in r["vals"]]
    site_bu_max = max(all_site_bu_vals) if all_site_bu_vals else 1

    # ── Render ────────────────────────────────────────────────────────────────
    env = Environment(loader=FileSystemLoader(Path(__file__).parent),
                      autoescape=False)
    env.filters["tojson"] = lambda v: json.dumps(v, ensure_ascii=False)
    env.filters["pct"]    = pct
    env.filters["hm"]     = lambda v: hm_class(v, sys_bu_max)
    env.filters["hm_s"]   = lambda v: hm_class(v, site_bu_max)

    tmpl = env.get_template("report_template.html")
    html = tmpl.render(
        year=year, month=month, label=label,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # KPI
        total_now=total_now, delta_total=delta_total,
        delta_total_pct=delta_total_pct,
        new_this=new_this, new_prev=new_prev, new_delta_pct=new_delta_pct,
        mod_this=mod_this, mod_prev=mod_prev, mod_delta_pct=mod_delta_pct,
        overall_health=overall_health,
        # Health
        health_bars=health_bars,
        # System
        sys_dist=sys_dist, sys_new=sys_new,
        bu_labels_m=bu_labels_m,
        sys_bu_matrix=sys_bu_matrix, sys_bu_totals=sys_bu_totals,
        sys_bu_max=sys_bu_max,
        # BU
        bu_dist=bu_dist, bu_new=bu_new,
        bu_trend_months=bu_trend_months, bu_trend_data=bu_trend_data,
        # Project
        proj_dist=proj_dist,
        # Site
        site_dist=site_dist, site_trend_data=site_trend_data,
        site_bu_matrix=site_bu_matrix, site_bu_totals=site_bu_totals,
        site_bu_max=site_bu_max,
        # Dept
        dept_dist=dept_dist,
        # Trend
        trend_months=bu_trend_months,
        trend_total=trend_total, trend_new=trend_new, trend_mod=trend_mod,
        # Changes
        new_tags=new_tags, mod_tags=mod_tags,
    )

    out_path = Path(__file__).parent / f"report_{label}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"[KPM] Report written → {out_path}")
    return str(out_path)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        y, m = int(sys.argv[1]), int(sys.argv[2])
    else:
        now = datetime.now()
        y, m = now.year, now.month
    generate(y, m)
