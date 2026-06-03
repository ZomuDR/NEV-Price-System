<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const loading = ref(false)
const dashboardData = ref<any>(null)
const pieChartType = ref('manufacturer')
const currentTime = ref(new Date())

const greeting = computed(() => {
  const hour = currentTime.value.getHours()
  if (hour >= 5 && hour < 9) return '早上好'
  if (hour >= 9 && hour < 12) return '上午好'
  if (hour >= 12 && hour < 14) return '中午好'
  if (hour >= 14 && hour < 18) return '下午好'
  if (hour >= 18 && hour < 22) return '晚上好'
  return '夜深了'
})

const formattedTime = computed(() => {
  return currentTime.value.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZone: 'Asia/Shanghai'
  })
})

const formatValue = (value: number | null | undefined, unit: string = '') => {
  if (value === null || value === undefined || value === 0) return '-'
  return `${value}${unit}`
}

setInterval(() => {
  currentTime.value = new Date()
}, 1000)

const fetchDashboard = async () => {
  loading.value = true
  try {
    console.log('Fetching dashboard data...')
    const response = await axios.get('/api/dashboard/')
    console.log('Response received:', response)
    console.log('Response data:', response.data)
    dashboardData.value = response.data
    console.log('Dashboard data set:', dashboardData.value)
  } catch (error: any) {
    console.error('Failed to fetch dashboard data:', error)
    console.error('Error response:', error.response)
    console.error('Error message:', error.message)
  } finally {
    loading.value = false
  }
}

const pieOption = computed(() => {
  if (!dashboardData.value) return {}
  
  let data: any[] = []
  let title = ''
  
  if (pieChartType.value === 'manufacturer') {
    data = dashboardData.value.manufacturer_dist.map((item: any) => ({
      name: item.manufacturer,
      value: item.count
    }))
    title = '厂商分布'
  } else if (pieChartType.value === 'energy_type') {
    data = dashboardData.value.energy_type_dist.map((item: any) => ({
      name: item.energy_type,
      value: item.count
    }))
    title = '能源类型分布'
  } else if (pieChartType.value === 'car_class') {
    data = dashboardData.value.car_class_dist.map((item: any) => ({
      name: item.car_class,
      value: item.count
    }))
    title = '级别分布'
  }
  
  const colors = [
    '#00c853', '#00e676', '#69f0ae', '#b9f6ca',
    '#1de9b6', '#64ffda', '#a7ffeb', '#e0f2f1',
    '#80cbc4', '#4db6ac', '#26a69a', '#009688'
  ]
  
  return {
    title: {
      text: title,
      left: 'center',
      textStyle: { color: '#00c853', fontSize: 16 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#888' }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#1a2f3b',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#fff'
          }
        },
        labelLine: { show: false },
        data,
        color: colors
      }
    ]
  }
})

const barOption = computed(() => {
  if (!dashboardData.value) return {}
  
  const data = dashboardData.value.price_ranges
  const categories = data.map((item: any) => item.range)
  const values = data.map((item: any) => item.count)
  
  return {
    title: {
      text: '价格区间分布',
      left: 'center',
      textStyle: { color: '#00c853', fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLine: { lineStyle: { color: '#444' } },
      axisLabel: { color: '#888', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#444' } },
      axisLabel: { color: '#888' },
      splitLine: { lineStyle: { color: '#333' } }
    },
    series: [
      {
        name: '数量',
        type: 'bar',
        data: values,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#00e676' },
              { offset: 1, color: '#00c853' }
            ]
          },
          borderRadius: [5, 5, 0, 0]
        },
        barWidth: '50%'
      }
    ]
  }
})

onMounted(() => {
  fetchDashboard()
})
</script>

