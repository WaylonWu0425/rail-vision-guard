const labels = {
  person: '人员',
  car: '汽车',
  obstacle: '障碍物',
  rail: '轨道',
  'signal-and-sign': '信号与标志',
  vehicle: '车辆',
};

export function detectionLabel(key) {
  return labels[key] ?? key;
}
