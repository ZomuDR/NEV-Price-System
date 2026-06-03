<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Refresh, TrendCharts, InfoFilled } from '@element-plus/icons-vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface Model {
  id: number
  name: string
  version: string
  model_type: string
  is_active: boolean
  metrics: Record<string, any>
  description: string
  created_at: string
}

const loading = ref(false)
const predicting = ref(false)
const models = ref<Model[]>([])
const selectedModelId = ref<number | null>(null)
const featureOptions = ref<any>({})
const predictedPrice = ref<number | null>(null)
const modelMetrics = ref<any>(null)
const similarCars = ref<any[]>([])

const predictMode = ref<'user' | 'manufacturer' | 'dealer'>('user')

const userVisibleFields = [
  'manufacturer', 'car_class', 'energy_type',
  'motor_power', 'electric_range', 'acceleration_time',
  'max_horsepower', 'max_speed'
]

const professionalFields = [
  'fuel_tank_volume', 'curb_weight', 'wheelbase', 'max_torque',
  'nedc_fuel_consumption', 'gear_count', 'width', 'displacement',
  'front_track', 'seat_count'
]

const getDefaultValue = (field: string) => {
  const active = activeModel.value
  const defaults = active?.feature_defaults || {}
  const v = defaults[field]
  return v === undefined || v === null ? 0 : v
}

const visibleFields = computed(() => {
  if (predictMode.value === 'manufacturer') return [...userVisibleFields, ...professionalFields]
  if (predictMode.value === 'dealer') return [...userVisibleFields, ...professionalFields]
  return userVisibleFields
})

const applyDefaultsForUserMode = () => {
  if (predictMode.value !== 'user') return
  professionalFields.forEach(f => {
    if (features.value[f] === null || features.value[f] === '' || features.value[f] === undefined) {
      features.value[f] = getDefaultValue(f)
    }
  })
}

const features = ref<Record<string, any>>({
  manufacturer: '',
  car_class: '',
  energy_type: '',
  motor_power: null,
  max_horsepower: null,
  max_speed: null,
  fuel_tank_volume: null,
  curb_weight: null,
  wheelbase: null,
  max_torque: null,
  nedc_fuel_consumption: null,
  gear_count: null,
  width: null,
  displacement: null,
  acceleration_time: null,
  electric_range: null,
  front_track: null,
  seat_count: null
})

const activeModel = computed(() => models.value.find(m => m.is_active))

const energyType = computed(() => features.value.energy_type)

const isPureElectric = computed(() => energyType.value === '纯电动')
const isHydrogenFuelCell = computed(() => energyType.value === '氢燃料电池')
const isPHEV = computed(() => energyType.value === '插电式混合动力')
const isEREV = computed(() => energyType.value === '增程式')

const showFuelRelatedFields = computed(() => {
  return !isPureElectric.value && !isHydrogenFuelCell.value
})

const showElectricRange = computed(() => {
  return true
})

watch(energyType, () => {
  if (isPureElectric.value || isHydrogenFuelCell.value) {
    features.value.fuel_tank_volume = 0
    features.value.nedc_fuel_consumption = 0
    features.value.displacement = 0
  }
})

const showField = (field: string) => {
  if (!visibleFields.value.includes(field)) return false
  if (!showFuelRelatedFields.value && ['fuel_tank_volume', 'nedc_fuel_consumption', 'displacement'].includes(field)) {
    return false
  }
  return true
}

watch(predictMode, () => {
  applyDefaultsForUserMode()
})

watch(activeModel, () => {
  applyDefaultsForUserMode()
})

const fetchModels = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/models/`)
    models.value = response.data
    const active = models.value.find(m => m.is_active)
    if (active) {
      selectedModelId.value = active.id
    }
    applyDefaultsForUserMode()
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  }
}

const fetchFeatureOptions = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/feature-options/`)
    featureOptions.value = response.data
  } catch (error) {
    ElMessage.error('获取特征选项失败')
  }
}

const handlePredict = async () => {
  if (!features.value.manufacturer || !features.value.car_class || !features.value.energy_type) {
    ElMessage.warning('请填写厂商、级别和能源类型')
    return
  }

  applyDefaultsForUserMode()

  predicting.value = true
  similarCars.value = []
  try {
    const response = await axios.post(`${API_BASE}/api/predict/`, {
      features: features.value,
      model_id: selectedModelId.value
    })
    predictedPrice.value = response.data.predicted_price
    modelMetrics.value = response.data.model_metrics

    if (predictMode.value === 'dealer') {
      const similarRes = await axios.post(`${API_BASE}/api/similar-cars/`, {
        features: features.value,
        predicted_price: predictedPrice.value
      })
      similarCars.value = similarRes.data.similar_cars || []
    }

    ElMessage.success('预测完成!')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '预测失败')
  } finally {
    predicting.value = false
  }
}

