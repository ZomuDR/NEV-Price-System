<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import {useUserStore} from "../../stores/user"

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const password = ref('')
const loginType = ref('user')
const errorType = ref(null)
const remainingAttempts = ref(5)

const handleLogin = async () => {
  try {
    const response = await axios.post(`${API_BASE}/api/login/`, {
      username: username.value,
      password: password.value
    })

    const userData = response.data.user
    localStorage.setItem('authToken', response.data.token)
    localStorage.setItem('loginType', loginType.value)

    userStore.setUser(userData)
    userStore.setToken(response.data.token)

    const token = response.data.token
    const profileRes = await axios.get(`${API_BASE}/api/profile/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
    userStore.setUser(profileRes.data)

    if (loginType.value === 'admin') {
      if (!userData.is_admin) {
        errorType.value = 'not_admin'
        return
      }
      router.push('/system/admin')
    } else {
      router.push('/system/first')
    }
  } catch (error) {
    if (error.response?.data?.code === 'user_not_found') {
      errorType.value = 'user_not_found'
      remainingAttempts.value = null
    } else {
      errorType.value = 'invalid_credentials'
      remainingAttempts.value -= 1
    }
  }
}

</script>

<template>
  <div class="login-container">
    <div class="energy-header">
      <div class="circuit-line"></div>
      <h1>NeoPrice X<span>价格预测系统</span></h1>
    </div>

    <form @submit.prevent="handleLogin" class="login-form">
      <div class="login-type-selector">
        <button 
          type="button"
          class="type-btn" 
          :class="{ active: loginType === 'user' }"
          @click="loginType = 'user'"
        >
          用户登录
        </button>
        <button 
          type="button"
          class="type-btn" 
          :class="{ active: loginType === 'admin' }"
          @click="loginType = 'admin'"
        >
          管理员登录
        </button>
      </div>

      <div class="form-group">
        <input
            v-model="username"
            type="text"
            :placeholder="loginType === 'admin' ? '请输入管理员用户名' : '请输入用户名'"
            required
            class="energy-input"
        >
        <svg class="input-icon" viewBox="0 0 24 24">
          <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
        </svg>
      </div>

      <div class="form-group">
        <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
            class="energy-input"
        >
        <svg class="input-icon" viewBox="0 0 24 24">
          <path d="M12,17C10.89,17 10,16.1 10,15C10,13.89 10.89,13 12,13A2,2 0 0,1 14,15A2,2 0 0,1 12,17M18,20V10H6V20H18M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V10C4,8.89 4.89,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
        </svg>
      </div>

      <transition name="slide-fade">
        <div v-if="errorType" class="error-box">
          <template v-if="errorType === 'user_not_found'">
            ❗ 用户不存在，请创建一个新用户
          </template>
          <template v-else-if="errorType === 'not_admin'">
            ⚠️ 该账号不是管理员账号
          </template>
          <template v-else>
            🔒 用户名或密码错误（剩余尝试次数：{{ remainingAttempts }}）
          </template>
        </div>
      </transition>

      <button type="submit" class="energy-button">
        <div class="button-hover"></div>
        登录
      </button>

      <p class="register-link">
        新用户？<a @click="router.push('/register')">创建账户</a>
      </p>
    </form>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  background: linear-gradient(135deg, #1a2f3b 0%, #2c5364 50%, #1a2f3b 100%);
  min-height: 100vh;
  width: 100%;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(0, 255, 136, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(125, 253, 217, 0.06) 0%, transparent 50%);
  pointer-events: none;
}

.energy-header {
  text-align: center;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.circuit-line {
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00c853, transparent);
  animation: circuit-pulse 2s ease-in-out infinite;
}

@keyframes circuit-pulse {
  0%, 100% { opacity: 0.3; transform: scaleX(0.8); }
  50% { opacity: 1; transform: scaleX(1); }
}

.energy-header h1 {
  font-size: 2.5rem;
  color: #00c853;
  text-shadow: 0 0 20px rgba(0, 200, 83, 0.5);
  position: relative;
  z-index: 1;
}

.energy-header h1 span {
  font-size: 1.2rem;
  color: #7dfdd9;
  margin-left: 0.5rem;
}

.login-form {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 200, 83, 0.2);
  border-radius: 16px;
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 1;
}

.login-type-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 4px;
}

.type-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #aaa;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-btn.active {
  background: #00c853;
  color: #fff;
  box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4);
}

.type-btn:hover:not(.active) {
  color: #fff;
}

.form-group {
  position: relative;
  margin-bottom: 1.25rem;
}

.energy-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 200, 83, 0.3);
  border-radius: 8px;
  color: #fff;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.energy-input:focus {
  outline: none;
  border-color: #00c853;
  box-shadow: 0 0 15px rgba(0, 200, 83, 0.3);
}

.energy-input::placeholder {
  color: #666;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  fill: #00c853;
}

.error-box {
  background: rgba(255, 82, 82, 0.1);
  border: 1px solid rgba(255, 82, 82, 0.3);
  border-radius: 8px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  color: #ff5252;
  font-size: 0.9rem;
  text-align: center;
}

.energy-button {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #00c853, #00e676);
  color: #fff;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.energy-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 200, 83, 0.5);
}

.button-hover {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.energy-button:hover .button-hover {
  left: 100%;
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
  color: #888;
}

.register-link a {
  color: #00c853;
  text-decoration: none;
  cursor: pointer;
}

.register-link a:hover {
  text-decoration: underline;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

@media (max-width: 480px) {
  .energy-header h1 {
    font-size: 1.8rem;
  }
  
  .energy-header h1 span {
    display: block;
    font-size: 1rem;
    margin-left: 0;
    margin-top: 0.5rem;
  }
  
  .login-form {
    padding: 1.5rem;
  }
}
</style>