<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-sm w-full mx-4 shadow-xl">
      <div class="flex flex-col items-center space-y-4">
        <!-- 动画效果 -->
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
        
        <!-- 加载提示文字 -->
        <div class="text-center">
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">{{ title }}</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ message }}</p>
          <p v-if="showTip" class="mt-4 text-xs text-gray-400 dark:text-gray-500">
            AI正在思考中，这可能需要一些时间...
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: '请稍候'
  },
  message: {
    type: String,
    default: 'AI正在处理您的请求...'
  }
})

const showTip = ref(false)

// 如果加载时间超过5秒，显示提示信息
onMounted(() => {
  setTimeout(() => {
    showTip.value = true
  }, 5000)
})
</script> 