export const railStatusLabels = {
  online: '在线',
  offline: '离线',
  unknown: '未知',
  pending: '待核查',
  done: '已处理',
}

export function cameraRailState(status) {
  return ({ '0': 'online', '1': 'offline' })[String(status)] || 'unknown'
}

export function alarmRailState(flag) {
  if (flag === true || flag === 1 || flag === '1') return 'done'
  if (flag === false || flag === 0 || flag === '0') return 'pending'
  return 'unknown'
}

export function cameraDisplayName(camera) {
  return camera.name || '摄像头 ' + camera.id
}

export function cameraNameForEvent(event, cameras) {
  const camera = event.cameraId == null ? null : cameras.find(item => String(item.id) === String(event.cameraId))
  return camera ? cameraDisplayName(camera) : event.cameraName || '来源未记录'
}
