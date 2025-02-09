const pythonService = require('../services/pythonService');

/**
 * 草稿生成控制器
 */
class DraftController {
  /**
   * 生成内容草稿
   */
  async generateDraft(req, res, next) {
    try {
      const { sessionId } = req.params;
      const result = await pythonService.generateDraft(sessionId);
      res.status(200).json({
        status: 'success',
        data: result
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * 修改草稿内容
   */
  async reviseDraft(req, res, next) {
    try {
      const { sessionId } = req.params;
      const { feedback } = req.body;
      
      const result = await pythonService.processInput(sessionId, `revise: ${feedback}`);
      res.status(200).json({
        status: 'success',
        data: result
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new DraftController(); 