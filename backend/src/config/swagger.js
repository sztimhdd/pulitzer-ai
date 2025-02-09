const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: '内容协作 API',
      version: '1.0.0',
      description: '基于LLM的内容协作系统API文档',
      contact: {
        name: 'API Support',
        email: 'support@example.com'
      }
    },
    servers: [
      {
        url: 'https://wmilysrsttsc.sealosgzg.site/api/v1',
        description: '生产服务器'
      },
      {
        url: 'http://localhost:3000/api/v1',
        description: '开发服务器'
      }
    ],
    components: {
      schemas: {
        Error: {
          type: 'object',
          properties: {
            status: {
              type: 'string',
              example: 'error'
            },
            message: {
              type: 'string',
              example: '错误信息'
            }
          }
        },
        Session: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              format: 'uuid',
              example: '123e4567-e89b-12d3-a456-426614174000'
            },
            state: {
              type: 'string',
              enum: ['TOPIC_SELECTION', 'OUTLINE_REVIEW', 'INTERVIEW', 'DRAFT_GENERATION', 'DRAFT_REVIEW', 'COMPLETE'],
              example: 'TOPIC_SELECTION'
            },
            lastInteraction: {
              type: 'string',
              format: 'date-time'
            },
            context: {
              type: 'object'
            }
          }
        }
      },
      responses: {
        NotFound: {
          description: '未找到请求的资源',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              }
            }
          }
        },
        ServerError: {
          description: '服务器内部错误',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Error'
              }
            }
          }
        }
      }
    }
  },
  apis: [
    './src/routes/collaborationRoutes.js',
    './src/routes/interviewRoutes.js',
    './src/routes/draftRoutes.js'
  ],
};

module.exports = swaggerJsdoc(options); 