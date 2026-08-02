# Discovery workflow

## Build one search specification

Capture an exact run start, recency cutoff, geography, workplace types, target functions, seniority range, excluded methods, sources, fit threshold, and delivery size. Use one cutoff across all sources even when a platform exposes only coarse date filters.

Search role families separately when one large query would suppress results. Titles expand discovery; the full JD controls eligibility and fit.

## Cover only requested sources

Attempt every user-requested source and label each as `searched`, `authentication required`, `blocked`, or `no qualifying results`. Public employer career pages and ATS pages may verify a candidate or supply the canonical application link. They must not be described as a successfully searched job board when that board was inaccessible.

For each candidate preserve:

- source and source URL
- canonical employer or ATS URL
- title, company, location, and workplace type
- displayed age and normalized `posted_at`
- application method
- full JD text or a stable private reference to it
- verification timestamp

Exclude LinkedIn Easy Apply when the search specification requires external applications. Do not click an application control while screening.

## Normalize time

Convert relative ages using the observation timestamp. Preserve the display string and store an ISO 8601 timestamp for sorting. For date-only posts, retain the precision. Exclude a result from a strict cutoff when its age cannot be established.

## Deduplicate

Prefer an employer requisition ID or canonical ATS URL. Otherwise match a platform job ID, then normalized company, role, location, and materially identical JD content. Merge source names and URLs into the surviving record.

Filter against the user's private ledger before scoring or delivery. Keep the ledger outside the repository and skill directory.

## Research sponsorship only as needed

Start with the current JD and employer FAQ. If ranking benefits from additional evidence, check authoritative public records for the exact legal entity and relevant time period. Preserve the source, period, and entity-match confidence in private run data.

Current negative JD language overrides historical evidence. A silent JD survives but remains unconfirmed.
