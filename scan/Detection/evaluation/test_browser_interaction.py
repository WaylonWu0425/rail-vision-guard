"""Read-only dataset regression: mock POST so no human labels are changed."""


def main():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
        page = browser.new_page(viewport={"width":1600,"height":1000})
        errors, posts = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.add_init_script("window.confirm=()=>{throw Error('Native confirm must not be used')}")
        def intercept(route):
            if route.request.method == 'POST':
                posts.append(route.request.post_data_json)
                if len(posts)==1:
                    route.fulfill(status=403,content_type='application/json',body='{"error":"expired test session","code":"token_expired"}')
                else:
                    route.fulfill(status=200, content_type='application/json', body='{"saved":true,"reviewed":false}')
            else:
                route.continue_()
        page.route('**/annotation/*', intercept)
        page.goto('http://127.0.0.1:8799/')
        page.wait_for_function("document.getElementById('status').textContent.includes('复核')")
        first_source=page.locator('#source').inner_text()
        before=page.locator('#boxes button').count()
        canvas=page.locator('#canvas').bounding_box()
        page.mouse.move(canvas['x']+80,canvas['y']+80)
        page.mouse.down()
        page.mouse.move(canvas['x']+160,canvas['y']+180,steps=5)
        page.mouse.up()
        assert page.locator('#boxes button').count()==before+1, 'Pointer drawing failed'
        page.locator('#next').click()
        assert page.locator('#leave').is_visible()
        page.locator('#cancelLeave').click()
        assert page.locator('#source').inner_text()==first_source
        assert page.locator('#boxes button').count()==before+1
        page.locator('#next').click()
        page.locator('#discardLeave').click()
        page.wait_for_function("document.getElementById('source').textContent.includes('162706')")
        page.locator('#add').click()
        page.locator('#next').click()
        page.locator('#saveLeave').click()
        page.wait_for_function("document.getElementById('source').textContent.includes('162712')")
        assert len(posts)==2 and posts[0]['reviewed'] is False and posts[1]==posts[0]
        page.locator('#add').click()
        page.locator('#filter').select_option('all')
        assert page.locator('#leave').is_visible()
        page.locator('#cancelLeave').click()
        assert page.locator('#filter').input_value()=='priority'
        assert not errors,errors
        print('PASS: pointer drawing; inline cancel/discard/save-and-switch; expired-token automatic refresh preserves payload; filter cancel; no native confirmation; no real POST writes; no page errors')
        browser.close()


if __name__ == '__main__':
    main()
