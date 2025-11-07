"""
Debug Agent - Troubleshooting and error analysis
"""

from agents.base import BaseAgent, AgentContext, AgentResponse
from core.llm_router import AgentType
from services.sandbox import execute_code


class DebugAgent(BaseAgent):
    """Agent specialized in debugging"""
    
    def __init__(self):
        super().__init__(AgentType.DEBUG)
    
    def build_system_prompt(self) -> str:
        return """You are an expert debugger specialized in:

1. Error Analysis:
   - Parse stack traces
   - Identify root causes
   - Explain error messages

2. Debugging Strategies:
   - Add logging statements
   - Test hypotheses
   - Isolate problems

3. Solutions:
   - Provide fixes
   - Suggest preventive measures
   - Explain why errors occur

Always:
- Analyze the full error context
- Suggest multiple solutions if applicable
- Explain the debugging process
- Recommend testing approaches"""
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Debug code and provide solutions"""
        try:
            # Check if we can run the code in sandbox
            can_execute = self._can_sandbox_execute(context)
            
            messages = [
                {"role": "system", "content": self.build_system_prompt()},
                {"role": "user", "content": self._build_debug_prompt(context)}
            ]
            
            # If we have runnable code, try executing it
            execution_result = None
            if can_execute and context.selected_code:
                execution_result = await self._safe_execute(context)
                if execution_result:
                    messages.append({
                        "role": "assistant",
                        "content": f"Execution result:\n{execution_result}"
                    })
            
            debug_analysis = await self.get_completion(
                messages=messages,
                temperature=0.3
            )
            
            response = AgentResponse(
                success=True,
                content=debug_analysis,
                metadata={
                    "execution_attempted": can_execute,
                    "execution_result": execution_result
                },
                actions=self._generate_debug_actions(debug_analysis),
                confidence=0.8
            )
            
            await self.log_interaction(context, response)
            return response
            
        except Exception as e:
            self.logger.error(f"Debug failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"Debug analysis failed: {str(e)}",
                confidence=0.0
            )
    
    def _build_debug_prompt(self, context: AgentContext) -> str:
        parts = [f"Debug Request: {context.user_query}"]
        
        if context.selected_code:
            parts.append(f"\nCode to debug:\n```\n{context.selected_code}\n```")
        
        if context.additional_context.get('error_message'):
            parts.append(f"\nError Message:\n{context.additional_context['error_message']}")
        
        if context.additional_context.get('stack_trace'):
            parts.append(f"\nStack Trace:\n{context.additional_context['stack_trace']}")
        
        parts.append("\nProvide:")
        parts.append("1. Root cause analysis")
        parts.append("2. Step-by-step debugging approach")
        parts.append("3. Recommended fixes")
        parts.append("4. Prevention strategies")
        
        return "\n".join(parts)
    
    def _can_sandbox_execute(self, context: AgentContext) -> bool:
        """Check if code can be executed in sandbox"""
        # Simple heuristic - can be enhanced
        if not context.selected_code:
            return False
        
        # Check for main execution patterns
        if any(pattern in context.selected_code for pattern in [
            'if __name__',
            'function main(',
            'def main(',
        ]):
            return True
        
        return False
    
    async def _safe_execute(self, context: AgentContext) -> str:
        """Safely execute code in sandbox"""
        try:
            result = await execute_code(
                code=context.selected_code,
                language="python",  # Default - detect from context
                timeout=30
            )
            
            output = []
            if result.get('stdout'):
                output.append(f"STDOUT:\n{result['stdout']}")
            if result.get('stderr'):
                output.append(f"STDERR:\n{result['stderr']}")
            output.append(f"Exit Code: {result.get('exit_code', 'unknown')}")
            
            return "\n\n".join(output)
            
        except Exception as e:
            return f"Execution failed: {str(e)}"
    
    def _generate_debug_actions(self, analysis: str) -> list:
        """Generate debugging actions"""
        return [
            {"type": "add_logging", "description": "Add debug logging"},
            {"type": "add_breakpoint", "description": "Set breakpoint"},
            {"type": "run_tests", "description": "Run related tests"}
        ]
