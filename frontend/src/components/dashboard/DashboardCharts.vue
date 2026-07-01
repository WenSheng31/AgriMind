<template>
  <div>
    <h2 class="mb-3 text-lg font-semibold text-slate-800 dark:text-white">農場數據總覽</h2>

    <!-- 趨勢（近 30 天） -->
    <div class="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
      <ChartCard
        title="溫度 / 濕度趨勢（近 30 天）"
        class="lg:col-span-2"
        :loading="loading"
        :empty="!timeSeries.length"
      >
        <TemperatureHumidityChart :time-series="timeSeries" :farm-names="farmNames" />
      </ChartCard>

      <ChartCard title="降水量（近 30 天）" :loading="loading" :empty="!timeSeries.length">
        <PrecipitationChart :time-series="timeSeries" :farm-names="farmNames" />
      </ChartCard>
    </div>

    <!-- 最新狀態 -->
    <div class="grid grid-cols-1 gap-4">
      <ChartCard title="各農場土壤養分 (NPK)" :loading="loading" :empty="!latestList.length">
        <SoilNutrientChart :latest-per-farm="latestList" />
      </ChartCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import ChartCard from './ChartCard.vue'
import TemperatureHumidityChart from './TemperatureHumidityChart.vue'
import PrecipitationChart from './PrecipitationChart.vue'
import SoilNutrientChart from './SoilNutrientChart.vue'

const { showToast } = useToast()

const loading = ref(false)
const timeSeries = ref([])
const latestList = ref([])

const farmNames = computed(() => {
  const map = {}
  timeSeries.value.forEach((d) => {
    if (!map[d.farm_id]) map[d.farm_id] = d.farm_name
  })
  return map
})

async function loadData() {
  loading.value = true
  try {
    const data = await api.getDashboardOverview(30)
    timeSeries.value = data.time_series
    latestList.value = data.latest_per_farm
  } catch (error) {
    timeSeries.value = []
    latestList.value = []
    showToast(error.message || '載入農場數據失敗', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
