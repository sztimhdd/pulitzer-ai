<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
    <!-- 工具栏 -->
    <div class="flex items-center justify-between p-4 border-b dark:border-gray-700">
      <h3 class="text-lg font-medium">文章预览</h3>
      <div class="flex items-center space-x-2">
        <button
          @click="downloadMarkdown"
          class="btn btn-primary"
        >
          下载 Markdown
        </button>
        <button
          @click="copyToClipboard"
          class="btn btn-primary"
        >
          复制全文
        </button>
      </div>
    </div>

    <!-- 预览内容 -->
    <div class="p-6">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-4 border-primary-500 border-t-transparent"></div>
      </div>
      <div
        v-else
        class="prose dark:prose-invert max-w-none"
        v-html="markdownContent"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { marked } from 'marked'
import { useSessionStore } from '../stores/session'

const props = defineProps({
  content: {
    type: String,
    required: true
  }
})

const loading = ref(true)
const markdownContent = ref('')
const sessionStore = useSessionStore()

// 配置 marked 选项
marked.setOptions({
  breaks: true, // 支持 GitHub 风格的换行
  gfm: true,    // 启用 GitHub 风格的 Markdown
  headerIds: true,
  mangle: false,
  sanitize: false
})

// 监听内容变化
watch(() => props.content, async (newContent) => {
  if (newContent) {
    loading.value = true
    try {
      // 使用marked将markdown转换为HTML
      markdownContent.value = marked(newContent)
    } catch (error) {
      console.error('Markdown转换失败:', error)
    } finally {
      loading.value = false
    }
  }
}, { immediate: true })

// 下载 Markdown 文件
function downloadMarkdown() {
  const blob = new Blob([props.content], { type: 'text/markdown' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `article-${Date.now()}.md`
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

// 复制到剪贴板
async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(props.content)
    // TODO: 显示成功提示
  } catch (error) {
    console.error('复制失败:', error)
    // TODO: 显示错误提示
  }
}
</script>

<style>
/* Markdown 样式优化 */
.prose {
  font-size: 1.1rem;
  line-height: 1.75;
}

.prose h1 {
  font-size: 2em;
  margin-top: 2em;
  margin-bottom: 1em;
}

.prose h2 {
  font-size: 1.5em;
  margin-top: 1.75em;
  margin-bottom: 0.75em;
}

.prose h3 {
  font-size: 1.25em;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.prose p {
  margin-top: 1.25em;
  margin-bottom: 1.25em;
}

.prose ul,
.prose ol {
  margin-top: 1em;
  margin-bottom: 1em;
  padding-left: 1.5em;
}

.prose li {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.prose blockquote {
  margin: 1.5em 0;
  padding-left: 1em;
  border-left: 4px solid #e5e7eb;
  font-style: italic;
  color: #6b7280;
}

.prose code {
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.875em;
}

.prose pre {
  background-color: #1f2937;
  color: #e5e7eb;
  padding: 1em;
  border-radius: 0.5em;
  overflow-x: auto;
}

.dark .prose code {
  background-color: #374151;
}

.dark .prose blockquote {
  border-left-color: #4b5563;
  color: #9ca3af;
}
</style> 