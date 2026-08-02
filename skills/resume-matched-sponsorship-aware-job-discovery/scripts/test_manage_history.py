import unittest

from manage_history import filter_unseen, record_jobs


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.job = {"company": "Example Company", "role": "Data Analyst", "location": "Remote", "url": "https://linkedin.com/jobs/view/123?tracking=x", "sources": ["LinkedIn"]}

    def test_tracking_url_is_deduplicated(self):
        ledger = {"version": 1, "jobs": []}
        record_jobs(ledger, {"jobs": [self.job]}, "presented", "2030-01-01T00:00:00Z")
        duplicate = dict(self.job, url="https://www.linkedin.com/jobs/view/123/")
        self.assertEqual(filter_unseen(ledger, {"jobs": [duplicate]})["jobs"], [])

    def test_cross_platform_fingerprint(self):
        ledger = {"version": 1, "jobs": []}
        record_jobs(ledger, {"jobs": [self.job]}, "presented", "2030-01-01T00:00:00Z")
        duplicate = dict(self.job, url="https://example.com/jobs/456", sources=["Employer careers"])
        self.assertEqual(filter_unseen(ledger, {"jobs": [duplicate]})["jobs"], [])

    def test_applied_is_not_downgraded(self):
        ledger = {"version": 1, "jobs": []}
        record_jobs(ledger, {"jobs": [self.job]}, "applied", "2030-01-01T00:00:00Z")
        record_jobs(ledger, {"jobs": [self.job]}, "presented", "2030-01-02T00:00:00Z")
        self.assertEqual(ledger["jobs"][0]["status"], "applied")


if __name__ == "__main__":
    unittest.main()
