import copy
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from flaketrail.review import BASELINE, CANDIDATE, capture, encoded, main, propose, validate_capture, verify, write_report


class ReviewWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture = capture("currency-cache")

    def test_capture_is_a_real_failing_order_and_cannot_count_as_provider_evidence(self):
        self.assertEqual(self.capture["status"], "failure_captured")
        self.assertFalse(self.capture["observed"]["passed"])
        self.assertEqual(self.capture["failure"]["test"], "default_checkout")
        self.assertFalse(self.capture["providerExecutionVerified"])
        self.assertFalse(self.capture["duoExecutionVerified"])
        self.assertEqual(len(self.capture["executionSourcesSha256"]), 4)

    def test_candidate_is_real_file_change_and_baseline_fails_the_same_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "isolation.json"
            config.write_text(encoded(BASELINE), encoding="utf-8")
            baseline = verify(self.capture, config_path=config)
            self.assertEqual(baseline["status"], "rejected")
            self.assertFalse(baseline["checks"][0]["accepted"])
            preview = propose(self.capture, config_path=config)
            self.assertIn('-  "resetAfterEach": false', preview["diff"])
            self.assertEqual(json.loads(config.read_text()), BASELINE)
            proposed = propose(self.capture, config_path=config, apply=True)
            self.assertEqual(proposed["status"], "applied")
            self.assertEqual(json.loads(config.read_text()), CANDIDATE)
            result = verify(self.capture, config_path=config)
            self.assertEqual(result["status"], "verified_finite")
            self.assertEqual(result["minimization"]["minimalOrder"], ["set_eur", "default_checkout"])
            self.assertIsNone(result["minimization"]["repair"])
            self.assertEqual(len(result["checks"]), 11)
            self.assertTrue(result["assertionsSourceUnchanged"])
            self.assertTrue(all(not item["accepted"] for item in result["negativeControls"]))
            skip = next(item for item in result["negativeControls"] if item["name"] == "skip_victim")
            self.assertTrue(skip["observed"]["passed"])
            write_report(result, directory, "verify")
            suite = ET.parse(Path(directory) / "verify.xml").getroot()
            self.assertEqual(suite.attrib["tests"], "14")
            self.assertEqual(suite.attrib["failures"], "0")

    def test_stale_sources_and_changed_fingerprint_cannot_apply_a_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "isolation.json"
            original = encoded(BASELINE)
            config.write_text(original, encoding="utf-8")
            for mutate in (
                lambda record: record.update(sourceSha256="0" * 64),
                lambda record: record["executionSourcesSha256"].update({"flaketrail/worker.py": "0" * 64}),
                lambda record: record["failure"].update(failure="invented result"),
                lambda record: record.update(order=["default_checkout"]),
            ):
                with self.subTest(mutate=mutate):
                    stale = copy.deepcopy(self.capture)
                    mutate(stale)
                    with self.assertRaises(ValueError):
                        propose(stale, config_path=config, apply=True)
                    self.assertEqual(config.read_text(), original)

    def test_skip_assertion_settings_or_existing_candidate_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "isolation.json"
            for invalid in ({**BASELINE, "skipTests": ["default_checkout"]}, {**BASELINE, "assertions": False}, {**BASELINE, "resetAfterEach": "true"}, CANDIDATE):
                config.write_text(encoded(invalid), encoding="utf-8")
                with self.subTest(config=invalid), self.assertRaises(ValueError):
                    propose(self.capture, config_path=config, apply=True)
                self.assertEqual(json.loads(config.read_text()), invalid)

    def test_cli_capture_returns_red_with_real_junit_and_json(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main(["capture", "--output", directory]), 1)
            saved = json.loads((Path(directory) / "capture.json").read_text())
            validate_capture(saved)
            suite = ET.parse(Path(directory) / "capture.xml").getroot()
            self.assertEqual(suite.attrib["tests"], "5")
            self.assertEqual(suite.attrib["failures"], "1")

    def test_malformed_capture_fails_closed_and_keeps_unresolved_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            incoming = Path(directory) / "invalid.json"
            incoming.write_text('{"status":"failure_captured"}', encoding="utf-8")
            self.assertEqual(main(["propose", "--capture", str(incoming), "--output", directory]), 2)
            saved = json.loads((Path(directory) / "propose.json").read_text())
            self.assertEqual(saved["status"], "unresolved")
            self.assertFalse(saved["providerExecutionVerified"])


if __name__ == "__main__":
    unittest.main()
