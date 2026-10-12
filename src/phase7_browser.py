"""Real installed-Chrome QA and screenshots, distinct from AppTest."""
import contextlib
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
from .common import ROOT,write_json,sha256

PAGES=[('','Executive Overview','01_executive_overview'),('regional','Regional Intelligence','02_regional_intelligence'),
       ('presentations','Presentation Intelligence','03_presentation_intelligence'),('forecasting','Forecasting & Model Evaluation','04_forecasting'),
       ('decision_intelligence','Decision Intelligence','05_decision_intelligence'),('scenario_simulator','Scenario Simulator','06_scenario_simulator')]

@contextlib.contextmanager
def server(root=ROOT,python=None):
    with socket.socket() as s: s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    out=root/'outputs/phase7/validation'; out.mkdir(parents=True,exist_ok=True)
    command=[str(python or sys.executable),'-m','streamlit','run','app.py','--server.headless=true','--server.address=127.0.0.1',f'--server.port={port}','--browser.gatherUsageStats=false']
    cleanup={'stopped':False,'listener_closed':False}
    with (out/'browser_server.log').open('w',encoding='utf-8') as log:
        process=subprocess.Popen(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+30
            while time.monotonic()<deadline:
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/_stcore/health',timeout=2) as r:
                        if r.status==200 and r.read()==b'ok': break
                except OSError: time.sleep(.25)
            else: raise RuntimeError('Browser QA server did not become healthy')
            yield f'http://127.0.0.1:{port}'
        finally:
            if process.poll() is None:
                if os.name=='nt': subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],stdout=log,stderr=subprocess.STDOUT,check=False)
                else: process.terminate()
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)
            cleanup['stopped']=process.poll() is not None
            with socket.socket() as s: s.settimeout(1); cleanup['listener_closed']=s.connect_ex(('127.0.0.1',port))!=0
            write_json(out/'browser_server_cleanup.json',cleanup)
            if not all(cleanup.values()): raise RuntimeError('QA server cleanup incomplete')

