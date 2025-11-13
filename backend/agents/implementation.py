"""
Implementation Agent - Generates and edits code
"""

from typing import List, Dict, Any
import re
import json
import copy

from agents.base import BaseAgent, AgentContext, AgentResponse
from core.llm_router import AgentType
from core.config import settings
from services.vector_store import search_code
from tools.definitions import TOOL_FUNCTIONS


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": copy.deepcopy(definition)
    }
    for definition in TOOL_FUNCTIONS
]


class ImplementationAgent(BaseAgent):
    """Agent specialized in code implementation"""
    
    def __init__(self):
        super().__init__(AgentType.IMPLEMENTATION)
    
    def build_system_prompt(self) -> str:
        return """You are an expert software engineer specialized in writing clean, efficient, and maintainable code.

Your responsibilities:
- Implement features based on requirements
- Write idiomatic code following best practices
- Include necessary imports and dependencies
- Add clear comments for complex logic
- Consider edge cases and error handling
- Generate complete, runnable code

Code formatting rules:
- Use consistent indentation
- Follow language-specific conventions
- Write self-documenting code
- Keep functions focused and small
- Use meaningful variable names

Always provide:
1. Complete implementation (not pseudocode)
2. All necessary imports
3. Error handling where appropriate
4. Brief explanation of approach"""
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Generate code implementation"""
        try:
            # Search for relevant code examples
            related_code = await self._find_related_code(context)
            
            # Build prompt
            messages = [
                {"role": "system", "content": self.build_system_prompt()},
                {"role": "user", "content": self._build_prompt(context, related_code)}
            ]

            models_used: List[str] = []

            # Initial completion with tool support (chat model)
            raw_response = await self.get_completion(
                messages=messages,
                temperature=0.3,
                raw=True,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                override_model=settings.MODEL_TOOL_CALL
            )
            models_used.append(settings.MODEL_TOOL_CALL)

            assistant_message = self._normalize_message(raw_response.choices[0].message)
            content = assistant_message.get("content") or ""
            tool_calls = self._extract_tool_calls(assistant_message)
            requires_tool = bool(tool_calls)

            conversation_messages = copy.deepcopy(messages) + [assistant_message]

            if not requires_tool:
                # Follow-up with reasoner for higher-quality code when no tool branch
                reasoner_response = await self.get_completion(
                    messages=messages,
                    temperature=0.3,
                    raw=True,
                    override_model=settings.MODEL_IMPLEMENTATION
                )
                models_used.append(settings.MODEL_IMPLEMENTATION)

                assistant_message = self._normalize_message(reasoner_response.choices[0].message)
                content = assistant_message.get("content") or ""
                tool_calls = self._extract_tool_calls(assistant_message)
                requires_tool = bool(tool_calls)
                conversation_messages = copy.deepcopy(messages) + [assistant_message]

            # Parse response
            code_blocks = self._extract_code_blocks(content)
            actions = self._generate_actions(code_blocks)

            conversation_state = {
                "messages": conversation_messages,
                "agent": self.agent_type.value,
                "context": context.model_dump()
            }

            response = AgentResponse(
                success=True,
                content=content,
                metadata={
                    "code_blocks": len(code_blocks),
                    "related_examples": len(related_code),
                    "models_used": models_used
                },
                actions=actions,
                confidence=0.9 if code_blocks else 0.5,
                requires_tool=requires_tool,
                tool_calls=tool_calls,
                conversation_state=conversation_state
            )
            
            await self.log_interaction(context, response)
            return response
            
        except Exception as e:
            self.logger.error(f"Implementation failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"Failed to generate implementation: {str(e)}",
                confidence=0.0
            )

    def _normalize_message(self, message: Any) -> Dict[str, Any]:
        if hasattr(message, "model_dump"):
            return message.model_dump()
        if isinstance(message, dict):
            return message
        return {
            "role": getattr(message, "role", "assistant"),
            "content": getattr(message, "content", ""),
        }

    def _extract_tool_calls(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        tool_calls: List[Dict[str, Any]] = []
        if "tool_calls" in message and message["tool_calls"]:
            for call in message["tool_calls"]:
                if hasattr(call, "model_dump"):
                    call = call.model_dump()
                tool_calls.append(call)
        elif message.get("function_call"):
            tool_calls.append({
                "id": message["function_call"].get("name"),
                "type": "function",
                "function": message["function_call"]
            })
        return tool_calls

    async def continue_with_tool(
        self,
        conversation_state: Dict[str, Any],
        tool_results: List[Dict[str, Any]]
    ) -> AgentResponse:
        messages = copy.deepcopy(conversation_state.get("messages", []))
        if not messages:
            raise ValueError("Conversation state is missing messages")

        augmented_messages = copy.deepcopy(messages)
        for result in tool_results:
            augmented_messages.append({
                "role": "tool",
                "tool_call_id": result.get("call_id"),
                "name": result.get("name"),
                "content": result.get("output", "")
            })

        models_used: List[str] = []

        raw_response = await self.get_completion(
            messages=augmented_messages,
            temperature=0.3,
            raw=True,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            override_model=settings.MODEL_TOOL_CALL
        )
        models_used.append(settings.MODEL_TOOL_CALL)

        assistant_message = self._normalize_message(raw_response.choices[0].message)
        content = assistant_message.get("content") or ""
        tool_calls = self._extract_tool_calls(assistant_message)
        requires_tool = bool(tool_calls)

        conversation_messages = augmented_messages + [assistant_message]

        if not requires_tool:
            reasoner_response = await self.get_completion(
                messages=augmented_messages,
                temperature=0.3,
                raw=True,
                override_model=settings.MODEL_IMPLEMENTATION
            )
            models_used.append(settings.MODEL_IMPLEMENTATION)

            assistant_message = self._normalize_message(reasoner_response.choices[0].message)
            content = assistant_message.get("content") or ""
            tool_calls = self._extract_tool_calls(assistant_message)
            requires_tool = bool(tool_calls)
            conversation_messages = augmented_messages + [assistant_message]

        code_blocks = self._extract_code_blocks(content)
        actions = self._generate_actions(code_blocks)

        new_conversation_state = {
            "messages": conversation_messages,
            "agent": self.agent_type.value,
            "context": conversation_state.get("context")
        }

        response = AgentResponse(
            success=True,
            content=content,
            metadata={
                "code_blocks": len(code_blocks),
                "carried_tool_calls": len(tool_results),
                "models_used": models_used
            },
            actions=actions,
            confidence=0.9 if code_blocks else 0.5,
            requires_tool=requires_tool,
            tool_calls=tool_calls,
            conversation_state=new_conversation_state
        )

        return response
    
    async def _find_related_code(self, context: AgentContext) -> List[Dict]:
        """Find related code examples from vector store"""
        try:
            results = await search_code(
                query=context.user_query,
                workspace_id=context.workspace_path,
                limit=3
            )
            return results
        except Exception as e:
            self.logger.warning(f"Code search failed: {e}")
            return []
    
    def _build_prompt(self, context: AgentContext, related_code: List[Dict]) -> str:
        """Build implementation prompt"""
        parts = [self.format_context(context)]
        
        if related_code:
            parts.append("\n\nRelated code examples from your codebase:")
            for i, example in enumerate(related_code, 1):
                parts.append(
                    f"\nExample {i} ({example['file_path']}):\n"
                    f"```{example['language']}\n{example['content']}\n```"
                )
        
        parts.append("\n\nProvide a complete implementation:")
        
        return "\n".join(parts)
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown response"""
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                "language": language or "unknown",
                "code": code.strip()
            })
        
        return code_blocks
    
    def _generate_actions(self, code_blocks: List[Dict[str, str]]) -> List[Dict]:
        """Generate suggested actions from code blocks"""
        actions = []
        
        for i, block in enumerate(code_blocks):
            # Suggest creating new file or editing existing
            action_type = "create_file" if i == 0 else "edit_file"
            
            actions.append({
                "type": action_type,
                "language": block["language"],
                "code": block["code"],
                "description": f"Apply {block['language']} code"
            })
        
        return actions
