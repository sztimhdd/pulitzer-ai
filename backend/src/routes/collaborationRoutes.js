const express = require('express');
const router = express.Router();
const collaborationController = require('../controllers/collaborationController');

/**
 * @swagger
 * /collaboration/sessions:
 *   post:
 *     summary: 创建新的写作协作会话
 *     tags: [协作会话]
 *     responses:
 *       201:
 *         description: 会话创建成功
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
 *                     sessionId:
 *                       type: string
 *                       format: uuid
 *                     status:
 *                       type: string
 *                       example: initialized
 *                     session:
 *                       $ref: '#/components/schemas/Session'
 *       500:
 *         $ref: '#/components/responses/ServerError'
 */
router.post('/sessions', collaborationController.createSession);

/**
 * @swagger
 * /collaboration/sessions/{sessionId}:
 *   get:
 *     summary: 获取会话状态
 *     tags: [协作会话]
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
 *         description: 会话状态
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: success
 *                 data:
 *                   $ref: '#/components/schemas/Session'
 *       404:
 *         $ref: '#/components/responses/NotFound'
 */
router.get('/sessions/:sessionId', collaborationController.getSession);

/**
 * @swagger
 * /collaboration/sessions/{sessionId}:
 *   delete:
 *     summary: 结束会话
 *     tags: [协作会话]
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
 *         description: 会话已结束
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: success
 *                 message:
 *                   type: string
 *                   example: 会话已结束
 *       404:
 *         $ref: '#/components/responses/NotFound'
 */
router.delete('/sessions/:sessionId', collaborationController.endSession);

// 消息相关路由
router.post('/sessions/:sessionId/input', collaborationController.processInput);
router.get('/sessions/:sessionId/messages', collaborationController.getMessages);

// 状态相关路由
router.get('/sessions/:sessionId/state', collaborationController.getSessionState);

// 大纲相关路由
router.get('/sessions/:sessionId/outline', collaborationController.getOutline);
router.put('/sessions/:sessionId/outline', collaborationController.updateOutline);

// 草稿相关路由
router.get('/sessions/:sessionId/draft', collaborationController.getDraft);
router.put('/sessions/:sessionId/draft', collaborationController.updateDraft);

module.exports = router; 