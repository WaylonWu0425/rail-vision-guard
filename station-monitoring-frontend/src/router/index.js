import {createRouter, createWebHistory} from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import store from '@/store';


const routes = [
    {
        path: '/',
        name: 'HomePage',
        component: () => import('@/views/HomePage.vue'),
        children: [
            //   实时预览
            {
                path: '/monitoringscreen',
                name: 'MonitoringScreen',
                component: () => import('@/views/MonitoringScreen.vue')
                // component: () => import('@/views/ruanzhu_test/MonitoringScreen01.vue')
            },
            {
                path: '/cameramanagement',
                name: 'CameraManagement',
                component: () => import('@/views/CameraManagement.vue')
            },
            {
                path: '/alarm',
                name: 'Alarm',
                component: () => import('@/views/Alarm.vue')
                // component: () => import('@/views/ruanzhu_test/Alarm01.vue')
            },
            {
                path: '/alarmrecord',
                name: 'AlarmRecord',
                component: () => import('@/views/AlarmRecord.vue')
            },
            {
                path: '/video',
                name: 'Video',
                component: () => import('@/views/video.vue')
            },
            {
                path: '/imageDetection',
                redirect: '/originalRecognition'
            },
            {
                path: '/originalRecognition',
                name: 'OriginalRecognition',
                component: () => import('@/views/OriginalRecognition.vue')
            },
            {
                path: '/couplingSensing',
                name: 'CouplingSensing',
                component: () => import('@/views/CouplingSensing.vue')
            },
            {
                path: '/ballMachine',
                name: 'BallMachine',
                component: () => import('@/views/BallMachine.vue')
            },
            {
                path: '/gunMachine',
                name: 'GunMachine',
                component: () => import('@/views/GunMachine.vue')
            },
            {
                path: '/stockTrack',
                name: 'StockTrack',
                component: () => import('@/views/StockTrack.vue')
            },
            {
                path: '/userProfile',
                name: 'UserProfile',
                component: () => import('@/views/UserProfile.vue')
            },
            {
                path: '/switch',
                name: 'Switch',
                component: () => import('@/views/Switch.vue')
            },
            {
                path: '/userManagement',
                name: 'UserManagement',
                component: () => import('@/views/UserManagement.vue'),
            },
            {
                path: '/aiChat',
                name: 'AIChat',
                component: () => import('@/views/AIChat.vue')
            },
            {
                path: '/dataStatistics',
                name: 'DataStatistics',
                component: () => import('@/views/DataStatistics.vue')
                // component: () => import('@/views/ruanzhu_test/DataStatistics01.vue')
            },
            {
                path: '/jobManagement',
                name: 'JobManagement',
                component: () => import('@/views/JobManagement.vue')
            },
            //   我的任务
            {
                path: '/employeeTask',
                name: 'EmployeeTask',
                component: () => import('@/views/EmployeeTask.vue')
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
        component: () => import('@/views/Sidebar.vue'),
        meta: {requiresAuth: true} // 需要登录
    },
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
});

router.beforeEach((to) => {
    if (to.matched.some(record => record.meta.requiresAuth)
        && !store.getters['user/getLoginStatus']) {
        return { name: 'Login', query: { redirect: to.fullPath } };
    }
    return true;
});
export default router;
