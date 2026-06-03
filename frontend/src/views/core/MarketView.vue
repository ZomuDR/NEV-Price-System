<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowUp, ArrowDown, Search, Refresh, Grid, List, Star, StarFilled } from '@element-plus/icons-vue'

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
  electric_range: number | null
  acceleration_time: number | null
  price: number
  is_favorite?: boolean
}

const cars = ref<Car[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const searchField = ref('')
const searchValue = ref('')
const searchMode = ref<'fuzzy' | 'exact'>('fuzzy')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const viewMode = ref<'grid' | 'list'>('grid')
const favorites = ref<Set<number>>(new Set())

const sortField = ref('id')
const sortOrder = ref<'asc' | 'desc'>('asc')

const isLoggedIn = computed(() => !!localStorage.getItem('authToken'))

const searchFields = [
  { label: '全部字段', value: '' },
  { label: '型号', value: 'model_name' },
  { label: '厂商', value: 'manufacturer' },
  { label: '级别', value: 'car_class' },
  { label: '能源类型', value: 'energy_type' },
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
      params
    })
    cars.value = response.data.results || response.data
    total.value = response.data.count || cars.value.length
    
    if (isLoggedIn.value) {
      await checkFavorites()
    }
  } catch (error) {
    ElMessage.error('获取车型数据失败')
  } finally {
    loading.value = false
  }
}

