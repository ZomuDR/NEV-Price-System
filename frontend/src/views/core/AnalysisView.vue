<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  RadarComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

use([
  CanvasRenderer,
  BarChart,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  RadarComponent
])

interface Car {
  id: number
  model_name: string
  manufacturer: string
  car_class: string
  energy_type: string
  motor_power: number | null
  max_horsepower: number | null
  max_speed: number | null
  curb_weight: number | null
  wheelbase: number | null
  max_torque: number | null
  acceleration_time: number | null
  electric_range: number | null
  seat_count: number | null
  price: number
}

const cars = ref<Car[]>([])
const loading = ref(false)

const carAId = ref<number | null>(null)
const carBId = ref<number | null>(null)

const carA = computed(() => cars.value.find(c => c.id === carAId.value) || null)
const carB = computed(() => cars.value.find(c => c.id === carBId.value) || null)

const fetchCars = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/cars/`, {
      params: { page: 1, page_size: 2000 }
    })
    cars.value = response.data.results || response.data
  } catch (e) {
    ElMessage.error('获取车型列表失败')
  } finally {
    loading.value = false
  }
}

const toNum = (v: any) => {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

const radarIndicators = computed(() => {
  const a = carA.value
  const b = carB.value
  if (!a || !b) return []

  const fields = [
    { key: 'motor_power', name: '功率(kW)' },
    { key: 'max_horsepower', name: '马力(Ps)' },
    { key: 'max_speed', name: '极速(km/h)' },
    { key: 'electric_range', name: '续航(km)' },
    { key: 'max_torque', name: '扭矩(N·m)' },
    { key: 'wheelbase', name: '轴距(mm)' },
    { key: 'curb_weight', name: '整备质量(kg)' },
    { key: 'seat_count', name: '座位数' }
  ]

  return fields.map(f => {
    const maxVal = Math.max(toNum((a as any)[f.key]), toNum((b as any)[f.key]))
    return { name: f.name, max: maxVal > 0 ? maxVal * 1.2 : 1 }
  })
})

const radarOption = computed(() => {
  const a = carA.value
  const b = carB.value
  if (!a || !b) return {}

  const valueA = [
    toNum(a.motor_power),
    toNum(a.max_horsepower),
    toNum(a.max_speed),
    toNum(a.electric_range),
    toNum(a.max_torque),
    toNum(a.wheelbase),
    toNum(a.curb_weight),
    toNum(a.seat_count)
  ]

  const valueB = [
    toNum(b.motor_power),
    toNum(b.max_horsepower),
    toNum(b.max_speed),
    toNum(b.electric_range),
    toNum(b.max_torque),
    toNum(b.wheelbase),
    toNum(b.curb_weight),
    toNum(b.seat_count)
  ]

  return {
    title: {
      text: '核心参数雷达对比',
      left: 'center',
      textStyle: { color: '#00c853', fontSize: 16 }
    },
    tooltip: { trigger: 'item' },
    legend: {
      bottom: 0,
      textStyle: { color: '#666' }
    },
    radar: {
      indicator: radarIndicators.value,
      splitNumber: 4,
      axisName: { color: '#666', fontSize: 11 },
      splitLine: { lineStyle: { color: ['#e5e7eb'] } },
      splitArea: { areaStyle: { color: ['rgba(0,0,0,0)', 'rgba(0,200,83,0.02)'] } },
      axisLine: { lineStyle: { color: '#e5e7eb' } }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: valueA,
            name: `${a.manufacturer} ${a.model_name}`,
            itemStyle: { color: '#00c853' },
            lineStyle: { color: '#00c853' },
            areaStyle: { color: 'rgba(0,200,83,0.15)' }
          },
          {
            value: valueB,
            name: `${b.manufacturer} ${b.model_name}`,
            itemStyle: { color: '#667eea' },
            lineStyle: { color: '#667eea' },
            areaStyle: { color: 'rgba(102,126,234,0.15)' }
          }
        ]
      }
    ]
  }
})

const barOption = computed(() => {
  const a = carA.value
  const b = carB.value
  if (!a || !b) return {}

  const labels = ['价格(万)', '百公里加速(s)', '续航(km)']
  const aVals = [toNum(a.price), toNum(a.acceleration_time), toNum(a.electric_range)]
  const bVals = [toNum(b.price), toNum(b.acceleration_time), toNum(b.electric_range)]

  return {
    title: {
      text: '关键指标柱状对比',
      left: 'center',
      textStyle: { color: '#00c853', fontSize: 16 }
    },
    tooltip: { trigger: 'axis' },
    legend: {
      bottom: 0,
      textStyle: { color: '#666' }
    },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      data: labels,
      axisLabel: { color: '#666' },
      axisLine: { lineStyle: { color: '#ddd' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#eee' } }
    },
    series: [
      {
        name: '车型A',
        type: 'bar',
        data: aVals,
        itemStyle: { color: '#00c853', borderRadius: [6, 6, 0, 0] }
      },
      {
        name: '车型B',
        type: 'bar',
        data: bVals,
        itemStyle: { color: '#667eea', borderRadius: [6, 6, 0, 0] }
      }
    ]
  }
})

const summary = computed(() => {
  const a = carA.value
  const b = carB.value
  if (!a || !b) return []

  const rows = [
    { label: '价格(万)', a: a.price, b: b.price, better: a.price < b.price ? 'A' : (a.price > b.price ? 'B' : '-') },
    { label: '加速(s)（越小越好）', a: a.acceleration_time, b: b.acceleration_time, better: toNum(a.acceleration_time) < toNum(b.acceleration_time) ? 'A' : (toNum(a.acceleration_time) > toNum(b.acceleration_time) ? 'B' : '-') },
    { label: '续航(km)', a: a.electric_range, b: b.electric_range, better: toNum(a.electric_range) > toNum(b.electric_range) ? 'A' : (toNum(a.electric_range) < toNum(b.electric_range) ? 'B' : '-') },
    { label: '功率(kW)', a: a.motor_power, b: b.motor_power, better: toNum(a.motor_power) > toNum(b.motor_power) ? 'A' : (toNum(a.motor_power) < toNum(b.motor_power) ? 'B' : '-') },
    { label: '马力(Ps)', a: a.max_horsepower, b: b.max_horsepower, better: toNum(a.max_horsepower) > toNum(b.max_horsepower) ? 'A' : (toNum(a.max_horsepower) < toNum(b.max_horsepower) ? 'B' : '-') }
  ]

  return rows
})

onMounted(() => {
  fetchCars()
})
</script>

<template>
  <div class="analysis-container" v-loading="loading">
    <div class="analysis-header">
      <div class="header-title">
        <h1>市场分析</h1>
        <p class="subtitle">选择两款车型，进行多维度参数对比</p>
      </div>
      <el-button @click="fetchCars" :icon="Refresh">刷新车型</el-button>
    </div>

    <div class="select-card">
      <div class="select-row">
        <div class="select-item">
          <div class="label">车型A</div>
          <el-select v-model="carAId" filterable placeholder="选择车型A" style="width: 100%">
            <el-option v-for="car in cars" :key="car.id" :label="`${car.manufacturer} ${car.model_name}`" :value="car.id" />
          </el-select>
        </div>
        <div class="select-item">
          <div class="label">车型B</div>
          <el-select v-model="carBId" filterable placeholder="选择车型B" style="width: 100%">
            <el-option v-for="car in cars" :key="car.id" :label="`${car.manufacturer} ${car.model_name}`" :value="car.id" />
          </el-select>
        </div>
      </div>
      
      <div class="hint" v-if="!carA || !carB">
        请选择两款车型后查看对比图表
      </div>
    </div>

    <div class="charts" v-if="carA && carB">
      <div class="chart-card">
        <v-chart class="chart" :option="radarOption" autoresize />
      </div>
      <div class="chart-card">
        <v-chart class="chart" :option="barOption" autoresize />
      </div>

      <div class="summary-card">
        <h3>对比结论</h3>
        <div class="summary-grid">
          <div class="summary-row header">
            <span>指标</span>
            <span>A</span>
            <span>B</span>
            <span>优势</span>
          </div>
          <div class="summary-row" v-for="(row, idx) in summary" :key="idx">
            <span class="metric">{{ row.label }}</span>
            <span>{{ row.a ?? '-' }}</span>
            <span>{{ row.b ?? '-' }}</span>
            <span class="better" :class="row.better === 'A' ? 'a' : (row.better === 'B' ? 'b' : '')">
              {{ row.better }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.analysis-container {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-color);
}

.analysis-header {
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

.select-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;

  .select-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .label {
    color: #666;
    font-size: 0.85rem;
    margin-bottom: 8px;
  }

  .hint {
    margin-top: 12px;
    color: #888;
    font-size: 0.9rem;
  }
}

.charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  .chart-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px;

    .chart {
      height: 360px;
    }
  }

  .summary-card {
    grid-column: span 2;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;

    h3 {
      margin: 0 0 12px 0;
      color: var(--text-color);
      font-size: 1.05rem;
    }

    .summary-grid {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .summary-row {
      display: grid;
      grid-template-columns: 1.4fr 1fr 1fr 0.6fr;
      gap: 10px;
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: rgba(255, 255, 255, 0.85);

      &.header {
        border: none;
        background: transparent;
        color: #888;
        font-size: 0.85rem;
        padding: 0 12px;
      }

      .metric {
        color: var(--text-color);
      }

      .better {
        font-weight: 700;
        text-align: center;

        &.a {
          color: #00c853;
        }

        &.b {
          color: #667eea;
        }
      }
    }
  }
}

@media (max-width: 1100px) {
  .charts {
    grid-template-columns: 1fr;

    .summary-card {
      grid-column: auto;
    }
  }

  .select-card .select-row {
    grid-template-columns: 1fr;
  }
}
</style>
