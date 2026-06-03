<script setup lang="ts">
import { ref, computed} from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  House,
  TrendCharts,
  Notebook,
  QuestionFilled,
  User,
  UserFilled,
  Setting,
  Menu,
  Sunny,
  Moon,
  Shop,
  Star
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import defaultAvatar from '../../media/avatars/default_avatar.png'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 顶部导航标签
const tabs = ref([
  { path: '/system/first', title: '首页' },
  { path: '/system/analysis', title: '分析' },
  { path: '/system/history', title: '页面' },
  { path: '/system/settings', title: '系统' }
])

// 侧边栏菜单项
const menuItems = ref([
  { path: '/system/first', title: '首页', icon: House },
  { path: '/system/market', title: '市场车型', icon: Shop },
  { path: '/system/favorites', title: '我的收藏', icon: Star },
  { path: '/system/predict', title: '价格预测', icon: TrendCharts },
  { path: '/system/analysis', title: '市场分析', icon: Notebook },
  { path: '/system/history', title: '历史记录', icon: House },
  { path: '/system/help', title: '帮助中心', icon: QuestionFilled },
  { path: '/system/profile', title: '个人中心', icon: User },
  { path: '/system/settings', title: '系统设置', icon: Setting },
  { path: '/system/admin', title: '数据管理', icon: Setting, adminOnly: true },
  { path: '/system/user-admin', title: '用户管理', icon: UserFilled, adminOnly: true },
  { path: '/system/model-admin', title: '模型管理', icon: TrendCharts, adminOnly: true }
])

// 计算当前激活的标签和菜单
const activeTab = computed(() => {
  const basePath = route.path.split('/').slice(0, 3).join('/')
  return basePath || '/system'
})

const activeMenu = computed(() => route.path)

const loginType = computed(() => localStorage.getItem('loginType') || 'user')

const filteredMenuItems = computed(() => {
  if (loginType.value === 'admin') {
    return menuItems.value
  }
  return menuItems.value.filter(item => !item.adminOnly)
})

// 当前页面标题
const currentPageTitle = computed(() => {
  const menuItem = menuItems.value.find(item => item.path === route.path)
  return menuItem ? menuItem.title : '首页'
})

// 切换顶部标签
const switchTab = (path: string) => {
  router.push(path)
}

// 导航到菜单项
const navigateTo = (path: string) => {
  router.push(path)
}

// 侧边栏状态
const sidebarOpen = ref(true)

// 切换侧边栏
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

// 主题模式
const isDark = ref(false)

// 切换主题
const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// 退出登录
const logout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.removeItem('authToken')
    router.push('/login')
  }).catch(() => {})
}
</script>

<template>
  <div class="system-container">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="header-left">
        <el-button class="mobile-menu-btn" text @click="toggleSidebar">
          <el-icon><Menu /></el-icon>
        </el-button>
        <div class="logo-area" @click="toggleSidebar" style="cursor: pointer;">
          <div class="logo">N X</div>
          <div class="system-name">NeoPrice X</div>
        </div>
      </div>

      <div class="nav-tabs">
        <div
            v-for="tab in tabs"
            :key="tab.path"
            :class="['tab-item', { active: activeTab === tab.path }]"
            @click="switchTab(tab.path)"
        >
          {{ tab.title }}
        </div>
      </div>

      <div class="user-info">
        <div class="user-wrapper" @click="logout">
          <div class="avatar">
            <el-avatar :src="userStore.avatarUrl || defaultAvatar"></el-avatar>
          </div>
          <div class="user-details">
            <div class="username">{{ userStore.user.username}}</div>
            <div class="current-page">当前 / {{ currentPageTitle }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主体内容区 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <div class="sidebar" :class="{ open: sidebarOpen }">
        <div class="sidebar-section">
          <div class="section-title">功能导航</div>
          <div
              v-for="item in filteredMenuItems"
              :key="item.path"
              :class="['menu-item', { active: activeMenu === item.path }]"
              @click="navigateTo(item.path)"
          >
            <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
            <span>{{ item.title }}</span>
          </div>
        </div>

        <div class="sidebar-footer">
          <div class="theme-toggle" @click="toggleTheme">
            <el-icon v-if="isDark"><Sunny /></el-icon>
            <el-icon v-else><Moon /></el-icon>
            <span>{{ isDark ? '白天模式' : '黑夜模式' }}</span>
          </div>
        </div>

        
      </div>

      <!-- 主内容区 -->
      <div class="content-area">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/system' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="page-content">
          <!-- 仪表板头部 -->
          <div class="dashboard-header">
            <h1 class="dashboard-title">
              <el-icon><TrendCharts /></el-icon>
              {{ currentPageTitle }}
            </h1>
            <p class="dashboard-subtitle">
              基于人工智能算法的新能源汽车价格预测系统，提供实时市场分析和精准价格预测，帮助您做出最佳购车决策
            </p>
          </div>
            <router-view/>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
$primary: #00c853;
$primary-dark: #009624;
$primary-light: #5efc82;
$secondary: #2962ff;
$dark: #1a2f3b;
$dark-light: #2c5364;
$light: #f5f7fa;
$gray: #78909c;
$text: #37474f;
$white: #ffffff;

.system-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: $light;
  color: $text;
  font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, sans-serif;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  background: linear-gradient(135deg, $dark 0%, $dark-light 100%);
  color: $white;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mobile-menu-btn {
  display: none;
  
  @media (max-width: 991px) {
    display: flex;
  }
}

:deep(.mobile-menu-btn) {
  background: none !important;
  border: none !important;
  color: $white !important;
  font-size: 22px;
  cursor: pointer;
  padding: 5px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, $primary 0%, $secondary 100%);
  color: $white;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.system-name {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
  
  @media (max-width: 768px) {
    display: none;
  }
}

.nav-tabs {
  display: none;
  
  @media (min-width: 992px) {
    display: flex;
    gap: 8px;
  }
}

.tab-item {
  padding: 8px 20px;
  height: 40px;
  line-height: 40px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  transition: all 0.3s ease;
  opacity: 0.7;
  border-radius: 8px;

  &:hover {
    opacity: 1;
    background: rgba(255, 255, 255, 0.1);
  }

  &.active {
    opacity: 1;
    background: rgba(0, 200, 83, 0.2);
    color: $primary-light;
  }
}

.user-info {
  display: flex;
  align-items: center;
}

.user-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 25px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
}

