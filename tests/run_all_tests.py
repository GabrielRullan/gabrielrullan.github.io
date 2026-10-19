"""
tests/run_all_tests.py - Master test runner coordinating all test suites for vA, vB, and vD.

Executes:
1. tests/test_facts.py
2. tests/test_distinctness.py
3. tests/test_html_standards.py
4. tests/test_headless_responsive.py

Outputs:
- Formatted console report with pass/fail counts and execution times.
- Structured summary written to tests/test_results.json.
- Exit code 0 if all pass, 1 otherwise.
"""

import json
import sys
import time
import unittest
from pathlib import Path

# Add tests directory to python path
TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import test_facts
import test_distinctness
import test_html_standards
import test_headless_responsive
import test_brand_kit

SUITES = [
    ("Fact Integrity (CV_gen & Prohibition of Day Rate)", test_facts.TestFactIntegrity),
    ("5-Dimension Pairwise Distinctness Rubric", test_distinctness.TestPairwiseDistinctness),
    ("HTML Standards, SEO, Accessibility, Links & Budget", test_html_standards.TestHtmlStandards),
    ("Headless Chrome Responsive, Overflow & Runtime Audit", test_headless_responsive.TestHeadlessResponsive),
    ("Personal Freelance Brand Kit Verification", test_brand_kit.TestBrandKit),
]


def run_all() -> bool:
    print("=" * 80)
    print(" GABRIEL RUL-LAN WEBSITE REDESIGN - E2E AUTOMATED VERIFICATION SUITE")
    print(f" Target Directory: {REPO_ROOT}")
    print("=" * 80)

    overall_results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_suites": len(SUITES),
        "total_tests": 0,
        "total_passed": 0,
        "total_failed": 0,
        "total_errors": 0,
        "suites": []
    }

    all_passed = True
    start_total_time = time.time()

    for suite_name, test_class in SUITES:
        print(f"\n[RUNNING SUITE] {suite_name}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite_tests_count = suite.countTestCases()
        overall_results["total_tests"] += suite_tests_count

        start_time = time.time()
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)
        duration = round(time.time() - start_time, 2)

        failures_count = len(result.failures)
        errors_count = len(result.errors)
        passed_count = suite_tests_count - failures_count - errors_count

        overall_results["total_passed"] += passed_count
        overall_results["total_failed"] += failures_count
        overall_results["total_errors"] += errors_count

        suite_passed = result.wasSuccessful()
        if not suite_passed:
            all_passed = False

        status_str = "PASS" if suite_passed else "FAIL"
        print(f"[{status_str}] {suite_name}: {passed_count}/{suite_tests_count} passed ({duration}s)")

        failure_details = []
        for test, trace in result.failures:
            failure_details.append({"test": str(test), "type": "FAILURE", "trace": trace})
        for test, trace in result.errors:
            failure_details.append({"test": str(test), "type": "ERROR", "trace": trace})

        overall_results["suites"].append({
            "name": suite_name,
            "test_class": test_class.__name__,
            "total": suite_tests_count,
            "passed": passed_count,
            "failed": failures_count,
            "errors": errors_count,
            "duration_seconds": duration,
            "status": status_str,
            "issues": failure_details
        })

    total_duration = round(time.time() - start_total_time, 2)
    overall_results["duration_seconds"] = total_duration
    overall_results["status"] = "PASSED" if all_passed else "FAILED"

    # Save structured results
    results_path = TESTS_DIR / "test_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(overall_results, f, indent=2)

    # Print summary table
    print("\n" + "=" * 80)
    print(" SUMMARY EXECUTION REPORT")
    print("=" * 80)
    print(f"{'Suite Name':<55} | {'Status':<6} | {'Passed/Total':<12}")
    print("-" * 80)
    for s in overall_results["suites"]:
        print(f"{s['name']:<55} | {s['status']:<6} | {s['passed']}/{s['total']}")
    print("-" * 80)
    print(f"TOTAL TESTS : {overall_results['total_tests']}")
    print(f"PASSED      : {overall_results['total_passed']}")
    print(f"FAILED      : {overall_results['total_failed']}")
    print(f"ERRORS      : {overall_results['total_errors']}")
    print(f"TOTAL TIME  : {total_duration}s")
    print(f"OVERALL     : {'SUCCESS (ALL PASSED)' if all_passed else 'FAILURE'}")
    print(f"Report saved to: {results_path}")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
