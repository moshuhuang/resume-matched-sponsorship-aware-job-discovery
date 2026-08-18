# AI Job Discovery & Fit-Ranking Skill

> A reusable AI skill that turns multi-platform job discovery into a personalized, resume-aware application shortlist.

**[View Live Product](https://claude.ai/code/artifact/fa91279a-015b-43f6-8c53-1df7345fca04)** · **[How It Works](#how-it-works)** · **[Install](#install)**

`Multi-platform discovery` · `Full-JD analysis` · `Sponsorship-aware screening` · `Explainable fit ranking`

## Product Demo

<p align="center">
  <img src="docs/product-dashboard.png" alt="Job discovery dashboard showing screened jobs, application status, and role categories" width="100%">
</p>

<p align="center"><em>From a broad search to a focused application queue: the dashboard tracks screened roles, qualified opportunities, and next actions.</em></p>

<p align="center">
  <img src="docs/fit-ranked-shortlist.png" alt="Ranked job shortlist with fit scores, sponsorship signals, match rationale, and application links" width="100%">
</p>

<p align="center"><em>Each shortlisted role includes an explainable fit score, sponsorship signal, match rationale, and direct application path.</em></p>

## How It Works

![AI Job Discovery and Fit-Ranking Skill architecture](docs/job-discovery-architecture.png)

The skill follows one decision path: discover recent roles, understand each full job description, decide eligibility and fit, then return a deduplicated application shortlist. Sponsorship is one input to the decision—not the product's entire purpose.

### Decision Logic

```mermaid
flowchart LR
    A[Discover recent roles] --> B[Open full JD]
    B --> C{Explicit sponsorship conflict?}
    C -- Yes --> X[Reject]
    C -- No or silent --> D[Compare JD with candidate profile]
    D --> E{Fit threshold met?}
    E -- No --> X
    E -- Yes --> F[Deduplicate and check local history]
    F --> G[Rank by fit, then recency]
    G --> H[Return application links]
```

## Why I Built This

If you are an international student, have you ever carefully filtered LinkedIn for the newest opportunities, opened ten job postings, and discovered that nine of them explicitly state that sponsorship is not available?

Repeating this process consumes a significant amount of time and energy before an application even begins. I built Resume-Matched & Sponsorship-Aware Job Discovery to turn that search into a focused list of opportunities worth applying to. It searches according to your preferences, removes roles with explicit sponsorship conflicts, and compares each full job description against your resume—not just the job title—to identify positions that genuinely match your experience.

I know that job searching can be a long process in which most visible feedback comes in the form of silence, rejection, or disqualification. This tool cannot remove that uncertainty, and a sponsorship-silent posting is never treated as a guarantee. I hope it can reduce some of the avoidable negative feedback caused by sponsorship constraints during the search stage and help candidates spend more time applying to opportunities that truly fit. Wishing everyone a smoother job search—and the right opportunity.

This open-source agent skill discovers recent roles across job boards and employer career sites, applies work-authorization constraints, evaluates full-job-description fit, excludes high-volume LinkedIn Easy Apply routes when requested, and keeps a private local history ledger so the same job is not shown twice.

## What it does

- Searches user-selected sources with one shared recency cutoff.
- Opens the full job description instead of judging fit from the title alone.
- Rejects explicit sponsorship denials and incompatible authorization requirements.
- Keeps sponsorship-silent roles and labels uncertainty honestly.
- Scores resume fit from responsibilities, must-haves, tools, domain, and seniority.
- Prefers employer or ATS application links and can exclude LinkedIn Easy Apply.
- Deduplicates cross-posted jobs and suppresses roles already presented, applied to, or skipped.
- Returns a ranked shortlist; it never submits an application.

The sponsorship rule is deliberately conservative: a current explicit denial is a hard veto, while a silent posting survives with an `unknown` signal. Historical H-1B activity may strengthen ranking, but it does not override the current posting or prove that a specific role will sponsor.

## Install

With GitHub CLI 2.90 or later:

```bash
gh skills install OWNER/resume-matched-sponsorship-aware-job-discovery resume-matched-sponsorship-aware-job-discovery
```

For a manual Codex installation, copy `skills/resume-matched-sponsorship-aware-job-discovery` into your local skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/resume-matched-sponsorship-aware-job-discovery "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Keep your real resume, candidate profile, job descriptions, and history ledger outside this repository. Start from [`candidate-profile.example.md`](examples/candidate-profile.example.md), save the completed file in a private local directory, and point the agent to it in your prompt.

## Example prompt

> Use `$resume-matched-sponsorship-aware-job-discovery` to find US analyst roles posted in the last 72 hours across LinkedIn, Indeed, Glassdoor, and employer career pages. Exclude LinkedIn Easy Apply. Reject explicit current-or-future sponsorship denials, compare each full JD with my private candidate profile, suppress jobs in my local history ledger, and return up to 25 roles ranked by fit and then recency. Do not apply.

## Sponsorship decision policy

| Current evidence | Decision |
|---|---|
| Explicitly no current or future sponsorship | Reject |
| Permanent unrestricted authorization required | Reject |
| Incompatible citizenship or clearance requirement | Reject or candidate-specific verification |
| Conditional or case-by-case sponsorship | Keep and verify |
| Explicit sponsorship support | Keep and rank higher |
| No sponsorship language | Keep as unknown |

E-Verify participation, OPT acceptance, and historical H-1B filings are useful signals, but none independently proves future sponsorship for a specific opening.

## Included utilities

The skill bundles three dependency-free Python utilities:

- `screen_jd.py` extracts sponsorship and work-authorization signals from JD text.
- `manage_history.py` prevents repeat recommendations using a user-chosen local JSON ledger.
- `render_shortlist.py` sorts qualifying jobs by fit and recency and can render Markdown, HTML, or CSV.

Run the tests from the skill directory:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
```

## Privacy and safety

This public repository contains no real resume, candidate identity, immigration timeline, job-search history, browser session, credential, or application record. Runtime data is local by design and ignored by Git. The skill must never request passwords, cookies, session tokens, authorization headers, or complete authenticated network requests. It respects authentication boundaries, CAPTCHAs, site access controls, and platform terms.

Before publishing a fork, run the included privacy scan:

```bash
python3 tools/privacy_scan.py .
```

## Limitations

This is an agent workflow plus deterministic screening helpers, not an unattended crawler. Coverage depends on pages the user can lawfully access, job-board availability, and the agent's browsing tools. Regex results are triage signals rather than legal or immigration advice, and every selected role should be checked again before applying.

## Attribution and license

This project is adapted in part from GitHub's [`technical-job-search`](https://github.com/github/awesome-copilot/tree/main/skills/technical-job-search) skill in [`github/awesome-copilot`](https://github.com/github/awesome-copilot). See [NOTICE](NOTICE) for attribution. The repository is licensed under the [MIT License](LICENSE).
