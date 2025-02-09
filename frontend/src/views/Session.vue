<template>
  <div class="min-h-screen flex flex-col">
    <!-- 顶部导航 -->
    <nav class="bg-white dark:bg-gray-800 shadow-sm p-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <router-link 
          to="/"
          class="flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <ArrowLeftIcon class="w-5 h-5 mr-2" />
          返回
        </router-link>
        <div class="flex items-center space-x-4">
          <button 
            @click="toggleDarkMode"
            class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <SunIcon v-if="isDark" class="w-5 h-5" />
            <MoonIcon v-else class="w-5 h-5" />
          </button>
          <button 
            v-if="currentSession?.state === 'COMPLETE'"
            @click="downloadDraft"
            class="btn btn-primary"
          >
            下载文章
          </button>
          <button 
            v-if="currentSession?.state === 'DRAFT_REVIEW' || currentSession?.state === 'COMPLETE'"
            @click="togglePreview"
            class="btn btn-primary"
          >
            {{ showPreview ? '返回对话' : '预览文章' }}
          </button>
          <button 
            @click="showSettings = !showSettings"
            class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <Cog6ToothIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </nav>

    <!-- 加载指示器 -->
    <LoadingIndicator
      v-if="isLoading"
      :title="loadingTitle"
      :message="loadingMessage"
    />

    <!-- 主要内容区 -->
    <div v-else class="flex-1 flex flex-col">
      <!-- 消息列表 -->
      <div class="flex-1 max-w-3xl mx-auto w-full p-4">
        <MessageList :messages="messages" />
        
        <!-- 大纲编辑器 -->
        <div v-if="showOutlineEditor" class="mt-4">
          <OutlineEditor
            :modelValue="currentOutline"
            @update:modelValue="currentOutline = $event"
            :disabled="loading"
          />
        </div>

        <!-- 消息输入 -->
        <div v-else class="mt-4">
          <MessageInput
            v-model="newMessage"
            :loading="loading"
            @submit="handleMessageSubmit"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'
import { useDark, useToggle } from '@vueuse/core'
import { API_BASE_URL, API_ROUTES, SESSION_STATES } from '../config/api'
import { 
  ArrowLeftIcon, 
  SunIcon, 
  MoonIcon,
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon
} from '@heroicons/vue/24/outline'
import ArticlePreview from '../components/ArticlePreview.vue'
import MessageInput from '../components/MessageInput.vue'
import OutlineEditor from '../components/OutlineEditor.vue'
import ProgressIndicator from '../components/ProgressIndicator.vue'
import ArticleSettings from '../components/ArticleSettings.vue'
import WritingTips from '../components/WritingTips.vue'
import MessageList from '../components/MessageList.vue'
import LoadingIndicator from '../components/LoadingIndicator.vue'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()
const isDark = useDark()
const toggleDarkMode = useToggle(isDark)
const messages = ref([])
const showLoading = inject('showLoading')
const hideLoading = inject('hideLoading')
const showToast = inject('showToast')
const newMessage = ref('')
const currentOutline = ref({
  sections: [],
  title: '',
  description: ''
})
const loading = ref(false)
const isLoading = ref(false)
const loadingTitle = ref('请稍候')
const loadingMessage = ref('正在处理...')
const showOutlineEditor = computed(() => {
  return sessionStore.currentSession?.state === 'OUTLINE_REVIEW'
})

const stages = [
  '主题确认',
  '大纲制定',
  '内容访谈',
  '草稿生成',
  '修改完善'
]

const currentStage = computed(() => {
  switch (sessionStore.currentSession?.state) {
    case 'TOPIC_SELECTION': return 0
    case 'OUTLINE_REVIEW': return 1
    case 'INTERVIEW': return 2
    case 'DRAFT_GENERATION': return 3
    case 'DRAFT_REVIEW': return 4
    case 'COMPLETE': return 5
    default: return 0
  }
})

const currentSession = computed(() => sessionStore.currentSession)

const showPreview = ref(false)
const previewContent = ref('')

// 添加设置相关的状态
const showSettings = ref(false)
const articleSettings = ref({
  style: 'narrative',
  professionLevel: 50,
  tone: 'professional',
  includeReferences: true,
  includeQuotes: true
})

// 添加文章统计数据
const articleStats = ref({
  wordCount: 0,
  keywords: [],
  paragraphLengths: [],
  readability: {
    clarity: 0,
    conciseness: 0,
    coherence: 0,
    engagement: 0
  },
  sentiment: 50
})

// 注入全局方法
const methods = inject('globalMethods')

