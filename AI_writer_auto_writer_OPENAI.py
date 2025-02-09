import os
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import requests
import time
from dataclasses import dataclass
from urllib.parse import urljoin
from openai import OpenAI
import re

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
    api_key: str = "sk-tjlmkuzuqihmsfydjsnbkuiygpcfwewvvanbhkwyjbmygpzc"
    base_url: str = "https://api.siliconflow.cn/v1"
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.4
    model: str = "deepseek-ai/DeepSeek-R1"
    stream: bool = True
    max_tokens: int = 4096

class LocalLLMClient:
    """Client for interacting with OpenAI API"""
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries
        )
        
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate text using OpenAI API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=self.config.stream
            )

            content = ""
            if self.config.stream:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                return content
            else:
                return response.choices[0].message.content

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None

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
        return """You are an experienced interviewer. Generate thoughtful, 
        probing questions that will help extract detailed information from the interviewee to help you build the article according to the given content type, outline and word count.
        1. Your question should focus on a specific aspect of the section that requires more detail or clarity.
        2. As one single question each time
        3. Use simple language and clear structure."""
    
    @staticmethod
    def get_analysis_system_prompt() -> str:
        return """You are an expert editor analyzing interview responses.
        Determine if the content meets the specified criteria based on completeness, depth, word count restriction, and quality."""
    
    @staticmethod
    def get_draft_system_prompt() -> str:
        return """You are an expert content creator synthesizing interview responses into a cohesive article.
        Maintain the interviewee's voice and style while ensuring professional quality and engaging flow, as well as meeting the outline structure and word count requirement."""

