<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import defaultAvatar from '../../../media/avatars/default_avatar.png'
import { ElMessage } from 'element-plus'

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

const userStore = useUserStore()
const router = useRouter()
const fileInput = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const isEditing = ref(false)

const user = ref({
  username: '',
  email: '',
  phone: '',
  address: '',
  avatar: '',
  is_admin: false,
  date_joined: ''
})

const userStats = ref({
  prediction_count: 0,
  favorite_count: 0
})

const editForm = ref({
  email: '',
  phone: '',
  address: ''
})

const avatarUrl = computed(() => {
  if (!user.value.avatar) return defaultAvatar
  return user.value.avatar.startsWith('http') 
    ? user.value.avatar 
    : `${API_BASE}${user.value.avatar}`
})

const fetchUserProfile = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('authToken')
    const response = await axios.get(`${API_BASE}/api/profile/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
    user.value = response.data
    editForm.value = {
      email: response.data.email || '',
      phone: response.data.phone || '',
      address: response.data.address || ''
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  } finally {
    loading.value = false
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleAvatarChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  if (!file.type.match('image.*')) {
    ElMessage.error('请选择图片文件')
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过2MB')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    user.value.avatar = e.target?.result as string
    saveAvatar()
  }
  reader.readAsDataURL(file)
}

const saveAvatar = async () => {
  try {
    const token = localStorage.getItem('authToken')
    await axios.put(`${API_BASE}/api/profile/`, {
      avatar: user.value.avatar
    }, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    })
    ElMessage.success('头像更新成功')
    userStore.setUser(user.value)
  } catch (error) {
    ElMessage.error('头像更新失败')
  }
}

const startEdit = () => {
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
  editForm.value = {
    email: user.value.email || '',
    phone: user.value.phone || '',
    address: user.value.address || ''
  }
}

const saveProfile = async () => {
  try {
    const token = localStorage.getItem('authToken')
    await axios.put(`${API_BASE}/api/profile/`, editForm.value, {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    })
    user.value = { ...user.value, ...editForm.value }
    userStore.setUser(user.value)
    isEditing.value = false
    ElMessage.success('信息更新成功')
  } catch (error) {
    ElMessage.error('信息更新失败')
  }
}

onMounted(() => {
  fetchUserProfile()
  fetchUserStats()
})

const fetchUserStats = async () => {
  try {
    const token = localStorage.getItem('authToken')
    const response = await axios.get(`${API_BASE}/api/user-stats/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
    userStats.value = response.data
  } catch (error) {
    console.error('获取用户统计失败:', error)
  }
}
</script>

