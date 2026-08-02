# Contributing

Contributions are welcome when they preserve the project's privacy and platform-safety boundaries. Use fictional data in tests and examples, keep the Python utilities dependency-free where practical, and add regression tests for screening-pattern changes.

Before opening a pull request, run:

```bash
python3 -m unittest discover -s skills/resume-matched-sponsorship-aware-job-discovery/scripts -p 'test_*.py'
python3 tools/privacy_scan.py .
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" skills/resume-matched-sponsorship-aware-job-discovery
```

Do not commit real resumes, names, email addresses, phone numbers, immigration dates, application histories, credentials, cookies, or browser data.