class ContentCollaborator:
    def __init__(self, llm_config: LLMConfig = None):
        self.state = CollabState.TOPIC_SELECTION
        self.topic = ""
        self.target_length = 0
        self.outline = {}
        self.interview_responses = []
        self.current_section = None
        self.draft = ""
        self.llm = LocalLLMClient(llm_config or LLMConfig())
        self.MAX_PROBING_QUESTIONS = 3  # Default value
        
    def _generate_initial_outline(self) -> Dict:
        """Generate initial outline using LLM based on content type and length"""
        system_prompt = f"""You are an expert content creator specializing in creating outlines for various document types.
        Your task is to create a clear, structured outline appropriate for a {self.target_length}-word {self.content_type}.
        The outline should follow standard conventions for the specific content type while ensuring appropriate depth and coverage.
        
        IMPORTANT: Return ONLY valid JSON in this exact format:
        {{
            "section_name": ["subsection1", "subsection2",...],
            "another_section": ["subsection1", "subsection2",...]
        }}
        
        Consider:
        - Appropriate sections for a {self.content_type}
        - Balanced coverage within {self.target_length} words
        - Standard structure expectations for this format
        - Logical flow between sections
        
        Do not include any explanations or comments - just the JSON object."""

        prompt = f"""Create a detailed outline for a {self.target_length}-word {self.content_type} about: {self.topic}

        Requirements:
        1. Follow standard {self.content_type} format and structure
        2. Design sections to fit within {self.target_length} words
        3. Include all essential elements for this type of {self.content_type}
        4. Ensure logical progression
        5. Balance section lengths appropriately
        
        Return ONLY a JSON object with appropriate sections and subsections."""

        try:
            outline_str = self.llm.generate(prompt, system_prompt)
            try:
                # Extract JSON if embedded in other text
                start_idx = outline_str.find('{')
                end_idx = outline_str.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = outline_str[start_idx:end_idx]
                    outline = json.loads(json_str)
                    if outline:  # Check if we got a non-empty outline
                        return outline
            except json.JSONDecodeError:
                print("Error parsing outline JSON")

            # If we get here, generate a type-specific outline
            content_type = self.content_type.lower()
            word_count = self.target_length
            
            if content_type == "memo":
                return {
                    "Purpose": ["Issue Overview", "Key Points"],
                    "Background": ["Context", "Relevant Information"],
                    "Discussion": ["Analysis", "Implications"],
                    "Recommendations": ["Action Items", "Next Steps"]
                }
            elif content_type == "article":
                return {
                    "Introduction": ["Context", "Main Points"],
                    "Background": ["Historical Context", "Current Situation"],
                    "Analysis": ["Key Findings", "Supporting Evidence"],
                    "Conclusion": ["Summary", "Implications"]
                }
            elif content_type == "user manual":
                return {
                    "Overview": ["Purpose", "System Components"],
                    "Setup": ["Installation", "Initial Configuration"],
                    "Usage": ["Basic Features", "Advanced Functions"],
                    "Troubleshooting": ["Common Issues", "Solutions"]
                }
            elif content_type == "story":
                return {
                    "Setting": ["Time", "Place", "Context"],
                    "Characters": ["Main Character", "Supporting Characters"],
                    "Plot": ["Conflict", "Rising Action", "Climax"],
                    "Resolution": ["Outcome", "Conclusion"]
                }
            else:
                return {
                    "Introduction": ["Context", "Purpose"],
                    "Main Content": ["Key Points", "Supporting Details"],
                    "Conclusion": ["Summary", "Next Steps"]
                }
                
        except Exception as e:
            print(f"Error generating outline: {e}")
            return {
                "Introduction": ["Context", "Purpose"],
                "Main Content": ["Key Points", "Analysis"],
                "Conclusion": ["Summary", "Next Steps"]
            }
            

    def _generate_interview_question(self) -> Tuple[str, str]:
        """Generate question and rationale for current section"""
        context = "\n".join([
            f"Q&A {i+1}:" + json.dumps(resp) 
            for i, resp in enumerate(self.interview_responses)
        ])
        
        prompt = f"""Topic: {self.topic}
        Content Type: {self.content_type}
        Current section: {self.current_section}
        Previous responses: {context}
        
        Generate:
        1. A focused interview question for this section
        2. A rationale explaining why this question is important
        
        Format your response as:
        QUESTION: [your question]
        RATIONALE: [explanation of why this question matters]"""
        
        result = self.llm.generate(
            prompt,
            system_prompt=ContentPrompts.get_interview_system_prompt()
        )
        
        try:
            question = result.split('QUESTION:')[1].split('RATIONALE:')[0].strip()
            rationale = result.split('RATIONALE:')[1].strip()
            return question, rationale
        except:
            return "Could you tell me more about this topic?", "Basic exploration of the topic"

    def _get_max_probing_questions(self) -> int:
        """Determine appropriate number of follow-up questions using LLM"""
        system_prompt = """You are an expert content strategist.
        Analyze the content parameters and suggest an appropriate number of follow-up questions per section.
        Consider content depth, complexity, and word count constraints."""
        
        prompt = f"""Content Parameters:
        - Type: {self.content_type}
        - Word Count: {self.target_length}
        - Outline: {json.dumps(self.outline)}
        
        Determine the optimal maximum number of follow-up questions per section.
        Consider:
        1. Depth needed for each section
        2. Word count limitations
        3. Complexity of the topic
        4. Standard length for this content type
        
        Return ONLY a number between 1 and 5.""" 


        try:
            result = self.llm.generate(prompt, system_prompt)
            numbers = re.findall(r'\d+', result)
            if numbers:
                return min(5, max(1, int(numbers[0])))
            return 3  # Default fallback
        except:
            return 3  # Default fallback

    def _should_probe_deeper(self, response: str) -> bool:
        """Analyze if the response needs follow-up questions"""
        section_questions = len([
            resp for resp in self.interview_responses 
            if resp["section"] == self.current_section
        ])
        
        if section_questions >= self.MAX_PROBING_QUESTIONS:
            return False
            
        prompt = f"""Previous response: {response}
        
        Should this response be followed up with more probing questions?
        Consider:
        1. Are there unexplored aspects?
        2. Could more details enhance the content?
        3. Are there missing examples or evidence?
        4. Would emotional/experiential content add value?
        5. Does the word count limit allow for more depth?
        
        Respond with only 'yes' or 'no'."""
        
        result = self.llm.generate(
            prompt,
            system_prompt=ContentPrompts.get_analysis_system_prompt()
        )
        return result and result.lower().strip() == 'yes'

    def _is_section_complete(self) -> bool:
        """Determine if current section has sufficient content"""
        section_responses = [
            resp for resp in self.interview_responses 
            if resp["section"] == self.current_section
        ]
        
        prompt = f"""Current section: {self.current_section}
        Section responses: {json.dumps(section_responses)}
        
        Is this section complete enough to move on?
        Consider:
        1. Have key points been covered?
        2. Is there sufficient depth?
        3. Are there good examples/evidence?
        4. Does it flow well?
        5. Does the word count limit allow for more depth?
        
        Respond with only 'yes' or 'no'."""
        
        result = self.llm.generate(
            prompt,
            system_prompt=ContentPrompts.get_analysis_system_prompt()
        )
        return result and result.lower().strip() == 'yes'

    def _generate_draft(self) -> str:
        """Generate article draft from interview responses"""
        prompt = f"""Topic: {self.topic}
        Target length: {self.target_length} words
        Outline: {json.dumps(self.outline)}
        Interview content: {json.dumps(self.interview_responses)}
        
        Generate a complete article that:
        1. Follows the outline structure
        2. Incorporates interview content naturally
        3. Maintains consistent voice/style
        4. Includes appropriate transitions
        5. Creates engaging flow
        5. Meet the word count requirement
        
        Return the article in Markdown format."""
        
        result = self.llm.generate(
            prompt,
            system_prompt=ContentPrompts.get_draft_system_prompt()
        )
        return result or "Error generating draft."

    def process_user_input(self, user_input: str) -> str:
        """Process user input based on current state"""
        if self.state == CollabState.TOPIC_SELECTION:
            return self._handle_topic_selection(user_input)
        elif self.state == CollabState.OUTLINE_REVIEW:
            return self._handle_outline_review(user_input)
        elif self.state == CollabState.INTERVIEW:
            return self._handle_interview(None)
        elif self.state == CollabState.DRAFT_REVIEW:
            return self._handle_draft_review(user_input)
        elif self.state == CollabState.COMPLETE:
            if user_input.lower() in ['exit', 'quit']:
                return "Goodbye!"
            return "Content creation complete. Type 'exit' to quit."
        else:
            return "I'm not sure how to proceed. Let's start over with topic selection."

    def _handle_topic_selection(self, user_input: str) -> str:
        

        """Handle topic selection phase"""
        # Initial welcome and content type selection
        if not hasattr(self, 'selection_stage'):
            self.selection_stage = 'content_type'
            return (
                "Welcome to the Content Collaboration System!\n\n"
                "What type of content would you like to create?\n"
                "Options: Article, Story, Manual, Blog Post, Report, Memo, Biography\n"
                "Please select one: "
            )
        
        # Handle content type selection
        elif self.selection_stage == 'content_type':
            content_type = user_input.strip().lower()
            valid_types = {'article', 'story', 'manual', 'blog post', 'report', 'memo', 'biography'}
            
            if content_type not in valid_types:
                return (
                    "Sorry, that's not a valid content type. Please choose from:\n"
                    "Article, Story, Manual, Blog Post, Report, Memo, Biography"
                )
                
            self.content_type = user_input
            self.selection_stage = 'topic'
            return f"Great! Please provide a topic for your {self.content_type}:"     
          
        # Initial topic prompt
        if not self.topic:
            system_prompt = """You are an experienced content creator and editor.
            Help guide users in refining their topic and choosing appropriate content structure.
            Consider the topic's scope, target audience, and best format for delivery."""
            
            prompt = f"""User wants to create content about: {user_input}

            Please analyze this topic and suggest the best content type (article, manual, story, etc).
            Provide thoughtful feedback on the topic's scope and potential.
            
            Return your response in this format:
            CONTENT_TYPE: [suggested content type]
            TOPIC: [refined topic/title]
            FEEDBACK: [your brief analysis and suggestions]
            """
            
            try:
                response = self.llm.generate(prompt, system_prompt)
                # Parse the response
                content_type = response.split('CONTENT_TYPE:')[1].split('\n')[0].strip()
                refined_topic = response.split('TOPIC:')[1].split('\n')[0].strip()
                feedback = response.split('FEEDBACK:')[1].strip()
                
                self.content_type = content_type
                self.topic = refined_topic
                
                return (f"I see you want to create a {content_type}. "
                    f"I suggest we refine the topic to: '{refined_topic}'\n\n"
                    f"{feedback}\n\n"
                    f"Does this direction work for you? (yes/no)\n"
                    f"If not, please share your thoughts and we can refine it further.")
                
            except Exception as e:
                print(f"Error in topic analysis: {e}")
                self.topic = user_input  # Fallback to direct user input
                return ("I'll help you create content about this topic.\n"
                    "What length (in words) would you like to aim for?")
        
        # Handle topic refinement
        elif not hasattr(self, 'topic_confirmed'):
            if user_input.lower() in ['y', 'yes', 'ok', 'sure', 'good']:
                self.topic_confirmed = True
                return "Great! What length (in words) would you like to aim for?"
            else:
                # Use LLM to refine topic based on feedback
                system_prompt = """You are an experienced content creator helping refine a topic.
                Consider user feedback and suggest improvements while maintaining the original intent."""
                
                prompt = f"""Original topic: {self.topic}
                Content type: {self.content_type}
                User feedback: {user_input}
                
                Please suggest a refined topic that addresses the user's feedback."""
                
                try:
                    refined_topic = self.llm.generate(prompt, system_prompt)
                    self.topic = refined_topic
                    return f"How about this refined topic: '{refined_topic}'\nDoes this work better? (yes/no)"
                except Exception as e:
                    print(f"Error in topic refinement: {e}")
                    return "Could you clarify what changes you'd like to make to the topic?"
        
        # Handle length specification
        else:
            try:
                self.target_length = int(user_input)
                # Generate outline based on confirmed topic and type
                self.outline = self._generate_initial_outline()
                self.state = CollabState.OUTLINE_REVIEW
                return f"Here's a proposed outline for your {self.content_type}:\n{json.dumps(self.outline, indent=2)}\n\nDoes this outline work for you? (yes/no)"
            except ValueError:
                return "Please provide a number for the target length (in words)."

    def _handle_outline_review(self, user_input: str) -> str:
        """Handle outline review phase"""
        if user_input.lower() in ['y', 'yes', 'looks good', 'good', 'okay', 'ok']:
            self.state = CollabState.INTERVIEW
            self.current_section = list(self.outline.keys())[0]
            return self._generate_interview_question()
        else:
            # Use LLM to modify outline based on user feedback
            context = {
                "topic": self.topic,
                "content_type": self.content_type,
                "target_length": self.target_length,
                "previous_outline": self.outline,
                "conversation_history": self.interview_responses
            }
            
            system_prompt = f"""You are an expert {self.content_type} writer and editor.
            Your task is to create or modify an outline that's specifically appropriate for a {self.target_length}-word {self.content_type} about {self.topic}.
            
            Consider:
            1. Standard structure for {self.content_type}
            2. Appropriate depth for {self.target_length} words
            3. Key elements that must be covered
            4. Logical flow and progression
            5. Balance between sections
            6. Maintaining user's voice and style
            
            IMPORTANT: Return ONLY valid JSON with this exact format:
            {{
                "section_name": ["subsection1", "subsection2", ...],
                "another_section": ["subsection1", "subsection2", ...]
            }}
            
            Do not include any explanations or comments - just the JSON object."""
            
            prompt = f"""Context Information:
            {json.dumps(context, indent=2)}
            
            User feedback: {user_input}
            
            Create or modify the outline to be specifically appropriate for a {self.target_length}-word {self.content_type} about {self.topic}.
            
            Important considerations:
            1. Structure should follow standard {self.content_type} format
            2. Sections should be balanced for {self.target_length} words
            3. Include all essential elements for {self.content_type}
            4. Maintain clear progression and flow
            5. Consider user's feedback carefully
            
            Return ONLY the JSON outline object in the specified format."""
            
            try:
                # Get modified outline from LLM
                modified_outline_str = self.llm.generate(prompt, system_prompt)
                
                # Try to extract JSON if it's embedded in other text
                try:
                    # Look for JSON-like structure
                    start_idx = modified_outline_str.find('{')
                    end_idx = modified_outline_str.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = modified_outline_str[start_idx:end_idx]
                        # Parse the extracted JSON
                        new_outline = json.loads(json_str)
                        
                        # Validate the structure
                        if all(isinstance(k, str) and isinstance(v, list) 
                            and all(isinstance(i, str) for i in v) 
                            for k, v in new_outline.items()):
                            self.outline = new_outline
                            return (
                                f"I've updated the outline for your {self.target_length}-word {self.content_type} "
                                f"about {self.topic}:\n"
                                f"{json.dumps(self.outline, indent=2)}\n\n"
                                f"Does this look better? If not, feel free to suggest more changes."
                            )
                    
                    raise ValueError("Invalid outline structure")
                    
                except (json.JSONDecodeError, ValueError):
                    return (
                        f"I couldn't properly modify the outline for your {self.content_type}. "
                        "Could you please provide more specific suggestions? For example:\n"
                        "- Add a section about X\n"
                        "- Remove the section on Y\n"
                        "- Move Z to come before W\n"
                        "- Split section X into A and B"
                    )
                    
            except Exception as e:
                print(f"Error in outline modification: {e}")
                return (
                    "I encountered an error while trying to modify the outline. "
                    "Could you please provide your suggested changes in a different way? "
                    "Try being more specific about what sections you'd like to add, "
                    "remove, or modify."
                )

    def _handle_interview(self, user_input: str) -> str:
        """Handle interview phase using LLM for answers"""
        print("\n=== Interview Process ===")
        print(f"Current State: {self.state}")
        print(f"Current Section: {self.current_section}")
        print(f"Questions asked in this section: {len([r for r in self.interview_responses if r['section'] == self.current_section])}")
        
        # Get question and rationale
        question, rationale = self._generate_interview_question()
        
        print("\n--- Generating Question ---")
        print(f"Q: {question}")
        print(f"Rationale: {rationale}")
        
        # Create answer prompt
        answer_prompt = f"""Topic: {self.topic}
        Section: {self.current_section}
        
        Question: {question}
        Rationale: {rationale}
        
        Provide a 200 word concise answer to the above question using simple english. 
        Use the Rationale provided to help generate your answer."""
        
        print("\n--- Generating Answer ---")
        # Get answer from LLM
        answer = self.llm.generate(
            answer_prompt,
            system_prompt="You are an expert being interviewed about this topic."
        )
        print(f"A: {answer}")
        
        # Save the response
        self.interview_responses.append({
            "section": self.current_section,
            "question": question,
            "rationale": rationale,
            "response": answer
        })
        
        print("\n--- Analysis ---")
        # Check if we should continue with more questions
        should_probe = self._should_probe_deeper(answer)
        print(f"Should probe deeper? {should_probe}")
        
        if should_probe:
            return f"Moving to follow-up question...\n\nQ: {question}\nRationale: {rationale}"
        else:
            print("\n=== Section Complete ===")
            return self._move_to_next_section_or_draft()

    def _move_to_next_section_or_draft(self) -> str:
        """Helper method to handle section transitions"""
        sections = list(self.outline.keys())
        current_index = sections.index(self.current_section)
        
        if current_index + 1 < len(sections):
            self.current_section = sections[current_index + 1]
            # Get next question and rationale
            question, rationale = self._generate_interview_question()
            return (
                f"Moving on to section: {self.current_section}\n\n"
                f"Next Question: {question}\n"
                f"Rationale: {rationale}"
            )
        else:
            self.draft = self._generate_draft()
            self.state = CollabState.DRAFT_REVIEW
            return f"Great! I'll generate a draft based on our discussion.\n\n{self.draft}\n\nIs this draft acceptable? (yes/no)"

    def _handle_draft_review(self, user_input: str) -> str:
        """Handle draft review phase with intelligent feedback incorporation"""
        if user_input.lower() in ['y', 'yes', 'looks good', 'good', 'okay', 'ok']:
            self.state = CollabState.COMPLETE
            return (
                f"Great! Content creation complete. Here's your final Markdown document:\n\n"
                f"{self.draft}\n\n"
                f"You can copy this Markdown content and use it as needed."
            )
        
        # Use LLM to analyze feedback and modify draft
        system_prompt = """You are an expert editor reviewing and modifying article content.
        Consider style, tone, structure, clarity, and completeness while implementing changes.
        Maintain the author's voice while improving the content based on feedback.
        Return the modified article in Markdown format."""
        
        context = {
            "topic": self.topic,
            "content_type": self.content_type,  # Include content type for better context
            "target_length": self.target_length,
            "outline": self.outline,
            "interview_responses": self.interview_responses
        }
        
        prompt = f"""Current draft:
        {self.draft}

        Original context:
        {json.dumps(context, indent=2)}

        User feedback:
        {user_input}

        Please modify the draft to address this feedback while:
        1. Maintaining consistent style and voice
        2. Preserving successful elements
        3. Ensuring clarity and flow
        4. Following the original outline
        5. Incorporating relevant interview content
        6. Adhering to the {self.content_type} format and conventions

        Return the complete modified article in Markdown format."""
        
        try:
            modified_draft = self.llm.generate(prompt, system_prompt)
            if not modified_draft:
                return (
                    "I encountered an error while modifying the draft. "
                    "Could you please provide more specific feedback about what you'd like to change? "
                    "For example:\n"
                    "- Clarify a specific section\n"
                    "- Add more detail about X\n"
                    "- Make the tone more formal/casual\n"
                    "- Reorganize the structure"
                )
            
            self.draft = modified_draft
            return (
                f"I've updated the draft based on your feedback:\n\n{self.draft}\n\n"
                f"How's this version? Feel free to suggest more changes, or type 'yes' if you're satisfied."
            )
            
        except Exception as e:
            print(f"Error in draft modification: {e}")
            return (
                "I encountered an error while modifying the draft. "
                "Could you please rephrase your feedback or be more specific about the desired changes? "
                "You can focus on specific aspects like clarity, structure, detail level, or tone."
            )
# Example usage:
if __name__ == "__main__":
    try:
        config = LLMConfig()
        collaborator = ContentCollaborator(config)
    except Exception as e:
        print(f"Error initializing the system: {e}")
        exit(1)

    print("\nWelcome to the Content Collaboration System!")
    print("Type 'quit' at any time to exit the program.\n")

    try:
        while True:
            if collaborator.state == CollabState.INTERVIEW:
                response = collaborator.process_user_input(None)
                print(response)
                time.sleep(2)
                continue

            user_input = input("> ").strip()
            
            if user_input.lower() in ['quit', 'exit'] and collaborator.state != CollabState.COMPLETE:
                print("\nThank you for using the Content Collaboration System. Goodbye!")
                break

            if not user_input:
                print("Please provide some input.")
                continue

            response = collaborator.process_user_input(user_input)
            print(response)
            
            if response == "Goodbye!":
                break

    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        print("\nThank you for using the Content Collaboration System!")
