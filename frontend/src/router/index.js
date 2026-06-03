import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import System from '@/views/System.vue'
import Help from '@/views/core/HelpView.vue'

const routes = [
    {
        path: '/',
        name: 'login',
        redirect: '/login'

    },
    {
        path: '/login',
        component: Login
    },
    {
        path: '/register',
        component: Register
    },
    {
        path: '/system',
        name: 'System',
        component: System,
        redirect: '/system/first',
        children: [
            {
                path: 'first',
                name: 'First',
                component: () => import('@/views/core/FirstView.vue')
            },
            {
                path: 'market',
                name: 'Market',
                component: () => import('@/views/core/MarketView.vue'),
                meta: { title: '市场车型' }
            },
            {
                path: 'favorites',
                name: 'Favorites',
                component: () => import('@/views/core/FavoritesView.vue'),
                meta: { title: '我的收藏' }
            },
            {
                path: 'predict',
                name: 'Predict',
                component: () => import('@/views/core/PredictView.vue'),
                meta: { title: '价格预测' }
            },
            {
                path: 'analysis',
                name: 'Analysis',
                component: () => import('@/views/core/AnalysisView.vue'),
                meta: { title: '市场分析' }
            },
            {
                path: 'history',
                name: 'History',
                component: () => import('@/views/core/HistoryView.vue'),
                meta: { title: '历史记录' }
            },
            {
                path: 'help',
                name: 'Help',
                component: Help,
                meta: { title: '帮助中心' }
            },
            {
                path: 'profile',
                name: 'Profile',
                component: () => import('@/views/user/ProfileView.vue'),
                meta: { title: '个人中心' }
            },
            {
                path: 'settings',
                name: 'Settings',
                component: () => import('@/views/user/SettingsView.vue'),
                meta: { title: '账户设置' }
            },
            {
                path: 'admin',
                name: 'Admin',
                component: () => import('@/views/admin/AdminView.vue'),
                meta: { title: '数据管理' }
            },
            {
                path: 'user-admin',
                name: 'UserAdmin',
                component: () => import('@/views/admin/UserManageView.vue'),
                meta: { title: '用户管理' }
            },
            {
                path: 'model-admin',
                name: 'ModelAdmin',
                component: () => import('@/views/admin/ModelAdminView.vue'),
                meta: { title: '模型管理' }
            }
        ]
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/error/NotFound.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const isAuthenticated = localStorage.getItem('authToken') !== null

    if (to.meta.requiresAuth && !isAuthenticated) {
        next({ name: 'Login' })
    } else {
        next()
    }
})


export default router
