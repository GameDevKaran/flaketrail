"""One fresh subprocess for one known order; no user code, imports or shell."""
import json
import sys
from .fixtures import run_order

def main():
    body = sys.stdin.buffer.read(16385)
    if len(body) > 16384:
        raise ValueError("worker input too large")
    request = json.loads(body)
    print(json.dumps(run_order(request["scenario"], request["order"], request.get("repair", "none"))))

if __name__ == "__main__":
    main()
