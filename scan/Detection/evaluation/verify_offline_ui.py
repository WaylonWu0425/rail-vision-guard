"""Read-only frontend regression on the existing idle service; no task start."""
import argparse
from pathlib import Path


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
        page=browser.new_page(viewport={'width':1600,'height':1000})
        errors=[];posts=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
        page.goto('http://127.0.0.1:8802/')
        page.wait_for_function("document.getElementById('points').textContent.includes('4 个顶点')")
        page.locator('#events').evaluate('e=>e.scrollTop=e.scrollHeight')
        before=page.locator('#events').evaluate('e=>e.scrollTop')
        page.wait_for_timeout(1400)
        after=page.locator('#events').evaluate('e=>e.scrollTop')
        assert before>0 and before==after
        page.locator('#draw').click()
        assert page.locator('#region').evaluate("e=>e.classList.contains('drawing')")
        expected=page.evaluate("()=>{for(const run of allRuns)for(const e of run.events){const r=run.recordings.find(r=>r.status==='ready'&&r.model===e.model&&r.startMediaSeconds<=e.mediaSeconds&&e.mediaSeconds<r.endMediaSeconds);if(r)return e.mediaSeconds-r.startMediaSeconds}return null}")
        assert expected is not None
        page.locator('#events button').filter(has_text='关联录像').first.click()
        page.wait_for_function("expected=>{const v=document.getElementById('playback');return v.readyState>=2&&!v.seeking&&Math.abs(v.currentTime-expected)<.1}",arg=expected)
        page.locator('#playback').evaluate('v=>v.currentTime=1')
        page.wait_for_function("()=>{const v=document.getElementById('playback');return !v.seeking&&Math.abs(v.currentTime-1)<.1}")
        page.screenshot(path=str(args.output/'offline_ui_readonly.png'))
        assert not posts,posts
        assert not errors,errors
        print('PASS: latest frontend, frozen ROI sync, list scroll, draw, actual event-offset video seek and manual seek, zero POSTs/errors; fixed HTTP backend not claimed live')
        browser.close()
