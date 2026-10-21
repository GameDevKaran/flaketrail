import http.client
from http.server import ThreadingHTTPServer
import json
import threading
import unittest
from flaketrail.web import Handler, GATE

class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,method,path,body=None,headers=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=90)
        connection.request(method,path,body,headers or {})
        response=connection.getresponse();result=(response.status,dict(response.getheaders()),response.read());connection.close();return result
    def test_health_and_csp_truthful(self):
        status,headers,body=self.request('GET','/api/health');self.assertEqual(status,200);self.assertEqual(json.loads(body)['sponsorExecution'],'not_verified');self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
    def test_actual_budget_limited_http_analysis(self):
        status,_,body=self.request('POST','/api/diagnose',json.dumps({'scenario':'currency-cache','budget':1}),{'Content-Type':'application/json'})
        self.assertEqual(status,200);result=json.loads(body);self.assertEqual(result['status'],'unresolved');self.assertEqual(result['runs'],1)
    def test_foreign_origin_rejected(self):
        status,_,_=self.request('POST','/api/diagnose','{}',{'Content-Type':'application/json','Origin':'https://foreign.example'});self.assertEqual(status,403)
    def test_arbitrary_code_field_rejected(self):
        status,_,_=self.request('POST','/api/diagnose','{"source":"import os"}',{'Content-Type':'application/json'});self.assertEqual(status,400)
    def test_oversized_request_rejected(self):
        status,_,_=self.request('POST','/api/diagnose','x'*8193,{'Content-Type':'application/json'});self.assertEqual(status,413)
    def test_non_json_rejected(self):
        status,_,_=self.request('POST','/api/diagnose','{}');self.assertEqual(status,415)
    def test_one_active_analysis_only(self):
        GATE.acquire()
        try:status,_,_=self.request('POST','/api/diagnose','{"scenario":"currency-cache"}',{'Content-Type':'application/json'});self.assertEqual(status,503)
        finally:GATE.release()
    def test_unknown_files_not_exposed(self):
        status,_,_=self.request('GET','/.env');self.assertEqual(status,404)

if __name__=='__main__':unittest.main()
