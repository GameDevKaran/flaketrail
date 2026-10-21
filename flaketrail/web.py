from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import threading
from urllib.parse import urlsplit
from .engine import diagnose, list_scenarios

ROOT = Path(__file__).resolve().parents[1]
GATE = threading.BoundedSemaphore(1)
ASSETS = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/styles.css": ("styles.css", "text/css; charset=utf-8")}

class Handler(BaseHTTPRequestHandler):
    server_version = "FlakeTrail"
    def setup(self):
        super().setup()
        self.connection.settimeout(90)
    def log_message(self, *_args):
        pass  # Do not log supplied payloads or browser reports.
    def reply(self, status, payload, content_type="application/json; charset=utf-8"):
        data=payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(status)
        for key,value in {"Content-Type":content_type,"Content-Length":str(len(data)),"Cache-Control":"no-store","X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY","Referrer-Policy":"no-referrer","Content-Security-Policy":"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'","Permissions-Policy":"camera=(), microphone=(), geolocation=()"}.items():self.send_header(key,value)
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        route=urlsplit(self.path).path
        if route in ASSETS:
            name,kind=ASSETS[route]
            self.reply(200,(ROOT/"web"/name).read_bytes(),kind)
        elif route=="/api/health":
            commit=os.getenv("SOURCE_COMMIT","")
            self.reply(200,{"application":"FlakeTrail","status":"ok","sourceCommit":commit if re.fullmatch(r"[a-f0-9]{40}",commit) else None,"sponsorExecution":"not_verified","retention":"no_server_results; optional_browser_save"})
        elif route=="/api/scenarios":self.reply(200,list_scenarios())
        else:self.reply(404,{"error":"Not found"})
    def do_POST(self):
        if urlsplit(self.path).path!="/api/diagnose":self.reply(404,{"error":"Not found"});return
        origin=os.getenv("FLAKETRAIL_PUBLIC_ORIGIN") or "http://"+self.headers.get("Host","")
        if (self.headers.get("Origin") and self.headers["Origin"]!=origin) or self.headers.get("Sec-Fetch-Site")=="cross-site":self.reply(403,{"error":"Cross-origin request rejected"});return
        if self.headers.get("Content-Type","").split(";")[0].strip()!="application/json":self.reply(415,{"error":"JSON content type required"});return
        if self.headers.get("Transfer-Encoding"):self.reply(400,{"error":"A bounded Content-Length is required"});return
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0<length<=8192:self.reply(413,{"error":"Request must be 1–8192 bytes"});return
            request=json.loads(self.rfile.read(length))
            if not isinstance(request,dict):raise ValueError("Expected a JSON object")
            if set(request)-{"scenario","budget","order"}:raise ValueError("Only scenario, budget and known test order are accepted")
        except (ValueError,TypeError):self.reply(400,{"error":"Invalid bounded diagnosis request"});return
        if not GATE.acquire(blocking=False):self.reply(503,{"error":"Another diagnosis is running. Try again shortly."});return
        try:
            self.reply(200,diagnose(request.get("scenario"),request.get("budget",40),request.get("order")))
        except (ValueError,TypeError):self.reply(400,{"error":"Choose a known scenario, unique known test IDs and an integer budget from 1 to 40"})
        except Exception:self.reply(500,{"error":"Diagnosis unavailable; no successful result is claimed"})
        finally:GATE.release()

def main():
    server=ThreadingHTTPServer((os.getenv("HOST","127.0.0.1"),int(os.getenv("PORT","8786"))),Handler)
    server.daemon_threads=True
    print("FLAKETRAIL_PORT="+str(server.server_port),flush=True)
    server.serve_forever()

if __name__=="__main__":main()
