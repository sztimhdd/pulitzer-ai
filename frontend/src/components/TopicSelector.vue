<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-medium">推荐主题</h3>
      <button 
        @click="refreshTopics"
        class="text-primary-600 hover:text-primary-700 dark:text-primary-400"
      >
        <ArrowPathIcon class="w-5 h-5" />
      </button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <button
        v-for="topic in suggestedTopics"
        :key="topic.id"
        @click="$emit('select', topic)"
        class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow text-left"
      >
        <h4 class="font-medium mb-2">{{ topic.title }}</h4>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ topic.description }}</p>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { 
  ArrowPathIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  TrashIcon,
  ArrowLeftIcon,
  SunIcon,
  MoonIcon,
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  DocumentIcon,
  NewspaperIcon,
  AcademicCapIcon
} from '@heroicons/vue/24/outline'

const suggestedTopics = ref([
  {
    id: 1,
    title: '人工智能对未来工作的影响',
    description: '探讨AI技术发展对就业市场和工作方式的改变'
  },
  {
    id: 2,
    title: '可持续发展与环保科技',
    description: '分析新能源技术和环保创新对可持续发展的贡献'
  },
  {
    id: 3,
    title: '数字化转型与企业创新',
    description: '研究企业如何通过数字化转型提升竞争力'
  },
  {
    id: 4,
    title: '远程办公与团队协作',
    description: '探讨后疫情时代的工作模式变革与挑战'
  }
])

function refreshTopics() {
  // TODO: 从API获取新的推荐主题
  suggestedTopics.value = suggestedTopics.value.reverse()
}

defineEmits(['select'])
</script> 