"""
DevOps Agent - Infrastructure, CI/CD, and deployment
"""

from agents.base import BaseAgent, AgentContext, AgentResponse
from core.llm_router import AgentType


class DevOpsAgent(BaseAgent):
    """Agent specialized in DevOps and infrastructure"""
    
    def __init__(self):
        super().__init__(AgentType.DEVOPS)
    
    def build_system_prompt(self) -> str:
        return """You are an expert DevOps engineer specialized in:

1. CI/CD Pipelines:
   - GitHub Actions
   - GitLab CI
   - Jenkins
   - Automated testing and deployment

2. Infrastructure as Code:
   - Docker/Docker Compose
   - Kubernetes
   - Terraform
   - Ansible

3. Cloud Platforms:
   - AWS
   - Azure
   - Google Cloud
   - DigitalOcean

4. Monitoring & Logging:
   - Prometheus/Grafana
   - ELK Stack
   - Application monitoring
   - Error tracking

5. Best Practices:
   - Immutable infrastructure
   - Blue-green deployments
   - Rollback strategies
   - Security hardening

Always provide:
- Working configuration files
- Best practices explanations
- Security considerations
- Scalability considerations"""
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Generate DevOps configurations"""
        try:
            messages = [
                {"role": "system", "content": self.build_system_prompt()},
                {"role": "user", "content": self._build_devops_prompt(context)}
            ]
            
            devops_config = await self.get_completion(
                messages=messages,
                temperature=0.3
            )
            
            config_type = self._infer_config_type(context)
            
            response = AgentResponse(
                success=True,
                content=devops_config,
                metadata={
                    "config_type": config_type,
                },
                actions=[
                    {"type": "create_config", "config_type": config_type}
                ],
                confidence=0.85
            )
            
            await self.log_interaction(context, response)
            return response
            
        except Exception as e:
            self.logger.error(f"DevOps agent failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"DevOps configuration failed: {str(e)}",
                confidence=0.0
            )
    
    def _build_devops_prompt(self, context: AgentContext) -> str:
        parts = [f"DevOps Request: {context.user_query}"]
        
        if context.workspace_path:
            parts.append(f"\nProject: {context.workspace_path}")
        
        if context.selected_code:
            parts.append(f"\nExisting configuration:\n```\n{context.selected_code}\n```")
        
        parts.append("\nProvide:")
        parts.append("- Complete configuration files")
        parts.append("- Setup instructions")
        parts.append("- Best practices")
        parts.append("- Security considerations")
        
        return "\n".join(parts)
    
    def _infer_config_type(self, context: AgentContext) -> str:
        """Infer type of DevOps configuration"""
        query_lower = context.user_query.lower()
        
        if "docker" in query_lower:
            return "docker"
        elif "kubernetes" in query_lower or "k8s" in query_lower:
            return "kubernetes"
        elif "ci" in query_lower or "pipeline" in query_lower:
            return "ci_cd"
        elif "terraform" in query_lower:
            return "terraform"
        elif "monitoring" in query_lower:
            return "monitoring"
        else:
            return "infrastructure"
