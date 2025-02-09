<script setup>
import { ref, provide } from 'vue'
import Toast from './components/Toast.vue'
import LoadingOverlay from './components/LoadingOverlay.vue'

const toast = ref(null)
const loading = ref(false)
const loadingMessage = ref('')

// 创建全局方法
const globalMethods = {
  showToast: (message) => {
    toast.value?.addToast(message)
  },
  showLoading: (message = '加载中...') => {
    loadingMessage.value = message
    loading.value = true
  },
  hideLoading: () => {
    loading.value = false
    loadingMessage.value = ''
  }
}

// 提供全局方法
provide('globalMethods', globalMethods)
</script>

<template>
  <Toast ref="toast" />
  <LoadingOverlay 
    :loading="loading"
    :message="loadingMessage"
  />
  <router-view v-slot="{ Component }">
    <transition
      enter-active-class="animate__animated animate__fadeIn"
      leave-active-class="animate__animated animate__fadeOut"
      mode="out-in"
    >
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<style>
/* 全局样式 */
.prose {
  @apply text-gray-900 dark:text-gray-100;
  line-height: 1.6;
}

.prose p {
  @apply mb-4;
}

.prose h1, .prose h2, .prose h3, .prose h4 {
  @apply font-bold mb-4;
}

.prose h1 { @apply text-2xl; }
.prose h2 { @apply text-xl; }
.prose h3 { @apply text-lg; }

.prose ul, .prose ol {
  @apply mb-4 pl-6;
}

.prose ul { @apply list-disc; }
.prose ol { @apply list-decimal; }

.prose a {
  @apply text-primary-600 dark:text-primary-400 hover:underline;
}

.prose blockquote {
  @apply pl-4 border-l-4 border-gray-300 dark:border-gray-600 italic;
}

.prose code {
  @apply bg-gray-100 dark:bg-gray-800 px-1 rounded;
}

.prose pre {
  @apply bg-gray-100 dark:bg-gray-800 p-4 rounded-lg mb-4 overflow-x-auto;
}
</style>
