// Real browser -> Vue -> local recognition HTTP -> original model -> rendered image.
// No mocked inference, login response, camera frames or database responses.
const { chromium } = require('C:/Users/吴炜/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const root = path.resolve(__dirname, '../..');
  const out = path.join(root, process.argv[2] || 'docs/original-recognition-ui-20261026');
  fs.mkdirSync(out, { recursive: true });
  const report = { status: 'running', frontend: 'http://localhost:8082', steps: [], pageErrors: [] };
  const browser = await chromium.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: true });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  page.setDefaultTimeout(30000);
  let recognitionPage = false;
  page.on('pageerror', error => { if (recognitionPage) report.pageErrors.push(error.message); });
  try {
    assert(process.env.RECOGNITION_TEST_ACCOUNT && process.env.RECOGNITION_TEST_PASSWORD, 'Set test account/password');
    await page.goto('http://localhost:8082/login?redirect=/originalRecognition', { waitUntil: 'domcontentloaded', timeout: 120000 });
    await page.locator('input[name="username"]').fill(process.env.RECOGNITION_TEST_ACCOUNT);
    await page.locator('input[name="password"]').fill(process.env.RECOGNITION_TEST_PASSWORD);
    await page.getByRole('button', { name: '登录工作台', exact: true }).click();
    await page.waitForURL('**/originalRecognition', { timeout: 45000 });
    recognitionPage = true;
    await page.getByText('本机原版识别服务已连接', { exact: true }).waitFor();
    report.steps.push('real account login and recognition route connected');

    for (const viewport of [{ width: 1860, height: 980 }, { width: 1920, height: 1080 }, { width: 1366, height: 768 }, { width: 1280, height: 720 }]) {
      await page.setViewportSize(viewport);
      const layout = await page.locator('.original-page').evaluate(el => {
        const rect = el.getBoundingClientRect(), parent = el.parentElement.getBoundingClientRect();
        return { width: rect.width, parentWidth: parent.width, scrollWidth: el.scrollWidth, clientWidth: el.clientWidth };
      });
      assert(Math.abs(layout.width - layout.parentWidth) < 3, `Workspace not full width: ${JSON.stringify(layout)}`);
      assert(layout.scrollWidth <= layout.clientWidth + 1, `Horizontal overflow: ${JSON.stringify(layout)}`);
      assert((await page.locator('.metrics-grid strong').allTextContents()).every(text => text.trim().startsWith('—')), 'No counts should be shown before inference');
      assert.equal(await page.locator('.results-section .el-table').count(), 0, 'Premature no-detections table');
      assert(await page.getByRole('button', { name: '开始识别', exact: true }).isDisabled());
      assert.equal(await page.locator('.model-info').getAttribute('open'), null);
      await page.screenshot({ path: path.join(out, `empty_${viewport.width}.png`), fullPage: true });
    }
    await page.setViewportSize({ width: 1860, height: 980 });
    report.steps.push('empty state fills workspace at 1280/1366/1860/1920 widths; no horizontal overflow, premature zero counts or results table; model details collapsed');
    const chooser = page.waitForEvent('filechooser');
    await page.getByRole('button', { name: '选择本地视频', exact: true }).click();
    await chooser;
    report.steps.push('empty-state file action opens native chooser');
    await page.getByRole('button', { name: '图片', exact: true }).click();
    await page.locator('#original-file').setInputFiles(path.join(root, 'scan/Detection/simulation_images/02_person_intrusion_v2.png'));
    await page.getByText('原始预览 · 尚未识别', { exact: true }).waitFor();
    await page.getByText('待开始', { exact: true }).waitFor();
    assert((await page.locator('.metrics-grid strong').allTextContents()).every(text => text.trim().startsWith('—')));
    await page.waitForFunction(() => document.querySelector('img[alt="所选图片原始预览，尚未运行识别"]')?.naturalWidth > 0);
    await page.screenshot({ path: path.join(out, 'selected_image.png'), fullPage: true });
    report.steps.push('selected image previews before inference, without displaying predictions');
    await page.getByRole('button', { name: '开始识别', exact: true }).click();
    await page.getByText('识别完成', { exact: true }).waitFor({ timeout: 120000 });
    const preview = page.locator('img[alt="原版 best.pt 人车检测结果"]');
    await preview.waitFor();
    await page.waitForFunction(() => document.querySelector('img[alt="原版 best.pt 人车检测结果"]')?.naturalWidth > 0);
    assert((await page.locator('.section-heading').innerText()).includes('人员'));
    await page.screenshot({ path: path.join(out, 'browser_image.png'), fullPage: true });
    report.steps.push('uploaded synthetic test image -> real best.pt inference -> result image and counts rendered (not an accuracy evaluation)');

    await page.getByRole('button', { name: '本地视频', exact: true }).click();
    assert((await page.locator('.metrics-grid strong').allTextContents()).every(text => text.trim().startsWith('—')), 'Changing input must clear old predictions');
    await page.locator('#original-file').setInputFiles('D:/AAA空信242/比赛/进行中/第八届全球校园人工智能算法精英大赛/真实车站监控视频/飞书20261016-162518.mp4');
    await page.getByText('原始预览 · 尚未识别', { exact: true }).waitFor();
    await page.waitForFunction(() => document.querySelector('video[aria-label="所选视频原始预览，尚未运行识别"]')?.videoWidth > 0);
    await page.screenshot({ path: path.join(out, 'selected_video.png'), fullPage: true });
    report.steps.push('real MP4 original preview and controls available before inference');
    await page.locator('#original-file').setInputFiles('D:/AAA空信242/比赛/进行中/第八届全球校园人工智能算法精英大赛/真实车站监控视频/环境监控.avi');
    await page.getByRole('button', { name: '开始识别', exact: true }).click();
    await page.getByRole('button', { name: '暂停识别', exact: true }).waitFor();
    await page.getByRole('button', { name: '暂停识别', exact: true }).click();
    await page.getByText('已暂停', { exact: true }).waitFor();
    await page.getByRole('button', { name: '继续识别', exact: true }).click();
    await page.getByText('识别完成', { exact: true }).waitFor({ timeout: 120000 });
    assert((await page.locator('.playback-controls').innerText()).includes('第 68 帧'));
    const aspect = await preview.evaluate(el => {
      const style = getComputedStyle(el);
      return { fit: style.objectFit, naturalWidth: el.naturalWidth, naturalHeight: el.naturalHeight };
    });
    assert.equal(aspect.fit, 'contain');
    assert(aspect.naturalWidth > 0 && aspect.naturalHeight > 0);
    await page.locator('.model-info > summary').click();
    assert.notEqual(await page.locator('.model-info').getAttribute('open'), null);
    await page.locator('.model-info > summary').click();
    await page.locator('.results-section > summary').click();
    assert.equal(await page.locator('.results-section').getAttribute('open'), null);
    await page.locator('.results-section > summary').click();
    report.steps.push('media uses contain without cropping; model details and result rows expand/collapse');
    await page.screenshot({ path: path.join(out, 'browser_video.png'), fullPage: true });
    report.steps.push('real AVI upload -> pause/resume -> all 68 frames processed -> preview and current-frame result rendered');
    const scroll = await page.locator('.original-page').evaluate(el => {
      el.scrollTop = el.scrollHeight;
      return { clientHeight: el.clientHeight, scrollHeight: el.scrollHeight, scrollTop: el.scrollTop };
    });
    assert(scroll.scrollHeight <= scroll.clientHeight || scroll.scrollTop > 0);
    report.steps.push('workspace scrolls to lower detection results without stretching the video');

    // Start another real video task and explicitly stop it. Never opens hardware.
    await page.getByRole('button', { name: '开始识别', exact: true }).click();
    await page.getByRole('button', { name: '停止识别', exact: true }).waitFor();
    await page.getByRole('button', { name: '停止识别', exact: true }).click();
    await page.getByText('已停止', { exact: true }).waitFor();
    report.steps.push('explicit stop reaches stopped state');
    await page.getByRole('button', { name: '本机摄像头', exact: true }).click();
    await page.getByText('本机摄像头编号', { exact: true }).waitFor();
    report.steps.push('USB input UI available; no real device opened');
    await page.getByRole('button', { name: '网络摄像头', exact: true }).click();
    await page.getByText('已配置的网络摄像头', { exact: true }).waitFor();
    await page.waitForTimeout(800);
    report.steps.push('network camera selection UI available; no RTSP stream opened');
    await page.getByRole('button', { name: '本地视频', exact: true }).click();
    await page.locator('#original-file').setInputFiles('D:/AAA空信242/比赛/进行中/第八届全球校园人工智能算法精英大赛/真实车站监控视频/环境监控.avi');
    const started = page.waitForResponse(r => r.url().endsWith('/original/jobs') && r.request().method() === 'POST');
    await page.getByRole('button', { name: '开始识别', exact: true }).click();
    const created = await (await started).json();
    await page.getByRole('button', { name: '返回智能检测', exact: true }).click();
    await page.waitForURL('**/imageDetection');
    await page.waitForTimeout(1000);
    const released = await page.request.get(`http://127.0.0.1:5002/original/jobs/${created.data.id}`);
    const finalJob = (await released.json()).data;
    assert(['stopped', 'finished'].includes(finalJob.state) && finalJob.captureReleased);
    report.steps.push('leaving route stops video task and releases capture');
    assert.equal(report.pageErrors.length, 0, report.pageErrors.join('\n'));
    report.status = 'passed';
  } catch (error) {
    report.status = 'failed'; report.error = error.message;
    await page.screenshot({ path: path.join(out, 'browser_failure.png'), fullPage: true }).catch(() => {});
    process.exitCode = 1;
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(out, 'browser_verification.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report));
  }
})();
