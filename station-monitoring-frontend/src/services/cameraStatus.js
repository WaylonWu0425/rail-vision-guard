/**
 * 摄像头状态 WebSocket 的页面级共享客户端。
 *
 * 同一浏览器标签页只建立一条状态连接；页面离开时取消订阅，最后一个订阅者
 * 退出后才断开。服务重启或网络恢复后会自动重连，并要求页面重新读取快照，
 * 避免只依赖可能丢失的增量状态消息。
 */
const listeners = new Map();

let socket = null;
let reconnectTimer = null;
let reconnectAttempt = 0;
let sequence = 0;

const BACKOFF_DELAYS = [1000, 2000, 4000, 8000, 10000];

const wsUrl = () => {
  const configured = process.env.VUE_APP_CAMERA_STATUS_WS_URL;
  if (configured) return configured;

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/ws/cameraStatus`;
};

const broadcast = (type, payload = {}) => {
  listeners.forEach((listener) => {
    try {
      listener({type, ...payload});
    } catch (error) {
      console.error('摄像头状态订阅回调失败:', error);
    }
  });
};

const clearReconnectTimer = () => {
  if (reconnectTimer) {
    window.clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
};

const scheduleReconnect = () => {
  if (!listeners.size || reconnectTimer) return;
  const baseDelay = BACKOFF_DELAYS[Math.min(reconnectAttempt, BACKOFF_DELAYS.length - 1)];
  const delay = baseDelay + Math.round(Math.random() * 300);
  reconnectAttempt += 1;
  broadcast('reconnecting', {delay});
  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, delay);
};

const connect = () => {
  if (!listeners.size || (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING))) {
    return;
  }

  try {
    socket = new WebSocket(wsUrl());
  } catch (error) {
    broadcast('error', {message: '无法创建摄像头状态连接'});
    scheduleReconnect();
    return;
  }

  socket.onopen = () => {
    reconnectAttempt = 0;
    broadcast('connected');
  };

  socket.onmessage = (event) => {
    try {
      const raw = JSON.parse(event.data);
      const updates = (Array.isArray(raw) ? raw : [raw]).filter(item => item && item.id != null);
      if (updates.length) broadcast('update', {updates});
    } catch (error) {
      console.warn('摄像头状态消息格式错误:', error);
    }
  };

  socket.onerror = () => {
    broadcast('error', {message: '摄像头状态连接异常，正在重试'});
  };

  socket.onclose = () => {
    socket = null;
    if (listeners.size) {
      broadcast('disconnected');
      scheduleReconnect();
    }
  };
};

export const subscribeCameraStatus = (listener) => {
  const id = ++sequence;
  listeners.set(id, listener);
  listener({type: socket?.readyState === WebSocket.OPEN ? 'connected' : 'connecting'});
  connect();

  return () => {
    listeners.delete(id);
    if (listeners.size) return;
    clearReconnectTimer();
    if (socket) {
      const current = socket;
      socket = null;
      current.close();
    }
  };
};

export const reconnectCameraStatus = () => {
  clearReconnectTimer();
  if (socket) {
    const current = socket;
    socket = null;
    current.close();
  }
  reconnectAttempt = 0;
  connect();
};