.user-details {
  margin-left: 10px;
  
  @media (max-width: 576px) {
    display: none;
  }
}

.username {
  color: #dcf1ff;
  font-size: 13px;
  font-weight: 500;
}

.current-page {
  font-size: 11px;
  color: $primary-light;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  background: $white;
  padding: 20px 0;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex-shrink: 0;
  transition: all 0.3s ease;
  
  &:not(.open) {
    width: 0;
    padding: 0;
    overflow: hidden;
  }
  
  @media (max-width: 991px) {
    position: fixed;
    left: -220px;
    top: 60px;
    height: calc(100vh - 60px);
    z-index: 900;
    width: 220px;
    padding: 20px 0;
    overflow-y: auto;
    
    &.open {
      left: 0;
    }
    
    &:not(.open) {
      width: 220px;
      padding: 0;
    }
  }
}

.sidebar-section {
  margin-bottom: 20px;
  padding: 0 15px;
}

.sidebar-footer {
  margin-top: auto;
  padding: 15px;
  border-top: 1px solid #f0f4f8;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f8fbfe;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
  color: $dark;
  
  &:hover {
    background: rgba(0, 200, 83, 0.1);
  }
  
  .el-icon {
    font-size: 18px;
    color: $primary;
  }
}

.section-title {
  font-size: 12px;
  color: $gray;
  padding: 10px 0 12px;
  margin-bottom: 8px;
  border-bottom: 1px solid #f0f4f8;
  font-weight: 600;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;

  &::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 12px;
    background: $primary;
    border-radius: 2px;
    margin-right: 8px;
  }
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-radius: 8px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: $text;
  font-size: 14px;

  &:hover {
    background: rgba(0, 200, 83, 0.08);
    color: $primary-dark;
    transform: translateX(3px);
  }

  &.active {
    background: rgba(0, 200, 83, 0.12);
    color: $primary-dark;
    font-weight: 600;
    border-left: 3px solid $primary;
  }
}

.menu-icon {
  margin-right: 10px;
  font-size: 18px;
  width: 20px;
  text-align: center;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: $light;
}

.breadcrumb {
  padding: 12px 20px;
  background: $white;
  border-bottom: 1px solid #e8ecf0;
  flex-shrink: 0;
}

.page-content {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  position: relative;
}

.dashboard-header {
  margin-bottom: 20px;
}

.dashboard-title {
  font-size: 22px;
  font-weight: 700;
  color: $dark;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;

  .el-icon {
    color: $primary;
    background: rgba(0, 200, 83, 0.1);
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.dashboard-subtitle {
  font-size: 14px;
  color: $gray;
  line-height: 1.5;
}

@media (max-width: 1200px) {
  .nav-tabs {
    margin: 0 20px;
  }

  .tab-item {
    padding: 0 15px;
    font-size: 14px;
  }

  .sidebar {
    width: 220px;
  }
}
</style>