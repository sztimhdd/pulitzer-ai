<template>
  <div class="min-h-screen p-4 md:p-8">
    <!-- 顶部导航 -->
    <nav class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold">AI 写作助手</h1>
      <button 
        @click="toggleDarkMode"
        class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
      >
        <SunIcon v-if="isDark" class="w-6 h-6" />
        <MoonIcon v-else class="w-6 h-6" />
      </button>
    </nav>

    <div class="max-w-4xl mx-auto">
      <div class="grid gap-8 md:grid-cols-2">
        <!-- 左侧：创建新会话 -->
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <h2 class="text-xl font-semibold mb-4">开始新的写作</h2>
          <form @submit.prevent="createNewSession" class="space-y-8">
            <div>
              <label class="block text-sm font-medium mb-4">选择文章类型</label>
              <ArticleTypeSelector v-model="type" @select="type = $event" />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">文章主题</label>
              <input
                v-model="topic"
                type="text"
                class="w-full px-4 py-2 rounded-lg border dark:bg-gray-700 dark:border-gray-600"
                placeholder="输入文章主题..."
                required
              >
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">目标字数</label>
              <input
                v-model="wordCount"
                type="number"
                min="100"
                step="100"
                class="w-full px-4 py-2 rounded-lg border dark:bg-gray-700 dark:border-gray-600"
                placeholder="输入目标字数..."
                required
              >
            </div>

            <button 
              type="submit"
              class="btn btn-primary w-full"
              :disabled="!topic || !topic.trim()"
            >
              开始写作
            </button>
          </form>
        </div>

        <!-- 右侧：推荐主题和历史会话 -->
        <div class="space-y-8">
          <!-- 推荐主题 -->
          <TopicSelector @select="selectTopic" />
          
          <!-- 历史会话 -->
          <SessionHistory 
            :sessions="sessions"
            @select="goToSession"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useDark, useToggle } from '@vueuse/core'
import { useSessionStore } from '../stores/session'
import { SunIcon, MoonIcon } from '@heroicons/vue/24/outline'
import ArticleTypeSelector from '../components/ArticleTypeSelector.vue'
import TopicSelector from '../components/TopicSelector.vue'
import SessionHistory from '../components/SessionHistory.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const isDark = useDark()
const toggleDarkMode = useToggle(isDark)
const methods = inject('globalMethods')

const topic = ref('')
const type = ref('blog')
const wordCount = ref(1000)

const sessions = computed(() => sessionStore.sessions)

async function createNewSession() {
  if (!topic.value || !topic.value.trim()) {
    methods?.showToast('请输入文章主题')
    return
  }

  try {
    const session = await sessionStore.createSession(
      topic.value,
      type.value,
      Number(wordCount.value)
    )

    if (session?.id) {
      await router.push(`/session/${session.id}`)
    } else {
      throw new Error('创建会话失败：未获取到会话ID')
    }
  } catch (error) {
    console.error('创建会话失败:', error)
    methods?.showToast(error.message || '创建会话失败')
  }
}

function goToSession(sessionId) {
  router.push(`/session/${sessionId}`)
}

function selectTopic(selectedTopic) {
  topic.value = selectedTopic.title
}
</script> 