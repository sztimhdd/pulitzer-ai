import os
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import requests
import time
from dataclasses import dataclass
from urllib.parse import urljoin
from openai import OpenAI
import traceback
import sys
import argparse
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 减少第三方库的日志输出
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# 加载环境变量
load_dotenv()

class CollabState(Enum):
    TOPIC_SELECTION = "topic_selection"
    OUTLINE_REVIEW = "outline_review"
    INTERVIEW = "interview"
    DRAFT_GENERATION = "draft_generation"
    DRAFT_REVIEW = "draft_review"
    COMPLETE = "complete"

@dataclass
class LLMConfig:
    """Configuration for OpenAI API endpoint"""
    api_key: str = os.getenv('OPENAI_API_KEY')
    base_url: str = os.getenv('OPENAI_API_BASE', 'https://api.siliconflow.cn/v1')
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.7
    model: str = "deepseek-ai/DeepSeek-R1"
    stream: bool = True
    max_tokens: int = 4096

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_base = os.getenv('OPENAI_API_BASE', 'https://api.siliconflow.cn/v1')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                timeout=30.0,
                max_retries=3
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
        
    def chat(self, messages, temperature=0.7):
        """调用 OpenAI chat completion API"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=messages,
                temperature=temperature,
                max_tokens=4096,
                stream=True
            )
            
            # 收集完整响应
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    
            return full_response
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

class LocalLLMClient:
    """Client for interacting with OpenAI API"""
    def __init__(self, config: LLMConfig):
        self.config = config
        try:
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
                timeout=config.timeout,
                max_retries=config.max_retries
            )
            print("OpenAI client initialized successfully", file=sys.stderr)
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}", file=sys.stderr)
            raise
        self.conversation_history = []
        
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": prompt})

            request_data = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": self.config.stream
            }

            # 调试信息写入stderr
            print("=== LLM Request Details ===", file=sys.stderr)
            print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)
            print(f"Base URL: {self.config.base_url}", file=sys.stderr)
            print("\nRequest Payload:", file=sys.stderr)
            print(json.dumps(request_data, indent=2, ensure_ascii=False), file=sys.stderr)

            try:
                response = self.client.chat.completions.create(**request_data)
                full_response = []
                
                if self.config.stream:
                    # 流式处理
                    current_line = []
                    for chunk in response:
                        if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                            content = chunk.choices[0].delta.content
                            if content:
                                current_line.append(content)
                                # 如果遇到换行符，打印当前行
                                if '\n' in content:
                                    print(f"Response: {''.join(current_line)}", file=sys.stderr)
                                    current_line = []
                                full_response.append(content)
                    
                    # 打印最后一行（如果有）
                    if current_line:
                        print(f"Response: {''.join(current_line)}", file=sys.stderr)
                    
                    complete_response = ''.join(full_response)
                else:
                    complete_response = response.choices[0].message.content
                    print(f"Response: {complete_response}", file=sys.stderr)

                # 保存到对话历史
                self.conversation_history.append({
                    "role": "user",
                    "content": prompt
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": complete_response
                })

                return complete_response

            except Exception as api_error:
                print(f"API Error Details:", file=sys.stderr)
                print(f"Type: {type(api_error).__name__}", file=sys.stderr)
                print(f"Message: {str(api_error)}", file=sys.stderr)
                if hasattr(api_error, 'response'):
                    print(f"Response: {api_error.response}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                raise

        except Exception as e:
            print(f"General Error in LLM generation:", file=sys.stderr)
            print(f"Type: {type(e).__name__}", file=sys.stderr)
            print(f"Message: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []

    def add_context(self, context: str, role: str = "system"):
        """添加上下文信息"""
        self.conversation_history.append({
            "role": role,
            "content": context
        })

class ContentPrompts:
    """Collection of prompts for the content collaboration system"""
    @staticmethod
    def get_initial_system_prompt() -> str:
        return """You are an experienced journalist and high-level content creator working to help users create quality content through an interactive process. Your role combines professional journalism skills with content creation expertise.

        Process Overview:
        1. Topic Selection & Outline:
           - Help users refine their topic choice
           - Create structured, logical outlines
           - Adapt and revise based on feedback

        2. Interview Phase:
           - Ask thoughtful, probing questions
           - Draw out unique insights and perspectives
           - Respect user preferences about depth and detail
           - Recognize when to probe deeper vs. move on
           - Allow users to skip or move forward when desired

        3. Content Creation:
           - Synthesize information effectively
           - Maintain user's voice and style
           - Create engaging, well-structured content
           - Incorporate feedback constructively

        Interaction Guidelines:
        - Maintain a professional yet approachable tone
        - Be responsive to user preferences and pace
        - Offer constructive suggestions
        - Respect user's time and effort
        - Guide without being overbearing
        - Allow users to control the process
        
        Key Principles:
        - Focus on quality over quantity
        - Respect user's expertise and perspective
        - Maintain flexibility in approach
        - Ensure clarity in communication
        - Support iterative improvement"""

    
    @staticmethod
    def get_outline_system_prompt() -> str:
        return """You are an experienced journalist and content creator. 
        Create a well-structured outline for the content per the user's request and word count requirement.
        The outline should have clear sections and subsections."""
    
    @staticmethod
    def get_interview_system_prompt() -> str:
        return """You are an experienced interviewer. Generate thoughtful, casual toned,probing questions that will help extract detailed information from the interviewee to help you build the article according to the given content type, outline and word count.
        1. Your question should focus on a specific aspect of the section that requires more detail or clarity.
        2. As one single question each time
        3. Use simple language and clear structure."""
    
    @staticmethod
    def get_analysis_system_prompt() -> str:
        return """You are an expert editor analyzing interview responses.
        Determine if the content meets the specified criteria based on completeness, depth, and quality."""
    
    @staticmethod
    def get_draft_system_prompt() -> str:
        return """You are an expert content creator synthesizing interview responses into a cohesive article.
        Maintain the interviewee's voice and style while ensuring professional quality and engaging flow."""

