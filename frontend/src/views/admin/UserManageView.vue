<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

interface User {
  id: number
  username: string
  email: string
  phone: string
  address: string
  is_staff: boolean
  is_active: boolean
  date_joined: string
}

const users = ref<User[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const searchField = ref('')
const searchValue = ref('')
const searchMode = ref<'fuzzy' | 'exact'>('fuzzy')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const editingUser = ref<User | null>(null)

const sortField = ref('id')
const sortOrder = ref<'asc' | 'desc'>('asc')

const token = computed(() => localStorage.getItem('authToken'))

const searchFields = [
  { label: '全部字段', value: '' },
  { label: '用户名', value: 'username' },
  { label: '邮箱', value: 'email' },
  { label: '手机号', value: 'phone' },
]

const fetchUsers = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: sortOrder.value === 'asc' ? sortField.value : `-${sortField.value}`
    }

    if (searchMode.value === 'fuzzy' && searchKeyword.value) {
      params.search = searchKeyword.value
    } else if (searchField.value && searchValue.value) {
      params[searchField.value] = searchValue.value
    }

    const response = await axios.get(`${API_BASE}/api/admin/users/`, {
      params,
      headers: { 'Authorization': `Token ${token.value}` }
    })
    users.value = response.data.results || response.data
    total.value = response.data.count || users.value.length
  } catch (error) {
    ElMessage.error('获取用户数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const handleSort = (field: string) => {
  if (sortField.value === field) {
    if (sortOrder.value === 'asc') {
      sortOrder.value = 'desc'
    } else if (sortOrder.value === 'desc') {
      sortField.value = 'id'
      sortOrder.value = 'asc'
    }
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
  fetchUsers()
}

const getSortIcon = (field: string) => {
  if (sortField.value !== field) return 'none'
  return sortOrder.value
}

const handleEdit = (user: User) => {
  editingUser.value = { ...user }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!editingUser.value) return
  
  try {
    await axios.patch(
      `${API_BASE}/api/admin/users/${editingUser.value.id}/`,
      editingUser.value,
      {
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        }
      }
    )
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchUsers()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleDelete = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`${API_BASE}/api/admin/users/${user.id}/`, {
      headers: { 'Authorization': `Token ${token.value}` }
    })
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchUsers()
}

const clearSearch = () => {
  searchKeyword.value = ''
  searchField.value = ''
  searchValue.value = ''
  currentPage.value = 1
  fetchUsers()
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="admin-container">
    <div class="admin-header">
      <h2>用户管理</h2>
    </div>

    <div class="search-bar">
      <div class="search-mode">
        <el-radio-group v-model="searchMode" size="small">
          <el-radio-button value="fuzzy">模糊搜索</el-radio-button>
          <el-radio-button value="exact">精确搜索</el-radio-button>
        </el-radio-group>
      </div>

      <template v-if="searchMode === 'fuzzy'">
        <el-input
          v-model="searchKeyword"
          placeholder="输入关键词搜索用户"
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </template>

      <template v-else>
        <el-select v-model="searchField" placeholder="选择字段" class="field-select">
          <el-option
            v-for="field in searchFields"
            :key="field.value"
            :label="field.label"
            :value="field.value"
          />
        </el-select>
        <el-input
          v-model="searchValue"
          placeholder="输入搜索值"
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </template>

      <el-button @click="clearSearch">重置</el-button>
      <el-button @click="fetchUsers">刷新</el-button>
    </div>

    <el-table :data="users" v-loading="loading" stripe class="user-table">
      <el-table-column prop="id" label="ID" width="70" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('id')">
            ID
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('id') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('id') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" width="120" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('username')">
            用户名
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('username') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('username') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="180" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('email')">
            邮箱
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('email') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('email') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="address" label="地址" min-width="150" show-overflow-tooltip />
      <el-table-column prop="is_staff" label="管理员" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_staff ? 'success' : 'info'" size="small">
            {{ row.is_staff ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="date_joined" label="注册时间" width="170">
        <template #default="{ row }">
          {{ new Date(row.date_joined).toLocaleString('zh-CN') }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="handlePageChange"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      title="编辑用户"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form v-if="editingUser" :model="editingUser" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="editingUser.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editingUser.email" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editingUser.phone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="editingUser.address" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="editingUser.is_staff" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editingUser.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-container {
  padding: 20px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.admin-header h2 {
  color: var(--text-color);
  margin: 0;
  background: linear-gradient(135deg, #00c853, #00e676);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
  padding: 16px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.search-mode {
  margin-right: 10px;
}

.search-input {
  width: 300px;
}

.field-select {
  width: 150px;
}

.sortable-header {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  transition: color 0.3s ease;
}

.sortable-header:hover {
  color: #00c853;
}

.sort-icons {
  display: inline-flex;
  flex-direction: column;
  margin-left: 4px;
  font-size: 10px;
}

.sort-icons .el-icon {
  height: 12px;
  line-height: 12px;
  color: #999;
  transition: color 0.3s ease;
}

.sort-icons .el-icon.active {
  color: #00c853;
}

.user-table {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 16px;
  background: var(--card-bg);
  border-radius: 12px;
}

:deep(.el-table) {
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: var(--bg-color);
}

:deep(.el-table th) {
  background: linear-gradient(180deg, #f8f9fa 0%, #f0f2f5 100%);
  font-weight: 600;
}

:deep(.el-table tr:hover > td) {
  background-color: rgba(0, 200, 83, 0.05) !important;
}

:deep(.el-dialog) {
  background: var(--bg-color);
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #1a2f3b 0%, #2c5364 100%);
  padding: 16px 20px;
  margin: 0;
}

:deep(.el-dialog__title) {
  color: #fff;
  font-weight: 600;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #fff;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}
</style>