import argparse
import json
from .engine import diagnose, list_scenarios

parser = argparse.ArgumentParser(description="Replay original FlakeTrail fixtures; no provider evidence is inferred")
parser.add_argument("scenario", nargs="?", default="currency-cache")
parser.add_argument("--budget", type=int, default=40)
parser.add_argument("--list", action="store_true")
args = parser.parse_args()
print(json.dumps(list_scenarios() if args.list else diagnose(args.scenario,args.budget), indent=2))
