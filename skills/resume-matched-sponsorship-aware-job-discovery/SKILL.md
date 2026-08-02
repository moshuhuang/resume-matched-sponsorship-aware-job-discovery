---
name: resume-matched-sponsorship-aware-job-discovery
description: Discover, open, screen, deduplicate, and rank recent job postings against a private candidate profile and future sponsorship needs. Use when an agent needs to search LinkedIn, Indeed, Glassdoor, public job boards, or employer career pages; apply one recency cutoff across sources; optionally exclude LinkedIn Easy Apply; reject explicit sponsorship conflicts; evaluate full-job-description fit; suppress previously presented or applied jobs; and return application links without submitting applications.
---

# Resume-Matched & Sponsorship-Aware Job Discovery

Produce a current, repeat-free application shortlist without asking the user to collect job links manually. Treat job titles as discovery hints and base fit on the full job description and factual candidate evidence.

## Load private inputs

Ask for the path to a private candidate profile or resume evidence file. Recommend starting from the repository's `examples/candidate-profile.example.md` and storing the completed file outside the repository. Never copy private input into the skill directory, output, logs, or source control.

Read [references/discovery-workflow.md](references/discovery-workflow.md) before searching, [references/fit-rubric.md](references/fit-rubric.md) before scoring, [references/output-schema.md](references/output-schema.md) before formatting results, and [references/privacy-boundaries.md](references/privacy-boundaries.md) before using an authenticated site.

If no current candidate evidence is available, complete discovery and sponsorship screening, retain the surviving links locally, and label fit `Pending profile`. Do not invent a score.

## Run the workflow

1. Convert the request into target functions, geography, workplace types, excluded methods, seniority, sources, batch size, and an exact cutoff. Interpret `past three days` as `run_started_at - 72 hours`.
2. Search each requested source and record its access state. Do not claim coverage for a source that was blocked, inaccessible, or required authentication the user did not provide.
3. Collect candidates in bounded batches. Preserve source URLs, application method, displayed age, and canonical timestamp. Exclude LinkedIn Easy Apply when requested.
4. Deduplicate cross-posted roles and prefer the active employer or ATS page as the application URL.
5. Open the full JD. Run `python3 scripts/screen_jd.py --file <jd.txt>` when JD text is available. Reject explicit sponsorship conflicts before scoring fit.
6. Keep sponsorship-silent roles as `unknown`. Use explicit support or recent exact-entity sponsorship history only as ranking evidence.
7. Score the surviving roles against the private candidate evidence using the fit rubric. Reject hard qualification conflicts and roles below the requested threshold.
8. Filter against a private ledger with `python3 scripts/manage_history.py filter --ledger <private-ledger.json> --input <candidates.json> --output <unseen.json>`.
9. Sort qualifying unseen roles by numeric fit descending and normalized posting time descending. Use company and role only as deterministic tie-breakers.
10. Return application links directly in chat unless another format is requested. After delivery, record the batch as `presented`; upgrade jobs to `applied` or `skipped` only when the user reports that outcome.

## Enforce sponsorship policy

Apply current evidence in this order:

1. Reject explicit no-current-or-future-sponsorship language.
2. Reject permanent unrestricted-authorization requirements.
3. Reject an incompatible citizenship or security-clearance requirement; ask for candidate-specific verification when compatibility is genuinely unclear.
4. Keep conditional language such as `may sponsor` or `case by case` and label it `verify`.
5. Keep a silent JD and label it `unknown`.
6. Rank explicit current support above historical company evidence.

Do not treat E-Verify participation, OPT acceptance, or a historical H-1B filing as proof that a specific role will provide future sponsorship. Do not treat parent companies, subsidiaries, clients, and staffing agencies as interchangeable legal entities.

## Respect site and account boundaries

Use read-only browser assistance to navigate result pages and read visible JDs. Never request or extract passwords, cookies, session tokens, Authorization headers, or complete authenticated network requests. Never bypass CAPTCHAs, authentication, access controls, rate limits, or anti-automation measures. Stop on the affected source and report the boundary.

Do not submit applications, contact recruiters, save jobs, or modify an external account. Opening an employer application page only to confirm the active canonical posting is allowed when the user's request permits browsing.

## Output only actionable survivors

Default to 25 unseen qualifying roles per batch. Report the total scanned count, qualifying count, source coverage, and shortlist. Do not show rejected jobs or rejection evidence unless the user requests an audit.

For multiple roles use:

```text
Rank | Fit | Posted | Role and application link | Company | Location | Workplace | Source(s) | Sponsorship signal | Why it matches
```

Make the title the clickable application link. Never represent `unknown` sponsorship as confirmed support. Never present a role as current unless its posting and application link were verified during the run.

## Use bundled utilities

- `scripts/screen_jd.py`: deterministic sponsorship-language triage.
- `scripts/manage_history.py`: URL and fingerprint deduplication with a user-selected private ledger.
- `scripts/render_shortlist.py`: deterministic fit-first, recency-second sorting and optional Markdown, HTML, or CSV output.

These utilities support agent judgment; they do not replace full-JD review or candidate-specific analysis.
