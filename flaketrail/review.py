"""Review one owned cleanup configuration; never execute submitted code."""
import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from .engine import ROOT, diagnose, execute, source_hash
from .fixtures import SCENARIOS

CONFIG = ROOT / "review-fixture/isolation.json"
BASELINE = {"schemaVersion": 1, "resetAfterEach": False}
CANDIDATE = {"schemaVersion": 1, "resetAfterEach": True}
DEFAULT_CAPTURE = ROOT / "artifacts/review/capture.json"


def encoded(value):
    return json.dumps(value, indent=2) + "\n"


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def execution_sources():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ("flaketrail/fixtures.py", "flaketrail/engine.py", "flaketrail/worker.py", "flaketrail/review.py")}


def read_json(path):
    raw = Path(path).read_bytes()
    if len(raw) > 131072:
        raise ValueError("Review input exceeds 128 KiB")
    return json.loads(raw)


def configuration(path=CONFIG):
    value = read_json(path)
    if not isinstance(value, dict) or set(value) != set(BASELINE) or type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1 or type(value["resetAfterEach"]) is not bool:
        raise ValueError("Only schemaVersion=1 and a boolean resetAfterEach are allowed; tests/assertions cannot be configured away")
    return value


def context():
    return {
        "application": "FlakeTrail", "schemaVersion": 1,
        "recordedAt": datetime.now(timezone.utc).isoformat(),
        "execution": "owned_python_subprocesses",
        "providerExecutionVerified": False, "duoExecutionVerified": False,
        "ciMetadata": {key: os.environ.get(key) for key in ("CI_PROJECT_ID", "CI_PIPELINE_ID", "CI_PIPELINE_URL", "CI_JOB_ID", "CI_JOB_URL", "CI_COMMIT_SHA")},
        "limitations": [
            "Original planted development fixture; not a held-out fault or general repair.",
            "CI environment metadata and a local JSON file are not authenticated provider/Duo evidence.",
            "Cleanup policy is authored; no model-generated repair is claimed.",
            "Deletion-minimality and ten seeded orders are finite evidence, not an absence-of-flakes proof.",
        ],
    }


def capture(scenario):
    if scenario not in SCENARIOS:
        raise ValueError("Unknown owned scenario")
    order = list(SCENARIOS[scenario]["order"])
    observed = execute(scenario, order, "none")
    fingerprint = next((item for item in observed["failures"] if item["test"] == SCENARIOS[scenario]["victim"]), None)
    return {**context(), "kind": "original_failure_capture", "status": "failure_captured" if fingerprint else "unresolved", "scenario": scenario, "sourceSha256": source_hash(), "executionSourcesSha256": execution_sources(), "baselineConfigSha256": digest(BASELINE), "order": order, "failure": fingerprint, "observed": observed}


def validate_capture(record):
    if not isinstance(record, dict) or record.get("kind") != "original_failure_capture" or record.get("status") != "failure_captured":
        raise ValueError("A successful original failure capture is required")
    scenario = record.get("scenario")
    if not isinstance(scenario, str) or scenario not in SCENARIOS or record.get("order") != SCENARIOS[scenario]["order"]:
        raise ValueError("Capture must name the complete known owned order")
    if record.get("sourceSha256") != source_hash() or record.get("executionSourcesSha256") != execution_sources() or record.get("baselineConfigSha256") != digest(BASELINE):
        raise ValueError("Capture is stale or fixture/assertion source changed; do not rewrite the capture to pass")
    observed = execute(scenario, record["order"], "none")
    fingerprint = record.get("failure")
    if not isinstance(fingerprint, dict) or fingerprint.get("test") != SCENARIOS[scenario]["victim"] or fingerprint not in observed["failures"]:
        raise ValueError("Captured target fingerprint does not replay on the unchanged baseline")
    return observed


def propose(record, *, apply=False, config_path=CONFIG):
    validate_capture(record)
    current = configuration(config_path)
    if current != BASELINE:
        raise ValueError("Candidate file already differs from the baseline; preserve and review its existing changes")
    patch = "".join(difflib.unified_diff(encoded(BASELINE).splitlines(keepends=True), encoded(CANDIDATE).splitlines(keepends=True), fromfile="a/review-fixture/isolation.json", tofile="b/review-fixture/isolation.json"))
    result = {**context(), "kind": "reviewable_cleanup_proposal", "status": "applied" if apply else "proposed", "scenario": record["scenario"], "fixtureSourceSha256": source_hash(), "baselineConfigSha256": digest(BASELINE), "candidateConfigSha256": digest(CANDIDATE), "path": "review-fixture/isolation.json", "diff": patch, "candidate": CANDIDATE}
    if apply:
        # Only this fixed repository-owned policy changes; the test source is untouched.
        Path(config_path).write_text(encoded(CANDIDATE), encoding="utf-8", newline="\n")
    return result


def complete(observed, order):
    return observed["passed"] and observed["executed"] == len(order) and observed["assertions"] == len(order) and [item["test"] for item in observed["results"]] == order and all(item["status"] == "passed" and item["assertions"] == 1 for item in observed["results"])


