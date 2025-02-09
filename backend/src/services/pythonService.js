const pythonRunner = require('../utils/pythonRunner');
const { ApiError } = require('../utils/errorHandler');

class PythonService {
  constructor() {
    this.sessions = new Map(); // 存储会话状态
    this.messageHistory = new Map(); // 存储消息历史
  }

  /**
   * 创建新的写作协作会话
   */
  async createSession(sessionId, initialData = {}) {
    try {
      console.log('[PythonService] Creating session:', {
        sessionId,
        initialData
      });

      // 初始化会话状态
      const session = {
        id: sessionId,
        state: 'TOPIC_SELECTION',
        lastInteraction: new Date(),
        context: {
          initialization: initialData,
          selectedType: initialData.type,
          topic: initialData.topic,
          wordCount: initialData.wordCount
        }
      };

      // 初始化消息历史
      this.messageHistory.set(sessionId, []);

      this.sessions.set(sessionId, session);
      
      // 不在这里调用 Python 脚本，而是等待第一次用户输入
      console.log('[PythonService] Session created:', {
        sessionId,
        session
      });

      return { 
        sessionId, 
        status: 'initialized', 
        session,
        messages: []
      };
    } catch (error) {
      console.error('[PythonService] Create session error:', error);
      throw new ApiError(500, '创建会话失败: ' + error.message);
    }
  }

  /**
   * 获取会话信息
   */
  async getSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new ApiError(404, '会话不存在');
    }
    return session;
  }

  /**
   * 获取会话消息历史
   */
  async getSessionMessages(sessionId) {
    const messages = this.messageHistory.get(sessionId) || [];
    return {
      status: 'success',
      data: messages
    };
  }

  /**
   * 处理会话中的用户输入
   */
  async processInput(sessionId, input, context) {
    console.log(`[PythonService] Processing input for session ${sessionId}:`, { 
      input, 
      context,
      currentState: context?.currentState 
    });
    
    const session = await this.getSession(sessionId);
    const messages = this.messageHistory.get(sessionId) || [];
    
    try {
      // 验证输入
      if (!input && input !== '') {
        throw new ApiError(400, '输入内容不能为空');
      }

      // 处理初始化命令
      if (typeof input === 'object' && input.type === 'INITIALIZE_SESSION') {
        const { topic, articleType, wordCount, settings } = input.data;
        
        // 构造初始响应
        const initialResponse = {
          status: 'success',
          data: {
            response: `我将帮助您撰写一篇关于"${topic}"的${wordCount}字${articleType}文章。\n\n让我们开始讨论文章的大纲。我会为您生成一个初步的大纲建议。`,
            state: 'TOPIC_SELECTION',
            context: {
              ...session.context,
              initialization: {
                topic,
                type: articleType,
                wordCount,
                settings
              }
            },
            messages: [
              {
                role: 'assistant',
                content: `我将帮助您撰写一篇关于"${topic}"的${wordCount}字${articleType}文章。\n\n让我们开始讨论文章的大纲。我会为您生成一个初步的大纲建议。`
              }
            ]
          }
        };

        // 更新消息历史
        this.messageHistory.set(sessionId, initialResponse.data.messages);

        // 生成大纲
        const outlineResult = await pythonRunner.interact(sessionId, {
          type: 'GENERATE_OUTLINE',
          data: {
            topic,
            articleType,
            wordCount,
            settings
          }
        }, {
          ...context,
          currentState: 'TOPIC_SELECTION',
          messageHistory: initialResponse.data.messages
        });

        // 如果成功生成大纲，更新状态和响应
        if (outlineResult.status === 'success' && outlineResult.data.outline) {
          const outlineResponse = {
            status: 'success',
            data: {
              response: `我已经为您生成了一个初步的大纲建议，请审阅：\n\n${JSON.stringify(outlineResult.data.outline, null, 2)}`,
              state: 'OUTLINE_REVIEW',
              context: {
                ...session.context,
                outline: outlineResult.data.outline,
                initialization: {
                  topic,
                  type: articleType,
                  wordCount,
                  settings
                }
              },
              messages: [
                ...initialResponse.data.messages,
                {
                  role: 'assistant',
                  content: `我已经为您生成了一个初步的大纲建议，请审阅：\n\n${JSON.stringify(outlineResult.data.outline, null, 2)}`
                }
              ]
            }
          };

          // 更新会话状态
          session.state = 'OUTLINE_REVIEW';
          session.context.outline = outlineResult.data.outline;
          
          // 更新消息历史
          this.messageHistory.set(sessionId, outlineResponse.data.messages);
          return outlineResponse;
        }

        return initialResponse;
      }

      // 添加用户输入到消息历史
      messages.push({
        role: 'user',
        content: typeof input === 'object' ? JSON.stringify(input) : input
      });

      // 传递完整的上下文到Python脚本
      const result = await pythonRunner.interact(sessionId, input, {
        ...context,
        currentState: session.state,
        lastState: session.state,
        messageHistory: messages
      });

      // 更新会话状态
      session.lastInteraction = new Date();
      
      // 从 result.data 中提取数据
      const { response, state, context: newContext } = result.data;
      
      // 更新会话上下文
      session.context = {
        ...session.context,
        ...newContext,
        lastInput: input,
        lastResponse: response,
        currentState: state || session.state
      };

      // 如果有新状态，更新会话状态
      if (state) {
        console.log(`[PythonService] State transition: ${session.state} -> ${state}`);
        session.state = state;
      }

      // 添加AI响应到消息历史
      if (response) {
        messages.push({
          role: 'assistant',
          content: response
        });
      }

      // 更新消息历史
      this.messageHistory.set(sessionId, messages);

      // 构造标准响应格式
      const standardResponse = {
        status: 'success',
        data: {
          response,
          state: session.state,
          context: {
            sessionId,
            currentState: session.state,
            lastInput: input,
            outline: session.context.outline || {},
            settings: session.context.settings || {},
            initialization: context?.initialization || null,
            selectedType: session.context.selectedType,
            topic: session.context.topic,
            wordCount: session.context.wordCount
          },
          messages
        }
      };

      console.log(`[PythonService] Final response:`, standardResponse);
      return standardResponse;
    } catch (error) {
      console.error(`[PythonService] Error:`, error);
      throw error;
    }
  }

  /**
   * 生成内容草稿
   */
  async generateDraft(sessionId) {
    const session = await this.getSession(sessionId);
    
    try {
      // 调用Python生成草稿
      const result = await pythonRunner.runScript({
        args: ['--generate-draft', '--session', sessionId]
      });

      session.context.draft = result;
      return { draft: result };
    } catch (error) {
      throw new ApiError(500, '生成草稿失败: ' + error.message);
    }
  }

  /**
   * 修改草稿内容
   */
  async reviseDraft(sessionId, feedback) {
    const session = await this.getSession(sessionId);
    
    try {
      // 发送修改请求到Python
      const result = await pythonRunner.runScript({
        args: ['--revise-draft', '--feedback', feedback, '--session', sessionId]
      });

      session.context.draft = result;
      return { draft: result };
    } catch (error) {
      throw new ApiError(500, '修改草稿失败: ' + error.message);
    }
  }

  /**
   * 结束会话
   */
  async endSession(sessionId) {
    const session = await this.getSession(sessionId);
    
    try {
      // 清理Python进程
      await pythonRunner.runScript({
        args: ['--end-session', '--session', sessionId]
      });

      this.sessions.delete(sessionId);
      return true;
    } catch (error) {
      throw new ApiError(500, '结束会话失败: ' + error.message);
    }
  }
}

module.exports = new PythonService();