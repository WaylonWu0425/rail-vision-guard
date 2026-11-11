<template>
  <svg class="rail-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path :d="paths[name]"/>
  </svg>
</template>

<script setup>
defineProps({ name: { type: String, required: true } })
const paths = {
  overview: 'M3 5h18v13H3z M6 14l4-4 4 2 4-4 M9 21h6',
  preview: 'M3 6h18v12H3z M10 9l5 3-5 3z',
  recognition: 'M8 3H3v5 M16 3h5v5 M3 16v5h5 M21 16v5h-5 M9 9h6v6H9z',
  alert: 'M6 15V9a6 6 0 0 1 12 0v6l2 2H4z M10 21h4 M12 7v4 M12 14h.01',
  playback: 'M3 5h18v14H3z M10 9l5 3-5 3z M6 5v14 M18 5v14',
  camera: 'M3 6h16v9H3z M19 8l3-2v9l-3-2 M8 15v4h5 M7 10h4',
  track: 'M8 3v18 M16 3v18 M5 5h14 M5 10h14 M5 15h14 M5 20h14',
  platform: 'M3 16h18v4H3z M5 16V8h14v8 M3 8l3-4h12l3 4z M9 10v6 M15 10v6',
  review: 'M8 5H5v16h14V5h-3 M8 3h8v4H8z M8 14l3 3 5-6',
  statistics: 'M4 4v16h17 M8 16v-4 M13 16V8 M18 16V5',
  chat: 'M4 5h16v12H9l-5 4V5z M8 11h.01 M12 11h.01 M16 11h.01',
  users: 'M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2 M18 15a4 4 0 0 1 3 4v2 M9.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M17 3a4 4 0 0 1 0 8',
  more: 'M5 9l7 7 7-7',
}
</script>
