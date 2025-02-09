import './assets/main.css'
import './style.css'
import 'animate.css'

import { createApp, ref, provide } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 创建应用实例
const app = createApp(App)

// 使用插件
app.use(createPinia())
app.use(router)

// 创建全局 loading 状态
const loading = ref(false)
const loadingMessage = ref('')

app.provide('loading', loading)
app.provide('loadingMessage', loadingMessage)

// 提供 loading 控制函数
app.provide('showLoading', (message = '加载中...') => {
  loadingMessage.value = message
  loading.value = true
})

app.provide('hideLoading', () => {
  loading.value = false
  loadingMessage.value = ''
})

// 挂载应用
app.mount('#app')
