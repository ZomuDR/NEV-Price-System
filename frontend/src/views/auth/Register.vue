<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

const router = useRouter()
const formData = ref({
  username: '',
  password: '',
  email: '',
  phone: '',
  address: ''
})
const errors = ref({
  username: '',
  email: '',
  phone: '',
  password:''
})

const handleRegister = async () => {
  // 重置错误信息
  errors.value = { username: '', email: '', phone: '',password:''}

  try {
    const response = await axios.post(`${API_BASE}/api/register/`, formData.value)
    if (response.status === 201) {
      alert('注册成功！')
      router.push('/login')
    }
  } catch (error) {
    console.error('完整错误信息:', error.response)
    if (error.response?.data?.errors) {
      // 结构化错误处理
      const backendErrors = error.response.data.errors
      errors.value = {
        username: backendErrors.username || '',
        email: backendErrors.email || '',
        phone: backendErrors.phone || '',
        password: backendErrors.password || ''
      }
    } else {
      alert('注册失败，请检查网络连接')
    }
  }
}
</script>

<template>
  <div class="register-container">
    <div class="energy-header">
      <div class="circuit-line"></div>
      <h1>加入NeoPrice X<span>注册页面</span></h1>
    </div>

    <form @submit.prevent="handleRegister" class="register-form">
      <!-- 用户名 -->
      <div class="form-group">
        <input
            v-model="formData.username"
            type="text"
            placeholder=" "
            class="energy-input"
            :class="{ 'input-error': errors.username }"
        >
        <label>用户名</label>
        <svg class="input-icon" viewBox="0 0 24 24">
          <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
        </svg>
        <transition name="slide-fade">
          <span v-if="errors.username" class="error-tip">{{ errors.username }}</span>
        </transition>
      </div>

      <!-- 密码 -->
      <div class="form-group">
        <input
            v-model="formData.password"
            type="password"
            placeholder=" "
            class="energy-input"
            :class="{ 'input-error': errors.password }"
        >
        <label>密码</label>
        <svg class="input-icon" viewBox="0 0 24 24">
          <path d="M12,17C10.89,17 10,16.1 10,15C10,13.89 10.89,13 12,13A2,2 0 0,1 14,15A2,2 0 0,1 12,17M18,20V10H6V20H18M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V10C4,8.89 4.89,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
        </svg>
        <transition name="slide-fade">
          <span v-if="errors.password" class="error-tip">{{ errors.password}}</span>
        </transition>
      </div>

      <!-- 邮箱 -->
      <div class="form-group">
        <input
            v-model="formData.email"
            type="email"
            placeholder=" "
            class="energy-input"
            :class="{ 'input-error': errors.email }"
        >
        <label>电子邮箱</label>
        <svg class="input-icon" viewBox="0 0 24 24">
          <path d="M20,8L12,13L4,8V6L12,11L20,6M20,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V6C22,4.89 21.1,4 20,4Z"/>
        </svg>
        <transition name="slide-fade">
          <span v-if="errors.email" class="error-tip">{{ errors.email }}</span>
        </transition>
      </div>

      <!-- 手机号 -->
      <div class="form-group">
        <input
            v-model="formData.phone"
            type="tel"
            placeholder=" "
            class="energy-input"
            :class="{ 'input-error': errors.phone }"
        >
        <label>手机号码</label>
        <svg class="input-icon" viewBox="0 0 24 24">
          <path d="M6.62,10.79C8.06,13.62 10.38,15.94 13.21,17.38L15.41,15.18C15.69,14.9 16.08,14.82 16.43,14.93C17.55,15.3 18.75,15.5 20,15.5A1,1 0 0,1 21,16.5V20A1,1 0 0,1 20,21A17,17 0 0,1 3,4A1,1 0 0,1 4,3H7.5A1,1 0 0,1 8.5,4C8.5,5.25 8.7,6.45 9.07,7.57C9.18,7.92 9.1,8.31 8.82,8.59L6.62,10.79Z"/>
        </svg>
        <transition name="slide-fade">
          <span v-if="errors.phone" class="error-tip">{{ errors.phone }}</span>
        </transition>
      </div>

      <!-- 地址 -->
      <div class="form-group">
        <textarea
            v-model="formData.address"
            placeholder=" "
            class="energy-input address-input"
        ></textarea>
        <label>联系地址</label>
        <svg class="input-icon" viewBox="0 0 24 24">
          <path d="M12,6.5A2.5,2.5 0 0,1 14.5,9A2.5,2.5 0 0,1 12,11.5A2.5,2.5 0 0,1 9.5,9A2.5,2.5 0 0,1 12,6.5M12,2A7,7 0 0,1 19,9C19,14.25 12,22 12,22C12,22 5,14.25 5,9A7,7 0 0,1 12,2M12,4A5,5 0 0,0 7,9C7,10 7,12 12,18.71C17,12 17,10 17,9A5,5 0 0,0 12,4Z"/>
        </svg>
      </div>

      <button type="submit" class="energy-button">
        <div class="button-wave"></div>
        立即注册
      </button>

      <p class="login-link">
        已有账号？<a @click="router.push('/login')">立即登录</a>
      </p>
    </form>
  </div>
