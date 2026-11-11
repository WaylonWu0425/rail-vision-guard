<template>
  <main class="auth-page">
    <div class="auth-shell">
      <section class="brand-pane" aria-label="视界巡警系统介绍">
        <div class="brand-row">
          <img class="brand-logo" src="@/assets/logo.png" alt="视界巡警标志" />
          <div>
            <strong>视界巡警</strong>
            <span>车站视频监控平台</span>
          </div>
        </div>

        <figure class="station-visual">
          <img src="@/assets/login-station-hero.webp" alt="现代车站站台空间示意图" />
        </figure>

        <div class="brand-copy">
          <p class="eyebrow">VIDEO MONITORING · INTELLIGENT DETECTION</p>
          <h1>车站视频监控与智能检测</h1>
          <p>接入摄像头实时画面，辅助识别人员与车辆，留存告警截图并回溯录像证据。</p>
        </div>
      </section>

      <section class="auth-pane" :aria-label="panelLabel">
        <div class="auth-panel">
          <slot />
        </div>
      </section>
    </div>

    <footer>视界巡警 · 车站视频监控管理系统</footer>
  </main>
</template>

<script setup>
defineProps({
  panelLabel: {
    type: String,
    default: '账户认证'
  }
})
</script>

<style scoped>
.auth-page {
  --brand-900: #182f47;
  --brand-800: #243e5c;
  --brand-700: #315a7e;
  --brand-100: #eaf1f7;
  --ink: #182230;
  --muted: #667085;
  --line: #d7dde5;
  width: 100%;
  height: 100vh;
  height: 100svh;
  min-height: 100vh;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  padding: clamp(24px, 4vw, 56px);
  overflow-y: auto;
  color: var(--ink);
  background: #f7f8fa;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", system-ui, sans-serif;
}
.auth-page, .auth-page * { box-sizing: border-box; }
.auth-shell {
  width: min(1240px, 100%);
  margin: auto;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(380px, .85fr);
  align-items: center;
  gap: clamp(40px, 6vw, 80px);
}
.brand-pane { min-width: 0; }
.brand-row { display: flex; align-items: center; gap: 12px; margin-bottom: 22px; }
.brand-logo { width: 38px; height: 42px; object-fit: contain; }
.brand-row div { display: flex; flex-direction: column; gap: 2px; }
.brand-row strong { color: var(--brand-900); font-size: 22px; font-weight: 650; letter-spacing: .04em; }
.brand-row span { color: var(--muted); font-size: 13px; }
.station-visual { height: clamp(310px, 40vw, 470px); margin: 0; overflow: hidden; border-radius: 12px; background: #e8edf2; }
.station-visual img { width: 100%; height: 100%; display: block; object-fit: cover; object-position: center; }
.brand-copy { margin-top: 24px; max-width: 680px; }
.eyebrow { margin: 0 0 7px; color: var(--brand-700); font-size: 12px; font-weight: 650; letter-spacing: .1em; }
.brand-copy h1 { margin: 0; color: var(--brand-900); font-size: clamp(27px, 3vw, 34px); line-height: 1.35; font-weight: 650; letter-spacing: .01em; }
.brand-copy p:last-child { margin: 12px 0 0; color: #475467; font-size: 16px; line-height: 1.75; }
.auth-pane { display: flex; justify-content: center; min-width: 0; }
.auth-panel {
  width: min(430px, 100%);
  padding: clamp(28px, 4vw, 40px);
  border: 1px solid #e4e7ec;
  border-radius: 12px;
  background: rgba(255, 255, 255, .96);
  box-shadow: 0 14px 40px rgba(24, 47, 71, .08);
}
footer { width: min(1240px, 100%); margin: 28px auto 0; color: #7a8594; font-size: 13px; text-align: center; }
@media (max-width: 1023px) {
  .auth-page { padding: 28px; }
  .auth-shell { grid-template-columns: minmax(0, 1fr) minmax(350px, .9fr); gap: 34px; }
  .station-visual { height: 330px; }
  .brand-copy h1 { font-size: 27px; }
}
@media (max-width: 899px) {
  .auth-page { padding: 24px 20px; }
  .auth-shell { grid-template-columns: 1fr; gap: 24px; align-items: start; }
  .brand-row { width: min(430px, 100%); margin: 0 auto; }
  .station-visual, .brand-copy { display: none; }
  .auth-pane { order: 2; }
  .auth-panel { box-shadow: 0 10px 28px rgba(24, 47, 71, .07); }
  footer { margin-top: 20px; }
}
@media (max-width: 480px) {
  .auth-page { padding: 18px 14px; }
  .auth-panel { padding: 26px 20px; border-radius: 10px; }
  .brand-logo { width: 34px; height: 38px; }
  .brand-row strong { font-size: 20px; }
}
@media (max-height: 760px) and (min-width: 900px) {
  .auth-page { padding-top: 24px; padding-bottom: 24px; }
  .station-visual { height: 300px; }
  .brand-copy { margin-top: 18px; }
  footer { margin-top: 18px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; }
}
</style>
