import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time
from .fixtures import SCENARIOS

ROOT = Path(__file__).resolve().parents[1]

def source_hash():
    return hashlib.sha256((ROOT / "flaketrail/fixtures.py").read_bytes()).hexdigest()

def execute(scenario, order, repair="none"):
    # Do not inherit provider credentials or unrelated application configuration.
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATH") if key in os.environ}
    env.update(PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    run = subprocess.run([sys.executable, "-m", "flaketrail.worker"], input=json.dumps({"scenario": scenario, "order": order, "repair": repair}), capture_output=True, text=True, encoding="utf-8", cwd=ROOT, env=env, timeout=3, shell=False)
    if run.returncode or len(run.stdout) > 65536:
        raise RuntimeError("Owned fixture worker failed; diagnosis is unresolved")
    return json.loads(run.stdout)

def list_scenarios():
    return [{"id": key, **value} for key, value in SCENARIOS.items()]

class BudgetExhausted(Exception):
    pass

def diagnose(scenario_id, budget=40, order=None):
    if scenario_id not in SCENARIOS or type(budget) is not int or not 1 <= budget <= 40:
        raise ValueError("Choose a known scenario and a run budget between 1 and 40")
    scenario = SCENARIOS[scenario_id]
    if order is not None and not isinstance(order, list):
        raise ValueError("Order must be a list of known test IDs")
    original = list(scenario["order"] if order is None else order)
    if not original or len(original) > 24 or any(not isinstance(x, str) or x not in scenario["order"] for x in original) or len(set(original)) != len(original):
        raise ValueError("Order must contain unique known test IDs")
    start = time.monotonic()
    trail = []
    result = {"application": "FlakeTrail", "schemaVersion": 1, "scenario": scenario_id, "title": scenario["title"], "sourceSha256": source_hash(), "execution": "local_owned_python_subprocesses", "sponsorExecution": "not_verified", "budget": budget, "runs": 0, "status": "unresolved", "originalOrder": original, "minimalOrder": None, "minimality": "not_established", "trail": trail, "repair": None, "limitations": ["Original planted development faults, not captured GitLab failures or held-out evaluation.", "A deletion-minimal sequence is not necessarily a globally shortest sequence.", "Ten separate seeded repair orders provide finite evidence, not proof that all flakes are absent.", "Only the repository-owned test catalog executes. No uploaded code, general repair or network-race diagnosis."]}
    fingerprint = None
    best = None
    def probe(sequence, phase):
        if len(trail) >= budget or time.monotonic() - start > 35:
            raise BudgetExhausted()
        observed = execute(scenario_id, list(sequence))
        matches = fingerprint is not None and fingerprint in observed["failures"]
        trail.append({"attempt": len(trail)+1, "phase": phase, "order": list(sequence), "failures": observed["failures"], "targetReproduced": matches})
        return observed, matches
    try:
        initial, _ = probe(original, "capture_replay")
        if not initial["failures"]:
            result["status"] = "not_reproduced"
            return result
        fingerprint = next((failure for failure in initial["failures"] if failure["test"] == scenario["victim"]), None)
        if not fingerprint:
            result["reason"] = "The captured order did not reproduce this scenario's nominated failure"
            return result
        result["failure"] = fingerprint
        trail[-1]["targetReproduced"] = True
        best = original
        _, alone_fails = probe([scenario["victim"]], "victim_alone")
        if alone_fails:
            result["reason"] = "The nominated test fails alone; order dependence is not established"
            return result
        result["victimPassesAlone"] = True
        granularity = 2
        while len(best) >= 2:
            chunk_size = math.ceil(len(best)/granularity)
            reduced = False
            for start_index in range(0, len(best), chunk_size):
                candidate = best[:start_index] + best[start_index+chunk_size:]
                if not candidate or scenario["victim"] not in candidate:
                    continue
                _, matches = probe(candidate, "remove_chunk")
                if matches:
                    best = candidate
                    granularity = max(2, granularity-1)
                    reduced = True
                    break
            if not reduced:
                if granularity >= len(best):
                    break
                granularity = min(len(best), granularity*2)
        # Explicit final replay and every single deletion prove only 1-minimality.
        _, confirmed = probe(best, "minimal_replay")
        if not confirmed:
            result["reason"] = "Candidate did not replay consistently"
            return result
        for index in range(len(best)):
            _, still_fails = probe(best[:index]+best[index+1:], "minimality_check")
            if still_fails:
                result["reason"] = "Further reduction remains possible"
                return result
        result.update(status="minimized", minimalOrder=best, minimality="deletion_1_minimal", repair=verify_repair(scenario_id, best))
    except (BudgetExhausted, subprocess.TimeoutExpired) as exc:
        result["reason"] = "Attempt/time budget exhausted; best known failing order retained" if isinstance(exc, BudgetExhausted) else "Worker timeout; no successful diagnosis claimed"
    except RuntimeError as exc:
        result["reason"] = str(exc)
    finally:
        result["runs"] = len(trail)
        result["bestKnownFailingOrder"] = best
        result["elapsedMs"] = round((time.monotonic()-start)*1000)
    return result

def verify_repair(scenario_id, minimal):
    start = time.monotonic()
    scenario = SCENARIOS[scenario_id]
    checks = []
    orders = [("minimal_reproducer", None, list(minimal))]
    for seed in range(7101, 7111):
        order = list(scenario["order"])
        random.Random(seed).shuffle(order)
        orders.append(("independent_seed", seed, order))
    for label, seed, order in orders:
        if time.monotonic() - start > 35:
            return {"status": "unresolved", "reason": "Repair time budget exhausted", "checks": checks}
        observed = execute(scenario_id, order, "reset")
        preserved = observed["executed"] == len(order) and observed["assertions"] == len(order)
        checks.append({"kind": label, "seed": seed, "order": order, "passed": observed["passed"], "assertionsPreserved": preserved, "assertions": observed["assertions"]})
    sham = execute(scenario_id, minimal, "skip_victim")
    rejected = sham["executed"] != len(minimal) or sham["assertions"] != len(minimal)
    return {"status": "verified_finite" if all(check["passed"] and check["assertionsPreserved"] for check in checks) and rejected else "rejected", "proposal": "Reset shared state and restore the fixture environment after every test; preserve the test bodies and assertions.", "kind": "authored_isolation_fix_not_model_generated", "checks": checks, "runCount": len(checks)+1, "sourceSha256": source_hash(), "negativeControl": {"proposal": "skip the failing test", "superficiallyPassed": sham["passed"], "accepted": not rejected, "executed": sham["executed"], "expected": len(minimal), "reason": "Coverage loss is rejected even if remaining tests pass"}, "patch": "finally:\n    state = fresh_state()\n    os.environ.pop('FLAKETRAIL_FIXTURE_REGION', None)\n"}
