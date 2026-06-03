// src/stores/user.js
import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const useUserStore = defineStore('user', {
    state: () => ({
        token: localStorage.getItem('authToken') || null,
        user: JSON.parse(localStorage.getItem('userInfo')) || null,
        isAuthenticated: !!localStorage.getItem('authToken'),
    }),

    getters: {
        avatarUrl: (state) => {
            if (!state.user?.avatar) return null
            return state.user.avatar.startsWith('http') 
                ? state.user.avatar 
                : `${API_BASE_URL}${state.user.avatar}`
        }
    },

    actions: {
        setToken(token) {
            this.token = token
            this.isAuthenticated = true
            localStorage.setItem('authToken', token)
            axios.defaults.headers.common['Authorization'] = `Token ${token}`
        },

        setUser(user) {
            this.user = user
            localStorage.setItem('userInfo', JSON.stringify(user))
        },

        async fetchCurrentUser() {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/current-user/`)
                this.setUser(response.data)
            } catch (error) {
                console.error('获取用户信息失败:', error)
            }
        },

        logout() {
            this.token = null
            this.user = null
            this.isAuthenticated = false
            localStorage.removeItem('authToken')
            localStorage.removeItem('userInfo')
            delete axios.defaults.headers.common['Authorization']
        }
    }
})