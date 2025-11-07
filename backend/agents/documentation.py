"""
Documentation Agent - Generates and maintains documentation
"""

from agents.base import BaseAgent, AgentContext, AgentResponse
from core.llm_router import AgentType


class DocumentationAgent(BaseAgent):
    """Agent specialized in documentation"""
    
    def __init__(self):
        super().__init__(AgentType.DOCUMENTATION)
    
    def build_system_prompt(self) -> str:
        return """You are an expert technical writer specialized in:

1. Code Documentation:
   - Clear docstrings (Google/NumPy style)
   - Inline comments for complex logic
   - README files
   - API documentation

2. Architecture Documentation:
   - System design documents
   - Architecture Decision Records (ADRs)
   - Component diagrams (Mermaid)

3. User Documentation:
   - Setup guides
   - Usage examples
   - Troubleshooting guides

Best Practices:
- Write for the intended audience
- Use clear, concise language
- Include code examples
- Keep documentation up-to-date
- Use proper formatting (Markdown)"""
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Generate documentation"""
        try:
            messages = [
                {"role": "system", "content": self.build_system_prompt()},
                {"role": "user", "content": self._build_doc_prompt(context)}
            ]
            
            doc_text = await self.get_completion(
                messages=messages,
                temperature=0.3  # Lower for consistent formatting
            )
            
            response = AgentResponse(
                success=True,
                content=doc_text,
                metadata={
                    "doc_type": self._infer_doc_type(context)
                },
                actions=[
                    {"type": "create_documentation", "content": doc_text}
                ],
                confidence=0.9
            )
            
            await self.log_interaction(context, response)
            return response
            
        except Exception as e:
            self.logger.error(f"Documentation failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"Documentation generation failed: {str(e)}",
                confidence=0.0
            )
    
    def _build_doc_prompt(self, context: AgentContext) -> str:
        parts = [f"Documentation Request: {context.user_query}"]
        
        if context.selected_code:
            parts.append(f"\nCode to document:\n```\n{context.selected_code}\n```")
        
        if context.current_file:
            parts.append(f"\nFile: {context.current_file}")
        
        parts.append("\nGenerate comprehensive documentation with:")
        parts.append("- Clear descriptions")
        parts.append("- Parameter/return value documentation")
        parts.append("- Usage examples")
        parts.append("- Proper formatting")
        
        return "\n".join(parts)
    
    def _infer_doc_type(self, context: AgentContext) -> str:
        query_lower = context.user_query.lower()
        
        if "readme" in query_lower:
            return "readme"
        elif "api" in query_lower:
            return "api"
        elif "docstring" in query_lower:
            return "docstring"
        else:
            return "general"
