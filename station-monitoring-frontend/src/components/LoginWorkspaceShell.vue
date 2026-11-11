<template>
  <main class="login-workspace">
    <header class="workspace-topbar">
      <div class="workspace-brand">
        <img :src="guardLogo" alt="视界巡警 GUARD 标志" width="49" height="53" />
        <strong>视界巡警</strong>
        <span class="brand-divider" aria-hidden="true"></span>
        <span class="brand-product">车站视频监控管理系统</span>
      </div>
      <span class="top-note">现场感知 · 协同处置</span>
    </header>

    <div class="workspace-stage">
      <aside class="login-scene" :class="{ 'is-paused': paused }" :data-phase="phase" aria-label="车站视频监控功能示意">
        <div class="scene-heading">
          <p class="scene-label">现场监控 · 智能辅助识别</p>
          <h1>看见现场。<br />追溯告警。</h1>
          <p class="scene-description">实时预览与人车检测，<br />连接告警截图和录像回放。</p>
        </div>

        <figure class="rail-art">
          <div class="illustration-toolbar">
            <span>⌑&nbsp; 固定机位 · 功能演示</span>
          </div>
          <svg class="station-drawing" viewBox="0 0 720 414" role="img" aria-labelledby="station-title station-desc">
            <title id="station-title">固定枪机、站台与人车检测示意</title>
            <desc id="station-desc">摄像头保持固定，系统分析画面中的人员与车辆，并展示告警截图及手动录像关联。画面不代表实际识别结果。</desc>
            <defs>
              <pattern id="login-ground-grid" width="44" height="24" patternUnits="userSpaceOnUse" patternTransform="matrix(1 .45 -1 .45 360 0)"><path d="M44 0H0V24" fill="none" stroke="#a8c6e0" stroke-width=".7" /></pattern>
              <linearGradient id="login-roof" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f9fcff" /><stop offset="1" stop-color="#c7e0f5" /></linearGradient>
              <linearGradient id="login-platform" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e8f3ff" /><stop offset="1" stop-color="#c0d9f1" /></linearGradient>
              <linearGradient id="login-coverage" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1976d2" stop-opacity=".18" /><stop offset="1" stop-color="#42a5f5" stop-opacity=".035" /></linearGradient>
              <linearGradient id="login-scan"><stop stop-color="#1976d2" stop-opacity="0" /><stop offset=".85" stop-color="#1976d2" stop-opacity=".12" /><stop offset="1" stop-color="#1976d2" stop-opacity=".32" /></linearGradient>
              <clipPath id="login-coverage-clip"><path d="M142 184 626 170 468 360Z" /></clipPath>
            </defs>
            <rect x="0" y="36" width="720" height="360" fill="url(#login-ground-grid)" opacity=".2" />
            <g class="architecture">
              <path d="m42 231 314-151 321 145-314 151Z" fill="#e7f1fb" stroke="#b9cee4" />
              <path d="m285 346 282-136 76 34-282 136Z" fill="#d6e6f5" stroke="#a8c2dd" />
              <g stroke="#9db6ce" stroke-width="2" fill="none"><path d="m311 353 282-136M338 366 620 230M57 220 340 83M80 231 363 94" /></g>
              <path d="m123 271 264-127 83 38-264 127Z" fill="url(#login-platform)" stroke="#8aafd4" />
              <path d="m123 271 83 38v10l-83-38Zm83 38 264-127v10L206 319Z" fill="#a5c7e6" stroke="#7fa5c9" />
              <path d="m132 271 258-124m-192 155 258-124" fill="none" stroke="#fff" stroke-width="3" />
              <path d="m199 298 260-125" fill="none" stroke="#5296ce" stroke-dasharray="2 4" />
              <g stroke="#7d9fbe" stroke-width="2.3"><path d="M203 238v-74m46 53v-75m46 53v-75m46 53V98m46 53V76" /></g>
              <path d="m111 171 263-127 101 44-263 127Z" fill="url(#login-roof)" stroke="#8daecd" />
              <path d="m111 171 101 44v8l-101-44Zm101 44L475 88v8L212 223Z" fill="#a9cbe8" stroke="#88accb" />
              <g stroke="#99bbd9" stroke-width=".8" fill="none"><path d="m136 159 100 44m-52-67 100 44m-52-67 100 44m-52-67 100 44m-52-67 100 44" /><path d="m141 184 263-127m-233 140 263-127" /></g>
              <path d="m336 307 152-73 34 16v23l-152 73-34-16Z" fill="#f5faff" stroke="#7eacd1" />
              <path d="m336 307 34 16v23l-34-16Z" fill="#c3dcf0" stroke="#7eacd1" />
              <path d="m336 307 152-73 34 16-152 73Z" fill="#fff" stroke="#7eacd1" />
              <path d="m345 312 17 8v10l-17-8Zm34 9 20-10v10l-20 10Zm26-13 20-10v10l-20 10Zm26-12 20-10v10l-20 10Zm26-13 20-10v10l-20 10Zm26-12 20-10v10l-20 10Z" fill="#709bbd" />
              <path d="m371 341 149-72" stroke="#1976d2" stroke-width="2" />
            </g>
            <g class="coverage">
              <path d="M142 184 626 170 468 360Z" fill="url(#login-coverage)" stroke="#1976d2" stroke-dasharray="5 5" />
              <g clip-path="url(#login-coverage-clip)"><rect class="scan-band" x="115" y="165" width="90" height="184" fill="url(#login-scan)" /><path class="scan-line" d="M205 165v184" stroke="#42a5f5" /></g>
              <path d="m219 289 112-54 66 29-112 54Z" fill="#1976d2" fill-opacity=".04" stroke="#498ecc" stroke-dasharray="4 4" />
            </g>
            <g class="fixed-camera">
              <path d="m107 284 17-8 17 8-17 8Z" fill="#c1d9ee" stroke="#82a7c9" />
              <path d="M124 283V171" stroke="#6c97be" stroke-width="4" /><path d="M124 178h13v-10" fill="none" stroke="#5e87ab" stroke-width="3" />
              <path d="m107 146 36 10 1 17-36-10Z" fill="#fff" stroke="#6999c0" /><path d="m107 146 11-6 37 10-12 6Z" fill="#e1eef9" stroke="#6999c0" /><path d="m143 156 12-6 1 17-12 6Z" fill="#bdd9ef" stroke="#6999c0" />
              <ellipse cx="150" cy="161" rx="3.2" ry="5" fill="#1976d2" /><circle class="camera-beacon" cx="111" cy="155" r="2" fill="#1976d2" />
              <path d="m108 141-11-13H46" stroke="#94b7d5" fill="none" /><text x="45" y="120" fill="#4f7393" font-size="11">固定枪机</text>
            </g>
            <g class="person-target"><ellipse cx="279" cy="273" rx="12" ry="4" fill="#709ec2" opacity=".18" /><circle cx="278" cy="239" r="5" fill="#416d98" /><path d="M275 246h7l3 13-6 2-8-2Z" fill="#1976d2" /><path d="m274 258-2 13m9-12 4 11m-12-21-5 10m14-10 7 8" fill="none" stroke="#416d98" stroke-width="2.5" stroke-linecap="round" /></g>
            <g class="vehicle-target" stroke="#759dbf"><ellipse cx="572" cy="229" rx="34" ry="9" fill="#709ec2" opacity=".12" /><path d="m537 206 39-19 30 14 3 15-39 19-31-14Z" fill="#fff" /><path d="m537 206 33 16 39-19-33-16Z" fill="#d8e9f8" /><path d="m547 204 12-18 17-8 20 10-3 18-24 12Z" fill="#e7f3ff" /><path d="m550 205 12-15 14-7 15 7-3 14-20 10Z" fill="#7eabc9" /><ellipse cx="548" cy="220" rx="3.5" ry="5.5" fill="#4c7190" /><ellipse cx="587" cy="226" rx="3.5" ry="5.5" fill="#4c7190" /></g>
            <g class="detection-box person-box"><path d="M260 246v-17h13m13 0h13v17m0 14v17h-13m-13 0h-13v-17" fill="none" stroke="#1976d2" stroke-width="1.8" /><rect x="259" y="207" width="47" height="18" rx="4" fill="#1976d2" /><text x="283" y="219" text-anchor="middle" fill="#fff" font-size="10">人员</text></g>
            <g class="detection-box vehicle-box"><path d="M529 193v-18h17m49 0h18v18m0 29v17h-18m-49 0h-17v-17" fill="none" stroke="#1976d2" stroke-width="1.8" /><rect x="529" y="153" width="46" height="18" rx="4" fill="#1976d2" /><text x="552" y="165" text-anchor="middle" fill="#fff" font-size="10">车辆</text></g>
            <g class="event-path"><path d="M300 277h36l55 34h77" fill="none" stroke="#c58a2b" stroke-width="1.7" stroke-dasharray="4 4" /><circle cx="300" cy="277" r="3.5" fill="#c58a2b" /></g>
            <g fill="#6989a6" font-size="10.5"><path d="m213 308-22 31H125m363-39 34 29h52" stroke="#a7bfd7" fill="none" /><text x="83" y="343">站台监控区域</text><text x="580" y="333">轨道区域</text></g>
          </svg>
          <figcaption>固定枪机采集画面 · 系统侧辅助识别</figcaption>
        </figure>

        <div class="evidence-card" aria-hidden="true">
          <div class="evidence-top"><i></i><strong>{{ phase === 3 ? '告警与录像关联' : '人员进入监控区域' }}</strong><span>功能示意</span></div>
          <div class="evidence-body">
            <svg viewBox="0 0 86 54" aria-hidden="true"><rect width="86" height="54" rx="4" fill="#eaf3fc" /><path d="M0 42 46 18l40 18M9 49 51 28l35 15" fill="none" stroke="#b0cce6" /><path d="m4 16 44-10 30 11-44 11Z" fill="#c7dff3" /><circle cx="48" cy="30" r="3" fill="#5d86a8" /><path d="M48 34v8m0-5-4 4m4-4 4 4m-4 1-3 5m3-5 3 5" stroke="#5d86a8" stroke-width="2" /><rect x="39" y="24" width="18" height="26" fill="none" stroke="#1976d2" /></svg>
            <div><strong>{{ phase === 3 ? '定位告警发生时刻' : '保留告警截图' }}</strong><small>{{ phase === 3 ? '同一摄像头 · 时间覆盖' : '画面 · 摄像头 · 发生时刻' }}</small></div>
          </div>
          <div class="recording-link">◷&nbsp; 手动录像 · 覆盖告警时刻</div>
          <div class="recording-timeline"><span></span><i></i><b></b></div>
        </div>

        <nav class="storyline" aria-label="功能演示阶段">
          <div class="storyline-steps">
            <button v-for="(step, index) in steps" :key="step" type="button" class="story-step" :class="{ active: phase === index }" :aria-pressed="phase === index" @click="selectPhase(index)"><span>0{{ index + 1 }}</span>{{ step }}<i></i></button>
          </div>
          <div class="storyline-description"><span>{{ stageTitles[phase] }}</span><span>0{{ phase + 1 }} / 04</span></div>
        </nav>
      </aside>

      <section class="login-auth-pane" aria-label="登录工作台" @focusin="onFormFocus" @focusout="onFormBlur">
        <div class="login-auth-content"><slot /></div>
      </section>
    </div>
    <footer class="workspace-footer"><span>视界巡警 · 车站视频监控管理系统</span><span>蓝白工作台 / 功能示意</span></footer>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import guardLogo from '@/assets/guard-logo.webp'

