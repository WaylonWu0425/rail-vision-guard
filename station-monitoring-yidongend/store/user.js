// store/user.js
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
    state: () => ({
        userInfo: {},
        isLogIn: false
    }),
    getters: {
        getUserInfo: (state) => state.userInfo,
        getLoginStatus: (state) => state.isLogIn,
        getUserRole: (state) => state.userInfo.role || '0'
    },
    actions: {
        login(user) {
            this.isLogIn = true;
            this.userInfo = user;
        },
        logout() {
            this.isLogIn = false;
            this.userInfo = {};
            uni.removeStorageSync('token');
            uni.removeStorageSync('userInfo');
        },
        changeAvatar(avatarUrl) {
            this.userInfo.avatar = avatarUrl;
        },
        updateUserInfo(userInfo) {
            this.userInfo = userInfo;
        }
    }
});