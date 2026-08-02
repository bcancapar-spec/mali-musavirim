#!/usr/bin/env python3
"""Run the complete local test suite and emit a machine-readable JSON report."""

from __future__ import annotations

import argparse
import io
import json
import platform
import sys
import unittest
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
SUITE_PATTERN = "test_*.py"


def case_id(value: Any) -> str:
    identifier = getattr(value, "id", None)
    return identifier() if callable(identifier) else str(value)


def build_report(start_dir: Path, verbosity: int) -> tuple[dict[str, Any], str]:
    loader = unittest.defaultTestLoader
    suite = loader.discover(str(start_dir), pattern=SUITE_PATTERN)
    discovered_count = suite.countTestCases()
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=verbosity).run(suite)
    report = {
        "schema_version": SCHEMA_VERSION,
        "method": "python_unittest_discovery",
        "discovery": {
            "start_dir": start_dir.as_posix(),
            "pattern": SUITE_PATTERN,
        },
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "result": {
            "discovered_test_count": discovered_count,
            "tests_run": result.testsRun,
            "passed": (
                result.testsRun
                - len(result.failures)
                - len(result.errors)
                - len(result.skipped)
                - len(result.expectedFailures)
                - len(result.unexpectedSuccesses)
            ),
            "failures": [case_id(case) for case, _ in result.failures],
            "errors": [case_id(case) for case, _ in result.errors],
            "skipped": [case_id(case) for case, _ in result.skipped],
            "expected_failures": [case_id(case) for case, _ in result.expectedFailures],
            "unexpected_successes": [case_id(case) for case in result.unexpectedSuccesses],
            "successful": result.wasSuccessful(),
        },
    }
    return report, stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verbosity", type=int, choices=(0, 1, 2), default=1)
    args = parser.parse_args()
    report, detail = build_report(args.start_dir.resolve(), args.verbosity)
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(rendered.encode("utf-8"))
    sys.stdout.buffer.write(rendered.encode("utf-8"))
    if detail and not report["result"]["successful"]:
        sys.stderr.write(detail)
    return 0 if report["result"]["successful"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
