const pythonService = require('../services/pythonService');
const { ApiError } = require('../utils/errorHandler');
const { v4: uuidv4 } = require('uuid');

/**
 * 协作会话控制器
 */
class CollaborationController {
  /**
   * 创建新的协作会话
   */
  async createSession(req, res, next) {
    try {
      const { topic, type, wordCount } = req.body;
      
      if (!topic || !type || !wordCount) {
        throw new ApiError(400, '缺少必要的参数：topic, type, wordCount');
      }

      const sessionId = uuidv4();
      console.log(`[CollaborationController] Creating session:`, {
        sessionId,
        topic,
        type,
        wordCount
      });

      // 传递初始化数据
      const initialData = {
        topic,
        type,
        wordCount,
        settings: req.body.settings || {} // 可选的文章设置
      };

      const result = await pythonService.createSession(sessionId, initialData);
      
      // 添加额外的会话信息
      const session = {
        ...result.session,
        id: sessionId,
        topic,
        type,
        wordCount,
        settings: initialData.settings
      };

      res.status(201).json({
        status: 'success',
        data: {
          sessionId,
          session
        }
      });
    } catch (error) {
      console.error('[CollaborationController] Error creating session:', error);
      next(error);
    }
  }

  /**
   * 获取会话状态
   */
  async getSessionStatus(req, res, next) {
    try {
      const { sessionId } = req.params;
      const session = await pythonService.getSession(sessionId);
      
      if (!session) {
        throw new ApiError(404, '会话不存在');
      }

      res.status(200).json({
        status: 'success',
        data: session
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * 结束协作会话
   */
  async endSession(req, res, next) {
    try {
      const { sessionId } = req.params;
      
      console.log(`[CollaborationController] Ending session:`, { sessionId });

      await pythonService.endSession(sessionId);
      
      res.status(200).json({
        status: 'success',
        message: '会话已结束'
      });
    } catch (error) {
      console.error('[CollaborationController] Error ending session:', error);
      next(error);
    }
  }

  /**
   * 处理用户输入
   */
  async processInput(req, res, next) {
    try {
      const { sessionId } = req.params;
      const { input, context } = req.body;

      if (!input) {
        throw new ApiError(400, '输入内容不能为空');
      }

      console.log(`[CollaborationController] Processing input for session ${sessionId}:`, {
        input,
        context
      });

      const result = await pythonService.processInput(sessionId, input, context);
      res.status(200).json(result);
    } catch (error) {
      next(error);
    }
  }

  /**
   * 获取会话消息历史
   */
  async getMessages(req, res, next) {
    try {
      const { sessionId } = req.params;
      const result = await pythonService.getSessionMessages(sessionId);
      res.status(200).json(result);
    } catch (error) {
      next(error);
    }
  }

  /**
   * 获取会话信息
   */
  async getSession(req, res, next) {
    try {
      const { sessionId } = req.params;
      const session = await pythonService.getSession(sessionId);
      
      res.status(200).json({
        status: 'success',
        data: session
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * 获取会话状态
   */
  async getSessionState(req, res, next) {
    try {
      const { sessionId } = req.params;
      const session = await pythonService.getSession(sessionId);
      
      res.status(200).json({
        status: 'success',
        data: {
          state: session.state
        }
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * 获取大纲
   */
  async getOutline(req, res, next) {
    try {
      const { sessionId } = req.params;
      const session = await pythonService.getSession(sessionId);
      
      res.status(200).json({
        status: 'success',
        data: {
          outline: session.context.outline || {}
        }
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * 更新大纲
   */
  async updateOutline(req, res, next) {
    try {
      const { sessionId } = req.params;
      const { outline } = req.body;
      
      const result = await pythonService.processInput(sessionId, {
        type: 'UPDATE_OUTLINE',
        outline
      });

      res.status(200).json(result);
    } catch (error) {
      next(error);
    }
  }

  /**
   * 获取草稿
   */
  async getDraft(req, res, next) {
    try {
      const { sessionId } = req.params;
      const session = await pythonService.getSession(sessionId);
      
      res.status(200).json({
        status: 'success',
        data: {
          draft: session.context.draft || ''
        }
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * 更新草稿
   */
  async updateDraft(req, res, next) {
    try {
      const { sessionId } = req.params;
      const { draft } = req.body;
      
      const result = await pythonService.processInput(sessionId, {
        type: 'UPDATE_DRAFT',
        draft
      });

      res.status(200).json(result);
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new CollaborationController(); 