// api/login.js
import request from '@/utils/request';

/**
 * 登录
 * @param {Object} data - 登录数据，包含email和password
 * @returns {Promise}
 */
export async function login(data) {
  return request({
    url: '/users/tokens',
    method: 'POST',
    data
  });
}

/**
 * 注册
 * @param {Object} data - 注册数据，包含email和password
 * @returns {Promise}
 */
export async function register(data) {
  return request({
    url: '/users',
    method: 'POST',
    data
  });
}

/**
 * 发送验证码
 * @param {Object} data - 验证码数据
 * @returns {Promise}
 */
export async function verifyCode(data) {
  return request({
    url: '/users/verifyCode',
    method: 'POST',
    data,
    timeout: 60000
  });
}

/**
 * 验证验证码
 * @param {Object} data - 验证码校验数据
 * @returns {Promise}
 */
export async function verifyCodeID(data) {
  return request({
    url: '/users/verifyCode/check',
    method: 'POST',
    data
  });
}