const steps = ['实时预览', '人车识别', '告警截图', '录像追溯']
const stageTitles = [
  '连接现场，保持清晰视野',
  '系统分析画面，辅助识别人员与车辆',
  '人员进入监控区域，保留告警截图',
  '手动录像覆盖告警时刻，便于回放追溯'
]
const phase = ref(0)
const userPaused = ref(false)
const formFocused = ref(false)
const reducedMotion = ref(false)
const hidden = ref(false)
const paused = computed(() => userPaused.value || formFocused.value || reducedMotion.value || hidden.value)
let timer = null
let mediaQuery = null

function schedule() {
  window.clearTimeout(timer)
  timer = null
  if (paused.value) return
  timer = window.setTimeout(() => {
    phase.value = (phase.value + 1) % steps.length
    schedule()
  }, 4000)
}
function selectPhase(index) {
  userPaused.value = true
  phase.value = index
  schedule()
}
function onFormFocus() { formFocused.value = true; schedule() }
function onFormBlur(event) {
  if (event.currentTarget.contains(event.relatedTarget)) return
  formFocused.value = false
  schedule()
}
function onVisibilityChange() { hidden.value = document.hidden; schedule() }
function onMotionChange(event) { reducedMotion.value = event.matches; schedule() }
onMounted(() => {
  mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion.value = mediaQuery.matches
  hidden.value = document.hidden
  mediaQuery.addEventListener('change', onMotionChange)
  document.addEventListener('visibilitychange', onVisibilityChange)
  schedule()
})
onBeforeUnmount(() => {
  window.clearTimeout(timer)
  mediaQuery?.removeEventListener('change', onMotionChange)
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>

<style scoped>
.login-workspace { --primary: #1976d2; width: 100%; min-height: 100vh; min-height: 100svh; padding: 0 56px; display: flex; flex-direction: column; box-sizing: border-box; background: #f4f7fb; color: #213a54; font-family: "Microsoft YaHei", "PingFang SC", sans-serif; -webkit-font-smoothing: antialiased; }
.login-workspace * { box-sizing: border-box; }
.workspace-topbar { height: 80px; flex: none; display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.workspace-brand { display: flex; align-items: center; gap: 12px; }
.workspace-brand img { width: 49px; height: 53px; object-fit: contain; }
.workspace-brand strong { font-size: 21px; letter-spacing: 2px; color: #203e61; }
.brand-divider { width: 1px; height: 22px; margin: 0 7px 0 12px; background: #ccd9e6; }
.brand-product, .top-note { font-size: 12px; color: #71879b; letter-spacing: 1px; }
.top-note::before { content: ''; display: inline-block; width: 22px; height: 1px; margin: 0 10px 4px 0; background: #7ca5cc; }
.workspace-stage { width: 100%; max-width: 1440px; height: clamp(640px, calc(100svh - 160px), 760px); flex: none; margin: auto; display: grid; grid-template-columns: 55fr 45fr; overflow: hidden; border: 1px solid #d5e3ef; border-radius: 12px; background: #fff; box-shadow: 0 24px 60px -36px #345f9240; }
.login-scene { position: relative; isolation: isolate; min-width: 0; overflow: hidden; display: flex; flex-direction: column; padding: 34px 44px 29px; border-right: 1px solid #d9e7f4; background: linear-gradient(135deg, #f1f7fd, #e9f3fc 72%, #edf6fd); }
.scene-heading { position: relative; z-index: 2; }
.scene-label { margin: 0; display: flex; align-items: center; gap: 11px; color: #426c94; font-size: 12px; letter-spacing: 1px; }
.scene-label::before { content: ''; width: 23px; height: 2px; background: var(--primary); }
.scene-heading h1 { margin: 18px 0 12px; color: #193e63; font-size: 45px; line-height: 1.36; letter-spacing: 1px; font-weight: 600; }
.scene-description { margin: 0; color: #58748e; font-size: 15px; line-height: 1.8; }
.rail-art { position: relative; min-height: 270px; flex: 1; margin: 16px -24px 10px; }
.illustration-toolbar { position: absolute; z-index: 5; top: 0; left: 8px; right: 8px; display: flex; align-items: center; justify-content: space-between; color: #5d7f9c; font-size: 12px; }
.station-drawing { position: absolute; top: 22px; left: 0; width: 100%; height: calc(100% - 36px); overflow: visible; }
.rail-art figcaption { position: absolute; bottom: 1px; left: 8px; color: #6685a0; font-size: 11px; }
.rail-art figcaption::before { content: '•'; margin-right: 7px; color: #75a6d2; }
.coverage { opacity: .58; transition: opacity .5s ease; }
.login-scene[data-phase="0"] .coverage, .login-scene[data-phase="1"] .coverage { opacity: 1; }
.scan-band, .scan-line { opacity: 0; }
.login-scene[data-phase="0"]:not(.is-paused) .scan-band, .login-scene[data-phase="0"]:not(.is-paused) .scan-line { animation: login-scan 3.2s ease-out 1 both; }
.login-scene[data-phase="0"]:not(.is-paused) .camera-beacon { animation: login-pulse 1.2s ease-in-out 2; }
.person-target { transform: translate(-70px, 30px); transition: transform 1.25s ease; }
.login-scene[data-phase="1"] .person-target, .login-scene[data-phase="2"] .person-target, .login-scene[data-phase="3"] .person-target { transform: translate(0); }
.detection-box { opacity: 0; transition: opacity .45s ease; }
.login-scene[data-phase="1"] .detection-box, .login-scene[data-phase="2"] .detection-box, .login-scene[data-phase="3"] .detection-box { opacity: 1; }
.login-scene[data-phase="1"]:not(.is-paused) .person-box { animation: login-detect .5s 1.35s both; }
.login-scene[data-phase="1"]:not(.is-paused) .vehicle-box { animation: login-detect .5s 2.1s both; }
.event-path { opacity: 0; transition: opacity .6s ease; }
.login-scene[data-phase="2"] .event-path, .login-scene[data-phase="3"] .event-path { opacity: 1; }
.login-scene[data-phase="2"]:not(.is-paused) .event-path path { animation: login-connect 1.2s ease-out 1 both; }
.evidence-card { position: absolute; z-index: 4; top: 105px; right: 23px; width: 238px; padding: 13px 14px 12px; border: 1px solid #cfdfea; border-radius: 8px; background: #fffffff5; box-shadow: 0 14px 32px -17px #416d9566; opacity: 0; transform: translateY(9px); transition: opacity .55s ease, transform .55s ease; pointer-events: none; }
.login-scene[data-phase="2"] .evidence-card, .login-scene[data-phase="3"] .evidence-card { opacity: 1; transform: translateY(0); }
.evidence-top { display: flex; align-items: center; gap: 6px; white-space: nowrap; color: #385875; font-size: 12px; }
.evidence-top i { width: 6px; height: 6px; border-radius: 50%; background: #d2942c; }
.evidence-top > span { margin-left: auto; padding: 1px 4px; border: 1px solid #e4ebf1; border-radius: 3px; color: #7d97aa; font-size: 10px; }
.evidence-body { display: flex; align-items: center; gap: 9px; margin: 10px 0; }
.evidence-body svg { width: 72px; height: 48px; flex: none; border: 1px solid #d9e9f5; border-radius: 4px; }
.evidence-body div { min-width: 0; display: flex; flex-direction: column; gap: 5px; }
.evidence-body strong { color: #2d5880; font-size: 12px; }
.evidence-body small { color: #748ca0; font-size: 10px; white-space: nowrap; }
.recording-link { padding-top: 9px; border-top: 1px solid #edf2f7; color: #6e8ca7; font-size: 11px; opacity: .45; }
.login-scene[data-phase="3"] .recording-link { opacity: 1; color: var(--primary); }
.recording-timeline { position: relative; height: 10px; margin-top: 9px; overflow: hidden; border-radius: 2px; background: #eaf2f9; }
.recording-timeline > span { position: absolute; top: 0; bottom: 0; left: 9%; width: 76%; background: #c0def9; }
.recording-timeline > i { position: absolute; top: 0; bottom: 0; left: 0; width: 0; background: #4d9bdf; transition: width 3s linear; }
.login-scene[data-phase="3"] .recording-timeline > i { width: 64%; }
.recording-timeline > b { position: absolute; top: 1px; bottom: 1px; left: 62%; border-left: 2px solid #dca038; }
.storyline { position: relative; z-index: 3; margin-top: auto; padding-top: 14px; border-top: 1px solid #c6daeb; }
.storyline-steps { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 9px; }
.story-step { position: relative; display: flex; align-items: center; gap: 6px; padding: 5px 0 11px; border: 0; background: none; color: #6b8aa5; font-size: 12px; white-space: nowrap; text-align: left; cursor: pointer; }
.story-step > span { color: #8cabc3; font-family: Consolas, monospace; font-size: 11px; }
.story-step > i { position: absolute; bottom: 0; width: 100%; height: 2px; overflow: hidden; border-radius: 2px; background: #cddfec; }
.story-step > i::after { content: ''; position: absolute; inset: 0; background: var(--primary); transform: scaleX(0); transform-origin: left; }
.story-step.active { color: #245d95; font-weight: 600; }
.story-step.active > i::after { animation: login-progress 4s linear forwards; }
.login-scene.is-paused .story-step.active > i::after { animation: none; transform: scaleX(1); }
.storyline-description { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 12px; color: #587b99; font-size: 12px; }
.storyline-description > span:last-child { color: #7798b2; font-family: Consolas, monospace; white-space: nowrap; }
.login-scene.is-paused .recording-timeline > i, .login-scene.is-paused .person-target { transition: none; }
.login-auth-pane { min-width: 0; display: flex; align-items: center; justify-content: center; padding: 44px 54px; }
.login-auth-content { width: min(410px, 100%); }
.workspace-footer { display: flex; align-items: center; justify-content: space-between; min-height: 48px; flex: none; gap: 20px; color: #8398aa; font-size: 11px; }
@keyframes login-scan { 0% { transform: translateX(0); opacity: 0; } 12%, 80% { opacity: 1; } 100% { transform: translateX(480px); opacity: 0; } }
@keyframes login-pulse { 0%, 100% { opacity: .5; } 50% { opacity: 1; } }
@keyframes login-detect { from { opacity: 0; } to { opacity: 1; } }
@keyframes login-connect { from { stroke-dashoffset: 24; opacity: 0; } to { stroke-dashoffset: 0; opacity: 1; } }
@keyframes login-progress { to { transform: scaleX(1); } }
@media (min-width: 1600px) { .login-workspace { padding: 0 80px; } .login-scene { padding: 41px 52px 32px; } .scene-heading h1 { font-size: 48px; } }
@media (max-width: 1100px) { .login-workspace { padding: 0 28px; } .workspace-stage { height: auto; min-height: 680px; } .login-scene { padding: 30px 26px 24px; } .scene-heading h1 { font-size: 35px; } .rail-art { margin-left: -15px; margin-right: -15px; } .evidence-card { width: 188px; padding: 10px; } .story-step { font-size: 10px; } .login-auth-pane { padding: 36px; } }
@media (max-width: 800px) { .workspace-stage { grid-template-columns: 1fr; height: auto; } .login-scene { min-height: 530px; border-right: 0; border-bottom: 1px solid #d9e7f4; } .evidence-card { display: none; } .login-auth-pane { padding: 32px; } .workspace-footer { padding: 12px 0; } }
@media (prefers-reduced-motion: reduce) { .login-workspace *, .login-workspace *::before, .login-workspace *::after { animation: none !important; transition: none !important; } }
</style>
