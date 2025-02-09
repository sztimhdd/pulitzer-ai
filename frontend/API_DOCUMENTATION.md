我会帮你创建 API_DOCUMENTATION.md 文件：

```markdown:API_DOCUMENTATION.md
# 内容协作系统 API 文档

基于LLM的内容协作系统API文档 v1.0.0

## 基础信息

- 生产环境基础URL: `https://wmilysrsttsc.sealosgzg.site/api/v1`
- 开发环境基础URL: `http://localhost:3000/api/v1`

所有请求和响应均使用 JSON 格式。

## 认证

目前API不需要认证。

## 错误响应格式

当发生错误时，API将返回以下格式的响应：
```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

## API 端点

### 1. 协作会话管理

#### 1.1 创建新会话

```http
POST /collaboration/sessions
```

响应示例：
```json
{
  "status": "success",
  "data": {
    "sessionId": "123e4567-e89b-12d3-a456-426614174000",
    "status": "initialized",
    "session": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "state": "TOPIC_SELECTION",
      "lastInteraction": "2024-02-06T19:20:30.123Z",
      "context": {}
    }
  }
}
```

#### 1.2 获取会话状态

```http
GET /collaboration/sessions/{sessionId}
```

参数：
- `sessionId`: 会话ID (UUID格式)

响应示例：
```json
{
  "status": "success",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "state": "TOPIC_SELECTION",
    "lastInteraction": "2024-02-06T19:20:30.123Z",
    "context": {}
  }
}
```

#### 1.3 结束会话

```http
DELETE /collaboration/sessions/{sessionId}
```

参数：
- `sessionId`: 会话ID (UUID格式)

响应示例：
```json
{
  "status": "success",
  "message": "会话已结束"
}
```

### 2. 面试/对话管理

#### 2.1 处理用户输入

```http
POST /interview/sessions/{sessionId}/input
```

参数：
- `sessionId`: 会话ID (UUID格式)

请求体：
```json
{
  "input": "我想写一篇关于人工智能的文章"
}
```

响应示例：
```json
{
  "status": "success",
  "data": {
    "response": "好的，让我们来讨论这篇文章的具体方向。您希望重点关注AI的哪些方面？",
    "state": "TOPIC_SELECTION",
    "context": {
      "lastInput": "我想写一篇关于人工智能的文章",
      "lastResponse": "..."
    }
  }
}
```

#### 2.2 获取下一个问题

```http
GET /interview/sessions/{sessionId}/next-question
```

参数：
- `sessionId`: 会话ID (UUID格式)

响应示例：
```json
{
  "status": "success",
  "data": {
    "question": "您期望这篇文章的目标读者群是谁？"
  }
}
```

#### 2.3 跳过当前问题

```http
POST /interview/sessions/{sessionId}/skip
```

参数：
- `sessionId`: 会话ID (UUID格式)

响应示例：
```json
{
  "status": "success",
  "data": {
    "message": "已跳过当前问题"
  }
}
```

### 3. 草稿管理

#### 3.1 生成草稿

```http
POST /draft/sessions/{sessionId}/draft
```

参数：
- `sessionId`: 会话ID (UUID格式)

响应示例：
```json
{
  "status": "success",
  "data": {
    "draft": "这是生成的文章草稿内容..."
  }
}
```

#### 3.2 修改草稿

```http
PUT /draft/sessions/{sessionId}/draft
```

参数：
- `sessionId`: 会话ID (UUID格式)

请求体：
```json
{
  "feedback": "请在开头添加更多背景介绍"
}
```

响应示例：
```json
{
  "status": "success",
  "data": {
    "draft": "这是修改后的文章草稿内容..."
  }
}
```

## 状态码说明

- 200: 请求成功
- 201: 创建成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 会话状态

会话可能的状态包括：
- TOPIC_SELECTION: 主题选择阶段
- OUTLINE_REVIEW: 大纲审查阶段
- INTERVIEW: 访谈阶段
- DRAFT_GENERATION: 草稿生成阶段
- DRAFT_REVIEW: 草稿审查阶段
- COMPLETE: 完成阶段

## 在线文档

您可以访问以下地址查看交互式API文档：
- 生产环境：https://wmilysrsttsc.sealosgzg.site/api/v1/docs
- 开发环境：http://localhost:3000/api/v1/docs
```

这个文档已经包含了所有必要的API信息，并使用了正确的Markdown格式。你可以将这个内容保存到项目根目录下的 API_DOCUMENTATION.md 文件中。


