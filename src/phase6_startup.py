"""Start an owned loopback server, check real HTTP responses, always stop it."""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from .common import ROOT

def startup(root=ROOT):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    directory=root/'outputs/phase6/validation'; directory.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,'-m','streamlit','run','app.py','--server.address=127.0.0.1',f'--server.port={port}','--server.headless=true','--browser.gatherUsageStats=false']
    result={'passed':False,'health_status':None,'root_status':None,'server_stopped':False}
    with (directory/'startup_server.log').open('w',encoding='utf-8') as log:
        process=subprocess.Popen(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+30
            while time.monotonic()<deadline:
                if process.poll() is not None: raise RuntimeError('Streamlit exited before healthy startup')
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health',timeout=2) as response:
                        result['health_status']=response.status
                        result['health_body']=response.read().decode()
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=2) as response:
                        result['root_status']=response.status
                        assert b'<html' in response.read().lower()
                    result['passed']=result['health_status']==result['root_status']==200 and result['health_body']=='ok'
                    break
                except OSError: time.sleep(.25)
            if not result['passed']: raise RuntimeError('Streamlit HTTP startup check failed')
        finally:
            if process.poll() is None:
                if os.name=='nt':
                    # Windows venv launchers may own a child interpreter.
                    subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],stdout=log,stderr=subprocess.STDOUT,check=False)
                else:
                    process.terminate()
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)
            result['server_stopped']=process.poll() is not None
            with socket.socket() as probe:
                probe.settimeout(1)
                result['listener_closed']=probe.connect_ex(('127.0.0.1',port))!=0
            result['passed']=result['passed'] and result['listener_closed']
            (directory/'startup_health.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    if not result['passed']: raise RuntimeError('Owned Streamlit listener did not close')
    return result

if __name__=='__main__': print(json.dumps(startup(),indent=2))
