"""SQL query functions for report data."""

from datetime import date, datetime
from typing import Any

from app.db import fetch_all, fetch_one


def get_summary(start: date, end: date) -> dict[str, Any]:
    """Return high-level counts for the report period."""
    row = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM tags) AS total_tags,
            (SELECT COUNT(*) FROM tags
             WHERE created_date >= %(start)s AND created_date < %(end)s
            ) AS new_tags,
            (SELECT COUNT(*) FROM tags
             WHERE updated_date >= %(start)s AND updated_date < %(end)s
               AND updated_date::date != created_date::date
            ) AS modified_tags
        """,
        {"start": start, "end": end},
    )
    return row or {"total_tags": 0, "new_tags": 0, "modified_tags": 0}


def get_new_tags(start: date, end: date) -> list[dict]:
    """Return list of tags created within the period."""
    return fetch_all(
        """
        SELECT
            tagname, description, node_name,
            site, bu, zone, floor,
            driver_type, data_type,
            owner, department,
            created_date
        FROM tags
        WHERE created_date >= %(start)s AND created_date < %(end)s
        ORDER BY created_date DESC
        """,
        {"start": start, "end": end},
    )


def get_modified_tags(start: date, end: date) -> list[dict]:
    """Return list of tags updated (but not newly created) within the period."""
    return fetch_all(
        """
        SELECT
            tagname, description,
            site, bu, zone,
            driver_type,
            owner, department,
            created_date, updated_date
        FROM tags
        WHERE updated_date >= %(start)s AND updated_date < %(end)s
          AND updated_date::date != created_date::date
        ORDER BY updated_date DESC
        """,
        {"start": start, "end": end},
    )


def get_distribution(field: str) -> list[dict]:
    """Return COUNT(*) grouped by the given column (safe whitelist used)."""
    allowed = {"site", "bu", "zone", "driver_type", "department", "data_type", "floor", "node_name"}
    if field not in allowed:
        raise ValueError(f"Field '{field}' is not allowed for distribution query.")
    return fetch_all(
        f"""
        SELECT
            COALESCE(NULLIF(TRIM({field}), ''), '(未設定)') AS label,
            COUNT(*) AS count
        FROM tags
        GROUP BY label
        ORDER BY count DESC
        """
    )


def get_top_new_by_site(start: date, end: date) -> list[dict]:
    """New tags breakdown by site for the period."""
    return fetch_all(
        """
        SELECT
            COALESCE(NULLIF(TRIM(site), ''), '(未設定)') AS label,
            COUNT(*) AS count
        FROM tags
        WHERE created_date >= %(start)s AND created_date < %(end)s
        GROUP BY label
        ORDER BY count DESC
        """,
        {"start": start, "end": end},
    )
