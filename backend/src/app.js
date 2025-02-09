require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { errorHandler } = require('./utils/errorHandler');
const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('./config/swagger');

// 导入路由
const collaborationRoutes = require('./routes/collaborationRoutes');
const interviewRoutes = require('./routes/interviewRoutes');
const draftRoutes = require('./routes/draftRoutes');

const app = express();

// CORS 配置
const corsOptions = {
  origin: process.env.NODE_ENV === 'development'
    ? 'http://localhost:5173'  // Vite 默认端口
    : ['https://wmilysrsttsc.sealosgzg.site'],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Accept'],
  credentials: true,
  maxAge: 86400
};

// 应用 CORS 配置
app.use(cors(corsOptions));

// 添加预检请求处理
app.options('*', cors(corsOptions));

// 其他中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Swagger文档
app.use('/api/v1/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Swagger JSON端点
app.get('/api/v1/docs.json', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.send(swaggerSpec);
});

// 添加全局请求日志中间件
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.originalUrl}`);
  console.log('Headers:', req.headers);
  console.log('Body:', req.body);
  next();
});

// API路由
app.use('/api/v1/collaboration', collaborationRoutes);
app.use('/api/v1/draft', draftRoutes);

// 404处理
app.use((req, res, next) => {
  res.status(404).json({
    status: 'error',
    message: '未找到请求的资源'
  });
});

// 错误处理中间件
app.use(errorHandler);

// 启动服务器
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';

app.listen(PORT, () => {
  console.log(`服务器运行在 ${NODE_ENV} 模式`);
  console.log(`服务器运行在端口 ${PORT}`);
  console.log(`API文档: ${API_BASE_URL}/api/v1/docs`);
});

module.exports = app; 