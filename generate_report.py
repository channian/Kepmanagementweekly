#!/usr/bin/env python3
"""
Kepware Tag Management Report Generator
========================================

Usage examples
--------------
# 本週報告（HTML）
python generate_report.py --mode weekly

# 本月報告（HTML + PDF）
python generate_report.py --mode monthly --pdf

# 自訂期間
python generate_report.py --start 2026-03-01 --end 2026-03-31

# 指定輸出目錄
python generate_report.py --mode weekly --output-dir /tmp/reports
"""

import argparse
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ── Period helpers ────────────────────────────────────────────────

def week_range() -> tuple[date, date]:
    today = date.today()
    start = today - timedelta(days=today.weekday())   # Monday
    end = start + timedelta(days=7)                   # next Monday (exclusive)
    return start, end


def month_range() -> tuple[date, date]:
    today = date.today()
    start = today.replace(day=1)
    if today.month == 12:
        end = today.replace(year=today.year + 1, month=1, day=1)
    else:
        end = today.replace(month=today.month + 1, day=1)
    return start, end


def period_label(mode: str, start: date, end: date) -> str:
    if mode == "weekly":
        return f"{start.strftime('%Y/%m/%d')} — {(end - timedelta(days=1)).strftime('%Y/%m/%d')} (週報)"
    if mode == "monthly":
        return f"{start.strftime('%Y/%m')} 月報"
    return f"{start.strftime('%Y-%m-%d')} ~ {(end - timedelta(days=1)).strftime('%Y-%m-%d')}"


# ── Main ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="產生 Kepware 點位管理週報/月報")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--mode",
        choices=["weekly", "monthly"],
        default="weekly",
        help="報告模式：weekly（本週）或 monthly（本月）",
    )
    parser.add_argument("--start", help="自訂起始日期 YYYY-MM-DD（搭配 --end 使用）")
    parser.add_argument("--end",   help="自訂結束日期 YYYY-MM-DD（不含當天）")
    parser.add_argument("--pdf",   action="store_true", help="同時產生 PDF 檔案")
    parser.add_argument("--demo",  action="store_true", help="使用內建假資料預覽報表（無需資料庫）")
    parser.add_argument(
        "--output-dir",
        default=os.getenv("REPORT_OUTPUT_DIR", "reports"),
        help="輸出目錄（預設：reports/）",
    )
    args = parser.parse_args()

    # Resolve period
    if args.start and args.end:
        start = date.fromisoformat(args.start)
        end   = date.fromisoformat(args.end)
        mode  = "custom"
    elif args.mode == "monthly":
        start, end = month_range()
        mode = "monthly"
    else:
        start, end = week_range()
        mode = "weekly"

    label = period_label(mode, start, end)
    print(f"產生報告：{label}")
    print(f"查詢期間：{start} ~ {end - timedelta(days=1)}")

    from app.renderer import render_html, save_html, save_pdf

    if args.demo:
        from app import demo_data as data_source
        print("[Demo 模式] 使用內建假資料，不需要資料庫連線。")
    else:
        from app import queries as data_source  # type: ignore[assignment]

    if args.demo:
        summary       = data_source.get_summary(start, end)
        new_tags      = data_source.get_new_tags(start, end)
        modified_tags = data_source.get_modified_tags(start, end)
        dist_site        = data_source.get_distribution("site")
        dist_bu          = data_source.get_distribution("bu")
        dist_zone        = data_source.get_distribution("zone")
        dist_driver_type = data_source.get_distribution("driver_type")
        dist_department  = data_source.get_distribution("department")
    else:
        print("查詢資料庫中…")
        try:
            summary       = data_source.get_summary(start, end)
            new_tags      = data_source.get_new_tags(start, end)
            modified_tags = data_source.get_modified_tags(start, end)
            dist_site        = data_source.get_distribution("site")
            dist_bu          = data_source.get_distribution("bu")
            dist_zone        = data_source.get_distribution("zone")
            dist_driver_type = data_source.get_distribution("driver_type")
            dist_department  = data_source.get_distribution("department")
        except Exception as exc:
            print(f"\n[錯誤] 無法連線或查詢資料庫：{exc}")
            print("請確認 .env 中的 PG_HOST / PG_DB / PG_USER / PG_PASSWORD 設定正確。")
            sys.exit(1)

    context = {
        "mode":           mode,
        "period_label":   label,
        "site_name":      os.getenv("SITE_NAME", ""),
        "generated_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary":        summary,
        "new_tags":       new_tags,
        "modified_tags":  modified_tags,
        "dist_site":        dist_site,
        "dist_bu":          dist_bu,
        "dist_zone":        dist_zone,
        "dist_driver_type": dist_driver_type,
        "dist_department":  dist_department,
    }

    html = render_html(context)

    # Output filenames
    date_str = start.strftime("%Y-%m-%d")
    suffix   = ("demo_" if args.demo else "") + mode
    out_dir  = Path(args.output_dir)
    html_path = out_dir / f"report_{date_str}_{suffix}.html"
    pdf_path  = out_dir / f"report_{date_str}_{suffix}.pdf"

    save_html(html, html_path)
    print(f"HTML 已產生：{html_path.resolve()}")

    if args.pdf:
        print("轉換 PDF 中…")
        try:
            save_pdf(html, pdf_path)
            print(f"PDF 已產生：{pdf_path.resolve()}")
        except ImportError as exc:
            print(f"[警告] {exc}")


if __name__ == "__main__":
    main()