class ContentCollaborator:
    def __init__(self, llm_config: LLMConfig = None):
        self.state = CollabState.TOPIC_SELECTION
        self.topic = ""
        self.content_type = ""
        self.target_length = 0
        self.outline = {}
        self.interview_responses = []
        self.current_section = None
        self.draft = ""
        self.settings = {}  # 添加设置字段
        self.config = llm_config or LLMConfig()  # 保存配置
        self.llm = LocalLLMClient(self.config)   # 使用配置创建LLM客户端
        self._last_question = ""
        
    def initialize(self, topic: str, content_type: str, target_length: int, settings: dict = None):
        """初始化协作器的设置"""
        self.topic = topic
        self.content_type = content_type
        self.target_length = target_length
        self.settings = settings or {}
        
        # 生成初始大纲
        self.outline = self._generate_initial_outline()
        self.state = CollabState.OUTLINE_REVIEW
        
        return self.outline

    def _generate_initial_outline(self) -> Dict:
        """生成初始大纲，考虑设置和要求"""
        try:
            # 将调试信息写入stderr而不是stdout
            print("=== LLM Request Details ===", file=sys.stderr)
            print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)
            print(f"URL: {self.config.base_url}", file=sys.stderr)
            print("\nPayload:", file=sys.stderr)
            print(json.dumps({
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": self._get_outline_system_prompt()},
                    {"role": "user", "content": self._get_outline_user_prompt()}
                ],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": self.config.stream
            }, indent=2), file=sys.stderr)

            outline_str = self.llm.generate(
                self._get_outline_user_prompt(), 
                self._get_outline_system_prompt()
            )
            try:
                # 尝试解析JSON
                start_idx = outline_str.find('{')
                end_idx = outline_str.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = outline_str[start_idx:end_idx]
                    outline = json.loads(json_str)
                    if outline:
                        return outline
            except json.JSONDecodeError:
                print("Error parsing outline JSON", file=sys.stderr)

            # 如果解析失败，返回默认大纲
            return self._get_default_outline()
        except Exception as e:
            print(f"Error generating outline: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)  # 打印完整的错误堆栈
            return self._get_default_outline()

    def _get_outline_system_prompt(self) -> str:
        """获取大纲生成的系统提示"""
        return f"""You are an expert content creator specializing in creating outlines for various document types.
        Your task is to create a clear, structured outline appropriate for a {self.target_length}-word {self.content_type}.
        The outline should follow standard conventions for the specific content type while ensuring appropriate depth and coverage.
        
        Additional requirements:
        {json.dumps(self.settings, indent=2, ensure_ascii=False)}
        
        IMPORTANT: Return ONLY valid JSON in this exact format:
        {{
            "section_name": ["subsection1", "subsection2",...],
            "another_section": ["subsection1", "subsection2",...]
        }}"""

    def _get_outline_user_prompt(self) -> str:
        """获取大纲生成的用户提示"""
        return f"""Create a detailed outline for a {self.target_length}-word {self.content_type} about: {self.topic}

        Requirements:
        1. Follow standard {self.content_type} format and structure
        2. Design sections to fit within {self.target_length} words
        3. Include all essential elements for this type of {self.content_type}
        4. Ensure logical progression
        5. Balance section lengths appropriately
        6. Consider these specific settings:
        {json.dumps(self.settings, indent=2, ensure_ascii=False)}
        
        Return ONLY a JSON object with appropriate sections and subsections."""

    def _handle_interview(self, user_input: str) -> str:
        """处理面试阶段的输入"""
        # 记录用户回答
        self.interview_responses.append({
            'section': self.current_section,
            'question': self._last_question,
            'answer': user_input
        })

        # 添加上下文信息
        context = f"""Previous responses for section '{self.current_section}':
        {json.dumps(self.interview_responses, indent=2, ensure_ascii=False)}
        
        Current outline:
        {json.dumps(self.outline, indent=2, ensure_ascii=False)}
        """
        
        self.llm.add_context(context)

        # 分析回答并生成后续问题
        return self._generate_follow_up_question(user_input)

    def _move_to_next_section_or_draft(self) -> str:
        """移动到下一个部分或开始生成草稿"""
        sections = list(self.outline.keys())
        current_index = sections.index(self.current_section)
        
        if current_index + 1 < len(sections):
            self.current_section = sections[current_index + 1]
            return self._generate_interview_question()
        else:
            self.draft = self._generate_draft()
            self.state = CollabState.DRAFT_REVIEW
            return f"基于我们的讨论，我生成了以下草稿：\n\n{self.draft}\n\n您觉得这个草稿怎么样？需要修改吗？"

    def _generate_interview_question(self) -> str:
        """生成针对当前部分的面试问题"""
        context = {
            'topic': self.topic,
            'content_type': self.content_type,
            'current_section': self.current_section,
            'outline': self.outline,
            'previous_responses': self.interview_responses,
            'settings': self.settings
        }
        
        prompt = f"""Generate a question for the '{self.current_section}' section.
        
        Context:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        Requirements:
        1. Focus on specific details needed for this section
        2. Consider previous responses
        3. Align with content type and settings
        4. Use clear, conversational language
        5. Ask one focused question at a time"""
        
        question = self.llm.generate(prompt, ContentPrompts.get_interview_system_prompt())
        self._last_question = question
        return question

    def _generate_draft(self) -> str:
        """根据面试响应生成内容草稿"""
        context = {
            'topic': self.topic,
            'content_type': self.content_type,
            'outline': self.outline,
            'responses': self.interview_responses,
            'settings': self.settings,
            'target_length': self.target_length
        }
        
        prompt = f"""Generate a complete draft based on the interview responses.
        
        Context:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        Requirements:
        1. Follow the outline structure
        2. Incorporate interview responses naturally
        3. Maintain consistent style and tone
        4. Target approximately {self.target_length} words
        5. Format in Markdown
        6. Consider all settings and requirements
        
        Return the complete draft in Markdown format."""
        
        draft = self.llm.generate(prompt, ContentPrompts.get_draft_system_prompt())
        return draft

    def process_user_input(self, user_input: str) -> str:
        """处理用户输入并返回适当的响应"""
        try:
            if self.state == CollabState.OUTLINE_REVIEW:
                return self._handle_outline_review(user_input)
            elif self.state == CollabState.INTERVIEW:
                return self._handle_interview(user_input)
            elif self.state == CollabState.DRAFT_REVIEW:
                return self._handle_draft_review(user_input)
            else:
                return "当前状态无法处理输入"
        except Exception as e:
            print(f"Error processing user input: {e}")
            return f"处理输入时出错: {str(e)}"

    def _handle_outline_review(self, user_input: str) -> str:
        """处理大纲审查阶段的输入"""
        if user_input.lower() in ['y', 'yes', 'ok', '好的', '可以']:
            self.state = CollabState.INTERVIEW
            self.current_section = list(self.outline.keys())[0]
            return self._generate_interview_question()
        
        # 尝试修改大纲
        try:
            # 如果输入是完整的JSON大纲
            if user_input.strip().startswith('{'):
                new_outline = json.loads(user_input)
                self.outline = new_outline
                return "大纲已更新。您觉得现在的大纲怎么样？如果满意，请输入'yes'继续。"
            
            # 处理自然语言的修改建议
            system_prompt = f"""You are an expert content organizer.
            Current outline:
            {json.dumps(self.outline, indent=2, ensure_ascii=False)}
            
            User feedback:
            {user_input}
            
            Modify the outline according to the feedback while:
            1. Maintaining logical structure
            2. Ensuring appropriate depth
            3. Following {self.content_type} conventions
            4. Considering the target length of {self.target_length} words
            
            Return ONLY the modified outline as a JSON object."""
            
            modified_outline = self.llm.generate(prompt=user_input, system_prompt=system_prompt)
            
            try:
                # 尝试解析修改后的大纲
                start_idx = modified_outline.find('{')
                end_idx = modified_outline.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    outline_json = modified_outline[start_idx:end_idx]
                    new_outline = json.loads(outline_json)
                    self.outline = new_outline
                    return f"我已根据您的建议修改了大纲：\n\n{json.dumps(new_outline, indent=2, ensure_ascii=False)}\n\n您觉得这个版本怎么样？如果满意，请输入'yes'继续。"
            except (json.JSONDecodeError, ValueError):
                return "抱歉，我无法正确理解您的修改建议。您可以：\n1. 直接提供JSON格式的完整大纲\n2. 用自然语言描述您想要的修改\n3. 输入'yes'接受当前大纲"
        except Exception as e:
            print(f"Error handling outline review: {e}")
            return "处理大纲修改时出错，请重试或提供更清晰的修改建议。"

    def _handle_draft_review(self, user_input: str) -> str:
        """处理草稿审查阶段的输入"""
        if user_input.lower() in ['y', 'yes', 'ok', '好的', '可以']:
            self.state = CollabState.COMPLETE
            return "太好了！内容创作已完成。您可以使用这个最终版本了。"
        
        # 分析修改建议
        analysis_prompt = f"""Analyze this feedback for the draft:
        {user_input}
        
        Categorize the feedback into these aspects:
        1. Content
        2. Structure
        3. Style
        4. Length
        5. Other
        
        Return the analysis in JSON format."""
        
        try:
            analysis = self.llm.generate(analysis_prompt, ContentPrompts.get_analysis_system_prompt())
            
            # 生成修改后的草稿
            revision_prompt = f"""Original draft:
            {self.draft}
            
            User feedback:
            {user_input}
            
            Feedback analysis:
            {analysis}
            
            Requirements:
            1. Address all feedback points
            2. Maintain consistent style
            3. Keep the structure clear
            4. Target {self.target_length} words
            5. Consider these settings:
            {json.dumps(self.settings, indent=2, ensure_ascii=False)}
            
            Return the complete revised draft in Markdown format."""
            
            revised_draft = self.llm.generate(revision_prompt, ContentPrompts.get_revision_system_prompt())
            self.draft = revised_draft
            
            return f"我已根据您的建议修改了草稿：\n\n{self.draft}\n\n您觉得这个版本怎么样？如果满意，请输入'yes'完成；如果还需要修改，请告诉我具体的建议。"
        except Exception as e:
            print(f"Error in draft revision: {e}")
            return "抱歉，修改草稿时出错。请提供更具体的修改建议，或者输入'yes'接受当前版本。"

    def _get_default_outline(self) -> Dict:
        """根据内容类型返回默认大纲"""
        content_type = self.content_type.lower()
        topic = self.topic

        # 通用的大纲结构
        common_outline = {
            "开篇": [
                "背景介绍",
                f"{topic}的重要性",
                "文章主要内容概述"
            ],
            "主体内容": [
                "当前现状分析",
                "主要挑战和机遇",
                "具体案例分析",
                "发展趋势预测"
            ],
            "总结与展望": [
                "关键要点总结",
                "实践建议",
                "未来展望"
            ]
        }
        
        # 根据内容类型调整大纲
        if content_type == "article":
            return {
                "引言": [
                    "研究背景",
                    "问题定义",
                    "研究意义"
                ],
                "文献综述": [
                    "相关理论基础",
                    "研究现状",
                    "存在的问题"
                ],
                "研究内容": [
                    "研究方法",
                    "数据分析",
                    "结果讨论"
                ],
                "结论": [
                    "主要发现",
                    "研究启示",
                    "未来展望"
                ]
            }
        elif content_type == "blog":
            return {
                "开篇": [
                    "问题引入",
                    f"为什么要讨论{topic}",
                    "主要观点预览"
                ],
                "主体内容": [
                    "核心观点阐述",
                    "实际案例分析",
                    "解决方案建议"
                ],
                "总结": [
                    "关键要点回顾",
                    "行动建议",
                    "读者互动问题"
                ]
            }
        elif content_type == "report":
            return {
                "执行摘要": [
                    "报告目的",
                    "主要发现",
                    "关键建议"
                ],
                "现状分析": [
                    "数据概览",
                    "问题识别",
                    "影响因素"
                ],
                "详细发现": [
                    "关键发现1",
                    "关键发现2",
                    "关键发现3"
                ],
                "建议": [
                    "短期建议",
                    "中长期建议",
                    "实施步骤"
                ]
            }
        else:
            # 返回通用大纲
            return common_outline

# 添加会话管理
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ContentCollaborator] = {}
        # 使用默认配置创建 LLMConfig
        self.config = LLMConfig()

    def get_or_create_session(self, session_id: str) -> ContentCollaborator:
        """获取或创建会话，确保会话存在"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ContentCollaborator(self.config)
        return self.sessions[session_id]

    def end_session(self, session_id: str) -> bool:
        """结束并清理会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# 创建全局会话管理器
