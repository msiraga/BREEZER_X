"""
Docker sandbox service for safe code execution
"""

import docker
from docker.models.containers import Container
from typing import Dict, Any, Optional, List
import asyncio
import uuid
import logging
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)

# Docker client
docker_client = docker.from_env()


class SandboxExecutionError(Exception):
    """Sandbox execution error"""
    pass


class Sandbox:
    """Docker-based code execution sandbox"""
    
    def __init__(
        self,
        language: str = "python",
        timeout: int = None,
        memory_limit: str = None,
        cpu_limit: int = None
    ):
        self.language = language
        self.timeout = timeout or settings.SANDBOX_TIMEOUT
        self.memory_limit = memory_limit or settings.SANDBOX_MEMORY_LIMIT
        self.cpu_limit = cpu_limit or settings.SANDBOX_CPU_LIMIT
        self.container: Optional[Container] = None
        self.container_id = f"breezer-sandbox-{uuid.uuid4().hex[:8]}"
        
    async def start(self):
        """Start sandbox container"""
        if not settings.SANDBOX_ENABLED:
            raise SandboxExecutionError("Sandbox is disabled")
        
        try:
            # Select base image based on language
            images = {
                "python": "python:3.11-slim",
                "javascript": "node:18-slim",
                "typescript": "node:18-slim",
                "go": "golang:1.21-alpine",
                "rust": "rust:1.75-slim",
            }
            
            image = images.get(self.language, "python:3.11-slim")
            
            # Pull image if not exists
            try:
                docker_client.images.get(image)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling image: {image}")
                docker_client.images.pull(image)
            
            # Create container
            self.container = docker_client.containers.create(
                image=image,
                name=self.container_id,
                detach=True,
                stdin_open=True,
                tty=True,
                mem_limit=self.memory_limit,
                cpu_quota=self.cpu_limit * 100000,  # Convert to microseconds
                network_mode="none",  # Isolated network
                read_only=False,
                working_dir="/workspace",
                volumes={
                    # Mount a tmpfs for workspace
                },
                environment={
                    "PYTHONUNBUFFERED": "1",
                    "NODE_ENV": "development"
                }
            )
            
            self.container.start()
            logger.info(f"✅ Sandbox started: {self.container_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start sandbox: {e}")
            raise SandboxExecutionError(f"Failed to start sandbox: {e}")
    
    async def execute(
        self,
        code: str,
        stdin: Optional[str] = None,
        files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute code in sandbox
        
        Args:
            code: Code to execute
            stdin: Standard input
            files: Additional files to create {filename: content}
            
        Returns:
            Execution result with stdout, stderr, exit_code
        """
        if not self.container:
            raise SandboxExecutionError("Sandbox not started")
        
        try:
            start_time = datetime.now()
            
            # Create files if provided
            if files:
                for filename, content in files.items():
                    self.container.exec_run(
                        f"sh -c 'cat > /workspace/{filename}'",
                        stdin=True,
                        socket=True
                    )
            
            # Write main code file
            if self.language == "python":
                code_file = "main.py"
                cmd = f"python /workspace/{code_file}"
            elif self.language in ["javascript", "typescript"]:
                code_file = "main.js"
                cmd = f"node /workspace/{code_file}"
            elif self.language == "go":
                code_file = "main.go"
                cmd = f"go run /workspace/{code_file}"
            elif self.language == "rust":
                code_file = "main.rs"
                cmd = f"rustc /workspace/{code_file} && ./main"
            else:
                raise SandboxExecutionError(f"Unsupported language: {self.language}")
            
            # Write code to file
            self.container.exec_run(
                f"sh -c 'cat > /workspace/{code_file}'",
                stdin=True,
                socket=True
            ).output.write(code.encode())
            
            # Execute with timeout
            exec_result = self.container.exec_run(
                cmd,
                stdin=stdin is not None,
                demux=True,
                workdir="/workspace"
            )
            
            stdout, stderr = exec_result.output
            stdout = stdout.decode() if stdout else ""
            stderr = stderr.decode() if stderr else ""
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exec_result.exit_code,
                "execution_time": execution_time,
                "success": exec_result.exit_code == 0
            }
            
        except Exception as e:
            logger.error(f"❌ Sandbox execution failed: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "execution_time": 0,
                "success": False,
                "error": str(e)
            }
    
    async def cleanup(self):
        """Stop and remove container"""
        if self.container:
            try:
                self.container.stop(timeout=5)
                self.container.remove(force=True)
                logger.info(f"🧹 Sandbox cleaned up: {self.container_id}")
            except Exception as e:
                logger.error(f"❌ Cleanup failed: {e}")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.cleanup()


async def execute_code(
    code: str,
    language: str = "python",
    timeout: int = None,
    stdin: Optional[str] = None,
    files: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to execute code in sandbox
    
    Args:
        code: Code to execute
        language: Programming language
        timeout: Execution timeout
        stdin: Standard input
        files: Additional files
        
    Returns:
        Execution result
    """
    async with Sandbox(language=language, timeout=timeout) as sandbox:
        result = await sandbox.execute(code, stdin=stdin, files=files)
    
    return result


async def cleanup_old_sandboxes():
    """Clean up any dangling sandbox containers"""
    try:
        containers = docker_client.containers.list(
            filters={"name": "breezer-sandbox-"}
        )
        
        for container in containers:
            try:
                container.stop(timeout=5)
                container.remove(force=True)
                logger.info(f"🧹 Cleaned up old sandbox: {container.name}")
            except Exception as e:
                logger.error(f"Failed to cleanup {container.name}: {e}")
                
    except Exception as e:
        logger.error(f"❌ Cleanup scan failed: {e}")
