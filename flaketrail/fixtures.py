"""Owned fixture programs. Each test contains exactly one retained assertion."""
import os

SCENARIOS = {
    "currency-cache": {"title": "Currency leaks between checkout tests", "description": "A regional checkout changes shared currency; a later default checkout inherits it.", "order": ["health", "set_eur", "inventory", "default_checkout", "receipt"], "victim": "default_checkout"},
    "environment-leak": {"title": "A region setting survives its test", "description": "One test sets an environment variable without restoring it.", "order": ["receipt", "set_region", "health", "default_region", "inventory"], "victim": "default_region"},
    "derived-cache": {"title": "A derived price cache outlives its input", "description": "A mode change and cache warm-up combine to contaminate a later price test.", "order": ["inventory", "enable_discount", "health", "warm_cache", "receipt", "regular_price"], "victim": "regular_price"},
}

def fresh_state():
    return {"currency": "USD", "discount": False, "cached_price": None}

def health(state):
    assert 2 + 2 == 4, "fixture arithmetic changed"
def inventory(state):
    assert len(["book", "pen"]) == 2, "fixture inventory changed"
def receipt(state):
    assert "receipt".upper() == "RECEIPT", "fixture receipt changed"
def set_eur(state):
    state["currency"] = "EUR"
    assert state["currency"] == "EUR", "currency setup failed"
def default_checkout(state):
    assert state["currency"] == "USD", "default checkout expected USD"
def set_region(state):
    os.environ["FLAKETRAIL_FIXTURE_REGION"] = "eu"
    assert os.environ["FLAKETRAIL_FIXTURE_REGION"] == "eu", "region setup failed"
def default_region(state):
    assert os.environ.get("FLAKETRAIL_FIXTURE_REGION", "us") == "us", "default region expected us"
def enable_discount(state):
    state["discount"] = True
    assert state["discount"] is True, "discount setup failed"
def warm_cache(state):
    state["cached_price"] = 80 if state["discount"] else 100
    assert state["cached_price"] in (80, 100), "cache setup failed"
def regular_price(state):
    assert state["cached_price"] in (None, 100), "regular price expected uncached or 100"

TESTS = {fn.__name__: fn for fn in [health, inventory, receipt, set_eur, default_checkout, set_region, default_region, enable_discount, warm_cache, regular_price]}

def run_order(scenario_id, order, repair="none"):
    scenario = SCENARIOS[scenario_id]
    if repair not in ("none", "reset", "skip_victim"):
        raise ValueError("unknown repair")
    if not isinstance(order, list) or len(order) > 24 or len(set(order)) != len(order) or any(name not in scenario["order"] for name in order):
        raise ValueError("unknown, repeated or excessive test IDs")
    state = fresh_state()
    os.environ.pop("FLAKETRAIL_FIXTURE_REGION", None)
    results = []
    for name in order:
        if repair == "skip_victim" and name == scenario["victim"]:
            results.append({"test": name, "status": "skipped", "assertions": 0})
            continue
        try:
            TESTS[name](state)
            results.append({"test": name, "status": "passed", "assertions": 1})
        except AssertionError as exc:
            results.append({"test": name, "status": "failed", "assertions": 1, "failure": str(exc)})
        finally:
            if repair == "reset":
                state = fresh_state()
                os.environ.pop("FLAKETRAIL_FIXTURE_REGION", None)
    failures = [{"test": item["test"], "failure": item["failure"]} for item in results if item["status"] == "failed"]
    return {"order": order, "results": results, "failures": failures, "passed": not failures, "executed": sum(item["status"] != "skipped" for item in results), "assertions": sum(item["assertions"] for item in results)}
