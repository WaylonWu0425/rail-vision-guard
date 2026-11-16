export const SENSOR_HEADER = 'time_s,ax_m_s2,ay_m_s2,az_m_s2';
export const SENSOR_TOLERANCE_S = 0.25;

export function parseAcceleration(text) {
  const lines = text.replace(/^\uFEFF/, '').trim().split(/\r?\n/);
  if (lines.shift()?.trim() !== SENSOR_HEADER || !lines.length || lines.length > 250000) {
    throw new Error('使用规定的 CSV 表头，且提供 1 至 250000 条加速度记录。');
  }
  const result = [];
  for (const [index, line] of lines.entries()) {
    const columns = line.split(',').map(value => value.trim());
    const [time, x, y, z] = columns.map(Number);
    if (columns.length !== 4 || columns.some(value => value === '') ||
        ![time, x, y, z].every(Number.isFinite) || time < 0 ||
        (result.length && time <= result.at(-1).time)) {
      throw new Error(`第 ${index + 2} 行无效。使用有限数值和严格递增的非负时间。`);
    }
    const magnitude = Math.hypot(x, y, z);
    if (!Number.isFinite(magnitude)) throw new Error(`第 ${index + 2} 行加速度超出数值范围。`);
    result.push({ time, x, y, z, magnitude });
  }
  return result;
}

export function createAlignment(track, sourceRange, videoDuration) {
  if (!track.file || !sourceRange || !videoDuration) return null;
  if (!track.position.trim() || !track.reference.trim() || !track.sameOperation) {
    return { error: '请填写采集位置和同步依据，并确认来自同一次作业。' };
  }
  const pairs = [track.first];
  if (track.useSecond) pairs.push(track.second);
  for (const { video, source } of pairs) {
    if (!Number.isFinite(video) || video < 0 || video > videoDuration ||
        !Number.isFinite(source) || source < sourceRange[0] || source > sourceRange[1]) {
      return { error: '同步点须落在各自的媒体或记录时间范围内。' };
    }
  }
  const [first, second] = pairs;
  if (second && (second.source <= first.source || second.video <= first.video)) {
    return { error: '第二同步点必须在两个时间轴上均晚于第一点。' };
  }
  const rate = second ? (second.video - first.video) / (second.source - first.source) : 1;
  if (!Number.isFinite(rate) || rate <= 0) return { error: '同步点间隔无效。' };
  return {
    pairs: pairs.map(pair => ({ ...pair })),
    rate,
    offset: first.video - rate * first.source,
    sourceRange: second ? [first.source, second.source] : [...sourceRange],
    method: second ? 'two_anchors' : 'one_anchor',
    position: track.position.trim(),
    reference: track.reference.trim(),
  };
}

export function alignedTime(videoTime, alignment) {
  if (!alignment || alignment.error || !Number.isFinite(videoTime)) return null;
  const time = (videoTime - alignment.offset) / alignment.rate;
  const [start, end] = alignment.sourceRange;
  if (!Number.isFinite(time) || time < start - 1e-8 || time > end + 1e-8) return null;
  return Math.min(end, Math.max(start, time));
}

export function accelerationAt(samples, sourceTime, alignment) {
  const [start, end] = alignment.sourceRange;
  let low = 0, high = samples.length;
  while (low < high) {
    const middle = Math.floor((low + high) / 2);
    if (samples[middle].time < sourceTime) low = middle + 1;
    else high = middle;
  }
  const candidates = [samples[low - 1], samples[low]].filter(sample => sample && sample.time >= start && sample.time <= end);
  const nearest = candidates.reduce((current, item) => (
    !current || Math.abs(item.time - sourceTime) < Math.abs(current.time - sourceTime) ? item : current
  ), null);
  if (!nearest) return null;
  const videoDelta = (nearest.time - sourceTime) * alignment.rate;
  return Math.abs(videoDelta) <= SENSOR_TOLERANCE_S ? { ...nearest, videoDelta } : null;
}

export function sourceIdentity(file) {
  return file ? { name: file.name, size: file.size, lastModified: file.lastModified } : null;
}
