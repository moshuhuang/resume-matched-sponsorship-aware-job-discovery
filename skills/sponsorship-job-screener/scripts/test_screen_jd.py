import unittest

from screen_jd import classify, find_signals


class SponsorshipTests(unittest.TestCase):
    def result(self, text):
        return classify(find_signals(text))[0]

    def test_current_or_future_denial(self):
        self.assertEqual(self.result("We do not provide current or future visa sponsorship."), "confirmed_no")

    def test_unrestricted_authorization(self):
        self.assertEqual(self.result("Authorized to work without current or future sponsorship."), "confirmed_no")

    def test_explicit_support(self):
        self.assertEqual(self.result("The company will sponsor qualified applicants."), "confirmed_support")

    def test_conditional_support(self):
        self.assertEqual(self.result("The company may sponsor on a case-by-case basis."), "verify")

    def test_silent_jd(self):
        self.assertEqual(self.result("Build dashboards and analyze operating metrics."), "unknown")


if __name__ == "__main__":
    unittest.main()
