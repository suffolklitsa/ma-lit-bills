import unittest

from lit_bills import records, topics
from scripts import digest, validate

TOPICS = topics.load()


class Matching(unittest.TestCase):
    def test_finds_ai(self):
        self.assertIn("ai", topics.match("An Act relative to artificial intelligence in hiring", TOPICS))

    def test_whole_words_only(self):
        self.assertNotIn("crypto-fintech", topics.match("An Act relative to cryptography standards", TOPICS))

    def test_several_topics(self):
        found = topics.match("An Act protecting biometric privacy and location data", TOPICS)
        self.assertIn("biometrics", found)
        self.assertIn("privacy", found)

    def test_exclusions(self):
        self.assertNotIn("privacy", topics.match("An Act relative to the privacy of the home in zoning", TOPICS))

    def test_unrelated_bill(self):
        self.assertEqual(topics.match("An Act designating the official state muffin", TOPICS), [])


DETAIL = {"PrimarySponsor": {"Name": "Jane Doe"}, "Cosponsors": [{}, {}],
          "BillHistory": "https://malegislature.gov/api/GeneralCourts/194/Documents/H101/DocumentHistoryActions"}
ACTIONS = [{"Date": "2025-02-27T00:00:00", "Branch": "House", "Action": "Referred to Advanced IT", "IsStricken": False},
                          {"Date": "2025-01-16T10:00:00", "Branch": "House", "Action": "Filed", "IsStricken": False},
                          {"Date": "2025-03-01T00:00:00", "Branch": "House", "Action": "struck", "IsStricken": True}]


class Records(unittest.TestCase):
    def test_record_shape(self):
        r = records.record(194, {"BillNumber": "H101", "DocketNumber": "HD5", "Title": " An Act x "}, DETAIL, ACTIONS, ["ai"], "candidate")
        self.assertEqual(r["url"], "https://malegislature.gov/Bills/194/H101")
        self.assertEqual(r["filed"], "2025-01-16")
        self.assertEqual(r["last_action"]["action"], "Referred to Advanced IT")
        self.assertEqual(len(r["history"]), 2)
        self.assertEqual(r["cosponsor_count"], 2)
        self.assertEqual(validate.check_bill(r, set(TOPICS)), [])

    def test_undated_actions_kept_last(self):
        acts = ACTIONS + [{"Date": None, "Branch": "House", "Action": "Accompanied a study order", "IsStricken": False}]
        r = records.record(194, {"BillNumber": "H101", "Title": "x"}, DETAIL, acts, ["ai"], "candidate")
        self.assertEqual(r["history"][-1], {"date": None, "branch": "House", "action": "Accompanied a study order"})
        self.assertEqual(r["filed"], "2025-01-16")
        self.assertEqual(validate.check_bill(r, set(TOPICS)), [])

    def test_summary_needs_review(self):
        r = records.record(194, {"BillNumber": "H101", "Title": "x"}, DETAIL, ACTIONS, ["ai"], "candidate")
        r["summary"] = {"text": "Does x.", "written_by": "a", "reviewed_by": "b", "reviewed_on": "2026-10-20"}
        self.assertTrue(any("only confirmed" in p for p in validate.check_bill(r, set(TOPICS))))


class Digest(unittest.TestCase):
    def test_only_confirmed_recent(self):
        a = records.record(194, {"BillNumber": "H1", "Title": "AI bill"}, DETAIL, ACTIONS, ["ai"], "confirmed")
        b = records.record(194, {"BillNumber": "H2", "Title": "Unreviewed"}, DETAIL, ACTIONS, ["ai"], "candidate")
        text = digest.digest([a, b], TOPICS, "2025-02-01")
        self.assertIn("H1", text)
        self.assertNotIn("H2", text)
        self.assertIn("Referred to Advanced IT", text)

    def test_quiet_week(self):
        a = records.record(194, {"BillNumber": "H1", "Title": "AI bill"}, DETAIL, ACTIONS, ["ai"], "confirmed")
        self.assertIn("No activity", digest.digest([a], TOPICS, "2026-01-01"))


if __name__ == "__main__":
    unittest.main()