<template>
  <div class="dashboard-container" v-loading="loading">
    <div class="dashboard-header">
      <div class="greeting-section">
        <h1>{{ greeting }}，欢迎使用 NeoPrice X</h1>
        <p class="current-time">{{ formattedTime }}</p>
      </div>
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">🚗</div>
          <div class="stat-info">
            <div class="stat-value">{{ dashboardData?.total_cars || 0 }}</div>
            <div class="stat-label">车型总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <div class="stat-value">{{ formatValue(dashboardData?.avg_price, '万') }}</div>
            <div class="stat-label">平均价格</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚡</div>
          <div class="stat-info">
            <div class="stat-value">{{ formatValue(dashboardData?.avg_motor_power, 'kW') }}</div>
            <div class="stat-label">平均功率(kW)</div>
          </div>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card pie-chart">
        <div class="chart-header">
          <h3>数据分布</h3>
          <div class="chart-tabs">
            <button 
              :class="{ active: pieChartType === 'manufacturer' }"
              @click="pieChartType = 'manufacturer'"
            >厂商</button>
            <button 
              :class="{ active: pieChartType === 'energy_type' }"
              @click="pieChartType = 'energy_type'"
            >能源类型</button>
            <button 
              :class="{ active: pieChartType === 'car_class' }"
              @click="pieChartType = 'car_class'"
            >级别</button>
          </div>
        </div>
        <v-chart class="chart" :option="pieOption" autoresize />
      </div>
      
      <div class="chart-card bar-chart">
        <v-chart class="chart" :option="barOption" autoresize />
      </div>
    </div>

    <div class="top-cards-row">
      <div class="top-card">
        <div class="top-card-header">
          <span class="top-icon">💎</span>
          <h3>最高价格 TOP3</h3>
        </div>
        <div class="top-list">
          <div 
            v-for="(car, index) in dashboardData?.top_expensive" 
            :key="car.id"
            class="top-item"
          >
            <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
            <div class="car-info">
              <div class="car-name">{{ car.model_name }}</div>
              <div class="car-manufacturer">{{ car.manufacturer }}</div>
            </div>
            <div class="car-value">{{ car.price }}万</div>
          </div>
        </div>
      </div>
      
      <div class="top-card">
        <div class="top-card-header">
          <span class="top-icon">🏎️</span>
          <h3>最快加速 TOP3</h3>
        </div>
        <div class="top-list">
          <div 
            v-for="(car, index) in dashboardData?.top_fast" 
            :key="car.id"
            class="top-item"
          >
            <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
            <div class="car-info">
              <div class="car-name">{{ car.model_name }}</div>
              <div class="car-manufacturer">{{ car.manufacturer }}</div>
            </div>
            <div class="car-value">{{ formatValue(car.acceleration_time, 's') }}</div>
          </div>
        </div>
      </div>
      
      <div class="top-card">
        <div class="top-card-header">
          <span class="top-icon">🔋</span>
          <h3>最长续航 TOP3</h3>
        </div>
        <div class="top-list">
          <div 
            v-for="(car, index) in dashboardData?.top_range" 
            :key="car.id"
            class="top-item"
          >
            <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
            <div class="car-info">
              <div class="car-name">{{ car.model_name }}</div>
              <div class="car-manufacturer">{{ car.manufacturer }}</div>
            </div>
            <div class="car-value">{{ formatValue(car.electric_range, 'km') }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="bottom-row">
      <div class="chart-card small-chart">
        <div class="chart-header">
          <h3>🏆 预测模型热门排行</h3>
        </div>
        <div class="placeholder-content">
          <div class="placeholder-icon">📊</div>
          <p>功能即将上线</p>
          <div class="placeholder-bar">
            <div class="placeholder-item">
              <span>XGBoost回归</span>
              <div class="progress-bar"><div class="progress" style="width: 85%"></div></div>
            </div>
            <div class="placeholder-item">
              <span>随机森林</span>
              <div class="progress-bar"><div class="progress" style="width: 70%"></div></div>
            </div>
            <div class="placeholder-item">
              <span>神经网络</span>
              <div class="progress-bar"><div class="progress" style="width: 55%"></div></div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chart-card small-chart">
        <div class="chart-header">
          <h3>📈 预测次数统计</h3>
        </div>
        <div class="stats-placeholder">
          <div class="stat-box">
            <div class="stat-num">{{ dashboardData?.today_predictions || 0 }}</div>
            <div class="stat-text">今日预测</div>
          </div>
          <div class="stat-box">
            <div class="stat-num">{{ dashboardData?.week_predictions || 0 }}</div>
            <div class="stat-text">本周预测</div>
          </div>
          <div class="stat-box">
            <div class="stat-num">{{ dashboardData?.month_predictions || 0 }}</div>
            <div class="stat-text">本月预测</div>
          </div>
        </div>
      </div>
      
      <div class="chart-card small-chart">
        <div class="chart-header">
          <h3>🔥 用户热门车型</h3>
        </div>
        <div class="placeholder-content">
          <div class="placeholder-icon">⭐</div>
          <p>功能即将上线</p>
          <div class="hot-cars-placeholder">
            <div class="hot-car-item">
              <span class="hot-rank">1</span>
              <span class="hot-name">数据收集中...</span>
            </div>
            <div class="hot-car-item">
              <span class="hot-rank">2</span>
              <span class="hot-name">数据收集中...</span>
            </div>
            <div class="hot-car-item">
              <span class="hot-rank">3</span>
              <span class="hot-name">数据收集中...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-color);
}

.dashboard-header {
  margin-bottom: 24px;
}

