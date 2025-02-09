import { defineStore } from 'pinia'
import { inject } from 'vue'
import { API_BASE_URL, API_ROUTES, API_STATUS, API_ERROR_CODES } from '../config/api'
import { withRetry } from '../utils/retry'

export const useSessionStore = defineStore('session', {
  state: () => ({
    currentSession: null,
    sessions: [],
    unsavedChanges: false,
    lastSaveTime: null,
    loading: false,
    error: null
  }),
  
  actions: {
    async createSession(topic, type, wordCount, settings = {}) {
      const showLoading = inject('showLoading')
      const hideLoading = inject('hideLoading')
      const showToast = inject('showToast')
      
      try {
        if (showLoading) showLoading('创建会话中...')
        
        const requestBody = {
          topic,
          type,
          wordCount: Number(wordCount),
          settings
        }
        
        console.log('Creating session with:', requestBody)
        
        const response = await fetch(`${API_BASE_URL}${API_ROUTES.CREATE_SESSION}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        })
        
        let responseText
        try {
          responseText = await response.text()
          console.log('Server response:', {
            status: response.status,
            text: responseText
          })
        } catch (e) {
          console.error('Failed to read response:', e)
          throw new Error('服务器连接失败')
        }
        
        if (!response.ok) {
          let errorMessage
          try {
            const errorData = JSON.parse(responseText)
            errorMessage = errorData.error?.message
          } catch (e) {
            console.error('Failed to parse error response:', e)
            errorMessage = responseText || `HTTP error! status: ${response.status}`
          }
          throw new Error(errorMessage)
        }
        
        let result
        try {
          result = JSON.parse(responseText)
        } catch (e) {
          console.error('Failed to parse response:', e)
          throw new Error('服务器返回的数据格式无效')
        }
        
        if (result.status === 'success' && result.data?.session) {
          this.currentSession = result.data.session
          this.sessions.push(result.data.session)
          return result.data.session
        } else {
          throw new Error(result.error?.message || '创建会话失败')
        }
      } catch (error) {
        console.error('Failed to create session:', error)
        if (showToast) showToast(error.message || '创建会话失败')
        this.error = error.message
        throw error
      } finally {
        if (hideLoading) hideLoading()
      }
    },
    
    async sendInput(sessionId, input) {
      const showLoading = inject('showLoading')
      const hideLoading = inject('hideLoading')
      const showToast = inject('showToast')
      
      try {
        if (showLoading) showLoading('发送中...')
        return await withRetry(async () => {
          if (!sessionId) {
            throw new Error('无效的会话ID')
          }
          
          const url = `https://wmilysrsttsc.sealosgzg.site/api/v1/interview/sessions/${sessionId}/input`
          const requestBody = { 
            input,
            context: {
              sessionId,
              currentState: this.currentSession?.state || 'TOPIC_SELECTION',
              topic: this.currentSession?.topic,
              type: this.currentSession?.type
            }
          }
          
          console.log('Sending input:', {
            url,
            method: 'POST',
            body: requestBody
          })
          
          const response = await fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
          })
          
          const responseText = await response.text()
          console.log('Server Response:', {
            status: response.status,
            text: responseText
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const data = JSON.parse(responseText)
          if (data.status !== 'success') {
            throw new Error(data.message || '请求失败')
          }
          
          if (data.data?.state) {
            this.currentSession = {
              ...this.currentSession,
              state: data.data.state
            }
          }
          
          return {
            response: data.data?.response || data.response,
            state: data.data?.state,
            context: data.data?.context || {}
          }
        })
      } catch (error) {
        console.error('Send input failed:', error)
        if (showToast) showToast(error.message || '发送失败')
        this.error = error.message
        throw error
      } finally {
        if (hideLoading) hideLoading()
      }
    },
    
    async getDraft(sessionId) {
      const showLoading = inject('showLoading')
      const hideLoading = inject('hideLoading')
      const showToast = inject('showToast')
      
      try {
        if (showLoading) showLoading('获取文章中...')
        const response = await fetch(`https://wmilysrsttsc.sealosgzg.site/api/v1/draft/sessions/${sessionId}/draft`)
        
        const data = await response.json()
        if (data.status === 'success') {
          return data.data.draft
        }
        throw new Error(data.message)
      } catch (error) {
        if (showToast) showToast(error.message || '获取文章失败')
        throw error
      } finally {
        if (hideLoading) hideLoading()
      }
    },
    
    async deleteSession(sessionId) {
      const showLoading = inject('showLoading')
      const hideLoading = inject('hideLoading')
      const showToast = inject('showToast')
      
      try {
        if (showLoading) showLoading('删除会话中...')
        const response = await fetch(`https://wmilysrsttsc.sealosgzg.site/api/v1/sessions/${sessionId}`, {
          method: 'DELETE'
        })
        
        const data = await response.json()
        if (data.status === 'success') {
          this.sessions = this.sessions.filter(session => session.id !== sessionId)
          if (this.currentSession?.id === sessionId) {
            this.currentSession = null
          }
          return true
        }
        throw new Error(data.message)
      } catch (error) {
        if (showToast) showToast(error.message || '删除会话失败')
        throw error
      } finally {
        if (hideLoading) hideLoading()
      }
    },
    
    async loadMessages(sessionId) {
      const showLoading = inject('showLoading')
      const hideLoading = inject('hideLoading')
      const showToast = inject('showToast')
      
      try {
        if (showLoading) showLoading('加载消息历史...')
        const response = await fetch(`https://wmilysrsttsc.sealosgzg.site/api/v1/collaboration/sessions/${sessionId}`)
        
        if (!response.ok) {
          console.warn(`加载会话失败: ${response.status}`)
          return []
        }
        
        const data = await response.json()
        if (data.status === 'success') {
          return data.data.messages || []
        }
        
        console.warn(`加载会话失败: ${data.message}`)
        return []
      } catch (error) {
        if (showToast) showToast('加载消息失败，请稍后重试')
        console.error('加载消息失败:', error)
        return []
      } finally {
        if (hideLoading) hideLoading()
      }
    },
    
    // 自动保存逻辑
    async autoSave(sessionId, content) {
      if (!this.unsavedChanges) return;
      
      try {
        await this.saveDraft(sessionId, content);
        this.lastSaveTime = new Date();
        this.unsavedChanges = false;
      } catch (error) {
        console.error('自动保存失败:', error);
      }
    },
    
    // 新增保存草稿方法
    async saveDraft(sessionId, content) {
      return await withRetry(async () => {
        const response = await fetch(`https://wmilysrsttsc.sealosgzg.site/api/v1/draft/sessions/${sessionId}/draft`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content }),
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.status === 'success') {
          return data.data;
        }
        throw new Error(data.message);
      });
    },

    // 在 session store 中添加分页加载消息的方法
    async loadMessagePage(sessionId, page, pageSize) {
      const showLoading = inject('showLoading')
      const hideLoading = inject('hideLoading')
      const showToast = inject('showToast')
      
      try {
        if (showLoading) showLoading('加载消息...')
        return await withRetry(async () => {
          const response = await fetch(
            `https://wmilysrsttsc.sealosgzg.site/api/v1/sessions/${sessionId}?page=${page}&pageSize=${pageSize}`
          )
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const data = await response.json()
          if (data.status === 'success') {
            return {
              messages: data.data.messages || [],
              total: data.data.total
            }
          }
          throw new Error(data.message)
        })
      } catch (error) {
        if (showToast) showToast(`加载消息失败: ${error.message}`)
        throw error
      } finally {
        if (hideLoading) hideLoading()
      }
    },

    // 加载会话
    async loadSession(sessionId) {
      try {
        console.log('Loading session:', sessionId)
        const response = await fetch(`${API_BASE_URL}${API_ROUTES.GET_SESSION(sessionId)}`)
        
        console.log('Session response:', {
          status: response.status,
          ok: response.ok
        })

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('会话不存在或已被删除')
          }
          throw new Error(`加载会话失败: ${response.status}`)
        }

        const data = await response.json()
        console.log('Session data:', data)

        if (data.status === API_STATUS.SUCCESS) {
          this.currentSession = data.data
          return data.data
        } else {
          throw new Error(data.error?.message || '加载会话失败')
        }
      } catch (error) {
        console.error('Failed to load session:', error)
        this.error = error.message
        throw error
      }
    },

    // 加载消息历史
    async loadMessages(sessionId) {
      try {
        const url = `${API_BASE_URL}${API_ROUTES.GET_MESSAGES(sessionId)}`
        console.log('Loading messages from:', url)
        
        const response = await fetch(url)
        console.log('Messages response:', {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries())
        })
        
        if (!response.ok) {
          const responseText = await response.text()
          console.warn('Failed to load messages:', {
            status: response.status,
            body: responseText
          })
          return []
        }
        
        const responseText = await response.text()
        console.log('Messages response text:', responseText)
        
        const data = JSON.parse(responseText)
        console.log('Parsed messages data:', data)
        
        if (data.status === 'success') {
          return data.data.messages || []
        }
        
        console.warn('Invalid messages response format:', data)
        return []
      } catch (error) {
        console.error('Failed to load messages:', error)
        return []
      }
    },
  }
}) 