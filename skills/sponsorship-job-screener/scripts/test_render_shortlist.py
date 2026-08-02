import unittest

from render_shortlist import sort_jobs


class SortTests(unittest.TestCase):
    def test_fit_precedes_recency(self):
        jobs = [
            {"fit": "80", "posted_at": "2030-01-02T00:00:00Z", "company": "B", "role": "Newer"},
            {"fit": "90", "posted_at": "2030-01-01T00:00:00Z", "company": "A", "role": "Older"},
        ]
        self.assertEqual([j["role"] for j in sort_jobs(jobs)], ["Older", "Newer"])

    def test_recency_breaks_equal_fit(self):
        jobs = [
            {"fit": "88", "posted_at": "2030-01-01T00:00:00Z", "company": "A", "role": "Older"},
            {"fit": "88", "posted_at": "2030-01-02T00:00:00Z", "company": "B", "role": "Newer"},
        ]
        self.assertEqual([j["role"] for j in sort_jobs(jobs)], ["Newer", "Older"])


if __name__ == "__main__":
    unittest.main()
