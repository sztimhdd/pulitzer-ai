<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <button
      v-for="type in articleTypes"
      :key="type.value"
      @click="$emit('select', type.value)"
      :class="[
        'p-4 rounded-lg text-left transition-colors',
        modelValue === type.value
          ? 'bg-primary-50 dark:bg-primary-900 ring-2 ring-primary-500'
          : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700'
      ]"
    >
      <div class="flex items-center space-x-3">
        <component 
          :is="type.icon" 
          class="w-6 h-6 text-primary-500"
        />
        <div>
          <h4 class="font-medium">{{ type.label }}</h4>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ type.description }}</p>
        </div>
      </div>
    </button>
  </div>
</template>

<script setup>
import { 
  DocumentTextIcon, 
  DocumentIcon, 
  NewspaperIcon, 
  AcademicCapIcon 
} from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  }
})

const articleTypes = [
  {
    value: 'blog',
    label: '博客文章',
    description: '适合个人观点和经验分享',
    icon: DocumentTextIcon
  },
  {
    value: 'technical',
    label: '技术文档',
    description: '详细的技术说明和教程',
    icon: DocumentIcon
  },
  {
    value: 'academic',
    label: '学术论文',
    description: '严谨的学术研究内容',
    icon: AcademicCapIcon
  },
  {
    value: 'news',
    label: '新闻报道',
    description: '时事新闻和深度报道',
    icon: NewspaperIcon
  }
]

defineEmits(['select', 'update:modelValue'])
</script> 