def verify(record, *, config_path=CONFIG):
    started = time.monotonic()
    validate_capture(record)
    candidate = configuration(config_path)
    scenario = record["scenario"]
    reduction = diagnose(scenario, 40, record["order"], include_repair=False)
    result = {**context(), "kind": "review_candidate_verification", "status": "unresolved", "scenario": scenario, "fixtureSourceSha256": source_hash(), "candidateConfigSha256": digest(candidate), "candidate": candidate, "minimization": reduction, "checks": [], "negativeControls": []}
    if reduction["status"] != "minimized" or reduction["failure"] != record["failure"]:
        result["reason"] = "Captured target did not reach a verified deletion-minimal reproducer"
        return result
    mode = "reset" if candidate["resetAfterEach"] else "none"
    orders = [("minimal_reproducer", None, reduction["minimalOrder"])]
    for seed in range(7101, 7111):
        order = list(record["order"])
        random.Random(seed).shuffle(order)
        orders.append(("independent_seed", seed, order))
    for kind, seed, order in orders:
        if time.monotonic() - started > 70:
            result["reason"] = "Verification budget exhausted"
            return result
        observed = execute(scenario, order, mode)
        result["checks"].append({"kind": kind, "seed": seed, "order": order, "accepted": complete(observed, order), "observed": observed})
    for name, repair in (("skip_victim", "skip_victim"), ("missing_cleanup", "none")):
        observed = execute(scenario, reduction["minimalOrder"], repair)
        result["negativeControls"].append({"name": name, "accepted": complete(observed, reduction["minimalOrder"]), "observed": observed})
    source_unchanged = source_hash() == record["sourceSha256"] and execution_sources() == record["executionSourcesSha256"]
    accepted = source_unchanged and all(check["accepted"] for check in result["checks"]) and all(not check["accepted"] for check in result["negativeControls"])
    result.update(status="verified_finite" if accepted else "rejected", assertionsSourceUnchanged=source_unchanged, elapsedMs=round((time.monotonic()-started)*1000))
    return result


def write_report(report, directory, stem):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{stem}.json").write_text(encoded(report), encoding="utf-8")
    suite = ET.Element("testsuite", name=f"flaketrail.{stem}")
    rows = []
    if report.get("kind") == "original_failure_capture":
        rows = [(item["test"], item["status"] == "passed", item.get("failure", "Unresolved test")) for item in report["observed"]["results"]]
    elif report.get("kind") == "review_candidate_verification":
        rows = [(f"{item['kind']}.{item['seed']}", item["accepted"], "Failure or lost assertion coverage") for item in report["checks"]]
        rows += [(f"reject.{item['name']}", not item["accepted"], "Invalid control passed the gate") for item in report["negativeControls"]]
        rows.append(("release_gate", report["status"] == "verified_finite", report.get("reason", "Candidate did not meet the repair gate")))
    else:
        rows = [(stem, report.get("status") in ("proposed", "applied"), report.get("reason", "Unresolved workflow"))]
    suite.set("tests", str(len(rows)))
    suite.set("failures", str(sum(not passed for _, passed, _ in rows)))
    for name, passed, reason in rows:
        case = ET.SubElement(suite, "testcase", classname="flaketrail.review", name=name)
        if not passed:
            ET.SubElement(case, "failure", message=reason).text = reason
    ET.ElementTree(suite).write(directory / f"{stem}.xml", encoding="utf-8", xml_declaration=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Capture, propose and verify a reviewable owned fixture cleanup change")
    parser.add_argument("command", choices=("capture", "propose", "verify"))
    parser.add_argument("--scenario", choices=tuple(SCENARIOS), default="currency-cache")
    parser.add_argument("--capture", type=Path, default=DEFAULT_CAPTURE)
    parser.add_argument("--output", type=Path, default=DEFAULT_CAPTURE.parent)
    parser.add_argument("--apply", action="store_true", help="Apply only the fixed cleanup policy during propose")
    args = parser.parse_args(argv)
    try:
        if args.apply and args.command != "propose":
            raise ValueError("--apply is only valid for propose")
        if args.command == "capture":
            report = capture(args.scenario)
            code = 1 if report["status"] == "failure_captured" else 2
        elif args.command == "propose":
            report = propose(read_json(args.capture), apply=args.apply)
            code = 0
        else:
            report = verify(read_json(args.capture))
            code = 0 if report["status"] == "verified_finite" else 1
    except (ValueError, OSError, RuntimeError, KeyError, subprocess.TimeoutExpired) as exc:
        report = {**context(), "status": "unresolved", "reason": str(exc)}
        code = 2
    write_report(report, args.output, args.command)
    print(json.dumps({"command": args.command, "status": report["status"], "artifact": str(args.output / f"{args.command}.json"), "providerExecutionVerified": False}))
    return code


if __name__ == "__main__":
    sys.exit(main())
