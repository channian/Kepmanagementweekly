"""HTML and optional PDF report renderer."""

import json
import os
from datetime import date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    def format_dt(value) -> str:
        if value is None:
            return ""
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d %H:%M") if isinstance(value, datetime) else value.strftime("%Y-%m-%d")
        return str(value)

    def format_number(value) -> str:
        try:
            return f"{int(value):,}"
        except (TypeError, ValueError):
            return str(value)

    def tojson_filter(value) -> str:
        return json.dumps(value, ensure_ascii=False, default=str)

    env.filters["format_dt"] = format_dt
    env.filters["format_number"] = format_number
    env.filters["tojson"] = tojson_filter
    return env


def render_html(context: dict) -> str:
    """Render the report template with the given context and return HTML string."""
    env = _make_env()
    template = env.get_template("report.html")
    return template.render(**context)


def save_html(html: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def save_pdf(html: str, output_path: Path) -> None:
    """Convert HTML to PDF using WeasyPrint (optional dependency)."""
    try:
        from weasyprint import HTML  # type: ignore
    except ImportError:
        raise ImportError(
            "WeasyPrint is not installed. Run: pip install weasyprint\n"
            "Or use --no-pdf to skip PDF generation."
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(str(output_path))
