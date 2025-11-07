"""
Refactoring Agent - Code improvement and restructuring
"""

from agents.base import BaseAgent, AgentContext, AgentResponse
from core.llm_router import AgentType


class RefactoringAgent(BaseAgent):
    """Agent specialized in code refactoring"""
    
    def __init__(self):
        super().__init__(AgentType.REFACTORING)
    
    def build_system_prompt(self) -> str:
        return """You are an expert code refactoring specialist focused on:

1. Code Quality Improvements:
   - Extract methods/functions
   - Reduce complexity
   - Eliminate duplication (DRY)
   - Improve naming

2. Design Patterns:
   - Apply appropriate patterns
   - SOLID principles
   - Clean architecture

3. Performance:
   - Optimize algorithms
   - Reduce memory usage
   - Improve efficiency

4. Maintainability:
   - Simplify logic
   - Improve readability
   - Better structure

Refactoring Principles:
- Preserve behavior (no functional changes)
- Make incremental changes
- Maintain or improve tests
- Document significant changes"""
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Refactor code"""
        try:
            if not context.selected_code:
                return AgentResponse(
                    success=False,
                    content="No code selected for refactoring",
                    confidence=0.0
                )
            
            messages = [
                {"role": "system", "content": self.build_system_prompt()},
                {"role": "user", "content": self._build_refactor_prompt(context)}
            ]
            
            refactored_code = await self.get_completion(
                messages=messages,
                temperature=0.2  # Low temperature for consistent refactoring
            )
            
            response = AgentResponse(
                success=True,
                content=refactored_code,
                metadata={
                    "original_length": len(context.selected_code),
                    "refactored_length": len(refactored_code)
                },
                actions=[
                    {"type": "apply_refactoring", "code": refactored_code}
                ],
                confidence=0.85
            )
            
            await self.log_interaction(context, response)
            return response
            
        except Exception as e:
            self.logger.error(f"Refactoring failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"Refactoring failed: {str(e)}",
                confidence=0.0
            )
    
    def _build_refactor_prompt(self, context: AgentContext) -> str:
        return f"""Refactor the following code:

File: {context.current_file or 'unknown'}

Original Code:
```
{context.selected_code}
```

User Request: {context.user_query}

Provide:
1. Refactored code
2. Explanation of changes
3. Benefits of refactoring
4. Any trade-offs

Focus on:
- Readability
- Maintainability  
- Performance (if applicable)
- Best practices"""