const checkFavorites = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/favorites/`, {
      headers: { 'Authorization': `Token ${localStorage.getItem('authToken')}` }
    })
    const favoriteIds = response.data.map((fav: any) => fav.car_id)
    favorites.value = new Set(favoriteIds)
  } catch (error) {
    console.error('获取收藏列表失败')
  }
}

const toggleFavorite = async (car: Car, event: Event) => {
  event.stopPropagation()
  
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }
  
  try {
    if (favorites.value.has(car.id)) {
      await axios.delete(`${API_BASE}/api/favorites/${car.id}/remove/`, {
        headers: { 'Authorization': `Token ${localStorage.getItem('authToken')}` }
      })
      favorites.value.delete(car.id)
      ElMessage.success('已取消收藏')
    } else {
      await axios.post(`${API_BASE}/api/favorites/${car.id}/`, {}, {
        headers: { 'Authorization': `Token ${localStorage.getItem('authToken')}` }
      })
      favorites.value.add(car.id)
      ElMessage.success('收藏成功')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const isFavorite = (carId: number) => favorites.value.has(carId)

const handleSearch = () => {
  currentPage.value = 1
  fetchCars()
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
  fetchCars()
}

const getSortIcon = (field: string) => {
  if (sortField.value !== field) return 'none'
  return sortOrder.value
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

const getEnergyTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    '纯电动': 'success',
    '插电式混合动力': 'warning',
    '增程式': 'info',
    '氢燃料电池': 'danger',
    '燃油车': '',
  }
  return colors[type] || ''
}

const formatPrice = (price: number) => {
  return price?.toFixed(2) || '--'
}

const formatValue = (value: number | null | undefined, unit: string = '') => {
  if (value === null || value === undefined || value === 0) return '-'
  return `${value}${unit}`
}

onMounted(() => {
  fetchCars()
})
</script>

<template>
  <div class="market-container" v-loading="loading">
    <div class="market-header">
      <div class="header-title">
        <h1>市场车型</h1>
        <p class="subtitle">浏览数据库中的车型信息</p>
      </div>
      <div class="header-stats">
        <span class="total-count">共 {{ total }} 款车型</span>
      </div>
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
          placeholder="输入关键词搜索车型"
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
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
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </template>

      <el-button @click="clearSearch">重置</el-button>
      <el-button @click="fetchCars">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
      
      <div class="view-toggle">
        <el-button-group>
          <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" @click="viewMode = 'grid'">
            <el-icon><Grid /></el-icon>
          </el-button>
          <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
            <el-icon><List /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <div class="sort-bar">
      <span class="sort-label">排序：</span>
      <div class="sort-options">
        <button 
          class="sort-btn" 
          :class="{ active: sortField === 'id' }"
          @click="handleSort('id')"
        >
          默认
          <span class="sort-icons" v-if="sortField === 'id'">
            <el-icon :class="{ active: sortOrder === 'asc' }"><ArrowUp /></el-icon>
            <el-icon :class="{ active: sortOrder === 'desc' }"><ArrowDown /></el-icon>
          </span>
        </button>
        <button 
          class="sort-btn" 
          :class="{ active: sortField === 'price' }"
          @click="handleSort('price')"
        >
          价格
          <span class="sort-icons" v-if="sortField === 'price'">
            <el-icon :class="{ active: sortOrder === 'asc' }"><ArrowUp /></el-icon>
            <el-icon :class="{ active: sortOrder === 'desc' }"><ArrowDown /></el-icon>
          </span>
        </button>
        <button 
          class="sort-btn" 
          :class="{ active: sortField === 'motor_power' }"
          @click="handleSort('motor_power')"
        >
          功率
          <span class="sort-icons" v-if="sortField === 'motor_power'">
            <el-icon :class="{ active: sortOrder === 'asc' }"><ArrowUp /></el-icon>
            <el-icon :class="{ active: sortOrder === 'desc' }"><ArrowDown /></el-icon>
          </span>
        </button>
        <button 
          class="sort-btn" 
          :class="{ active: sortField === 'electric_range' }"
          @click="handleSort('electric_range')"
        >
          续航
          <span class="sort-icons" v-if="sortField === 'electric_range'">
            <el-icon :class="{ active: sortOrder === 'asc' }"><ArrowUp /></el-icon>
            <el-icon :class="{ active: sortOrder === 'desc' }"><ArrowDown /></el-icon>
          </span>
        </button>
        <button 
          class="sort-btn" 
          :class="{ active: sortField === 'acceleration_time' }"
          @click="handleSort('acceleration_time')"
        >
          加速
          <span class="sort-icons" v-if="sortField === 'acceleration_time'">
            <el-icon :class="{ active: sortOrder === 'asc' }"><ArrowUp /></el-icon>
            <el-icon :class="{ active: sortOrder === 'desc' }"><ArrowDown /></el-icon>
          </span>
        </button>
      </div>
    </div>

    <div v-if="cars.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">🚗</div>
      <p>暂无车型数据</p>
    </div>

    <div v-else :class="['cars-grid', viewMode]">
      <div v-for="car in cars" :key="car.id" class="car-card">
        <div class="car-header">
          <el-tag :type="getEnergyTypeColor(car.energy_type)" size="small">
            {{ car.energy_type }}
          </el-tag>
          <div class="header-right">
            <span class="car-class">{{ car.car_class }}</span>
            <el-icon 
              class="favorite-icon" 
              :class="{ active: isFavorite(car.id) }"
              @click="toggleFavorite(car, $event)"
            >
              <StarFilled v-if="isFavorite(car.id)" />
              <Star v-else />
            </el-icon>
          </div>
        </div>
        
        <div class="car-body">
          <h3 class="car-name">{{ car.model_name }}</h3>
          <p class="car-manufacturer">{{ car.manufacturer }}</p>
          
          <div class="car-specs">
            <div class="spec-item">
              <span class="spec-label">功率</span>
              <span class="spec-value">{{ formatValue(car.motor_power, 'kW') }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">马力</span>
              <span class="spec-value">{{ formatValue(car.max_horsepower, 'Ps') }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">最大速度</span>
              <span class="spec-value">{{ formatValue(car.max_speed, 'km/h') }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">续航</span>
              <span class="spec-value">{{ formatValue(car.electric_range, 'km') }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">百公里加速</span>
              <span class="spec-value">{{ formatValue(car.acceleration_time, 's') }}</span>
            </div>
          </div>
        </div>
        
        <div class="car-footer">
          <div class="car-price">
            <span class="price-label">指导价</span>
            <span class="price-value">{{ formatPrice(car.price) }}<span class="price-unit">万</span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.market-container {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-color);
}

.market-header {
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
  
  .header-stats {
    .total-count {
      color: #00c853;
      font-size: 1rem;
      font-weight: 500;
    }
  }
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
  
  .search-mode {
    margin-right: 10px;
  }
  
  .search-input {
    width: 300px;
  }
  
  .field-select {
    width: 120px;
  }
  
  .view-toggle {
    margin-left: auto;
  }
}

.sort-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  
  .sort-label {
    color: #888;
    font-size: 0.9rem;
  }
  
  .sort-options {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .sort-btn {
    padding: 6px 14px;
    border: 1px solid var(--border-color);
    background: transparent;
    color: #888;
    font-size: 0.85rem;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 4px;
    
    &:hover {
      border-color: #00c853;
      color: #00c853;
    }
    
    &.active {
      background: #00c853;
      border-color: #00c853;
      color: #fff;
    }
    
    .sort-icons {
      display: inline-flex;
      flex-direction: column;
      font-size: 8px;
      line-height: 8px;
      
      .el-icon {
        height: 10px;
        color: inherit;
        
        &.active {
          color: #fff;
        }
      }
    }
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  
  .empty-icon {
    font-size: 4rem;
    margin-bottom: 16px;
  }
  
  p {
    color: #888;
    font-size: 1rem;
  }
}

.cars-grid {
  display: grid;
  gap: 16px;
  
  &.grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
  
  &.list {
    grid-template-columns: 1fr;
    
    .car-card {
      flex-direction: row;
      align-items: center;
      
      .car-header {
        width: 120px;
        flex-shrink: 0;
        flex-direction: column;
        align-items: flex-start;
      }
      
      .car-body {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 20px;
        
        .car-name {
          min-width: 200px;
          margin: 0;
        }
        
        .car-specs {
          flex: 1;
          flex-wrap: wrap;
          gap: 12px;
        }
      }
      
      .car-footer {
        width: 150px;
        justify-content: flex-end;
      }
    }
  }
}

.car-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
  
  &:hover {
    border-color: #00c853;
    box-shadow: 0 4px 20px rgba(0, 200, 83, 0.15);
    transform: translateY(-2px);
  }
  
  .car-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .car-class {
      color: #888;
      font-size: 0.8rem;
    }
    
    .favorite-icon {
      font-size: 1.2rem;
      color: #ccc;
      cursor: pointer;
      transition: all 0.2s;
      
      &:hover {
        color: #f7ba2a;
        transform: scale(1.2);
      }
      
      &.active {
        color: #f7ba2a;
      }
    }
  }
  
  .car-body {
    flex: 1;
    
    .car-name {
      font-size: 1rem;
      color: var(--text-color);
      margin: 0 0 4px 0;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .car-manufacturer {
      color: #888;
      font-size: 0.85rem;
      margin: 0 0 12px 0;
    }
    
    .car-specs {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      
      .spec-item {
        display: flex;
        flex-direction: column;
        padding: 6px 10px;
        background: rgba(0, 200, 83, 0.05);
        border-radius: 6px;
        
        .spec-label {
          font-size: 0.7rem;
          color: #888;
        }
        
        .spec-value {
          font-size: 0.85rem;
          color: #00c853;
          font-weight: 500;
        }
      }
    }
  }
  
  .car-footer {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .car-price {
      display: flex;
      flex-direction: column;
      
      .price-label {
        font-size: 0.75rem;
        color: #888;
      }
      
      .price-value {
        font-size: 1.3rem;
        font-weight: bold;
        color: #00c853;
        
        .price-unit {
          font-size: 0.85rem;
          font-weight: normal;
        }
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .search-bar {
    .search-input {
      width: 100%;
    }
  }
  
  .cars-grid.list .car-card {
    flex-direction: column;
    
    .car-body {
      flex-direction: column;
      align-items: flex-start;
    }
  }
}
</style>