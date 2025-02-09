<template>
  <div class="space-y-4">
    <h3 class="font-medium text-lg">写作进度</h3>
    
    <!-- 进度条 -->
    <div class="relative">
      <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
        <div 
          class="h-full bg-primary-500 rounded-full transition-all duration-500"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>
    
    <!-- 阶段列表 -->
    <div class="space-y-4">
      <div 
        v-for="(stage, index) in stages" 
        :key="index"
        class="flex items-center"
      >
        <div 
          :class="[
            'w-6 h-6 rounded-full flex items-center justify-center mr-3',
            getStageClass(index)
          ]"
        >
          <CheckIcon
            v-if="currentStage > index"
            class="w-4 h-4"
          />
          <span v-else>{{ index + 1 }}</span>
        </div>
        <span 
          :class="[
            'text-sm',
            currentStage >= index 
              ? 'text-gray-900 dark:text-gray-100' 
              : 'text-gray-400'
          ]"
        >
          {{ stage.label }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CheckIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  currentStage: {
    type: Number,
    required: true
  }
})

const stages = [
  { label: '确定主题' },
  { label: '规划大纲' },
  { label: '内容讨论' },
  { label: '生成草稿' },
  { label: '完善文章' }
]

const progress = computed(() => {
  return Math.min(Math.round((props.currentStage / stages.length) * 100), 100)
})

function getStageClass(index) {
  if (props.currentStage > index) {
    return 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400'
  }
  if (props.currentStage === index) {
    return 'bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-400'
  }
  return 'bg-gray-100 text-gray-400 dark:bg-gray-800'
}
</script> 