<template>
  <TransitionGroup
    tag="div"
    enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut"
  >
    <div 
      v-if="loading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl">
        <div class="flex items-center space-x-3">
          <div class="relative">
            <div class="animate-spin rounded-full h-6 w-6 border-4 border-primary-500 border-t-transparent"></div>
            <!-- 进度指示器 -->
            <div 
              v-if="progress"
              class="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs text-gray-500"
            >
              {{ progress }}%
            </div>
          </div>
          <div class="flex flex-col">
            <span class="text-gray-700 dark:text-gray-200">{{ message }}</span>
            <!-- 子任务提示 -->
            <span 
              v-if="subTask"
              class="text-xs text-gray-500 mt-1"
            >
              {{ subTask }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </TransitionGroup>
</template>

<script setup>
defineProps({
  loading: Boolean,
  message: String,
  progress: Number,
  subTask: String
})
</script> 