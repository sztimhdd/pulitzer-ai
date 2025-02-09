<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
    <div class="flex items-center space-x-2 mb-2">
      <button
        v-for="mode in modes"
        :key="mode.value"
        @click="currentMode = mode.value"
        :class="[
          'px-3 py-1 text-sm rounded-md transition-colors',
          currentMode === mode.value
            ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
            : 'hover:bg-gray-100 dark:hover:bg-gray-700'
        ]"
      >
        {{ mode.label }}
      </button>
    </div>

    <div class="relative">
      <!-- 编辑模式 -->
      <textarea
        v-if="currentMode === 'edit'"
        v-model="inputContent"
        rows="3"
        class="w-full px-4 py-2 rounded-lg border dark:bg-gray-700 dark:border-gray-600 resize-none"
        :placeholder="placeholder"
        @keydown.enter.ctrl.prevent="submit"
      ></textarea>

      <!-- 预览模式 -->
      <div
        v-else
        class="w-full px-4 py-2 rounded-lg border dark:border-gray-600 min-h-[5rem] prose dark:prose-invert max-w-none"
        v-html="markdownPreview"
      ></div>

      <!-- 工具栏 -->
      <div class="flex items-center justify-between mt-2">
        <div class="flex items-center space-x-2">
          <button
            v-for="tool in tools"
            :key="tool.label"
            @click="insertTool(tool)"
            class="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
            :title="tool.label"
          >
            <component :is="tool.icon" class="w-5 h-5" />
          </button>
          
          <!-- 表情选择器 -->
          <div class="relative">
            <button
              @click="showEmoji = !showEmoji"
              class="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
            >
              <FaceSmileIcon class="w-5 h-5" />
            </button>
            
            <div
              v-if="showEmoji"
              class="absolute bottom-full left-0 mb-2 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border dark:border-gray-700 grid grid-cols-8 gap-1"
            >
              <button
                v-for="emoji in emojis"
                :key="emoji"
                @click="insertEmoji(emoji)"
                class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                {{ emoji }}
              </button>
            </div>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-500">
            Ctrl + Enter 发送
          </span>
          <button
            @click="submit"
            class="btn btn-primary"
            :disabled="!inputContent.trim()"
          >
            发送
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import {
  CodeBracketIcon,
  LinkIcon,
  PhotoIcon,
  FaceSmileIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  placeholder: {
    type: String,
    default: '输入消息...'
  }
})

const emit = defineEmits(['submit'])

const inputContent = ref('')
const currentMode = ref('edit')
const showEmoji = ref(false)

const modes = [
  { value: 'edit', label: '编辑' },
  { value: 'preview', label: '预览' }
]

const tools = [
  { 
    label: '代码块',
    icon: CodeBracketIcon,
    prefix: '```\n',
    suffix: '\n```'
  },
  {
    label: '链接',
    icon: LinkIcon,
    prefix: '[',
    suffix: '](url)'
  },
  {
    label: '图片',
    icon: PhotoIcon,
    prefix: '![',
    suffix: '](url)'
  }
]

const emojis = ['😊', '👍', '🎉', '💡', '❤️', '🔥', '✨', '🚀', '💪', '👏', '🤔', '💻', '📝', '🎯', '🌟', '💬']

const markdownPreview = computed(() => {
  return marked(inputContent.value)
})

function insertTool(tool) {
  const textarea = document.querySelector('textarea')
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selected = inputContent.value.substring(start, end)
  
  inputContent.value = 
    inputContent.value.substring(0, start) +
    tool.prefix +
    selected +
    tool.suffix +
    inputContent.value.substring(end)
    
  // 恢复焦点并选中内容
  textarea.focus()
  textarea.setSelectionRange(
    start + tool.prefix.length,
    start + tool.prefix.length + selected.length
  )
}

function insertEmoji(emoji) {
  inputContent.value += emoji
  showEmoji.value = false
}

function submit() {
  if (inputContent.value.trim()) {
    emit('submit', inputContent.value)
    inputContent.value = ''
    currentMode.value = 'edit'
  }
}
</script> 