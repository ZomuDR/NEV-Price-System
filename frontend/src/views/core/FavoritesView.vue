<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Delete, StarFilled } from '@element-plus/icons-vue'

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

interface FavoriteCar {
  id: number
  car_id: number
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
  created_at: string
}

const favorites = ref<FavoriteCar[]>([])
const loading = ref(false)

const fetchFavorites = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/favorites/`, {
      headers: { 'Authorization': `Token ${localStorage.getItem('authToken')}` }
    })
    favorites.value = response.data
  } catch (error) {
    ElMessage.error('获取收藏列表失败')
  } finally {
    loading.value = false
  }
}

const removeFavorite = async (favoriteId: number) => {
  try {
    await axios.delete(`${API_BASE}/api/favorites/item/${favoriteId}/`, {
      headers: { 'Authorization': `Token ${localStorage.getItem('authToken')}` }
    })
    favorites.value = favorites.value.filter(f => f.id !== favoriteId)
    ElMessage.success('已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
  }
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

const formatValue = (value: number | null | undefined, unit: string = '') => {
  if (value === null || value === undefined || value === 0) return '-'
  return `${value}${unit}`
}

const formatPrice = (price: number) => {
  return price?.toFixed(2) || '--'
}

onMounted(() => {
  fetchFavorites()
})
</script>

<template>
  <div class="favorites-container" v-loading="loading">
    <div class="favorites-header">
      <div class="header-title">
        <h1>我的收藏</h1>
        <p class="subtitle">已收藏 {{ favorites.length }} 款车型</p>
      </div>
    </div>

    <div v-if="favorites.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">⭐</div>
      <p>暂无收藏车型</p>
      <p class="empty-hint">在市场车型页面点击星星图标即可收藏</p>
    </div>

    <div v-else class="favorites-grid">
      <div v-for="fav in favorites" :key="fav.id" class="favorite-card">
        <div class="card-header">
          <el-tag :type="getEnergyTypeColor(fav.energy_type)" size="small">
            {{ fav.energy_type }}
          </el-tag>
          <div class="header-right">
            <span class="car-class">{{ fav.car_class }}</span>
            <el-icon class="favorite-icon active">
              <StarFilled />
            </el-icon>
          </div>
        </div>
        
        <div class="card-body">
          <h3 class="car-name">{{ fav.model_name }}</h3>
          <p class="car-manufacturer">{{ fav.manufacturer }}</p>
          
          <div class="car-specs">
            <div class="spec-item" v-if="fav.motor_power">
              <span class="spec-label">功率</span>
              <span class="spec-value">{{ formatValue(fav.motor_power, 'kW') }}</span>
            </div>
            <div class="spec-item" v-if="fav.max_horsepower">
              <span class="spec-label">马力</span>
              <span class="spec-value">{{ formatValue(fav.max_horsepower, 'Ps') }}</span>
            </div>
            <div class="spec-item" v-if="fav.max_speed">
              <span class="spec-label">极速</span>
              <span class="spec-value">{{ formatValue(fav.max_speed, 'km/h') }}</span>
            </div>
            <div class="spec-item" v-if="fav.electric_range">
              <span class="spec-label">续航</span>
              <span class="spec-value">{{ formatValue(fav.electric_range, 'km') }}</span>
            </div>
            <div class="spec-item" v-if="fav.acceleration_time">
              <span class="spec-label">加速</span>
              <span class="spec-value">{{ formatValue(fav.acceleration_time, 's') }}</span>
            </div>
          </div>
        </div>
        
        <div class="card-footer">
          <div class="car-price">
            <span class="price-label">指导价</span>
            <span class="price-value">{{ formatPrice(fav.price) }}<span class="price-unit">万</span></span>
          </div>
          <el-button type="danger" size="small" @click="removeFavorite(fav.id)" :icon="Delete">
            取消收藏
          </el-button>
        </div>
        
        <div class="card-time">
          收藏于 {{ fav.created_at }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.favorites-container {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-color);
}

.favorites-header {
  margin-bottom: 20px;
  
  .header-title {
    h1 {
      font-size: 1.8rem;
      color: var(--text-color);
      margin: 0 0 8px 0;
      background: linear-gradient(135deg, #f7ba2a, #ffd666);
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

.empty-state {
  text-align: center;
  padding: 80px 20px;
  
  .empty-icon {
    font-size: 5rem;
    margin-bottom: 20px;
  }
  
  p {
    color: #888;
    font-size: 1.1rem;
    margin: 0 0 8px 0;
  }
  
  .empty-hint {
    color: #aaa;
    font-size: 0.9rem;
  }
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.favorite-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
  position: relative;
  
  &:hover {
    border-color: #f7ba2a;
    box-shadow: 0 4px 20px rgba(247, 186, 42, 0.15);
    transform: translateY(-2px);
  }
  
  .card-header {
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
      color: #f7ba2a;
    }
  }
  
  .card-body {
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
        background: rgba(247, 186, 42, 0.08);
        border-radius: 6px;
        
        .spec-label {
          font-size: 0.7rem;
          color: #888;
        }
        
        .spec-value {
          font-size: 0.85rem;
          color: #f7ba2a;
          font-weight: 500;
        }
      }
    }
  }
  
  .card-footer {
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
        color: #f7ba2a;
        
        .price-unit {
          font-size: 0.85rem;
          font-weight: normal;
        }
      }
    }
  }
  
  .card-time {
    margin-top: 8px;
    font-size: 0.75rem;
    color: #aaa;
  }
}

@media (max-width: 768px) {
  .favorites-grid {
    grid-template-columns: 1fr;
  }
}
</style>