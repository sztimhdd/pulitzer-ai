const pythonService = require('../services/pythonService');
const { ApiError } = require('../utils/errorHandler');

/**
 * 面试/对话控制器
 */
class InterviewController {
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

      console.log(`[InterviewController] Processing input for session ${sessionId}:`, {
        input,
        context
      });

      const result = await pythonService.processInput(sessionId, input, context);
      
      // 直接返回标准化的响应
      res.status(200).json(result);
    } catch (error) {
      console.error('[InterviewController] Error:', error);
      next(error);
    }
  }

  /**
   * 获取下一个问题
   */
  async getNextQuestion(req, res, next) {
    try {
      const { sessionId } = req.params;
      const { context } = req.body;

      console.log(`[InterviewController] Getting next question for session ${sessionId}:`, {
        context
      });

      const result = await pythonService.processInput(sessionId, 'next', context);
      
      res.status(200).json({
        status: 'success',
        data: {
          response: result.response,
          state: result.state,
          context: {
            ...result.context,
            initialization: context?.initialization,
            settings: context?.settings,
            selectedType: context?.selectedType,
            topic: context?.topic,
            wordCount: context?.wordCount
          }
        }
      });
    } catch (error) {
      console.error('[InterviewController] Error getting next question:', error);
      next(error);
    }
  }

  /**
   * 跳过当前问题
   */
  async skipQuestion(req, res, next) {
    try {
      const { sessionId } = req.params;
      const { context } = req.body;

      console.log(`[InterviewController] Skipping question for session ${sessionId}:`, {
        context
      });

      const result = await pythonService.processInput(sessionId, 'skip', context);
      
      res.status(200).json({
        status: 'success',
        data: {
          response: result.response,
          state: result.state,
          context: {
            ...result.context,
            initialization: context?.initialization,
            settings: context?.settings,
            selectedType: context?.selectedType,
            topic: context?.topic,
            wordCount: context?.wordCount
          }
        }
      });
    } catch (error) {
      console.error('[InterviewController] Error skipping question:', error);
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
}

module.exports = new InterviewController(); 