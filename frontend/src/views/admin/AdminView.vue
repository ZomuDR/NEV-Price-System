<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowUp, ArrowDown, Sort } from '@element-plus/icons-vue'

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

interface Car {
  id: number
  model_name: string
  manufacturer: string
  car_class: string
  energy_type: string
  motor_power: number | null
  max_horsepower: number | null
  max_speed: number | null
  fuel_tank_volume: number | null
  curb_weight: number | null
  wheelbase: number | null
  max_torque: number | null
  nedc_fuel_consumption: number | null
  gear_count: number | null
  width: number | null
  displacement: number | null
  acceleration_time: number | null
  electric_range: number | null
  front_track: number | null
  seat_count: number | null
  price: number
}

const cars = ref<Car[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const searchField = ref('')
const searchValue = ref('')
const searchMode = ref<'fuzzy' | 'exact'>('fuzzy')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const editingCar = ref<Car | null>(null)

const sortField = ref('id')
const sortOrder = ref<'asc' | 'desc'>('asc')

const token = computed(() => localStorage.getItem('authToken'))

const searchFields = [
  { label: '全部字段', value: '' },
  { label: '型号', value: 'model_name' },
  { label: '厂商', value: 'manufacturer' },
  { label: '级别', value: 'car_class' },
  { label: '能源类型', value: 'energy_type' },
]

const sortableFields = [
  { label: 'ID', value: 'id', type: 'number' },
  { label: '型号', value: 'model_name', type: 'string' },
  { label: '厂商', value: 'manufacturer', value2: 'manufacturer', type: 'string' },
  { label: '级别', value: 'car_class', type: 'string' },
  { label: '能源类型', value: 'energy_type', type: 'string' },
  { label: '电动机总功率', value: 'motor_power', type: 'number' },
  { label: '最大马力', value: 'max_horsepower', type: 'number' },
  { label: '最高车速', value: 'max_speed', type: 'number' },
  { label: '价格', value: 'price', type: 'number' },
  { label: '百公里加速', value: 'acceleration_time', type: 'number' },
  { label: '纯电续航', value: 'electric_range', type: 'number' },
  { label: '整备质量', value: 'curb_weight', type: 'number' },
  { label: '轴距', value: 'wheelbase', type: 'number' },
]

const fetchCars = async () => {
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

    const response = await axios.get(`${API_BASE}/api/cars/`, {
      params,
      headers: token.value ? { 'Authorization': `Token ${token.value}` } : {}
    })
    cars.value = response.data.results || response.data
    total.value = response.data.count || cars.value.length
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchCars()
}

const handleSort = (field: string, type: string) => {
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
  fetchCars()
}

const getSortIcon = (field: string) => {
  if (sortField.value !== field) return 'none'
  return sortOrder.value
}

const handleEdit = (car: Car) => {
  editingCar.value = { ...car }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!editingCar.value) return
  
  try {
    await axios.patch(
      `${API_BASE}/api/cars/${editingCar.value.id}/`,
      editingCar.value,
      {
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        }
      }
    )
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchCars()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleDelete = async (car: Car) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除车型 "${car.model_name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`${API_BASE}/api/cars/${car.id}/`, {
      headers: { 'Authorization': `Token ${token.value}` }
    })
    ElMessage.success('删除成功')
    fetchCars()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchCars()
}

const clearSearch = () => {
  searchKeyword.value = ''
  searchField.value = ''
  searchValue.value = ''
  currentPage.value = 1
  fetchCars()
}

onMounted(() => {
  fetchCars()
})
</script>

<template>
  <div class="admin-container">
    <div class="admin-header">
      <h2>汽车数据管理</h2>
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
          placeholder="输入关键词搜索（如：比亚迪）"
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
      <el-button @click="fetchCars">刷新</el-button>
    </div>

    <el-table :data="cars" v-loading="loading" stripe class="car-table">
      <el-table-column prop="id" label="ID" width="70" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('id', 'number')">
            ID
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('id') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('id') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="model_name" label="型号" min-width="150" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('model_name', 'string')">
            型号
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('model_name') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('model_name') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="manufacturer" label="厂商" width="120" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('manufacturer', 'string')">
            厂商
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('manufacturer') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('manufacturer') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="car_class" label="级别" width="80" />
      <el-table-column prop="energy_type" label="能源类型" width="90" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('energy_type', 'string')">
            能源类型
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('energy_type') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('energy_type') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="motor_power" label="电机功率(kW)" width="100" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('motor_power', 'number')">
            电机功率
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('motor_power') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('motor_power') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="max_horsepower" label="马力(Ps)" width="80" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('max_horsepower', 'number')">
            马力
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('max_horsepower') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('max_horsepower') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="max_speed" label="最高速(km/h)" width="100" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('max_speed', 'number')">
            最高速
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('max_speed') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('max_speed') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="acceleration_time" label="百公里加速(s)" width="100" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('acceleration_time', 'number')">
            百公里加速
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('acceleration_time') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('acceleration_time') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格(万元)" width="100" sortable>
        <template #header>
          <div class="sortable-header" @click="handleSort('price', 'number')">
            价格
            <span class="sort-icons">
              <el-icon :class="{ active: getSortIcon('price') === 'asc' }"><ArrowUp /></el-icon>
              <el-icon :class="{ active: getSortIcon('price') === 'desc' }"><ArrowDown /></el-icon>
            </span>
          </div>
        </template>
        <template #default="{ row }">
          {{ row.price?.toFixed(2) }}
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
      title="编辑车型"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form v-if="editingCar" :model="editingCar" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="型号">
              <el-input v-model="editingCar.model_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="厂商">
              <el-input v-model="editingCar.manufacturer" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="级别">
              <el-input v-model="editingCar.car_class" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="能源类型">
              <el-input v-model="editingCar.energy_type" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电动机总功率(kW)">
              <el-input-number v-model="editingCar.motor_power" :precision="1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大马力(Ps)">
              <el-input-number v-model="editingCar.max_horsepower" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高车速(km/h)">
              <el-input-number v-model="editingCar.max_speed" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="油箱容积(L)">
              <el-input-number v-model="editingCar.fuel_tank_volume" :precision="1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="整备质量(kg)">
              <el-input-number v-model="editingCar.curb_weight" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="轴距(mm)">
              <el-input-number v-model="editingCar.wheelbase" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大扭矩(N·m)">
              <el-input-number v-model="editingCar.max_torque" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="NEDC油耗">
              <el-input-number v-model="editingCar.nedc_fuel_consumption" :precision="1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="挡位数">
              <el-input-number v-model="editingCar.gear_count" :min="1" :max="10" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="宽(mm)">
              <el-input-number v-model="editingCar.width" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排量(mL)">
              <el-input-number v-model="editingCar.displacement" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="百公里加速(s)">
              <el-input-number v-model="editingCar.acceleration_time" :precision="1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="纯电续航(km)">
              <el-input-number v-model="editingCar.electric_range" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="前轮距(mm)">
              <el-input-number v-model="editingCar.front_track" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="座位数(个)">
              <el-input-number v-model="editingCar.seat_count" :min="2" :max="9" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="价格(万元)">
              <el-input-number v-model="editingCar.price" :precision="2" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
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

.car-table {
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