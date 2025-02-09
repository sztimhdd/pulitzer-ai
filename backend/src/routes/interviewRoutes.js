const express = require('express');
const router = express.Router();
const interviewController = require('../controllers/interviewController');

// 添加路由日志中间件
router.use((req, res, next) => {
  console.log(`[Interview Route] ${new Date().toISOString()} - ${req.method} ${req.originalUrl}`);
  console.log('Request Body:', req.body);
  next();
});

/**
 * @swagger
 * /interview/sessions/{sessionId}/input:
 *   post:
 *     summary: 处理用户输入
 *     tags: [面试对话]
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: 会话ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - input
 *             properties:
 *               input:
 *                 type: string
 *                 description: 用户输入内容
 *     responses:
 *       200:
 *         description: 处理结果
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: success
 *                 data:
 *                   type: object
 *                   properties:
 *                     response:
 *                       type: string
 *                     state:
 *                       type: string
 *                     context:
 *                       type: object
 */
router.post('/sessions/:sessionId/input', interviewController.processInput);

/**
 * @swagger
 * /interview/sessions/{sessionId}/next-question:
 *   get:
 *     summary: 获取下一个问题
 *     tags: [面试对话]
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: 会话ID
 *     responses:
 *       200:
 *         description: 下一个问题
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: success
 *                 data:
 *                   type: object
 *                   properties:
 *                     question:
 *                       type: string
 */
router.get('/sessions/:sessionId/next-question', interviewController.getNextQuestion);

/**
 * @swagger
 * /interview/sessions/{sessionId}/skip:
 *   post:
 *     summary: 跳过当前问题
 *     tags: [面试对话]
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: 会话ID
 *     responses:
 *       200:
 *         description: 跳过成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: success
 *                 data:
 *                   type: object
 *                   properties:
 *                     message:
 *                       type: string
 *                       example: 已跳过当前问题
 */
router.post('/sessions/:sessionId/skip', interviewController.skipQuestion);

/**
 * 获取会话消息历史
 */
router.get('/sessions/:sessionId/messages', interviewController.getMessages);

module.exports = router; 