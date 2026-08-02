#!/usr/bin/env python3
"""Extract sponsorship and work-authorization signals from a job description."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PATTERNS = {
    "explicit_no_sponsorship": [
        r"(?:do|does|will)\s+not\s+(?:provide|offer|support)\s+(?:current\s+or\s+future\s+|now\s+or\s+future\s+)(?:employment\s+|visa\s+|immigration\s+)?sponsorship",
        r"(?:do|does|will)\s+not\s+(?:provide|offer|support)\s+(?:employment\s+|visa\s+|immigration\s+)?sponsorship",
        r"(?:do|does|will)\s+not\s+sponsor(?:\s+(?:candidates?|applicants?|employees?))?",
        r"no\s+(?:employment\s+|visa\s+|immigration\s+)?sponsorship",
        r"not\s+(?:eligible|available)\s+for\s+(?:visa\s+|immigration\s+)?sponsorship",
        r"unable\s+to\s+(?:provide|offer|support)\s+(?:visa\s+|immigration\s+)?sponsorship",
        r"(?:unable|not\s+able)\s+to\s+sponsor(?:\s+(?:candidates?|applicants?|employees?))?",
        r"without\s+(?:current\s+or\s+future|now\s+or\s+future)\s+sponsorship",
        r"(?:sponsorship|visa\s+support)\s+(?:is\s+)?not\s+(?:available|offered|provided|supported)",
        r"(?:cannot|can't)\s+sponsor(?:\s+(?:candidates?|applicants?|employees?))?",
    ],
    "unrestricted_authorization_required": [
        r"(?:must|required\s+to)\s+(?:have|possess)\s+(?:permanent\s+)?unrestricted\s+(?:u\.s\.\s+)?work\s+authorization",
        r"authorized\s+to\s+work\s+.*without\s+(?:current\s+or\s+future)\s+sponsorship",
        r"(?:citizen|permanent\s+resident|green\s+card)\s+only",
    ],
    "citizenship_or_clearance": [
        r"must\s+be\s+(?:a\s+)?u\.s\.\s+(?:citizen|person)",
        r"u\.s\.\s+citizens?(?:hip)?\s+(?:is\s+)?required",
        r"(?:active|obtain|maintain|eligible\s+for).{0,30}(?:security\s+clearance|secret\s+clearance|top\s+secret|ts/sci)",
    ],
    "explicit_sponsorship_support": [
        r"(?:visa\s+|immigration\s+)?sponsorship\s+(?:is\s+)?(?:available|provided|offered)",
        r"(?:we|employer|company)\s+(?:can|will)\s+sponsor",
        r"(?:can|will)\s+sponsor.{0,60}(?:h-?1b|employment\s+visa|work\s+visa|qualified\s+(?:candidates|applicants))",
        r"open\s+to\s+(?:candidates|applicants).{0,40}(?:requiring|needing)\s+sponsorship",
        r"h-?1b\s+(?:visa\s+)?sponsorship",
    ],
    "conditional_sponsorship": [
        r"sponsorship.{0,40}(?:case[- ]by[- ]case|depending\s+on|may\s+be\s+available|not\s+guaranteed)",
        r"(?:may|might)\s+(?:provide|offer)\s+(?:visa\s+|immigration\s+)?sponsorship",
        r"(?:we|employer|company)\s+(?:may|might)\s+sponsor",
    ],
    "temporary_work_authorization_signal": [
        r"\b(?:stem\s+)?opt\b",
        r"\bcpt\b",
        r"e-?verify",
        r"\bi-?983\b",
    ],
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def find_signals(text: str) -> dict[str, list[str]]:
    normalized = normalize(text)
    found = {}
    for category, patterns in PATTERNS.items():
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, normalized, flags=re.IGNORECASE):
                snippet = normalized[max(0, match.start() - 70) : match.end() + 70].strip()
                if snippet not in matches:
                    matches.append(snippet)
        if matches:
            found[category] = matches
    return found


def classify(signals: dict[str, list[str]]) -> tuple[str, str]:
    if any(key in signals for key in ("explicit_no_sponsorship", "unrestricted_authorization_required")):
        return "confirmed_no", "Explicit sponsorship or work-authorization restriction detected."
    if "conditional_sponsorship" in signals:
        return "verify", "Conditional sponsorship language detected."
    if "explicit_sponsorship_support" in signals:
        return "confirmed_support", "Explicit sponsorship-support language detected."
    if "citizenship_or_clearance" in signals:
        return "verify", "Citizenship or clearance language requires candidate-specific verification."
    return "unknown", "No reliable sponsorship statement detected."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, help="UTF-8 job-description text file")
    source.add_argument("--text", help="Job-description text")
    args = parser.parse_args()
    try:
        text = args.file.read_text(encoding="utf-8") if args.file else args.text
    except OSError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    signals = find_signals(text or "")
    classification, reason = classify(signals)
    print(json.dumps({"classification": classification, "reason": reason, "signals": signals}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
