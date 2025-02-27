/* Pulitzer AI 辅助创作工具 */

一、系统功能概述

AI辅助创作系统是一款面向普通用户的智能写作助手。系统通过预设的多层级内容模板(如小学作文、公众号文章等)和对应的AI对话策略,帮助用户将个人经历和想法转化为结构完整、表达生动的文章。用户只需选择合适的模板并与AI进行自然对话,系统就能通过智能提问挖掘内容要点,并在用户反馈的基础上不断优化文章。整个过程中,用户可以随时查看生成的内容,给出修改意见,直到最终得到满意的作品。系统无需复杂的配置和学习,为写作困难的用户提供了一个简单有效的创作解决方案。

二、系统使用案例

// 案例背景:一位架构师想要分享自己学习AI本地部署的经历和心得

// 阶段一:选择模板
USER_INPUT: {
    template_type: "公众号文章",
    sub_type: "经验分享",
    style: "技术干货+个人感悟",
    length: "1500-2000字"
}

// 阶段二:选题描述
USER_INPUT: "我想写一篇关于学习AI本地部署的经历,从看到儿子用Claude写游戏开始,到自己一步步探索不同的部署方案。"

AI_RESPONSE: "这是一个很有趣的主题。让我们从您的第一次接触AI开始。能详细说说当时看到儿子用Claude写游戏的场景吗?"

// 阶段三:内容挖掘 - 部分示例
AI_STRATEGY: "技术经验分享 - 起因动机"
USER_INPUT: "我看到儿子竟然一行代码不用写就让Claude帮他写好了一个真正能运行还挺好玩的小游戏"

AI_STRATEGY: "技术经验分享 - 学习过程"
AI_RESPONSE: "您是如何开始学习AI部署的?选择了什么工具?"
USER_INPUT: "我先是试着用了ollama,然后用了huggingface接触到了好多模型..."

AI_STRATEGY: "技术经验分享 - 具体实践"
AI_RESPONSE: "在硬件和参数配置方面遇到了哪些挑战?"
USER_INPUT: "显存不足,context满了..."

// 阶段四:内容整理与反馈
AI_OUTPUT: "[生成的第一版文章片段]"
USER_INPUT: "还是不够长,我觉得我分享了很多技术细节,能帮我都加进去,并且改写得引人入胜吗?"

AI_STRATEGY: "内容扩充 - 技术细节"
AI_OUTPUT: "[增加技术细节的第二版文章]"

// 阶段五:完稿输出
AI_OUTPUT: {
    format: "markdown",
    title: "当AI为架构师装上"编程之眼"",
    content: "[完整的文章内容]"
}

三、系统架构

1. 前端架构
   1.1 技术栈选择
       - 框架: React/Vue
       - 类型系统: TypeScript
       - 样式方案: Tailwind CSS
       - Markdown渲染: react-markdown
   
   1.2 核心组件
       - 模板选择器
       - 对话界面
       - 内容预览
       - 导出工具

2. 模板系统
   2.1 模板定义结构
       - 类型定义
           * 一级分类(作文/公众号等)
           * 二级分类(记叙文/议论文等)
           * 参数配置
               - 文风选项
               - 长度范围
               - 结构偏好
       
       - 提纲模板
           * 章节结构
           * 段落要求
           * 重点提示
       
       - 内容策略
           * 提问模式
           * 展开方向
           * 重点挖掘
   
   2.2 Prompt模板
       - 基础模板
           * 选题引导
           * 内容挖掘
           * 文风转换
       
       - 动态组合
           * 上下文管理
           * 参数注入
           * 模板混合

3. 对话管理
   3.1 状态控制
       - 创作阶段追踪
       - 上下文维护
       - 历史记录
   
   3.2 内容处理
       - 用户输入处理
       - AI响应生成
       - 反馈整合

4. API集成
   4.1 OpenAI接口
       - API封装
       - 错误处理
       - 重试机制
   
   4.2 响应处理
       - 数据解析
       - 格式转换
       - 展示适配

四、功能模块

1. 模板选择模块
   1.1 类型筛选
       - 分类展示
       - 参数配置
       - 预览功能
   
   1.2 创作初始化
       - 模板加载
       - 参数设置
       - 状态初始化

2. 对话交互模块
   2.1 输入处理
       - 文本输入
       - 命令识别
       - 状态切换
   
   2.2 展示输出
       - 消息列表
       - 状态提示
       - 操作按钮

3. 内容生成模块
   3.1 内容处理
       - 文本生成
       - 格式转换
       - 样式应用
   
   3.2 预览展示
       - 实时预览
       - 分段展示
       - 编辑功能

4. 导出模块
   4.1 格式转换
       - Markdown生成
       - 样式应用
       - 格式检查
   
   4.2 导出选项
       - 复制到剪贴板
       - 下载文件
       - 分享链接
