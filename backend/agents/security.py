"""
Security Agent - Security auditing and vulnerability detection
"""

from agents.base import BaseAgent, AgentContext, AgentResponse
from core.llm_router import AgentType


class SecurityAgent(BaseAgent):
    """Agent specialized in security analysis"""
    
    def __init__(self):
        super().__init__(AgentType.SECURITY)
    
    def build_system_prompt(self) -> str:
        return """You are an expert security auditor specialized in:

1. Vulnerability Detection:
   - SQL injection
   - XSS (Cross-Site Scripting)
   - CSRF
   - Authentication/Authorization flaws
   - Insecure dependencies

2. Security Best Practices:
   - Input validation
   - Output encoding
   - Secure authentication
   - Encryption and hashing
   - Secrets management

3. OWASP Top 10:
   - Broken access control
   - Cryptographic failures
   - Injection vulnerabilities
   - Insecure design
   - Security misconfiguration

4. Compliance:
   - Data protection (GDPR, CCPA)
   - Secure coding standards
   - Security headers

Always:
- Identify specific vulnerabilities
- Provide severity ratings
- Suggest concrete fixes
- Explain security implications"""
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Perform security audit"""
        try:
            if not context.selected_code:
                return AgentResponse(
                    success=False,
                    content="No code selected for security audit",
                    confidence=0.0
                )
            
            messages = [
                {"role": "system", "content": self.build_system_prompt()},
                {"role": "user", "content": self._build_security_prompt(context)}
            ]
            
            audit_result = await self.get_completion(
                messages=messages,
                temperature=0.2  # Low temperature for consistent analysis
            )
            
            vulnerabilities = self._parse_vulnerabilities(audit_result)
            
            response = AgentResponse(
                success=True,
                content=audit_result,
                metadata={
                    "vulnerabilities_found": len(vulnerabilities),
                    "severity": self._get_max_severity(vulnerabilities)
                },
                actions=self._generate_security_actions(vulnerabilities),
                confidence=0.9
            )
            
            await self.log_interaction(context, response)
            return response
            
        except Exception as e:
            self.logger.error(f"Security audit failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"Security audit failed: {str(e)}",
                confidence=0.0
            )
    
    def _build_security_prompt(self, context: AgentContext) -> str:
        return f"""Perform a security audit on the following code:

File: {context.current_file or 'unknown'}

Code:
```
{context.selected_code}
```

User Request: {context.user_query}

Analyze for:
1. Common vulnerabilities (OWASP Top 10)
2. Insecure patterns
3. Data exposure risks
4. Authentication/authorization issues
5. Injection vulnerabilities

Provide:
- List of vulnerabilities (with severity: CRITICAL, HIGH, MEDIUM, LOW)
- Explanation of each issue
- Recommended fixes
- Prevention strategies"""
    
    def _parse_vulnerabilities(self, audit_text: str) -> list:
        """Extract vulnerabilities from audit"""
        vulnerabilities = []
        for line in audit_text.split('\n'):
            if any(keyword in line.upper() for keyword in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'VULNERABILITY']):
                vulnerabilities.append(line.strip())
        return vulnerabilities
    
    def _get_max_severity(self, vulnerabilities: list) -> str:
        """Get maximum severity level"""
        if not vulnerabilities:
            return "NONE"
        
        for vuln in vulnerabilities:
            if "CRITICAL" in vuln.upper():
                return "CRITICAL"
        for vuln in vulnerabilities:
            if "HIGH" in vuln.upper():
                return "HIGH"
        for vuln in vulnerabilities:
            if "MEDIUM" in vuln.upper():
                return "MEDIUM"
        
        return "LOW"
    
    def _generate_security_actions(self, vulnerabilities: list) -> list:
        """Generate actions to fix vulnerabilities"""
        return [
            {
                "type": "fix_vulnerability",
                "description": vuln,
                "priority": "high" if any(sev in vuln.upper() for sev in ['CRITICAL', 'HIGH']) else "medium"
            }
            for vuln in vulnerabilities[:10]  # Top 10 issues
        ]
