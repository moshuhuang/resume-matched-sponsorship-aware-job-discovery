# Output and history schema

## Job record

Store one record per deduplicated candidate with these fields:

| Field | Rule |
|---|---|
| `fit` | Numeric 0-100 or `Pending profile`. |
| `posted_at` | ISO 8601 sorting source. |
| `posted` | Original human-readable age. |
| `role` | Display title. |
| `company` | Current employer or exact entity when known. |
| `location` | Location text from the current posting. |
| `workplace_type` | Remote, Hybrid, On-site, or Not stated. |
| `sources` | All discovery sources after deduplication. |
| `application_method` | External Apply, Easy Apply, or Not stated. |
| `sponsorship_signal` | `confirmed_support`, `verify`, `unknown`, or a rejection class. |
| `why_match` | At most two evidence-based strengths. |
| `url` | Active employer or ATS URL when available. |
| `source_urls` | Platform URLs retained in private run data. |
| `checked_at` | Verification timestamp. |

Filter rejected roles, below-threshold roles, excluded application methods, and ledger matches. Sort by numeric fit descending, then `posted_at` descending, then normalized company and role.

## Private history ledger

Use `presented`, `applied`, and `skipped`. Never downgrade `applied` or `skipped` to `presented`. Match canonical URLs first, then normalized company-role-location fingerprints. Keep the ledger outside source control.
