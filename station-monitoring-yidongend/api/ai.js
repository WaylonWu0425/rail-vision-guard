import request from '@/utils/request';

export async function aireport(data) {
  return request({
    url: '/ai',
    method: 'POST',
    data
  });
}

export async function askai(data) {
  return request({
    url: '/ai',
    method: 'GET',
    data,
	enableChunked:true
  });
}