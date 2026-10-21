import unittest
from flaketrail.engine import diagnose, execute, source_hash
from flaketrail.fixtures import SCENARIOS

class DiagnosisTests(unittest.TestCase):
    def test_all_owned_faults_minimize_and_preserve_assertions(self):
        for name in SCENARIOS:
            with self.subTest(scenario=name):
                result=diagnose(name)
                self.assertEqual(result['status'],'minimized',result)
                self.assertEqual(result['minimality'],'deletion_1_minimal')
                self.assertTrue(result['victimPassesAlone'])
                self.assertLessEqual(result['runs'],40)
                self.assertEqual(len(result['minimalOrder']),3 if name=='derived-cache' else 2)
                self.assertEqual(result['repair']['status'],'verified_finite')
                self.assertEqual(len(result['repair']['checks']),11)
                self.assertFalse(result['repair']['negativeControl']['accepted'])
                self.assertTrue(result['repair']['negativeControl']['superficiallyPassed'])
                self.assertTrue(all(c['assertionsPreserved'] for c in result['repair']['checks']))
    def test_budget_returns_partial_not_success(self):
        result=diagnose('currency-cache',1)
        self.assertEqual(result['status'],'unresolved')
        self.assertEqual(result['runs'],1)
        self.assertIsNone(result['minimalOrder'])
        self.assertIsNotNone(result['bestKnownFailingOrder'])
        self.assertIsNone(result['repair'])
    def test_clean_order_is_not_a_reproduced_failure(self):
        result=diagnose('currency-cache',40,['default_checkout','set_eur'])
        self.assertEqual(result['status'],'not_reproduced')
        self.assertIsNone(result['repair'])
    def test_failure_fingerprint_preserved(self):
        result=diagnose('currency-cache')
        for trial in result['trail']:
            if trial['targetReproduced']:
                self.assertIn(result['failure'],trial['failures'])
    def test_worker_process_environment_isolated(self):
        dirty=execute('environment-leak',['set_region','default_region'])
        clean=execute('environment-leak',['default_region'])
        self.assertFalse(dirty['passed'])
        self.assertTrue(clean['passed'])
    def test_unknown_code_and_invalid_budgets_rejected(self):
        for name,budget in [('import os',40),('currency-cache',0),('currency-cache',41),('currency-cache',True)]:
            with self.assertRaises(ValueError):diagnose(name,budget)
        with self.assertRaises(ValueError):diagnose('currency-cache',40,['../../secret'])
        with self.assertRaises(ValueError):diagnose('currency-cache',40,['health','health'])
        with self.assertRaises(ValueError):diagnose('currency-cache',40,{'health':True})
    def test_source_hash_is_reproducible(self):
        self.assertEqual(source_hash(),source_hash())
        self.assertEqual(len(source_hash()),64)

if __name__=='__main__':unittest.main()
