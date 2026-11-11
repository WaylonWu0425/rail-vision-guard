"""Read-only browser verification and evidence screenshots."""
import argparse
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
        page=browser.new_page(viewport={'width':1600,'height':1000})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        result=page.goto('http://127.0.0.1:8801/')
        page.wait_for_function("document.querySelectorAll('.panel canvas').length===5")
        assert result.status==200
        assert page.locator('.case').count()==16
        page.screenshot(path=str(args.output/'viewer.png'))
        page.locator('#scope').select_option('all')
        assert page.locator('.case').count()==84
        page.locator('#filter').select_option('duplicate_candidate')
        page.wait_for_function("document.getElementById('notice').textContent.includes('video_03_002027')")
        assert page.locator('.case').count()==1
        option=page.locator('#focus option').evaluate_all("xs=>xs.find(x=>x.textContent.includes('重复框')).value")
        page.locator('#focus').select_option(option)
        page.locator('.panel canvas').nth(1).screenshot(path=str(args.output/'duplicate_truth.png'))
        page.locator('.panel canvas').nth(3).screenshot(path=str(args.output/'duplicate_full1280.png'))
        page.locator('#filter').select_option('all')
        page.locator('.case').filter(has_text='photo_20261016-162712').click()
        page.wait_for_function("document.getElementById('notice').textContent.includes('photo_20261016-162712')")
        page.locator('#focus').select_option('0')
        page.locator('.panel canvas').nth(1).screenshot(path=str(args.output/'missed_person_truth.png'))
        page.locator('.case').filter(has_text='video_03_000887').click()
        page.wait_for_function("document.getElementById('notice').textContent.includes('video_03_000887')")
        option=page.locator('#focus option').evaluate_all("xs=>xs.find(x=>x.textContent.includes('full1280')&&x.textContent.includes('定位')).value")
        page.locator('#focus').select_option(option)
        page.locator('.panel canvas').nth(3).screenshot(path=str(args.output/'localization_full1280.png'))
        page.locator('.case').filter(has_text='video_02_000000').click()
        page.wait_for_function("document.getElementById('notice').textContent.includes('video_02_000000')")
        option=page.locator('#focus option').evaluate_all("xs=>xs.find(x=>x.textContent.includes('full640')&&x.textContent.includes('无人图')).value")
        page.locator('#focus').select_option(option)
        page.locator('.panel canvas').nth(2).screenshot(path=str(args.output/'signal_false_full640.png'))
        assert page.request.post('http://127.0.0.1:8801/annotation/anything',data='{}').status==501
        assert page.request.get('http://127.0.0.1:8801/',headers={'Host':'evil.invalid'}).status==403
        assert not errors,errors
        print('PASS: 16 representative / 84 total; five synchronized panels; duplicate filter; target crop; POST rejected; invalid Host rejected; no page errors')
        browser.close()


if __name__=='__main__':
    main()