// 处理响应
async function handleResponse(result) {
  if (result.status === 'success') {
    // 更新消息历史
    if (result.data.messages) {
      messages.value = result.data.messages.map(msg => ({
        role: msg.role || (msg.type === 'ai' ? 'assistant' : 'user'),
        content: msg.content,
        id: msg.id || Date.now(),
        timestamp: msg.timestamp || Date.now()
      }))
    } else if (result.data.response) {
      messages.value.push({
        role: 'assistant',
        content: result.data.response,
        id: Date.now(),
        timestamp: Date.now()
      })
    }

    // 更新会话状态
    if (result.data.state) {
      sessionStore.currentSession.state = result.data.state
    }

    // 更新上下文
    if (result.data.context) {
      sessionStore.currentSession.context = {
        ...sessionStore.currentSession.context,
        ...result.data.context
      }

      // 如果进入大纲审查状态，更新大纲
      if (result.data.state === 'OUTLINE_REVIEW' && result.data.context.outline) {
        currentOutline.value = result.data.context.outline
      }
    }
  }
}

// 发送消息
async function sendMessage(content) {
  try {
    loading.value = true
    error.value = null
    
    const sessionId = sessionStore.currentSession?.id
    if (!sessionId) {
      throw new Error('会话ID不存在')
    }

    console.log('Sending message:', {
      sessionId,
      content,
      currentState: sessionStore.currentSession?.state
    })

    const response = await fetch(
      `${API_BASE_URL}${API_ROUTES.SEND_MESSAGE(sessionId)}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          input: content
        })
      }
    )

    if (!response.ok) {
      throw new Error(`发送消息失败: ${response.status}`)
    }

    const result = await response.json()
    console.log('Message result:', result)
    await handleResponse(result)
    return result

  } catch (err) {
    console.error('Failed to send message:', err)
    error.value = err.message
    methods?.showToast(err.message || '发送消息失败')
    throw err
  } finally {
    loading.value = false
  }
}

// 监听会话变化
watch(() => sessionStore.currentSession, async (newSession, oldSession) => {
  console.log('Session changed:', {
    old: oldSession?.id,
    new: newSession?.id,
    state: newSession?.state,
    data: newSession
  })
  
  // 如果是新创建的会话，发送初始化消息
  if (newSession && (!oldSession || newSession.id !== oldSession.id)) {
    console.log('New session detected, initializing...')
    await initializeSession()
  }
}, { immediate: true, deep: true })

// 组件挂载时初始化
onMounted(async () => {
  const sessionId = route.params.id
  if (sessionId) {
    try {
      isLoading.value = true
      loadingTitle.value = '加载会话'
      loadingMessage.value = '正在加载会话信息...'
      await sessionStore.loadSession(sessionId)
    } catch (error) {
      console.error('Failed to load session:', error)
      methods?.showToast('加载会话失败')
      router.push('/')
    } finally {
      isLoading.value = false
    }
  }
})

// 处理大纲数据的格式化
function parseOutline(response) {
  try {
    console.log('Parsing outline from response:', response)
    
    // 从响应文本中提取大纲部分
    const outlineMatch = response.match(/基于您的设置，我生成了以下大纲：\s*([\s\S]*?)(?=\n\n|$)/)
    if (!outlineMatch) {
      console.warn('No outline pattern found in response')
      return null
    }
    
    const outlineText = outlineMatch[1]
    console.log('Extracted outline text:', outlineText)
    
    // 将大纲文本转换为结构化数据
    const outline = {}
    let currentSection = null
    
    outlineText.split('\n').forEach(line => {
      line = line.trim()
      if (!line) return
      
      console.log('Processing line:', line)
      
      // 处理主要章节
      if (line.startsWith('"') && line.endsWith('":')) {
        currentSection = line.slice(1, -2)
        outline[currentSection] = []
        console.log('Found section:', currentSection)
      }
      // 处理子项
      else if (line.startsWith('-') || line.startsWith('•')) {
        if (currentSection) {
          const item = line.slice(1).trim()
          outline[currentSection].push(item)
          console.log('Added item to section:', currentSection, item)
        }
      }
      // 处理普通文本作为子项
      else if (currentSection) {
        outline[currentSection].push(line)
        console.log('Added text to section:', currentSection, line)
      }
    })
    
    console.log('Final parsed outline:', outline)
    return outline
  } catch (error) {
    console.error('Failed to parse outline:', error)
    return null
  }
}

async function downloadDraft() {
  try {
    const draft = await sessionStore.getDraft(route.params.id)
    
    // 创建下载链接
    const blob = new Blob([draft], { type: 'text/markdown' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `article-${route.params.id}.md`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error(error)
  }
}

async function togglePreview() {
  if (!showPreview.value) {
    try {
      const draft = await sessionStore.getDraft(route.params.id)
      previewContent.value = draft
      showPreview.value = true
    } catch (error) {
      console.error(error)
    }
  } else {
    showPreview.value = false
    previewContent.value = ''
  }
}

async function updateOutline(newOutline) {
  try {
    const response = await sessionStore.sendInput(
      route.params.id,
      JSON.stringify({
        type: 'outline_update',
        outline: newOutline
      })
    )
    
    currentOutline.value = newOutline
    messages.value.push({
      id: Date.now(),
      type: 'ai',
      content: response.response
    })
  } catch (error) {
    console.error(error)
  }
}

// 添加更新设置的方法
async function updateSettings(settings) {
  try {
    const response = await sessionStore.sendInput(
      route.params.id,
      JSON.stringify({
        type: 'settings_update',
        settings
      })
    )
    
    messages.value.push({
      id: Date.now(),
      type: 'ai',
      content: response.response
    })
    
    showSettings.value = false
  } catch (error) {
    console.error(error)
  }
}

// 添加执行命令的方法
async function executeCommand(command) {
  await sendMessage(command)
}

// 添加加载更多消息的方法
async function loadMoreMessages({ page, pageSize }) {
  try {
    const result = await sessionStore.loadMessagePage(route.params.id, page, pageSize)
    return result
  } catch (error) {
    console.error('加载更多消息失败:', error)
  }
}

// 修改大纲保存函数
async function saveOutline(outline) {
  try {
    loading.value = true
    console.log('Saving outline:', outline)
    
    // 将大纲转换为后端期望的格式
    const outlineData = {}
    Object.entries(outline).forEach(([section, items]) => {
      if (Array.isArray(items)) {
        outlineData[section] = items.filter(item => item.trim() !== '')
      }
    })
    
    const message = {
      type: 'UPDATE_OUTLINE',
      data: outlineData
    }
    
    await sendMessage(JSON.stringify(message))
  } catch (error) {
    console.error('Failed to save outline:', error)
    methods?.showToast(error.message || '保存大纲失败')
  } finally {
    loading.value = false
  }
}

// 处理大纲取消
function cancelOutline() {
  currentOutline.value = null
}

// 处理消息提交
async function handleMessageSubmit(content) {
  try {
    loading.value = true
    error.value = null
    
    const session = sessionStore.currentSession
    if (!session) {
      throw new Error('会话不存在')
    }

    // 添加用户消息到本地显示
    messages.value.push({
      role: 'user',
      content
    })

    const response = await fetch(
      `${API_BASE_URL}${API_ROUTES.SEND_MESSAGE(session.id)}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          input: content,
          context: {
            sessionId: session.id,
            currentState: session.state
          }
        })
      }
    )

    if (!response.ok) {
      throw new Error(`发送消息失败: ${response.status}`)
    }

    const result = await response.json()
    await handleResponse(result)
    newMessage.value = '' // 清空输入
    return result
  } catch (err) {
    console.error('Failed to send message:', err)
    error.value = err.message
    methods?.showToast(err.message || '发送消息失败')
  } finally {
    loading.value = false
  }
}