<template>
  <div class="profile-container" v-loading="loading">
    <div class="profile-header">
      <div class="greeting-section">
        <h1>个人中心</h1>
        <p class="subtitle">管理您的账户信息</p>
      </div>
    </div>

    <div class="profile-content">
      <div class="profile-card avatar-card">
        <div class="avatar-wrapper" @click="triggerFileInput">
          <img :src="avatarUrl" alt="头像" class="avatar" />
          <div class="avatar-overlay">
            <span>更换头像</span>
          </div>
        </div>
        <input 
          ref="fileInput"
          type="file" 
          accept="image/*" 
          style="display: none" 
          @change="handleAvatarChange"
        />
        <div class="user-badge">
          <el-tag :type="user.is_admin ? 'warning' : 'success'" size="large">
            {{ user.is_admin ? '管理员' : '普通用户' }}
          </el-tag>
        </div>
      </div>

      <div class="profile-card info-card">
        <div class="card-header">
          <h3>基本信息</h3>
          <el-button 
            v-if="!isEditing" 
            type="primary" 
            size="small" 
            @click="startEdit"
          >
            编辑资料
          </el-button>
          <div v-else class="edit-actions">
            <el-button size="small" @click="cancelEdit">取消</el-button>
            <el-button type="primary" size="small" @click="saveProfile">保存</el-button>
          </div>
        </div>
        
        <div class="info-grid">
          <div class="info-item">
            <span class="label">用户名</span>
            <span class="value">{{ user.username }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">邮箱</span>
            <el-input 
              v-if="isEditing" 
              v-model="editForm.email" 
              size="small" 
              placeholder="请输入邮箱"
            />
            <span v-else class="value">{{ user.email || '未设置' }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">手机号</span>
            <el-input 
              v-if="isEditing" 
              v-model="editForm.phone" 
              size="small" 
              placeholder="请输入手机号"
            />
            <span v-else class="value">{{ user.phone || '未设置' }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">地址</span>
            <el-input 
              v-if="isEditing" 
              v-model="editForm.address" 
              size="small" 
              placeholder="请输入地址"
            />
            <span v-else class="value">{{ user.address || '未设置' }}</span>
          </div>
          
          <div class="info-item">
            <span class="label">注册时间</span>
            <span class="value">{{ user.date_joined ? new Date(user.date_joined).toLocaleDateString('zh-CN') : '-' }}</span>
          </div>
        </div>
      </div>

      <div class="profile-card stats-card">
        <div class="card-header">
          <h3>账户统计</h3>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-value">{{ userStats.prediction_count }}</div>
              <div class="stat-label">预测次数</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon">⭐</div>
            <div class="stat-info">
              <div class="stat-value">{{ userStats.favorite_count }}</div>
              <div class="stat-label">收藏车型</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon">📝</div>
            <div class="stat-info">
              <div class="stat-value">{{ userStats.prediction_count }}</div>
              <div class="stat-label">历史记录</div>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-card quick-actions">
        <div class="card-header">
          <h3>快捷操作</h3>
        </div>
        <div class="actions-grid">
          <div class="action-item" @click="router.push('/system/predict')">
            <span class="action-icon">🚗</span>
            <span class="action-text">价格预测</span>
          </div>
          <div class="action-item" @click="router.push('/system/history')">
            <span class="action-icon">📜</span>
            <span class="action-text">历史记录</span>
          </div>
          <div class="action-item" @click="router.push('/system/settings')">
            <span class="action-icon">⚙️</span>
            <span class="action-text">账户设置</span>
          </div>
          <div class="action-item" @click="router.push('/system/help')">
            <span class="action-icon">❓</span>
            <span class="action-text">帮助中心</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.profile-container {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-color);
}

.profile-header {
  margin-bottom: 24px;
  
  .greeting-section {
    h1 {
      font-size: 1.8rem;
      color: var(--text-color);
      margin: 0 0 8px 0;
      background: linear-gradient(135deg, #00c853, #00e676);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .subtitle {
      color: #888;
      font-size: 0.9rem;
      margin: 0;
    }
  }
}

.profile-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  grid-template-rows: auto auto;
  gap: 16px;
}

.profile-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.avatar-card {
  grid-row: span 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  
  .avatar-wrapper {
    position: relative;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    overflow: hidden;
    cursor: pointer;
    border: 3px solid #00c853;
    
    .avatar {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .avatar-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.3s;
      
      span {
        color: #fff;
        font-size: 0.85rem;
      }
    }
    
    &:hover .avatar-overlay {
      opacity: 1;
    }
  }
  
  .user-badge {
    margin-top: 16px;
  }
}

.info-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 {
      margin: 0;
      color: var(--text-color);
      font-size: 1.1rem;
    }
    
    .edit-actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    
    .info-item {
      display: flex;
      flex-direction: column;
      gap: 6px;
      
      .label {
        color: #888;
        font-size: 0.85rem;
      }
      
      .value {
        color: var(--text-color);
        font-size: 1rem;
      }
    }
  }
}

.stats-card {
  .card-header {
    margin-bottom: 16px;
    
    h3 {
      margin: 0;
      color: var(--text-color);
      font-size: 1.1rem;
    }
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    
    .stat-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;
      background: rgba(0, 200, 83, 0.05);
      border-radius: 8px;
      
      .stat-icon {
        font-size: 1.8rem;
      }
      
      .stat-info {
        .stat-value {
          font-size: 1.4rem;
          font-weight: bold;
          color: #00c853;
        }
        
        .stat-label {
          font-size: 0.75rem;
          color: #888;
        }
      }
    }
  }
}

.quick-actions {
  grid-column: span 2;
  
  .card-header {
    margin-bottom: 16px;
    
    h3 {
      margin: 0;
      color: var(--text-color);
      font-size: 1.1rem;
    }
  }
  
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    
    .action-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 20px;
      background: rgba(0, 200, 83, 0.05);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        background: rgba(0, 200, 83, 0.15);
        transform: translateY(-2px);
      }
      
      .action-icon {
        font-size: 1.8rem;
      }
      
      .action-text {
        color: var(--text-color);
        font-size: 0.9rem;
      }
    }
  }
}

@media (max-width: 900px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
  
  .avatar-card {
    grid-row: auto;
  }
  
  .quick-actions {
    grid-column: auto;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

.profile-container {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.profile-card {
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00c853, #00e676, #69f0ae);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover::before {
    opacity: 1;
  }
}

.avatar-card {
  &::before {
    background: linear-gradient(180deg, #00c853, #00e676);
    width: 3px;
    height: 100%;
    top: 0;
    left: 0;
    right: auto;
  }
}

.stats-card .stat-item {
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00c853, transparent);
    transform: scaleX(0);
    transition: transform 0.3s ease;
  }
  
  &:hover::after {
    transform: scaleX(1);
  }
  
  &:hover .stat-icon {
    transform: scale(1.2);
  }
  
  .stat-icon {
    transition: transform 0.3s ease;
  }
}

.quick-actions .action-item {
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 8px;
    padding: 2px;
    background: linear-gradient(135deg, #00c853, #00e676);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover::before {
    opacity: 1;
  }
}
</style>