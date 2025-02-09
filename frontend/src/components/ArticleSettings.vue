<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-medium">文章设置</h3>
      <button 
        @click="saveSettings"
        class="text-primary-600 hover:text-primary-700 dark:text-primary-400"
      >
        <CheckIcon class="w-5 h-5" />
      </button>
    </div>

    <div class="space-y-6">
      <!-- 写作风格 -->
      <div>
        <label class="block text-sm font-medium mb-2">写作风格</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="style in writingStyles"
            :key="style.value"
            @click="settings.style = style.value"
            :class="[
              'px-3 py-2 rounded-lg text-sm text-center transition-colors',
              settings.style === style.value
                ? 'bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-400'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            ]"
          >
            {{ style.label }}
          </button>
        </div>
      </div>

      <!-- 专业程度 -->
      <div>
        <label class="block text-sm font-medium mb-2">
          专业程度: {{ settings.professionLevel }}%
        </label>
        <input
          v-model="settings.professionLevel"
          type="range"
          min="0"
          max="100"
          step="10"
          class="w-full"
        >
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>通俗易懂</span>
          <span>专业深入</span>
        </div>
      </div>

      <!-- 语气设置 -->
      <div>
        <label class="block text-sm font-medium mb-2">语气</label>
        <select
          v-model="settings.tone"
          class="w-full px-3 py-2 rounded-lg border dark:bg-gray-700 dark:border-gray-600"
        >
          <option 
            v-for="tone in toneOptions" 
            :key="tone.value" 
            :value="tone.value"
          >
            {{ tone.label }}
          </option>
        </select>
      </div>

      <!-- 引用设置 -->
      <div>
        <label class="block text-sm font-medium mb-2">引用和参考</label>
        <div class="space-y-2">
          <label class="flex items-center">
            <input
              v-model="settings.includeReferences"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            >
            <span class="ml-2 text-sm">包含参考文献</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="settings.includeQuotes"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            >
            <span class="ml-2 text-sm">包含专家引用</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { CheckIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const settings = ref({ ...props.defaultSettings })

const writingStyles = [
  { value: 'narrative', label: '叙述性' },
  { value: 'analytical', label: '分析性' },
  { value: 'argumentative', label: '论证性' },
  { value: 'descriptive', label: '描述性' }
]

const toneOptions = [
  { value: 'formal', label: '正式' },
  { value: 'professional', label: '专业' },
  { value: 'casual', label: '随意' },
  { value: 'friendly', label: '友好' },
  { value: 'humorous', label: '幽默' }
]

// 监听设置变化
watch(settings, (newSettings) => {
  emit('update:modelValue', newSettings)
}, { deep: true })

// 保存设置
function saveSettings() {
  emit('save', settings.value)
}

// 初始化设置
watch(() => props.modelValue, (newValue) => {
  settings.value = { ...newValue }
}, { immediate: true })
</script> 