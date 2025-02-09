<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
    <h3 class="text-lg font-medium mb-6">文章分析</h3>
    
    <!-- 基本统计 -->
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400">字数</div>
        <div class="text-2xl font-semibold mt-1">{{ stats.wordCount }}</div>
      </div>
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
        <div class="text-sm text-gray-500 dark:text-gray-400">预计阅读时间</div>
        <div class="text-2xl font-semibold mt-1">{{ readingTime }}分钟</div>
      </div>
    </div>
    
    <!-- 详细分析 -->
    <div class="space-y-4">
      <!-- 关键词 -->
      <div>
        <h4 class="text-sm font-medium mb-2">主要关键词</h4>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="keyword in stats.keywords"
            :key="keyword.word"
            class="px-2 py-1 text-sm rounded-full bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-400"
          >
            {{ keyword.word }} ({{ keyword.count }})
          </span>
        </div>
      </div>
      
      <!-- 段落分析 -->
      <div>
        <h4 class="text-sm font-medium mb-2">段落分布</h4>
        <div class="h-24">
          <canvas ref="paragraphChart"></canvas>
        </div>
      </div>
      
      <!-- 可读性分析 -->
      <div>
        <h4 class="text-sm font-medium mb-2">可读性分析</h4>
        <div class="space-y-2">
          <div
            v-for="(score, metric) in stats.readability"
            :key="metric"
            class="flex items-center"
          >
            <span class="text-sm text-gray-600 dark:text-gray-400 w-24">
              {{ getMetricLabel(metric) }}
            </span>
            <div class="flex-1 ml-2">
              <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="getScoreClass(score)"
                  :style="{ width: `${score}%` }"
                ></div>
              </div>
            </div>
            <span class="ml-2 text-sm text-gray-500">{{ score }}%</span>
          </div>
        </div>
      </div>
      
      <!-- 情感分析 -->
      <div>
        <h4 class="text-sm font-medium mb-2">情感倾向</h4>
        <div class="flex items-center space-x-2">
          <EmojiSadIcon 
            class="w-5 h-5 text-gray-400"
          />
          <div class="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
            <div
              class="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full"
              :style="{ width: `${stats.sentiment}%` }"
            ></div>
          </div>
          <EmojiHappyIcon 
            class="w-5 h-5 text-gray-400"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import { EmojiHappyIcon, EmojiSadIcon } from '@heroicons/vue/24/outline'

Chart.register(...registerables)

const props = defineProps({
  stats: {
    type: Object,
    required: true
  }
})

const paragraphChart = ref(null)
let chart = null

const readingTime = computed(() => {
  return Math.ceil(props.stats.wordCount / 300) // 假设阅读速度为300字/分钟
})

const metricLabels = {
  clarity: '清晰度',
  conciseness: '简洁度',
  coherence: '连贯性',
  engagement: '吸引力'
}

function getMetricLabel(metric) {
  return metricLabels[metric] || metric
}

function getScoreClass(score) {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}

function initChart() {
  if (chart) {
    chart.destroy()
  }
  
  const ctx = paragraphChart.value.getContext('2d')
  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: props.stats.paragraphLengths.map((_, i) => `P${i + 1}`),
      datasets: [{
        label: '段落长度',
        data: props.stats.paragraphLengths,
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  })
}

onMounted(() => {
  initChart()
})

watch(() => props.stats, () => {
  initChart()
}, { deep: true })
</script> 