const handleModelChange = async (modelId: number) => {
  try {
    await axios.post(`${API_BASE}/api/models/${modelId}/activate/`)
    await fetchModels()
    ElMessage.success('模型已切换')
  } catch (error) {
    ElMessage.error('切换模型失败')
  }
}

const resetForm = () => {
  Object.keys(features.value).forEach(key => {
    features.value[key] = null
  })
  features.value.manufacturer = ''
  features.value.car_class = ''
  features.value.energy_type = ''
  predictedPrice.value = null
  modelMetrics.value = null
}

const getEnergyTypeTag = (type: string) => {
  const tags: Record<string, string> = {
    '纯电动': 'success',
    '插电式混合动力': 'warning',
    '增程式': 'info',
    '氢燃料电池': 'danger'
  }
  return tags[type] || ''
}

onMounted(() => {
  fetchModels()
  fetchFeatureOptions()
})
</script>

<template>
  <div class="predict-container">
    <div class="predict-header">
      <div class="header-title">
        <h1>价格预测</h1>
        <p class="subtitle">基于XGBoost算法的汽车价格预测模型</p>
      </div>
      <div class="header-controls">
        <div class="mode-selector">
          <span class="mode-label">预测模式:</span>
          <el-radio-group v-model="predictMode" size="small">
            <el-radio-button label="user">用户模式</el-radio-button>
            <el-radio-button label="manufacturer">制造商模式</el-radio-button>
            <el-radio-button label="dealer">销售商模式</el-radio-button>
          </el-radio-group>
        </div>
        <div class="model-selector">
          <span class="model-label">当前模型:</span>
          <el-select v-model="selectedModelId" @change="handleModelChange" style="width: 280px">
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="`${model.name} v${model.version}`"
              :value="model.id"
            >
              <div class="model-option">
                <span>{{ model.name }} v{{ model.version }}</span>
                <el-tag v-if="model.is_active" type="success" size="small">当前</el-tag>
              </div>
            </el-option>
          </el-select>
        </div>
      </div>
    </div>

    <div class="model-info" v-if="activeModel">
      <div class="info-item">
        <span class="info-label">模型类型</span>
        <span class="info-value">{{ activeModel.model_type }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">R2 Score</span>
        <span class="info-value">{{ activeModel.metrics?.r2_score || '-' }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">MAE</span>
        <span class="info-value">{{ activeModel.metrics?.mae || '-' }} 万元</span>
      </div>
      <div class="info-item">
        <span class="info-label">训练样本</span>
        <span class="info-value">{{ activeModel.metrics?.train_size || '-' }} 条</span>
      </div>
    </div>

    <div class="energy-type-notice" v-if="energyType">
      <el-tag :type="getEnergyTypeTag(energyType)" size="large">
        {{ energyType }}
      </el-tag>
      <span class="notice-text" v-if="isPureElectric">纯电动车型：无需填写油箱容积、油耗、排量</span>
      <span class="notice-text" v-else-if="isHydrogenFuelCell">氢燃料电池车型：无需填写油箱容积、油耗、排量</span>
      <span class="notice-text" v-else-if="isPHEV">插电混动车型：需填写所有参数</span>
      <span class="notice-text" v-else-if="isEREV">增程式车型：需填写所有参数</span>
    </div>

    <div class="predict-content">
      <div class="form-section">
        <div class="section-header">
          <h3>输入特征参数</h3>
          <el-button @click="resetForm" :icon="Refresh" size="small">重置</el-button>
        </div>

        <el-form label-width="140px" class="feature-form">
          <div class="form-row">
            <el-form-item label="厂商" required>
              <el-select v-model="features.manufacturer" filterable placeholder="选择厂商" style="width: 100%">
                <el-option
                  v-for="item in featureOptions.manufacturers"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="级别" required>
              <el-select v-model="features.car_class" placeholder="选择级别" style="width: 100%">
                <el-option
                  v-for="item in featureOptions.car_classes"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </div>

          <div class="form-row">
            <el-form-item label="能源类型" required>
              <el-select v-model="features.energy_type" placeholder="选择能源类型" style="width: 100%">
                <el-option
                  v-for="item in featureOptions.energy_types"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="电动机功率" v-if="showField('motor_power')">
              <el-input-number v-model="features.motor_power" :min="0" :max="1000" :step="10" style="width: 100%" />
            </el-form-item>
          </div>

          <div class="form-row" v-if="showField('max_horsepower') || showField('max_speed')">
            <el-form-item label="最大马力" v-if="showField('max_horsepower')">
              <el-input-number v-model="features.max_horsepower" :min="0" :max="2000" :step="10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="最高车速" v-if="showField('max_speed')">
              <el-input-number v-model="features.max_speed" :min="0" :max="500" :step="10" style="width: 100%" />
            </el-form-item>
          </div>

          <div class="form-row" v-if="showField('fuel_tank_volume') || showField('curb_weight')">
            <el-form-item label="油箱容积" v-if="showField('fuel_tank_volume')">
              <el-input-number v-model="features.fuel_tank_volume" :min="0" :max="200" :step="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="整备质量" v-if="showField('curb_weight')">
              <el-input-number v-model="features.curb_weight" :min="0" :max="5000" :step="50" style="width: 100%" />
            </el-form-item>
          </div>

          <div class="form-row" v-if="showField('wheelbase') || showField('max_torque')">
            <el-form-item label="轴距" v-if="showField('wheelbase')">
              <el-input-number v-model="features.wheelbase" :min="0" :max="4000" :step="10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="最大扭矩" v-if="showField('max_torque')">
              <el-input-number v-model="features.max_torque" :min="0" :max="2000" :step="10" style="width: 100%" />
            </el-form-item>
          </div>

          <div class="form-row" v-if="showField('nedc_fuel_consumption') || showField('gear_count')">
            <el-form-item label="NEDC油耗" v-if="showField('nedc_fuel_consumption')">
              <el-input-number v-model="features.nedc_fuel_consumption" :min="0" :max="50" :step="0.1" :precision="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="挡位数" v-if="showField('gear_count')">
              <el-input-number v-model="features.gear_count" :min="0" :max="20" :step="1" style="width: 100%" />
            </el-form-item>
          </div>

          <div class="form-row" v-if="showField('width') || showField('displacement')">
            <el-form-item label="宽度" v-if="showField('width')">
              <el-input-number v-model="features.width" :min="0" :max="2500" :step="10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="排量" v-if="showField('displacement')">
              <el-input-number v-model="features.displacement" :min="0" :max="10000" :step="100" style="width: 100%" />
            </el-form-item>
          </div>

          <div class="form-row" v-if="showField('acceleration_time') || showField('electric_range')">
            <el-form-item label="百公里加速" v-if="showField('acceleration_time')">
              <el-input-number v-model="features.acceleration_time" :min="0" :max="30" :step="0.1" :precision="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="纯电续航" v-if="showField('electric_range')">
              <el-input-number v-model="features.electric_range" :min="0" :max="2000" :step="10" style="width: 100%" />
            </el-form-item>
          </div>

          <div class="form-row" v-if="showField('front_track') || showField('seat_count')">
            <el-form-item label="前轮距" v-if="showField('front_track')">
              <el-input-number v-model="features.front_track" :min="0" :max="2000" :step="10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="座位数" v-if="showField('seat_count')">
              <el-input-number v-model="features.seat_count" :min="2" :max="9" :step="1" style="width: 100%" />
            </el-form-item>
          </div>
        </el-form>

        <div class="predict-action">
          <el-button type="primary" size="large" @click="handlePredict" :loading="predicting" :icon="TrendCharts">
            开始预测
          </el-button>
        </div>
      </div>

      <div class="result-section">
        <div class="section-header">
          <h3>预测结果</h3>
        </div>

        <div class="result-card" v-if="predictedPrice !== null">
          <div class="result-icon">💰</div>
          <div class="result-label">预测参考价格</div>
          <div class="result-value">
            {{ predictedPrice.toFixed(2) }}
            <span class="result-unit">万元</span>
          </div>
          <div class="result-note">
            <el-icon><InfoFilled /></el-icon>
            <span>此价格仅供参考，实际价格以市场为准</span>
          </div>
        </div>

        <div class="result-placeholder" v-else>
          <div class="placeholder-icon">📊</div>
          <p>填写特征参数后点击预测</p>
        </div>

        <div class="metrics-card" v-if="modelMetrics">
          <h4>模型评估指标</h4>
          <div class="metrics-grid">
            <div class="metric-item">
              <span class="metric-label">R2 Score</span>
              <span class="metric-value">{{ modelMetrics.r2_score }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">MAE</span>
              <span class="metric-value">{{ modelMetrics.mae }} 万</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">RMSE</span>
              <span class="metric-value">{{ modelMetrics.rmse }} 万</span>
            </div>
          </div>
        </div>

        <div class="compare-card" v-if="predictMode === 'dealer' && similarCars.length">
          <h4>相似车型参考</h4>
          <div class="compare-table">
            <div class="compare-row header">
              <span>车型</span>
              <span>厂商</span>
              <span>价格(万)</span>
            </div>
            <div class="compare-row" v-for="car in similarCars" :key="car.id">
              <span class="name" :title="car.model_name">{{ car.model_name }}</span>
              <span class="manufacturer">{{ car.manufacturer }}</span>
              <span class="price">{{ car.price }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.predict-container {
  padding: 20px;
  min-height: 100%;
  background: var(--bg-color);
}

.predict-header {
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
  
  .header-controls {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: flex-end;
    
    .mode-selector, .model-selector {
      display: flex;
      align-items: center;
      gap: 10px;
      
      .mode-label, .model-label {
        color: #888;
        font-size: 0.9rem;
        white-space: nowrap;
      }
    }
  }
}

.model-info {
  display: flex;
  gap: 20px;
  padding: 16px 20px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 20px;
  
  .info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    
    .info-label {
      font-size: 0.75rem;
      color: #888;
    }
    
    .info-value {
      font-size: 1rem;
      color: #00c853;
      font-weight: 500;
    }
  }
}

.energy-type-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(0, 200, 83, 0.05);
  border: 1px solid rgba(0, 200, 83, 0.2);
  border-radius: 8px;
  margin-bottom: 20px;
  
  .notice-text {
    color: #666;
    font-size: 0.9rem;
  }
}

.predict-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 20px;
}

.form-section, .result-section {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h3 {
    margin: 0;
    color: var(--text-color);
    font-size: 1.1rem;
  }
}

.feature-form {
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
}

.predict-action {
  margin-top: 24px;
  text-align: center;
  
  .el-button {
    width: 200px;
  }
}

.result-card {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, rgba(0, 200, 83, 0.1), rgba(0, 230, 118, 0.05));
  border-radius: 12px;
  margin-bottom: 20px;
  
  .result-icon {
    font-size: 3rem;
    margin-bottom: 16px;
  }
  
  .result-label {
    color: #888;
    font-size: 0.9rem;
    margin-bottom: 8px;
  }
  
  .result-value {
    font-size: 3rem;
    font-weight: bold;
    color: #00c853;
    
    .result-unit {
      font-size: 1.2rem;
      font-weight: normal;
    }
  }
  
  .result-note {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    margin-top: 16px;
    color: #888;
    font-size: 0.8rem;
  }
}

