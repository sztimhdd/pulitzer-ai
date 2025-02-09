<template>
  <div 
    ref="messageContainer"
    class="flex-1 overflow-y-auto space-y-6 scroll-smooth"
    @scroll="handleScroll"
  >
    <!-- 加载更多按钮 -->
    <div v-if="hasMoreMessages" class="text-center py-4">
      <button
        @click="loadMoreMessages"
        class="text-primary-600 hover:text-primary-700 dark:text-primary-400"
        :disabled="isLoading"
      >
        {{ isLoading ? '加载中...' : '加载更多' }}
      </button>
    </div>

    <TransitionGroup
      name="message"
      tag="div"
      class="space-y-6"
    >
      <div
        v-for="message in visibleMessages"
        :key="message.id || message.timestamp || Math.random()"
        :class="[
          'message-item animate__animated',
          message.type === 'ai' ? 'animate__fadeInLeft' : 'animate__fadeInRight'
        ]"
      >
        <!-- 消息内容 -->
        <slot 
          name="message"
          :message="message"
        ></slot>
      </div>
    </TransitionGroup>

    <!-- 新消息提示 -->
    <div
      v-if="hasNewMessages"
      class="fixed bottom-20 left-1/2 transform -translate-x-1/2"
    >
      <button
        @click="scrollToBottom"
        class="bg-primary-500 text-white px-4 py-2 rounded-full shadow-lg hover:bg-primary-600 transition-colors"
      >
        查看新消息
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'

const props = defineProps({
  messages: {
    type: Array,
    required: true
  },
  pageSize: {
    type: Number,
    default: 20
  }
})

const messageContainer = ref(null)
const visibleMessages = ref([])
const currentPage = ref(1)
const isLoading = ref(false)
const hasNewMessages = ref(false)
const isScrolledToBottom = ref(true)
const emit = defineEmits(['load-more'])
const hasMore = ref(true)

// 添加一个标志来跟踪组件是否已卸载
const isComponentMounted = ref(false)

// 更新加载更多消息的方法
async function loadMoreMessages() {
  if (isLoading.value || !hasMore.value) return
  
  isLoading.value = true
  try {
    const result = await emit('load-more', {
      page: currentPage.value,
      pageSize: props.pageSize
    })
    
    // 如果返回的消息数量小于页大小，说明没有更多消息了
    if (result && result.messages) {
      const newMessages = result.messages
      visibleMessages.value = [...newMessages, ...visibleMessages.value]
      hasMore.value = newMessages.length === props.pageSize
      currentPage.value++
    }
  } finally {
    isLoading.value = false
  }
}

// 更新消息监听
watch(() => props.messages, (newMessages) => {
  if (!newMessages) return
  
  // 只更新最新的消息
  const currentLength = visibleMessages.value.length
  const newLength = newMessages.length
  
  if (newLength > currentLength) {
    const newItems = newMessages.slice(currentLength)
    visibleMessages.value = [...visibleMessages.value, ...newItems]
    
    if (isScrolledToBottom.value) {
      scrollToBottom()
    } else {
      hasNewMessages.value = true
    }
  }
}, { deep: true })

// 修改滚动到底部的函数
function scrollToBottom() {
  if (!isComponentMounted.value) return
  const container = messageContainer.value
  if (!container) return

  requestAnimationFrame(() => {
    container.scrollTo({
      top: container.scrollHeight,
      behavior: 'smooth'
    })
    hasNewMessages.value = false
  })
}

// 修改处理滚动的函数
function handleScroll() {
  if (!isComponentMounted.value) return
  const container = messageContainer.value
  if (!container) return
  
  const { scrollTop, scrollHeight, clientHeight } = container
  isScrolledToBottom.value = Math.abs(scrollHeight - clientHeight - scrollTop) < 1
  
  if (isScrolledToBottom.value) {
    hasNewMessages.value = false
  }
  
  if (scrollTop === 0 && hasMore.value && !isLoading.value) {
    loadMoreMessages()
  }
}

// 计算是否还有更多消息
const hasMoreMessages = computed(() => {
  return visibleMessages.value.length < props.messages.length
})

onMounted(() => {
  isComponentMounted.value = true
  if (props.messages.length > 0) {
    visibleMessages.value = props.messages.slice(-props.pageSize)
    currentPage.value = Math.ceil(props.messages.length / props.pageSize)
    hasMore.value = props.messages.length === props.pageSize
    scrollToBottom()
  }
})

onBeforeUnmount(() => {
  isComponentMounted.value = false
})
</script>

<style scoped>
.message-enter-active,
.message-leave-active {
  transition: all 0.3s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style> 