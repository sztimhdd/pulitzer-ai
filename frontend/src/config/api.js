export const API_BASE_URL = '/api/v1'

export const API_ROUTES = {
  // 会话管理
  CREATE_SESSION: '/collaboration/sessions',
  GET_SESSION: (sessionId) => `/collaboration/sessions/${sessionId}`,
  DELETE_SESSION: (sessionId) => `/collaboration/sessions/${sessionId}`,
  
  // 消息交互
  SEND_MESSAGE: (sessionId) => `/collaboration/sessions/${sessionId}/input`,
  GET_MESSAGES: (sessionId) => `/collaboration/sessions/${sessionId}/messages`,
  
  // 会话状态
  GET_SESSION_STATE: (sessionId) => `/collaboration/sessions/${sessionId}/state`,
  
  // 大纲管理
  GET_OUTLINE: (sessionId) => `/collaboration/sessions/${sessionId}/outline`,
  UPDATE_OUTLINE: (sessionId) => `/collaboration/sessions/${sessionId}/outline`,
  
  // 草稿管理
  GET_DRAFT: (sessionId) => `/collaboration/sessions/${sessionId}/draft`,
  UPDATE_DRAFT: (sessionId) => `/collaboration/sessions/${sessionId}/draft`
}

// API 响应状态码
export const API_STATUS = {
  SUCCESS: 'success',
  ERROR: 'error'
}

// API 错误码
export const API_ERROR_CODES = {
  SESSION_NOT_FOUND: 'SESSION_NOT_FOUND',
  INVALID_INPUT: 'INVALID_INPUT',
  SERVER_ERROR: 'SERVER_ERROR'
}

// 会话状态常量
export const SESSION_STATES = {
  TOPIC_SELECTION: 'TOPIC_SELECTION',
  OUTLINE_REVIEW: 'OUTLINE_REVIEW',
  INTERVIEW: 'INTERVIEW',
  DRAFT_REVIEW: 'DRAFT_REVIEW',
  COMPLETE: 'COMPLETE'
}

// 文章类型常量
export const ARTICLE_TYPES = {
  ARTICLE: 'Article',
  BLOG: 'Blog',
  STORY: 'Story',
  MANUAL: 'Manual',
  REPORT: 'Report',
  MEMO: 'Memo',
  BIOGRAPHY: 'Biography'
} 