</template>

<style scoped>
body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}
.register-container {
  background: linear-gradient(135deg, #1a2f3b 0%, #2c5364 100%);
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 0;
}
.energy-header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  overflow: hidden;
  width: 100%;
  padding: 0 2rem;
}
.energy-header h1 {
  color: #00ff88;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
}
.energy-header span {
  display: block;
  font-size: 1.2rem;
  color: #7dfdd9;
  margin-top: 0.5rem;
}
.circuit-line {
  position: absolute;
  width: 300%;
  height: 3px;
  background: linear-gradient(90deg, transparent 25%, #00ff88 50%, transparent 75%);
  animation: circuitFlow 4s infinite linear;
  top: 1rem;
  filter: drop-shadow(0 0 5px #00ff88);
}
@keyframes circuitFlow {
  0% { transform: translateX(-66%); }
  100% { transform: translateX(66%); }
}

.register-form {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  padding: 2.5rem;
  border-radius: 20px;
  width: calc(100% - 4rem);
  max-width: 500px;
  box-shadow: 0 0 40px rgba(0, 255, 136, 0.1);
}

.form-group {
  position: relative;
  margin-bottom: 2rem;
}

.energy-input {
  width: 86%;
  padding: 1.2rem 1rem 1rem 3rem;
  background: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(0, 255, 136, 0.3);
  border-radius: 10px;
  color: #fff;
  font-size: 1rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

.address-input {
  height: 100px;
  resize: vertical;
  padding: 1rem 1rem 1rem 3rem;
}

.energy-input:focus {
  outline: none;
  border-color: #00ff88;
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  fill: rgba(0, 255, 136, 0.6);
}

.energy-input + label {
  position: absolute;
  left: 3rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(0, 255, 136, 0.6);
  transition: all 0.3s ease;
  pointer-events: none;
  background: rgba(26, 47, 59, 0.8);
  padding: 0 0.3rem;
}

.energy-input:focus + label,
.energy-input:not(:placeholder-shown) + label {
  top: -0.6rem;
  font-size: 0.8rem;
  color: #00ff88;
  background: #1a2f3b;
}

.energy-button {
  position: relative;
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #00ff88 0%, #7dfdd9 100%);
  border: none;
  border-radius: 10px;
  color: #1a2f3b;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  margin-top: 2rem;
}

.button-wave {
  position: absolute;
  background: rgba(255, 255, 255, 0.2);
  width: 50px;
  height: 100%;
  left: -60px;
  top: 0;
  transform: skewX(-30deg);
  transition: all 0.4s ease;
}

@keyframes wave {
  to {
    transform: scale(2);
    opacity: 0;
  }
}

.energy-button:active .button-wave {
  animation: wave 0.6s ease-out;
}

.input-error {
  border-color: #ff3c3c !important;
  animation: shake 0.4s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.error-tip {
  display: block;
  color: #ff5e5e;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  text-shadow: 0 0 8px rgba(255, 94, 94, 0.3);
}

.login-link {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 2rem;
}

.login-link a {
  color: #7dfdd9;
  text-decoration: none;
  position: relative;
  cursor: pointer;
}

.login-link a::after {
  content: '';
  position: absolute;
  width: 0;
  height: 1px;
  background: #7dfdd9;
  bottom: -2px;
  left: 0;
  transition: width 0.3s ease;
}

.login-link a:hover::after {
  width: 100%;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

@media (max-width: 480px) {
  .register-form {
    padding: 1.5rem;
  }

  .energy-header h1 {
    font-size: 2rem;
  }

  .energy-input {
    padding: 1rem 1rem 0.8rem 3rem;
  }
}
</style>