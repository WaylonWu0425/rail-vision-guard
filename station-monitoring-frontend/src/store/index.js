import { createStore } from 'vuex'
import user from "./user.js"
import job from "./modules/job.js"
import createPersistedState from 'vuex-persistedstate';

export default createStore({
   modules:{
      user:user,
      job:job,
   },
   plugins: [
      // 使用 vuex-persistedstate 插件
      createPersistedState({
         key: 'vuex-state', // 存储的 key 值
         paths: ['user.userInfo', 'user.isLogIn', 'job.tasks'], // 需要持久化的状态
      })
   ]
})
