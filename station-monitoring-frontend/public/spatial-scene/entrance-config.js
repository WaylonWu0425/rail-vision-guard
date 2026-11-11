export const entranceTiming = Object.freeze({
  total: 1350,
  brand: 160,
  data: 220,
  readout: 180,
  recover: 90,
  anchorFade: 150,
  labelFade: 180,
  frameDelay: 150,
  frame: 300,
  resourceDelay: 550,
  evidenceDelay: 680,
  side: 280,
  focusDelay: 1120,
  focus: 230,
  modelDelay: 120,
  model: 700,
  camera: 750,
  anchors: 850,
  labels: 980,
  sceneTotal: 1250,
  easing: 'cubic-bezier(.22,.7,.3,1)',
})
export const entranceVariables = Object.fromEntries(
  Object.entries(entranceTiming).map(([key,value]) => ['--entrance-' + key, typeof value === 'number' ? value + 'ms' : value])
)
export const entranceSessionKey = 'rail-overview-entrance-v1'
export const sceneSessionKey = 'rail-overview-view-v1'
