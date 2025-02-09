const express = require('express');
const router = express.Router();
const draftController = require('../controllers/draftController');

/**
 * @swagger
 * /draft/sessions/{sessionId}/draft:
 *   post:
 *     summary: 生成内容草稿
 *     tags: [草稿管理]
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
 *         description: 草稿生成成功
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
 *                     draft:
 *                       type: string
 *                       description: 生成的草稿内容
 *       404:
 *         $ref: '#/components/responses/NotFound'
 *       500:
 *         $ref: '#/components/responses/ServerError'
 */
router.post('/sessions/:sessionId/draft', draftController.generateDraft);

/**
 * @swagger
 * /draft/sessions/{sessionId}/draft:
 *   put:
 *     summary: 修改草稿内容
 *     tags: [草稿管理]
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
 *               - feedback
 *             properties:
 *               feedback:
 *                 type: string
 *                 description: 修改意见
 *     responses:
 *       200:
 *         description: 草稿修改成功
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
 *                     draft:
 *                       type: string
 *                       description: 修改后的草稿内容
 *       404:
 *         $ref: '#/components/responses/NotFound'
 *       500:
 *         $ref: '#/components/responses/ServerError'
 */
router.put('/sessions/:sessionId/draft', draftController.reviseDraft);

module.exports = router; 