let loadingPromise = null

export function ensurePlayerControlLoaded() {
  if (typeof window.PlayerControl === 'function') return Promise.resolve()
  if (loadingPromise) return loadingPromise

  loadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `${process.env.BASE_URL || '/'}module/PlayerControl.js`
    script.async = true
    script.onload = () => {
      if (typeof window.PlayerControl === 'function') resolve()
      else {
        script.remove()
        reject(new Error('播放器脚本已加载，但未提供 PlayerControl'))
      }
    }
    script.onerror = () => {
      script.remove()
      reject(new Error('播放器脚本加载失败'))
    }
    document.head.appendChild(script)
  }).catch(error => {
    loadingPromise = null
    throw error
  })

  return loadingPromise
}
