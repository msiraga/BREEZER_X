"""
Implementation Agent - Generates and edits code
"""

from typing import List, Dict
import re

from agents.base import BaseAgent, AgentContext, AgentResponse
from core.llm_router import AgentType
from services.vector_store import search_code


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
            
            # Get completion
            response_text = await self.get_completion(
                messages=messages,
                temperature=0.3  # Lower temperature for more consistent code
            )
            
            # Parse response
            code_blocks = self._extract_code_blocks(response_text)
            actions = self._generate_actions(code_blocks)
            
            response = AgentResponse(
                success=True,
                content=response_text,
                metadata={
                    "code_blocks": len(code_blocks),
                    "related_examples": len(related_code)
                },
                actions=actions,
                confidence=0.9 if code_blocks else 0.5
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