.greeting-section {
  margin-bottom: 20px;
  
  h1 {
    font-size: 1.8rem;
    color: var(--text-color);
    margin: 0 0 8px 0;
    background: linear-gradient(135deg, #00c853, #00e676);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .current-time {
    color: #888;
    font-size: 0.9rem;
    margin: 0;
  }
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #00c853;
    box-shadow: 0 4px 20px rgba(0, 200, 83, 0.15);
  }
  
  .stat-icon {
    font-size: 2.5rem;
  }
  
  .stat-info {
    .stat-value {
      font-size: 1.8rem;
      font-weight: bold;
      color: #00c853;
    }
    
    .stat-label {
      color: #888;
      font-size: 0.85rem;
    }
  }
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.chart-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    h3 {
      margin: 0;
      color: var(--text-color);
      font-size: 1rem;
    }
  }
  
  .chart-tabs {
    display: flex;
    gap: 4px;
    
    button {
      padding: 4px 12px;
      border: none;
      background: transparent;
      color: #888;
      font-size: 0.8rem;
      cursor: pointer;
      border-radius: 4px;
      transition: all 0.2s;
      
      &:hover {
        color: #00c853;
      }
      
      &.active {
        background: #00c853;
        color: #fff;
      }
    }
  }
  
  .chart {
    height: 280px;
  }
}

.top-cards-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.top-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  
  .top-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    
    .top-icon {
      font-size: 1.5rem;
    }
    
    h3 {
      margin: 0;
      color: var(--text-color);
      font-size: 1rem;
    }
  }
  
  .top-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .top-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
    background: rgba(0, 200, 83, 0.05);
    border-radius: 8px;
    
    .rank {
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      font-size: 0.8rem;
      font-weight: bold;
      background: #444;
      color: #fff;
      
      &.rank-1 { background: linear-gradient(135deg, #ffd700, #ffb700); }
      &.rank-2 { background: linear-gradient(135deg, #c0c0c0, #a0a0a0); }
      &.rank-3 { background: linear-gradient(135deg, #cd7f32, #b87333); }
    }
    
    .car-info {
      flex: 1;
      min-width: 0;
      
      .car-name {
        color: var(--text-color);
        font-size: 0.9rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      .car-manufacturer {
        color: #888;
        font-size: 0.75rem;
      }
    }
    
    .car-value {
      color: #00c853;
      font-weight: bold;
      font-size: 0.9rem;
    }
  }
}

.bottom-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.small-chart {
  .chart-header h3 {
    font-size: 0.95rem;
  }
  
  .placeholder-content {
    text-align: center;
    padding: 20px 0;
    
    .placeholder-icon {
      font-size: 2.5rem;
      margin-bottom: 8px;
    }
    
    p {
      color: #666;
      margin: 0 0 16px 0;
      font-size: 0.85rem;
    }
  }
  
  .placeholder-bar {
    display: flex;
    flex-direction: column;
    gap: 10px;
    
    .placeholder-item {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.8rem;
      color: #888;
      
      .progress-bar {
        flex: 1;
        height: 8px;
        background: #333;
        border-radius: 4px;
        overflow: hidden;
        
        .progress {
          height: 100%;
          background: linear-gradient(90deg, #00c853, #00e676);
          border-radius: 4px;
        }
      }
    }
  }
  
  .stats-placeholder {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    
    .stat-box {
      padding: 12px;
      background: rgba(0, 200, 83, 0.05);
      border-radius: 8px;
      
      .stat-num {
        font-size: 1.2rem;
        font-weight: bold;
        color: #00c853;
      }
      
      .stat-text {
        font-size: 0.7rem;
        color: #888;
      }
    }
  }
  
  .hot-cars-placeholder {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .hot-car-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      background: rgba(0, 200, 83, 0.05);
      border-radius: 6px;
      
      .hot-rank {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #333;
        border-radius: 50%;
        font-size: 0.7rem;
        color: #fff;
      }
      
      .hot-name {
        color: #888;
        font-size: 0.8rem;
      }
    }
  }
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .top-cards-row {
    grid-template-columns: 1fr;
  }
  
  .bottom-row {
    grid-template-columns: 1fr;
  }
}

.dashboard-container {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.stat-card {
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
  
  .stat-icon {
    transition: transform 0.3s ease;
  }
  
  &:hover .stat-icon {
    transform: scale(1.1);
  }
}

.chart-card {
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00c853, transparent);
    transition: width 0.3s ease;
  }
  
  &:hover::after {
    width: 80%;
  }
}

.top-card {
  .top-item {
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateX(5px);
      background: rgba(0, 200, 83, 0.1);
    }
  }
}

.stats-placeholder .stat-box {
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 200, 83, 0.15);
  }
}

</style>