export default {
  namespaced:true,
  state:{
    userInfo:{},
    isLogIn: false,
  },
  getters:{
    getUserInfo: (state) => state.userInfo,
    getLoginStatus: (state) => state.isLogIn,
    getUserRole: (state) => state.userInfo.role || '0' // 获取用户角色，默认为0(操作员)
  },
  mutations:{
    setUser:(state,user)=>{
        state.userInfo = user
    },
    setLoginStatus:(state, flag)=>{
        state.isLogIn = flag
    },
    updateAvatar: (state, avatarUrl) => {
      state.userInfo.avatar= avatarUrl ; // 保持响应式
    },
  },
  actions:{
    login({ commit }, user) {
      commit('setLoginStatus', true);
      commit('setUser', user); // 存储用户信息
    },
    logout({ commit }) {
      commit('setLoginStatus', false);
      commit('setUser', {}); // 清除用户信息
    },
    changeAvatar({ commit }, avatarUrl) {
      commit('updateAvatar', avatarUrl);
    },
    updateUserInfo({commit}, userInfo) {
      commit('setUser', userInfo);
    }
  }
};