<template>
  <div class="outline-editor">
    <div v-for="(items, section) in modelValue" :key="section" class="mb-6">
      <div class="flex items-center mb-2">
        <h4 class="text-lg font-medium">{{ section }}</h4>
        <button @click="removeSection(section)" class="ml-2 text-red-500 hover:text-red-700">
          <XMarkIcon class="h-4 w-4" />
        </button>
      </div>
      <ul class="space-y-2 pl-4">
        <li v-for="(item, index) in items" :key="index" class="flex items-center">
          <input
            type="text"
            :value="item"
            @input="updateItem(section, index, $event.target.value)"
            class="flex-1 p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
          >
          <button @click="removeItem(section, index)" class="ml-2 text-red-500 hover:text-red-700">
            <XMarkIcon class="h-4 w-4" />
          </button>
        </li>
        <li>
          <button
            @click="addItem(section)"
            class="text-primary-500 hover:text-primary-700 flex items-center"
          >
            <PlusIcon class="h-4 w-4 mr-1" />
            添加项目
          </button>
        </li>
      </ul>
    </div>
    
    <div class="mt-4">
      <button
        @click="addSection"
        class="text-primary-500 hover:text-primary-700 flex items-center"
      >
        <PlusIcon class="h-4 w-4 mr-1" />
        添加章节
      </button>
    </div>
    
    <div class="flex justify-end space-x-4 mt-6">
      <button
        @click="$emit('cancel')"
        class="px-4 py-2 border rounded hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        取消
      </button>
      <button
        @click="$emit('save', modelValue)"
        class="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600"
      >
        保存
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { XMarkIcon, PlusIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

// 创建本地响应式数据
const localOutline = ref({...props.modelValue})

// 监听 props 变化
watch(() => props.modelValue, (newVal) => {
  localOutline.value = {...newVal}
}, { deep: true })

function addSection() {
  const title = prompt('请输入章节标题')
  if (title) {
    localOutline.value[title] = []
    emit('update:modelValue', {...localOutline.value})
  }
}

function removeSection(title) {
  if (confirm(`确定要删除 "${title}" 章节吗？`)) {
    delete localOutline.value[title]
    emit('update:modelValue', {...localOutline.value})
  }
}

function addItem(title) {
  localOutline.value[title].push('')
  emit('update:modelValue', {...localOutline.value})
}

function removeItem(title, index) {
  localOutline.value[title].splice(index, 1)
  emit('update:modelValue', {...localOutline.value})
}

function updateItem(title, index, value) {
  localOutline.value[title][index] = value
  emit('update:modelValue', {...localOutline.value})
}
</script> 