// main.js
import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'


axios.defaults.baseURL = ''
axios.defaults.headers.common['Content-Type'] = 'application/json'

axios.interceptors.request.use(config => {
    const token = localStorage.getItem('authToken')
    if (token) {
        config.headers.Authorization = `Token ${token}`
    }
    return config
})

const app = createApp(App)

app.use(router)
app.use(createPinia())
app.use(ElementPlus)
app.mount('#app')