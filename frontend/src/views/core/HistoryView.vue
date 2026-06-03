<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

interface HistoryItem {
  id: number
  created_at: string
  model_name: string
  predicted_price: number
  manufacturer: string
  car_class: string
  energy_type: string
  motor_power: number | null
  electric_range: number | null
  acceleration_time: number | null
}

const loading = ref(false)
const history = ref<HistoryItem[]>([])

const fetchHistory = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/prediction-history/`, {
      headers: { 'Authorization': `Token ${localStorage.getItem('authToken')}` }
    })
    history.value = response.data || []
  } catch (e: any) {
    ElMessage.error(e.response?.data?.error || '获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const totalCount = computed(() => history.value.length)

const formatValue = (v: any) => {
  if (v === null || v === undefined || v === '' || v === 0) return '-'
  return String(v)
}

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="history-container" v-loading="loading">
    <div class="history-header">
      <div class="header-title">
        <h1>历史记录</h1>
        <p class="subtitle">共 {{ totalCount }} 条预测记录</p>
      </div>
      <el-button @click="fetchHistory" :icon="Refresh">刷新</el-button>
    </div>

    <div class="history-card">
      <el-table :data="history" style="width: 100%" height="600">
        <el-table-column prop="created_at" label="预测时间" width="170" />
        <el-table-column prop="manufacturer" label="厂商" width="120" />
        <el-table-column prop="car_class" label="级别" width="120" />
        <el-table-column prop="energy_type" label="能源类型" width="140" />
        <el-table-column label="电机功率(kW)" width="140">
          <template #default="scope">
            {{ formatValue(scope.row.motor_power) }}
          </template>
        </el-table-column>
        <el-table-column label="续航(km)" width="110">
          <template #default="scope">
            {{ formatValue(scope.row.electric_range) }}
          </template>
        </el-table-column>
        <el-table-column label="加速(s)" width="110">
          <template #default="scope">
            {{ formatValue(scope.row.acceleration_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="predicted_price" label="预测价格(万)" width="130" />
        <el-table-column prop="model_name" label="模型" min-width="140" />
      </el-table>

      <div class="empty" v-if="!history.length && !loading">
        暂无记录（需要登录后进行预测）
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.history-container {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-color);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;

  .header-title {
    h1 {
      font-size: 1.8rem;
      color: var(--text-color);
      margin: 0 0 8px 0;
      background: var(--gradient-primary);
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

.history-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px;
}

.empty {
  padding: 16px;
  color: #888;
}
</style>
