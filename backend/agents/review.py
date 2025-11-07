"""
Review Agent - Code review and suggestions
"""

from agents.base import BaseAgent, AgentContext, AgentResponse
from core.llm_router import AgentType


class ReviewAgent(BaseAgent):
    """Agent specialized in code review"""
    
    def __init__(self):
        super().__init__(AgentType.REVIEW)
    
    def build_system_prompt(self) -> str:
        return """You are an expert code reviewer focused on:

1. Code Quality:
   - Readability and maintainability
   - Proper naming conventions
   - Code organization and structure

2. Best Practices:
   - Design patterns
   - SOLID principles
   - DRY (Don't Repeat Yourself)

3. Potential Issues:
   - Bugs and logic errors
   - Performance problems
   - Security vulnerabilities
   - Edge cases not handled

4. Improvements:
   - Refactoring suggestions
   - Optimization opportunities
   - Missing error handling

Provide:
- Clear, actionable feedback
- Severity level (critical, warning, suggestion)
- Specific code examples
- Positive feedback on good practices"""
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Perform code review"""
        try:
            if not context.selected_code:
                return AgentResponse(
                    success=False,
                    content="No code selected for review",
                    confidence=0.0
                )
            
            messages = [
                {"role": "system", "content": self.build_system_prompt()},
                {"role": "user", "content": self._build_review_prompt(context)}
            ]
            
            review_text = await self.get_completion(
                messages=messages,
                temperature=0.4
            )
            
            issues = self._parse_issues(review_text)
            
            response = AgentResponse(
                success=True,
                content=review_text,
                metadata={
                    "issues_found": len(issues),
                    "code_length": len(context.selected_code)
                },
                actions=self._generate_fix_actions(issues),
                confidence=0.85
            )
            
            await self.log_interaction(context, response)
            return response
            
        except Exception as e:
            self.logger.error(f"Review failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"Review failed: {str(e)}",
                confidence=0.0
            )
    
    def _build_review_prompt(self, context: AgentContext) -> str:
        return f"""Review the following code:

File: {context.current_file or 'unknown'}

```
{context.selected_code}
```

User Query: {context.user_query}

Provide a structured review with:
1. Overall assessment
2. Issues found (if any)
3. Suggestions for improvement
4. Positive aspects"""
    
    def _parse_issues(self, review_text: str) -> list:
        """Extract issues from review"""
        # Simple parsing - can be enhanced
        issues = []
        for line in review_text.split('\n'):
            if any(keyword in line.lower() for keyword in ['bug', 'issue', 'problem', 'warning']):
                issues.append(line.strip())
        return issues
    
    def _generate_fix_actions(self, issues: list) -> list:
        """Generate actions to fix issues"""
        return [
            {
                "type": "apply_suggestion",
                "description": issue
            }
            for issue in issues[:5]  # Top 5 issues
        ]
