// request.js
// const BASE_URL = 'https://5723aw779ac3.vicp.fun';
const BASE_URL = 'http://localhost:6169';
// const BASE_URL = 'http://1.95.153.56:6169';

const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token');

    console.log('【token】', token)
    console.log('请求URL:', options.url);

    if (token) {
      options.header = options.header || {};
      options.header.auth = token;

      console.log('设置请求头:', options.header);
    }else{
      console.log('未设置请求头:', options.header);
    }
    options.url = BASE_URL + options.url;

    uni.request({
      ...options,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          // Token过期或未授权
          uni.showToast({
            title: '未授权，请登录',
            icon: 'none'
          });
          // 重定向到登录页
          uni.reLaunch({
            url: '/pages/login/login' // 这里需要根据你的实际登录页路径修改
          });
          reject(res);
        }  else {
          reject(res);
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};

export default request;
