import { ref, onUnmounted, watch } from 'vue'
import { entranceTiming, entranceVariables, entranceSessionKey } from '../../public/spatial-scene/entrance-config'

export function useOverviewEntrance(route) {
  const phase = ref('idle')
  const mode = ref('restore')
  const focusConfirmed = ref(false)
  const attentionReady = ref(false)
  const interrupted = ref(false)
  const media = window.matchMedia('(prefers-reduced-motion: reduce)')
  let timer, focusTimer
  function finish() {
    clearTimeout(timer)
    clearTimeout(focusTimer)
    attentionReady.value = false
    if (phase.value === 'running') phase.value = 'complete'
  }
  function interrupt() { interrupted.value = true; finish() }
  function enter() {
    interrupted.value = false
    finish()
    let seen = false
    try {
      seen = sessionStorage.getItem(entranceSessionKey) === '1'
      sessionStorage.setItem(entranceSessionKey, '1')
    } catch {
      seen = focusConfirmed.value
    }
    mode.value = seen || media.matches ? 'restore' : 'full'
    phase.value = mode.value === 'full' ? 'running' : 'complete'
    focusConfirmed.value = seen || media.matches
    if (phase.value === 'running') {
      focusTimer = window.setTimeout(() => { attentionReady.value = true }, entranceTiming.focusDelay)
      timer = window.setTimeout(finish, entranceTiming.total)
    }
  }
  watch(() => route.path, (path, previous) => {
    if (path === '/' && previous !== '/') enter()
    else if (path !== '/') finish()
  }, { immediate: true })
  const reduce = () => { if (media.matches) finish() }
  media.addEventListener('change', reduce)
  onUnmounted(() => { finish(); media.removeEventListener('change', reduce) })
  return { phase, mode, focusConfirmed, attentionReady, variables: entranceVariables, finish, interrupt, interrupted }
}