.result-placeholder {
  text-align: center;
  padding: 60px 20px;
  
  .placeholder-icon {
    font-size: 4rem;
    margin-bottom: 16px;
  }
  
  p {
    color: #888;
    font-size: 1rem;
  }
}

.metrics-card {
  padding: 16px;
  background: rgba(0, 200, 83, 0.05);
  border-radius: 8px;
  
  h4 {
    margin: 0 0 12px 0;
    color: var(--text-color);
    font-size: 0.9rem;
  }
  
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    
    .metric-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .metric-label {
        font-size: 0.75rem;
        color: #888;
      }
      
      .metric-value {
        font-size: 1rem;
        color: #00c853;
        font-weight: 500;
      }
    }
  }
}

.compare-card {
  margin-top: 16px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.06);
  border: 1px solid rgba(102, 126, 234, 0.15);
  border-radius: 10px;
  
  h4 {
    margin: 0 0 12px 0;
    color: var(--text-color);
    font-size: 0.9rem;
  }
  
  .compare-table {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .compare-row {
    display: grid;
    grid-template-columns: 1fr 90px 90px;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid var(--border-color);
    
    &.header {
      background: transparent;
      border: none;
      padding: 0 12px;
      color: #888;
      font-size: 0.8rem;
    }
    
    .name {
      color: var(--text-color);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .manufacturer {
      color: #666;
      text-align: center;
    }
    
    .price {
      color: #667eea;
      font-weight: 600;
      text-align: right;
    }
  }
}

.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

@media (max-width: 1200px) {
  .predict-content {
    grid-template-columns: 1fr;
  }
  
  .feature-form .form-row {
    grid-template-columns: 1fr;
  }
}

.predict-container {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-section {
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00c853, #00e676, #69f0ae);
    border-radius: 12px 12px 0 0;
  }
}

.result-section {
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 12px 12px 0 0;
  }
}

.result-card {
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(0, 200, 83, 0.1) 0%, transparent 70%);
    animation: pulse 3s ease-in-out infinite;
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.model-info {
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #00c853, #00e676);
    border-radius: 3px;
  }
}

.energy-type-notice {
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #00c853, #69f0ae);
  }
}

.predict-action .el-button {
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 200, 83, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
}

</style>