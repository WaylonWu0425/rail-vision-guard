import request from '@/utils/request';

//获取用户信息
export function getUser() {
    return request({
        url: '/users',
        method: 'GET',
    });
}

// 更新用户信息
export function updataUser(data) {
    return request({
        url: '/users/update',
        method: 'PATCH',
        data
    });
}

//更新密码
export function updatePassword(data) {
    return request({
        url: '/users/updatePassword',
        method: 'PUT',
        data
    })
}

//注销账号
export function deleteUser() {
    return request({
        url: '/users',
        method: 'DELETE',
    });
}