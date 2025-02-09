<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-medium">历史会话</h3>
      <div class="flex items-center space-x-2">
        <input
          v-model="searchQuery"
          type="text"
          class="px-3 py-1 text-sm rounded-lg border dark:bg-gray-700 dark:border-gray-600"
          placeholder="搜索会话..."
        >
        <button 
          @click="sortOrder = sortOrder === 'desc' ? 'asc' : 'desc'"
          class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <ArrowsUpDownIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <div class="space-y-4">
      <TransitionGroup
        enter-active-class="animate__animated animate__fadeIn"
        leave-active-class="animate__animated animate__fadeOut"
      >
        <div 
          v-for="session in filteredSessions" 
          :key="session.id"
          class="group bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg hover:shadow-xl transition-all"
        >
          <div class="flex items-start justify-between">
            <div 
              class="flex-1 cursor-pointer"
              @click="$emit('select', session.id)"
            >
              <h4 class="font-medium group-hover:text-primary-600 dark:group-hover:text-primary-400">
                {{ session.topic }}
              </h4>
              <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                <span>{{ getArticleType(session.type) }}</span>
                <span>{{ formatDate(session.lastInteraction) }}</span>
                <span :class="getStateClass(session.state)">
                  {{ getStateLabel(session.state) }}
                </span>
              </div>
            </div>
            <button 
              @click="deleteSession(session.id)"
              class="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-100 dark:hover:bg-red-900 text-red-600 dark:text-red-400"
            >
              <TrashIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowsUpDownIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { useSessionStore } from '../stores/session'

const props = defineProps({
  sessions: {
    type: Array,
    required: true
  }
})

const searchQuery = ref('')
const sortOrder = ref('desc')
const sessionStore = useSessionStore()

const articleTypes = {
  blog: '博客文章',
  technical: '技术文档',
  academic: '学术论文',
  news: '新闻报道'
}

const stateLabels = {
  TOPIC_SELECTION: '主题选择',
  OUTLINE_REVIEW: '大纲审查',
  INTERVIEW: '内容访谈',
  DRAFT_GENERATION: '生成草稿',
  DRAFT_REVIEW: '修改完善',
  COMPLETE: '已完成'
}

const stateClasses = {
  TOPIC_SELECTION: 'text-blue-600 dark:text-blue-400',
  OUTLINE_REVIEW: 'text-purple-600 dark:text-purple-400',
  INTERVIEW: 'text-yellow-600 dark:text-yellow-400',
  DRAFT_GENERATION: 'text-orange-600 dark:text-orange-400',
  DRAFT_REVIEW: 'text-green-600 dark:text-green-400',
  COMPLETE: 'text-gray-600 dark:text-gray-400'
}

const filteredSessions = computed(() => {
  let result = [...props.sessions]
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(session => 
      session.topic.toLowerCase().includes(query)
    )
  }
  
  result.sort((a, b) => {
    const dateA = new Date(a.lastInteraction)
    const dateB = new Date(b.lastInteraction)
    return sortOrder.value === 'desc' ? dateB - dateA : dateA - dateB
  })
  
  return result
})

function formatDate(date) {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function getArticleType(type) {
  return articleTypes[type] || type
}

function getStateLabel(state) {
  return stateLabels[state] || state
}

function getStateClass(state) {
  return stateClasses[state] || ''
}

async function deleteSession(sessionId) {
  if (confirm('确定要删除这个会话吗？')) {
    try {
      await sessionStore.deleteSession(sessionId)
    } catch (error) {
      console.error('删除会话失败:', error)
    }
  }
}

defineEmits(['select'])
</script> 