#!/usr/bin/env python3
"""Sort a job shortlist and render Markdown, HTML, or CSV."""

from __future__ import annotations

import argparse
import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


FIELDS = ("fit", "posted_at", "posted", "role", "company", "location", "workplace_type", "sources", "application_method", "sponsorship_signal", "why_match", "url", "checked_at")


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def safe_url(value: object) -> str:
    url = clean(value)
    parsed = urlparse(url)
    return url if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def numeric_fit(value: object) -> float:
    try:
        return float(clean(value))
    except ValueError:
        return -1.0


def timestamp(value: object) -> float:
    try:
        parsed = datetime.fromisoformat(clean(value).replace("Z", "+00:00"))
        return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).timestamp()
    except ValueError:
        return float("-inf")


def sort_jobs(jobs):
    jobs.sort(key=lambda job: (job["company"].casefold(), job["role"].casefold()))
    jobs.sort(key=lambda job: timestamp(job["posted_at"]), reverse=True)
    jobs.sort(key=lambda job: numeric_fit(job["fit"]), reverse=True)
    for rank, job in enumerate(jobs, 1):
        job["rank"] = str(rank)
    return jobs


def load_data(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise ValueError("Input must contain a jobs array")
    jobs = []
    for index, raw in enumerate(payload["jobs"], 1):
        job = {field: clean(raw.get(field)) for field in FIELDS}
        job["url"] = safe_url(raw.get("url"))
        if not job["role"] or not job["url"]:
            raise ValueError(f"Job {index} requires role and an http(s) URL")
        jobs.append(job)
    return payload, sort_jobs(jobs)


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def render_markdown(payload, jobs):
    lines = [f"# {clean(payload.get('title')) or 'Job Shortlist'}", "", f"Scanned: {clean(payload.get('scanned_count')) or 'Unknown'} | Qualifying: {len(jobs)}", "", "| Rank | Fit | Posted | Role | Company | Location | Workplace | Found on | Apply method | Sponsorship | Why it matches |", "|---:|---:|---|---|---|---|---|---|---|---|---|"]
    for job in jobs:
        role = f"[{md_escape(job['role'])}]({job['url']})"
        values = [job["rank"], job["fit"], job["posted"], role, job["company"], job["location"], job["workplace_type"], job["sources"], job["application_method"], job["sponsorship_signal"], job["why_match"]]
        lines.append("| " + " | ".join(md_escape(v) if i != 3 else v for i, v in enumerate(values)) + " |")
    return "\n".join(lines) + "\n"


def render_html(payload, jobs):
    rows = []
    for job in jobs:
        values = [job["rank"], job["fit"], job["posted"], job["company"], job["location"], job["workplace_type"], job["sources"], job["application_method"], job["sponsorship_signal"], job["why_match"]]
        link = f'<a href="{html.escape(job["url"], quote=True)}">{html.escape(job["role"])}</a>'
        cells = [html.escape(v) for v in values[:3]] + [link] + [html.escape(v) for v in values[3:]]
        rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")
    title = html.escape(clean(payload.get("title")) or "Job Shortlist")
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>body{{font:15px system-ui;margin:32px}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #ddd;padding:8px;text-align:left;vertical-align:top}}</style></head><body><h1>{title}</h1><table><tbody>{"".join(rows)}</tbody></table></body></html>\n'


def render_csv(path: Path, jobs):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("rank",) + FIELDS)
        writer.writeheader()
        writer.writerows(jobs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--html", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    if not any((args.markdown, args.html, args.csv)):
        parser.error("select at least one output")
    payload, jobs = load_data(args.input)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(payload, jobs), encoding="utf-8")
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(render_html(payload, jobs), encoding="utf-8")
    if args.csv:
        render_csv(args.csv, jobs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
