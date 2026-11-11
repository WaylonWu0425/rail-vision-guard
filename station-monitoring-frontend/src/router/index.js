import {createRouter, createWebHistory} from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import HomePage from '@/views/HomePage.vue';
import MonitoringScreen from '@/views/MonitoringScreen.vue';
import CameraManagement from '@/views/CameraManagement.vue';
import Sidebar from '@/views/Sidebar.vue';
import Alarm from '@/views/Alarm.vue';
import AlarmRecord from '@/views/AlarmRecord.vue';
import Video from '@/views/video.vue';
import BallMachine from '@/views/BallMachine.vue';
import GunMachine from '@/views/GunMachine.vue'
import StockTrack from '@/views/StockTrack.vue'
import UserProfile from '@/views/UserProfile.vue';
import Switch from "@/views/Switch.vue";
import UserManagement from "@/views/UserManagement.vue";
import ImageDetection from '@/views/ImageDetection.vue';
import DataStatistics from '@/views/DataStatistics.vue';
import JobManagement from '@/views/JobManagement.vue';
import EmployeeTask from '@/views/EmployeeTask.vue';
import {useStore} from 'vuex';


const routes = [
    {
        path: '/',
        name: 'HomePage',
        component: HomePage,
        children: [
            //   实时预览
            {
                path: '/monitoringscreen',
                name: 'MonitoringScreen',
                component: MonitoringScreen
                // component: () => import('@/views/ruanzhu_test/MonitoringScreen01.vue')
            },
            {
                path: '/cameramanagement',
                name: 'CameraManagement',
                component: CameraManagement
            },
            {
                path: '/alarm',
                name: 'Alarm',
                component: Alarm
                // component: () => import('@/views/ruanzhu_test/Alarm01.vue')
            },
            {
                path: '/alarmrecord',
                name: 'AlarmRecord',
                component: AlarmRecord
            },
            {
                path: '/video',
                name: 'Video',
                component: Video
            },
            {
                path: '/imageDetection',
                name: 'ImageDetection',
                component: ImageDetection
            },
            {
                path: '/ballMachine',
                name: 'BallMachine',
                component: BallMachine
            },
            {
                path: '/gunMachine',
                name: 'GunMachine',
                component: GunMachine
            },
            {
                path: '/stockTrack',
                name: 'StockTrack',
                component: StockTrack
            },
            {
                path: '/userProfile',
                name: 'UserProfile',
                component: UserProfile
            },
            {
                path: '/switch',
                name: 'Switch',
                component: Switch
            },
            {
                path: '/userManagement',
                name: 'UserManagement',
                component: UserManagement,
            },
            {
                path: '/aiChat',
                name: 'AIChat',
                component: () => import('@/views/AIChat.vue')
            },
            {
                path: '/dataStatistics',
                name: 'DataStatistics',
                component: DataStatistics
                // component: () => import('@/views/ruanzhu_test/DataStatistics01.vue')
            },
            {
                path: '/jobManagement',
                name: 'JobManagement',
                component: JobManagement
            },
            //   我的任务
            {
                path: '/employeeTask',
                name: 'EmployeeTask',
                component: EmployeeTask
                // component: () => import('@/views/ruanzhu_test/EmployeeTask01.vue')
            }
        ],
        meta: {requiresAuth: true} // 需要登录
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
        // component: () => import('@/views/ruanzhu_test/Login01.vue')
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
        // component: () => import('@/views/ruanzhu_test/Register01.vue')
    },
    {
        path: '/sidebar',
        name: 'Sidebar',
        component: Sidebar,
        meta: {requiresAuth: true} // 需要登录
    },
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
});

//
// router.beforeEach((to, from, next) => {
//   const isLoggedIn = checkLoginStatus(); // 检查用户是否登录
//   if (to.meta.requiresAuth && !isLoggedIn) {
//     // 如果需要登录且未登录，跳转到登录页，并记录目标页面
//     next({ name: 'Login', query: { redirect: to.fullPath } });
//   } else {
//     // 否则继续导航
//     next();
//   }
// });
//
// // 模拟检查登录状态
// function checkLoginStatus() {
//   const store = useStore();
//   return store.getters['user/getLoginStatus'];         // 从 Vuex 中获取登录状态
// }
export default router;
