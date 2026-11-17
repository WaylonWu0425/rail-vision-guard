const EPSILON = 1e-9;

const cross = (a, b, p) => (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);

function onEdge(a, b, p) {
  return Math.abs(cross(a, b, p)) <= EPSILON
    && p.x >= Math.min(a.x, b.x) - EPSILON && p.x <= Math.max(a.x, b.x) + EPSILON
    && p.y >= Math.min(a.y, b.y) - EPSILON && p.y <= Math.max(a.y, b.y) + EPSILON;
}

function intersects(a, b, c, d) {
  if (onEdge(a, b, c) || onEdge(a, b, d) || onEdge(c, d, a) || onEdge(c, d, b)) return true;
  return cross(a, b, c) * cross(a, b, d) < 0 && cross(c, d, a) * cross(c, d, b) < 0;
}

export function regionError(points) {
  if (points.length < 3) return '至少添加 3 个顶点。';
  let signedArea = 0;
  for (const [i, a] of points.entries()) {
    const b = points[(i + 1) % points.length];
    signedArea += a.x * b.y - b.x * a.y;
    if (Math.hypot(a.x - b.x, a.y - b.y) < 0.001) return '相邻顶点过近，请调整区域。';
    for (let j = i + 2; j < points.length; j++) {
      if (i === 0 && j === points.length - 1) continue;
      const c = points[j], d = points[(j + 1) % points.length];
      if (intersects(a, b, c, d)) return '区域边界相交，请按边界顺序重新添加顶点。';
    }
  }
  return Math.abs(signedArea) < 0.00002 ? '区域面积过小，请调整顶点。' : '';
}

export function detectionInReviewRegion(box, width, height, points) {
  const point = { x: Math.floor((Math.trunc(box[0]) + Math.trunc(box[2])) / 2) / width, y: Math.trunc(box[3]) / height };
  let inside = false;
  const pixelPoints = points.map(p => ({ x: Math.round(p.x * width) / width, y: Math.round(p.y * height) / height }));
  for (const [i, a] of pixelPoints.entries()) {
    const b = pixelPoints[(i + 1) % pixelPoints.length];
    if (onEdge(a, b, point)) return true;
    if ((a.y > point.y) !== (b.y > point.y)
      && point.x < a.x + (b.x - a.x) * (point.y - a.y) / (b.y - a.y)) inside = !inside;
  }
  return inside;
}
