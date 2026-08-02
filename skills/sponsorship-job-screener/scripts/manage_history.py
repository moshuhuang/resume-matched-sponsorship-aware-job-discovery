#!/usr/bin/env python3
"""Filter and record job-shortlist history for repeat-free future runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse


STATUS_PRIORITY = {"presented": 1, "applied": 2, "skipped": 2}


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).casefold()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def canonical_url(value: object) -> str:
    raw = clean(value)
    if not raw:
        return ""
    parsed = urlparse(raw)
    host = parsed.netloc.casefold().removeprefix("www.")
    path = re.sub(r"/+", "/", parsed.path).rstrip("/")
    linkedin = re.search(r"/jobs/view/(\d+)", path)
    if host.endswith("linkedin.com") and linkedin:
        path = f"/jobs/view/{linkedin.group(1)}"
    elif host.endswith("indeed.com"):
        job_key = parse_qs(parsed.query).get("jk") or parse_qs(parsed.query).get("vjk")
        if job_key:
            return f"https://indeed.com/viewjob?jk={job_key[0]}"
    return urlunparse((parsed.scheme.casefold() or "https", host, path, "", "", ""))


def fingerprint(job: dict[str, object]) -> str:
    identity = "|".join(
        (normalize(job.get("company")), normalize(job.get("role") or job.get("title")), normalize(job.get("location")))
    )
    return hashlib.sha256(identity.encode()).hexdigest()[:24]


def job_urls(job: dict[str, object]) -> set[str]:
    values = [job.get("url")]
    extra = job.get("source_urls") or job.get("urls") or []
    values.extend(extra if isinstance(extra, list) else [extra])
    return {canonical_url(value) for value in values if canonical_url(value)}


def load_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise ValueError(f"{path} must contain an object with a jobs array")
    return payload


def load_ledger(path: Path) -> dict[str, object]:
    return load_payload(path) if path.exists() else {"version": 1, "updated_at": None, "jobs": []}


def find_match(records, job):
    key, urls = fingerprint(job), job_urls(job)
    for record in records:
        if record.get("job_key") == key or urls.intersection(set(record.get("urls") or [])):
            return record
    return None


def filter_unseen(ledger, payload):
    records = ledger.get("jobs") or []
    output = dict(payload)
    output["jobs"] = [job for job in payload["jobs"] if find_match(records, job) is None]
    output["history_excluded_count"] = len(payload["jobs"]) - len(output["jobs"])
    return output


def record_jobs(ledger, payload, status, recorded_at):
    records = ledger.get("jobs") or []
    for job in payload["jobs"]:
        record = find_match(records, job)
        urls = sorted(job_urls(job))
        sources = job.get("sources") or job.get("source") or []
        if not isinstance(sources, list):
            sources = [sources] if sources else []
        if record is None:
            record = {
                "job_key": fingerprint(job), "company": clean(job.get("company")),
                "role": clean(job.get("role") or job.get("title")), "location": clean(job.get("location")),
                "urls": urls, "sources": sorted({clean(s) for s in sources if clean(s)}),
                "first_presented_at": recorded_at, "status": status,
            }
            records.append(record)
        else:
            record["urls"] = sorted(set(record.get("urls") or []).union(urls))
            record["sources"] = sorted(set(record.get("sources") or []).union(clean(s) for s in sources if clean(s)))
            if STATUS_PRIORITY[status] >= STATUS_PRIORITY.get(clean(record.get("status")), 0):
                record["status"] = status
        record["updated_at"] = recorded_at
        if status in {"applied", "skipped"}:
            record[f"{status}_at"] = recorded_at
    ledger["jobs"] = sorted(records, key=lambda item: (normalize(item.get("company")), normalize(item.get("role"))))
    ledger["updated_at"] = recorded_at
    return ledger


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("filter", "record"))
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--status", choices=tuple(STATUS_PRIORITY), default="presented")
    parser.add_argument("--at", default=datetime.now(timezone.utc).isoformat())
    args = parser.parse_args()
    ledger, payload = load_ledger(args.ledger), load_payload(args.input)
    if args.command == "filter":
        if not args.output:
            parser.error("filter requires --output")
        write_json(args.output, filter_unseen(ledger, payload))
    else:
        write_json(args.ledger, record_jobs(ledger, payload, args.status, args.at))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
