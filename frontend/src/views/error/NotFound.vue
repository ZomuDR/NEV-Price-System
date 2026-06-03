<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="logo-area">
        <div class="logo">N X</div>
        <div class="system-name">NeoPrice X</div>
      </div>
      <div class="error-code">404</div>
      <div class="error-message">您的页面找不到或者未开放</div>
      <div class="error-contact">请与管理员联系</div>
      <el-button type="primary" class="back-btn" @click="goBack">
        返回上一个页面
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
$primary: #00c853;
$primary-dark: #009624;
$white: #ffffff;
$gray: #666666;
$light-gray: #f5f7fa;

.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $light-gray 0%, #e8f5e9 100%);
}

.not-found-content {
  text-align: center;
  padding: 40px;
}

.logo-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 30px;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, $primary 0%, $primary-dark 100%);
  color: $white;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.system-name {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}

.error-code {
  font-size: 120px;
  font-weight: 800;
  color: $primary;
  line-height: 1;
  margin-bottom: 20px;
  text-shadow: 0 4px 20px rgba(0, 200, 83, 0.3);
}

.error-message {
  font-size: 20px;
  color: #1a1a1a;
  margin-bottom: 10px;
  font-weight: 500;
}

.error-contact {
  font-size: 16px;
  color: $gray;
  margin-bottom: 40px;
}

.back-btn {
  background: linear-gradient(135deg, $primary 0%, $primary-dark 100%) !important;
  border: none !important;
  padding: 12px 30px;
  font-size: 15px;
  border-radius: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4);
  }
}
</style>