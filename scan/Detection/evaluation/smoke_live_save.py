"""Real browser -> real HTTP -> temporary JSON -> reload. No mocked requests."""
import json
import tempfile
import threading
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
from werkzeug.serving import make_server

import workbench as bench


def main():
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        (root/'images').mkdir()
        cv2.imencode('.jpg',np.zeros((100,100,3),dtype=np.uint8))[1].tofile(str(root/'images'/'test.jpg'))
        bench.write(root/'manifest.json',dict(entries=[dict(id='synthetic',image='test.jpg',width=100,height=100,
                    priority=True,split='test',group='synthetic-only',source='Temporary test image',seconds=None)]))
        args=SimpleNamespace(dataset=root,port=0)
        app=bench.create_app(args)
        server=make_server('127.0.0.1',0,app,threaded=True)
        args.port=server.server_port
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True)
                page=browser.new_page(viewport={'width':1600,'height':1000})
                errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                url=f'http://127.0.0.1:{args.port}/'
                page.goto(url)
                page.wait_for_function("document.getElementById('status').textContent==='待人工复核'")
                page.locator('#add').click()
                page.locator('#reviewed').check()
                page.evaluate("token='intentionally-expired-test-token'")
                page.locator('#save').click()
                page.wait_for_function("document.getElementById('status').textContent==='已保存人工复核结果'")
                saved=bench.read(root/'annotations'/'synthetic.json')
                assert saved['reviewed'] is True and len(saved['boxes'])==1
                assert (root/'labels'/'synthetic.txt').exists()
                page.reload()
                page.wait_for_function("document.getElementById('status').textContent==='已人工复核'")
                assert page.locator('#reviewed').is_checked()
                assert page.locator('#boxes button').count()==1
                assert not errors,errors
                print(json.dumps(dict(realHttp=True,expiredTokenRecovery=True,jsonSaved=True,yoloSaved=True,
                                      reloadVerified=True,productionDatasetTouched=False,pageErrors=errors)))
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__=='__main__':
    main()
