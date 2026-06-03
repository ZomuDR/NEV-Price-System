<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Delete, Check } from '@element-plus/icons-vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface MLModel {
  id: number
  name: string
  version: string
  model_type: string
  is_active: boolean
  metrics: Record<string, any>
  description: string
  created_at: string
}

const models = ref<MLModel[]>([])
const loading = ref(false)
const token = computed(() => localStorage.getItem('authToken'))

const fetchModels = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/models/`)
    models.value = response.data
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  } finally {
    loading.value = false
  }
}

const activateModel = async (modelId: number) => {
  try {
    await axios.post(`${API_BASE}/api/models/${modelId}/activate/`, {}, {
      headers: { 'Authorization': `Token ${token.value}` }
    })
    ElMessage.success('模型已激活')
    await fetchModels()
  } catch (error) {
    ElMessage.error('激活失败')
  }
}

const deleteModel = async (model: MLModel) => {
  if (model.is_active) {
    ElMessage.warning('无法删除当前激活的模型')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${model.name} v${model.version}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    
    await axios.delete(`${API_BASE}/api/models/${model.id}/delete/`, {
      headers: { 'Authorization': `Token ${token.value}` }
    })
    ElMessage.success('删除成功')
    await fetchModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchModels()
})
</script>

<template>
  <div class="model-admin-container" v-loading="loading">
    <div class="admin-header">
      <div class="header-title">
        <h1>模型管理</h1>
        <p class="subtitle">管理机器学习预测模型</p>
      </div>
      <el-button @click="fetchModels" :icon="Refresh">刷新</el-button>
    </div>

    <div class="models-table">
      <el-table :data="models" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="模型名称" min-width="180" />
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column prop="model_type" label="类型" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '激活' : '未激活' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="R² Score" width="100">
          <template #default="{ row }">
            <span class="metric-value">{{ row.metrics?.r2_score || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="MAE" width="100">
          <template #default="{ row }">
            <span class="metric-value">{{ row.metrics?.mae || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="训练样本" width="100">
          <template #default="{ row }">
            {{ row.metrics?.train_size || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_active"
              type="success"
              size="small"
              @click="activateModel(row.id)"
              :icon="Check"
            >
              激活
            </el-button>
            <el-button
              v-if="!row.is_active"
              type="danger"
              size="small"
              @click="deleteModel(row)"
              :icon="Delete"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="info-card">
      <h3>说明</h3>
      <ul>
        <li>只有激活的模型会被用于价格预测</li>
        <li>同一时间只能有一个模型处于激活状态</li>
        <li>激活新模型会自动取消之前模型的激活状态</li>
        <li>无法删除当前激活的模型</li>
        <li>使用命令 <code>python manage.py train_model</code> 训练新模型</li>
      </ul>
    </div>
  </div>
</template>

<style scoped lang="scss">
.model-admin-container {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-color);
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .header-title {
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

.models-table {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  
  .metric-value {
    color: #00c853;
    font-weight: 500;
  }
}

.info-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  
  h3 {
    margin: 0 0 12px 0;
    color: var(--text-color);
  }
  
  ul {
    margin: 0;
    padding-left: 20px;
    color: #888;
    
    li {
      margin-bottom: 8px;
      
      code {
        background: rgba(0, 200, 83, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
        color: #00c853;
      }
    }
  }
}
</style>