// 初始化会话
async function initializeSession() {
  try {
    const session = sessionStore.currentSession
    if (!session) {
      console.log('No session found')
      return
    }
    
    // 检查必要的会话数据
    if (!session.topic || !session.type || !session.wordCount) {
      console.error('Missing required session data:', session)
      throw new Error('会话数据不完整')
    }
    
    console.log('Initializing session:', session)
    
    const message = {
      type: 'INITIALIZE_SESSION',
      data: {
        topic: session.topic,
        articleType: session.type,
        wordCount: session.wordCount,
        settings: session.settings || {},
        action: 'GENERATE_OUTLINE'
      }
    }
    
    loading.value = true
    console.log('Sending initialization message:', message)
    
    const response = await fetch(
      `${API_BASE_URL}${API_ROUTES.SEND_MESSAGE(session.id)}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          input: message,
          context: {
            sessionId: session.id,
            currentState: 'TOPIC_SELECTION',
            targetState: 'OUTLINE_REVIEW',
            initialization: {
              topic: session.topic,
              type: session.type,
              wordCount: session.wordCount,
              settings: session.settings || {}
            }
          }
        })
      }
    )
    
    if (!response.ok) {
      throw new Error(`初始化失败: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('Initialization response:', result)
    await handleResponse(result)
    
  } catch (error) {
    console.error('Initialization failed:', error)
    methods?.showToast(error.message || '初始化失败，请重试')
  } finally {
    loading.value = false
  }
}
</script> 