session_manager = SessionManager()

def handle_command(session_id, input_data, context):
    """处理各种命令"""
    try:
        command_type = input_data.get('type')
        command_data = input_data.get('data', {})
        
        logger.info(f"Received command: {command_type}")

        # 处理生成大纲命令
        if command_type == 'GENERATE_OUTLINE':
            result = handle_generate_outline(session_id, command_data, context)
            logger.info(f"Generated outline response: success={result['status']}")
            return result
        
        # 处理初始化命令
        elif command_type == 'INITIALIZE_SESSION':
            result = handle_initialize_session(session_id, command_data, context)
            logger.info(f"Initialized session: success={result['status']}")
            return result
        
        # 未知命令
        else:
            logger.warning(f"Unknown command type: {command_type}")
            return {
                "status": "error",
                "message": f"未知的命令类型: {command_type}"
            }
            
    except Exception as e:
        logger.error(f"Error handling command: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def handle_generate_outline(session_id, data, context):
    """生成文章大纲"""
    try:
        topic = data.get('topic')
        article_type = data.get('articleType')
        word_count = data.get('wordCount')
        
        logger.info(f"Generating outline for topic: {topic}")
        
        # 构造 LLM 提示词
        prompt = f'''你是一个专业的文章大纲生成助手。请严格按照以下要求生成大纲：

主题：{topic}
文章类型：{article_type}
字数要求：{word_count}字

要求：
1. 符合{article_type}的写作风格和结构
2. 合理分配{word_count}字的内容
3. 包含必要的章节和子章节
4. 确保逻辑流畅
5. 各部分篇幅合理

重要：请只返回JSON格式的大纲，不要包含任何其他文字说明。
格式示例：
{{
    "引言": ["背景介绍", "主要观点"],
    "正文": ["第一部分要点", "第二部分要点", "第三部分要点"],
    "结论": ["总结", "展望"]
}}

请直接返回JSON，不要有任何额外的解释或说明。
'''
        
        # 调用 LLM
        response = llm.chat(
            messages=[
                {"role": "system", "content": "你是一个专业的文章大纲生成助手。你只返回JSON格式的大纲，不返回任何其他内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # 尝试提取 JSON
        try:
            # 查找第一个 { 和最后一个 }
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                outline = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except:
            logger.warning("Failed to parse LLM response as JSON, using default outline")
            outline = {
                "引言": ["背景介绍", "主要观点"],
                "正文": ["第一部分", "第二部分", "第三部分"],
                "结论": ["总结", "展望"]
            }
        
        return {
            "status": "success",
            "data": {
                "outline": outline,
                "state": "OUTLINE_REVIEW",
                "response": "已生成大纲，请审阅。",
                "context": {
                    "outline": outline,
                    "topic": topic,
                    "articleType": article_type,
                    "wordCount": word_count
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating outline: {e}")
        return {
            "status": "error",
            "message": f"生成大纲失败: {str(e)}"
        }

def handle_initialize_session(session_id, data, context):
    """处理会话初始化"""
    try:
        topic = data.get('topic')
        article_type = data.get('articleType')
        word_count = data.get('wordCount')
        
        return {
            "status": "success",
            "data": {
                "response": f'我将帮助您撰写一篇关于"{topic}"的{word_count}字{article_type}文章。',  # 使用单引号包裹
                "state": "TOPIC_SELECTION",
                "context": {
                    "topic": topic,
                    "articleType": article_type,
                    "wordCount": word_count,
                    "initialization": data
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error initializing session: {e}")
        return {
            "status": "error",
            "message": f"初始化会话失败: {str(e)}"
        }

def process_input(session_id, user_input, context=None):
    """处理用户输入，返回适当的响应"""
    try:
        # 获取或创建会话
        collaborator = session_manager.get_or_create_session(session_id)
        
        # 尝试解析 JSON 输入
        input_data = None
        if isinstance(user_input, str) and user_input.startswith('{'):
            try:
                input_data = json.loads(user_input)
            except json.JSONDecodeError:
                pass

        # 处理初始化命令
        if (user_input.lower() == 'start' or 
            (input_data and input_data.get('type') == 'INITIALIZE_SESSION')):
            
            # 从context或input_data获取初始化信息
            if input_data and 'data' in input_data:
                init_data = input_data['data']
            elif context and 'initialization' in context:
                init_data = context['initialization']
            else:
                raise ValueError("Missing initialization data")

            # 使用初始化数据
            outline = collaborator.initialize(
                topic=init_data.get('topic', ''),
                content_type=init_data.get('articleType', 'Article'),
                target_length=init_data.get('wordCount', 1000),
                settings=init_data.get('settings', {})
            )
            
            response_data = {
                "status": "success",
                "data": {
                    "response": f"基于您的设置，我生成了以下大纲：\n\n{json.dumps(outline, indent=2, ensure_ascii=False)}\n\n您觉得这个大纲怎么样？需要调整吗？",
                    "state": collaborator.state.value.upper(),
                    "context": {
                        "sessionId": session_id,
                        "currentState": collaborator.state.value.upper(),
                        "lastInput": user_input,
                        "outline": outline,
                        "settings": init_data.get('settings', {}),
                        "initialization": {
                            "topic": init_data.get('topic', ''),
                            "type": init_data.get('articleType', ''),
                            "wordCount": init_data.get('wordCount', 1000),
                            "settings": init_data.get('settings', {})
                        },
                        "selectedType": init_data.get('articleType', ''),
                        "topic": init_data.get('topic', ''),
                        "wordCount": init_data.get('wordCount', 1000)
                    }
                }
            }
            
            print(json.dumps(response_data, ensure_ascii=False))
            return
        
        # 处理其他输入
        response = collaborator.process_user_input(
            input_data['data'] if input_data else user_input
        )
        
        response_data = {
            "status": "success",
            "data": {
                "response": response,
                "state": collaborator.state.value.upper(),
                "context": {
                    "sessionId": session_id,
                    "currentState": collaborator.state.value.upper(),
                    "lastInput": user_input,
                    "outline": collaborator.outline,
                    "settings": collaborator.settings,
                    "initialization": context.get('initialization') if context else None,
                    "selectedType": collaborator.content_type,
                    "topic": collaborator.topic,
                    "wordCount": collaborator.target_length
                }
            }
        }
        
        print(json.dumps(response_data, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error processing input: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        error_response = {
            "status": "error",
            "error": {
                "message": str(e),
                "type": type(e).__name__
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))

def test_llm_api():
    """测试 LLM API 连接和调用"""
    try:
        logger.info("Starting LLM API test")
        
        # 初始化客户端
        test_client = LLMClient()
        
        # 测试简单对话
        test_messages = [
            {"role": "system", "content": "你是一个帮助测试API的助手。"},
            {"role": "user", "content": "请说一句简单的话来测试API是否正常工作。"}
        ]
        
        logger.info("Sending test message")
        response = test_client.chat(test_messages)
        logger.info(f"Test response received: {response}")
        
        return {
            "status": "success",
            "message": "API test successful",
            "response": response
        }
        
    except Exception as e:
        logger.error(f"API test failed: {e}")
        return {
            "status": "error",
            "message": f"API test failed: {str(e)}"
        }

# 在主函数中添加测试选项
def main():
    """主入口函数"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', help='Session ID')
    parser.add_argument('--input', help='User input')
    parser.add_argument('--context', help='Context data')
    parser.add_argument('--test', action='store_true', help='Run API test')
    args = parser.parse_args()

    try:
        if args.test:
            result = test_llm_api()
            print(json.dumps(result, ensure_ascii=False))
            return

        session_id = args.session
        input_data = json.loads(args.input) if args.input else None
        context = json.loads(args.context) if args.context else {}

        logger.info(f"Received request for session {session_id}")

        if isinstance(input_data, dict) and input_data.get('type'):
            result = handle_command(session_id, input_data, context)
        else:
            result = process_input(session_id, input_data, context)

        logger.info(f"Sending response: success={result['status']}")
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Error in main: {e}")
        error_response = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_response, ensure_ascii=False))

# 确保 llm 对象已初始化
try:
    llm = LLMClient()
    logger.info("LLM client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM client: {e}")
    raise

if __name__ == "__main__":
    main()
