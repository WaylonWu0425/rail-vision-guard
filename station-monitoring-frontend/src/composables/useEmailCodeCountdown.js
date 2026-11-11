import { computed, onBeforeUnmount, ref } from 'vue'

export const useEmailCodeCountdown = (duration = 60) => {
  const remainingSeconds = ref(0)
  let timer = null

  const codeButtonText = computed(() => remainingSeconds.value > 0
    ? `${remainingSeconds.value} 秒后重发`
    : '获取验证码')

  const startCountdown = () => {
    if (timer) window.clearInterval(timer)
    remainingSeconds.value = duration
    timer = window.setInterval(() => {
      remainingSeconds.value -= 1
      if (remainingSeconds.value <= 0) {
        window.clearInterval(timer)
        timer = null
      }
    }, 1000)
  }

  onBeforeUnmount(() => {
    if (timer) window.clearInterval(timer)
  })

  return { remainingSeconds, codeButtonText, startCountdown }
}
