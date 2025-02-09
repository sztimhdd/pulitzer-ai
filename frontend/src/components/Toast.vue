<template>
  <TransitionGroup
    tag="div"
    enter-active-class="animate__animated animate__fadeInDown"
    leave-active-class="animate__animated animate__fadeOutUp"
    class="fixed top-4 right-4 z-50 space-y-2"
  >
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg"
    >
      {{ toast.message }}
    </div>
  </TransitionGroup>
</template>

<script setup>
import { ref } from 'vue'
import { TransitionGroup } from 'vue'

const toasts = ref([])

// 添加提示
function addToast(message, duration = 3000) {
  const id = Date.now()
  toasts.value.push({ id, message })
  setTimeout(() => {
    toasts.value = toasts.value.filter(toast => toast.id !== id)
  }, duration)
}

// 暴露方法给其他组件使用
defineExpose({ addToast })
</script> 