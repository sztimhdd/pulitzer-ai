<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
    <h3 class="text-lg font-medium mb-4">写作建议</h3>
    
    <div class="space-y-4">
      <!-- 当前阶段建议 -->
      <div class="bg-primary-50 dark:bg-primary-900 rounded-lg p-4">
        <h4 class="font-medium text-primary-700 dark:text-primary-300 mb-2">
          {{ getCurrentStageTitle }}
        </h4>
        <p class="text-sm text-primary-600 dark:text-primary-400">
          {{ getCurrentStageTip }}
        </p>
      </div>
      
      <!-- 通用建议列表 -->
      <div class="space-y-3">
        <div
          v-for="(tip, index) in generalTips"
          :key="index"
          class="flex items-start space-x-3"
        >
          <LightBulbIcon class="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ tip }}</p>
        </div>
      </div>
      
      <!-- 快捷命令 -->
      <div class="mt-6">
        <h4 class="text-sm font-medium mb-2">快捷命令</h4>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="command in quickCommands"
            :key="command.text"
            @click="$emit('execute-command', command.text)"
            class="px-3 py-2 text-sm text-left rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            {{ command.text }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { LightBulbIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  currentStage: {
    type: Number,
    required: true
  }
})

const stageTips = {
  0: {
    title: '确定主题方向',
    tip: '思考文章的目标读者和核心价值主张，确保主题具有足够的深度和广度。'
  },
  1: {
    title: '构建文章框架',
    tip: '合理安排各部分内容，确保逻辑流畅，层次分明。'
  },
  2: {
    title: '丰富内容细节',
    tip: '提供具体的例子和数据支持，使文章更有说服力。'
  },
  3: {
    title: '完善文章草稿',
    tip: '注意段落之间的过渡，保持文章的连贯性。'
  },
  4: {
    title: '优化和润色',
    tip: '检查语言表达，确保准确、简洁、生动。'
  }
}

const generalTips = [
  '使用简洁明了的语言表达核心观点',
  '适当添加例子和数据增强说服力',
  '注意段落之间的逻辑连接',
  '定期保存和预览文章内容'
]

const quickCommands = [
  { text: '帮我完善这段内容' },
  { text: '这里需要一个例子' },
  { text: '如何更好地表达' },
  { text: '建议下一步写什么' }
]

const getCurrentStageTitle = computed(() => {
  return stageTips[props.currentStage]?.title || '完成写作'
})

const getCurrentStageTip = computed(() => {
  return stageTips[props.currentStage]?.tip || '检查并优化整体内容。'
})

defineEmits(['execute-command'])
</script> 