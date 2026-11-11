"""Read-only browser check against the actual review dataset."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
        page=browser.new_page(viewport={"width":1600,"height":1000})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        response=page.goto('http://127.0.0.1:8799/')
        page.wait_for_function("document.getElementById('canvas').width > 300 && document.getElementById('status').textContent.includes('复核')")
        assert response.status==200
        assert page.locator('.sample').count()==10
        initial=page.locator('#zoom').inner_text()
        page.locator('#plus').click()
        assert page.locator('#zoom').inner_text()!=initial
        page.locator('#fit').click()
        page.locator('#next').click()
        page.wait_for_function("document.getElementById('source').textContent.includes('162706')")
        page.locator('#add').click()
        assert page.locator('#boxes button').count()==1
        page.locator('#coord0').fill('10')
        page.locator('#apply').click()
        assert '10, 0, 100, 100' in page.locator('#boxes').inner_text()
        page.locator('#delete').click()
        assert page.locator('#boxes button').count()==0
        # Discard in-memory edits; do not save the real dataset.
        page.reload()
        page.wait_for_function("document.getElementById('canvas').width > 300 && document.getElementById('status').textContent.includes('复核')")
        assert not errors,errors
        output=Path(__file__).resolve().parent/'browser_smoke.png'
        page.screenshot(path=str(output))
        print(json.dumps(dict(http=response.status,prioritySamples=10,zoom=True,navigation=True,addEditDelete=True,consoleErrors=errors,screenshot=str(output)),ensure_ascii=False))
        browser.close()


if __name__=='__main__':
    main()
