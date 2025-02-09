<template>
  <Transition
    enter-active-class="animate__animated animate__fadeIn"
    leave-active-class="animate__animated animate__fadeOut"
  >
    <div 
      v-if="loading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl">
        <div class="flex items-center space-x-3">
          <div class="animate-spin rounded-full h-6 w-6 border-4 border-primary-500 border-t-transparent"></div>
          <span class="text-gray-700 dark:text-gray-200">{{ message }}</span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  loading: Boolean,
  message: String
})
</script> 