def qa(root=ROOT):
    import pandas as pd
    from dashboard.formatting import number
    browser_path=next((p for p in [Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')] if p.is_file()),None)
    if browser_path is None: raise RuntimeError('Installed browser missing; no screenshot claim can be made')
    out=root/'outputs/phase7/validation'; screenshots=root/'docs/assets/screenshots'; screenshots.mkdir(parents=True,exist_ok=True)
    results=[]; issues=[]; errors=[]; downloads=[]
    with server(root) as url, sync_playwright() as p:
        browser=p.chromium.launch(executable_path=str(browser_path),headless=True)
        try:
            context=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1,accept_downloads=True)
            page=context.new_page(); page.on('pageerror',lambda error:errors.append(str(error)))
            for width in [1440,1280,768,390]:
                page.set_viewport_size({'width':width,'height':1000})
                for slug,title,filename in PAGES:
                    page.goto(url+'/'+slug,wait_until='domcontentloaded')
                    page.get_by_role('heading',name=title,exact=True).wait_for(timeout=60000)
                    page.locator('[data-testid="stPlotlyChart"]').first.wait_for(timeout=60000)
                    page.locator('[data-testid="stStatusWidget"]').wait_for(state='hidden',timeout=60000)
                    page.wait_for_timeout(1000)
                    if width>=1280:
                        expand=page.locator('[data-testid="stSidebarCollapsedControl"] button')
                        if expand.count() and expand.is_visible():
                            expand.click(); page.wait_for_timeout(500)
                    if width<=768:
                        collapse=page.locator('[data-testid="stSidebarCollapseButton"] button')
                        box=collapse.bounding_box() if collapse.count() else None
                        if box and box['x']>=0 and box['x']<width:
                            collapse.click(); page.wait_for_timeout(300)
                    exception=page.locator('[data-testid="stException"]').count()
                    bounds=page.evaluate('({width:window.innerWidth,scroll:document.documentElement.scrollWidth})')
                    metrics=page.locator('[data-testid="stMetric"]').count(); charts=page.locator('[data-testid="stPlotlyChart"]').count()
                    if exception or bounds['scroll']>width+2: issues.append({'page':title,'width':width,'exception':exception,'horizontal_overflow':bounds['scroll']-width})
                    target=screenshots/(filename+'.png') if width==1440 else screenshots/'qa'/str(width)/(filename+'.png')
                    target.parent.mkdir(parents=True,exist_ok=True); page.screenshot(path=str(target),full_page=True,animations='disabled')
                    if width==1440:
                        page.locator('[data-testid="stPlotlyChart"]').first.scroll_into_view_if_needed()
                        page.screenshot(path=str(screenshots/'qa'/('detail_'+filename+'.png')),animations='disabled')
                    results.append({'page':title,'width':width,'metric_cards':metrics,'charts':charts,'exceptions':exception,'horizontal_overflow_px':max(0,bounds['scroll']-width),
                        'screenshot':target.relative_to(root).as_posix(),'screenshot_sha256':sha256(target)})
                    print(f'Browser QA: {width}px {title}',flush=True)
            page.set_viewport_size({'width':1440,'height':1000}); page.goto(url+'/regional')
            page.get_by_role('heading',name='Regional Intelligence',exact=True).wait_for()
            widget=page.locator('[data-testid="stSelectbox"]').filter(has=page.get_by_text('Calendar year',exact=True))
            widget.get_by_role('combobox').click(); page.get_by_role('option',name='2024',exact=True).click()
            fact=pd.read_parquet(root/'outputs/tables/cost_analytics.parquet'); selected=fact[fact.month.dt.year.eq(2024)]
            expected=number(selected.prescription_items.sum(),'count')
            page.locator('[data-testid="stMetric"]').filter(has=page.get_by_text('Selected-region items',exact=True)).get_by_text(expected,exact=True).wait_for()
            # Wait for the rerun to finish replacing tables and download media.
            page.wait_for_timeout(1500)
            with page.expect_download() as event: page.get_by_role('button',name='Download filtered regional summary CSV',exact=True).click()
            path=out/'browser_regional_2024.csv'; event.value.save_as(str(path)); exported=pd.read_csv(path)
            assert len(exported)==7 and exported.prescription_items.sum()==selected.prescription_items.sum()
            downloads.append({'control':'regional summary','year':2024,'rows':len(exported),'item_sum_matches':True,'sha256':sha256(path)})
            expand=page.locator('[data-testid="stSidebarCollapsedControl"] button')
            if expand.count() and expand.is_visible(): expand.click(); page.wait_for_timeout(500)
            page.get_by_role('link',name='Scenario Simulator',exact=True).click(); page.get_by_role('heading',name='Scenario Simulator',exact=True).wait_for()
            volume=page.get_by_role('slider',name='Hypothetical prescription-item change (%)'); volume.focus()
            for _ in range(5): volume.press('ArrowRight')
            cost=page.get_by_role('slider',name='Hypothetical NIC-per-item change (%)'); cost.focus()
            for _ in range(5): cost.press('ArrowLeft')
            baseline=fact[fact.month.dt.year.eq(2025)].net_ingredient_cost_gbp.sum()
            page.locator('[data-testid="stMetric"]').filter(has=page.get_by_text('Hypothetical NIC',exact=True)).get_by_text(number(baseline*1.05*.95,'gbp'),exact=True).wait_for(timeout=30000)
            interactions={'native_navigation':True,'regional_year_change':True,'filtered_csv_actual_download':True,'scenario_keyboard_sliders':True,'scenario_nic_reconciled':True}
        finally: browser.close()
    result={'passed':not issues and not errors,'browser':'Installed Chrome/Edge via Playwright','page_viewport_checks':results,'issues':issues,'javascript_errors':errors,'downloads':downloads,'interactions':interactions,
        'visual_inspection':'Screenshot capture complete; human-equivalent image inspection is recorded separately.'}
    write_json(out/'browser_qa.json',result)
    if not result['passed']: raise AssertionError('Observed browser layout or execution issues; inspect browser_qa.json')
    return result

if __name__=='__main__': qa()
