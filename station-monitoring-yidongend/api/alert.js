import request from '@/utils/request';
export function getalert(data) {
  return request({
    url: '/warningConfigs',
    method: 'GET',
	data
  });
}

export function setalert(data) {
  return request({
    url: '/warningConfigs',
    method: 'PATCH',
	data
  });
}