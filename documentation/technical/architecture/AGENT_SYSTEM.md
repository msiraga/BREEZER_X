# BREEZER Agent System Architecture

**Multi-agent AI system with specialized roles and intelligent orchestration**

---

## System Overview

```
User Request
     ↓
Orchestrator (Brain)
     ↓
┌────┴────┬────────┬──────────┬─────────┬──────────┬──────────┬──────────┬─────────┐
│         │        │          │         │          │          │          │         │
Implementation Review Debug Documentation Refactoring Security DevOps Architect QA
Agent      Agent   Agent      Agent       Agent      Agent    Agent   Agent   Agent
```

**Total Agents:** 9 (7 implemented + 2 planned)

---

## The Orchestrator (Brain)

**Role:** Central intelligence that routes tasks to specialized agents

**Location:** `backend/agents/orchestrator.py`

**LLM Used:** 🧠 **DeepSeek Reasoner** (`deepseek-reasoner`)
- Why: Advanced reasoning for task analysis
- Context: Analyzes user intent
- Decision: Routes to best agent(s)

**Responsibilities:**
1. 🎯 **Task Analysis**
   - Understands user request
   - Identifies task type
   - Determines complexity

2. 🔀 **Agent Selection**
   - Single agent: Simple tasks
   - Multiple agents: Complex tasks
   - Sequential: When order matters

3. 🔄 **Workflow Management**
   - Coordinates multiple agents
   - Manages agent dependencies
   - Aggregates results

4. 📊 **Context Management**
   - Maintains conversation history
   - Provides relevant context to agents
   - Synthesizes final response

**Example Decision Tree:**
```
User: "Fix this bug and add tests"
  ↓
Orchestrator analyzes:
  1. Bug fixing → Debug Agent
  2. Add tests → QA Agent
  ↓
Routes to: Debug Agent → QA Agent (sequential)
```

---

## Agent #1: Implementation Agent

**Role:** 💻 Writes new code from specifications

**LLM:** DeepSeek Chat (`deepseek/deepseek-chat`)

**When Used:**
- Creating new features
- Writing new functions/classes
- Scaffolding projects
- Implementing algorithms

**Specializations:**
- ✅ Clean, idiomatic code
- ✅ Follows best practices
- ✅ Proper error handling
- ✅ Type hints/annotations
- ✅ Comprehensive docstrings

**Example:**
```
User: "Create a REST API endpoint for user authentication"
↓
Implementation Agent:
- Designs endpoint structure
- Writes FastAPI route
- Adds request/response models
- Includes error handling
- Adds authentication logic
```

**Output Format:**
```python
# Fully functional code with:
- Imports
- Type hints
- Error handling
- Documentation
- Tests (if requested)
```

---

## Agent #2: Review Agent

**Role:** 👀 Code review and quality assessment

**LLM:** DeepSeek Chat (`deepseek/deepseek-chat`)

**When Used:**
- Pull request reviews
- Code quality checks
- Best practice validation
- Architecture review

**Checks:**
- 🔍 **Code Quality**
  - Readability
  - Maintainability
  - Complexity

- 🏗️ **Architecture**
  - Design patterns
  - SOLID principles
  - Separation of concerns

- 🐛 **Potential Issues**
  - Edge cases
  - Error handling
  - Performance concerns

- 📝 **Documentation**
  - Missing docstrings
  - Unclear comments
  - API documentation

**Example:**
```
User: "Review this function"
↓
Review Agent:
✅ Good: Clear variable names
⚠️  Concern: Missing error handling
❌ Issue: O(n²) complexity, use hash map
💡 Suggestion: Add type hints
```

**Output Format:**
```
Score: 7/10

Strengths:
- Clean code structure
- Good naming conventions

Issues:
1. Missing error handling (line 23)
2. Performance concern (line 45)
3. No input validation

Recommendations:
- Add try-except blocks
- Use dict for O(1) lookup
- Validate inputs
```

---

## Agent #3: Debug Agent

**Role:** 🐛 Diagnoses and fixes bugs

**LLM:** DeepSeek Reasoner (`deepseek/deepseek-reasoner`)
- Why: Requires deep reasoning for root cause analysis

**When Used:**
- Error messages
- Unexpected behavior
- Performance issues
- Logic errors

**Approach:**
1. 🔍 **Analyze Error**
   - Read stack trace
   - Identify error type
   - Locate problematic code

2. 🧪 **Hypothesis**
   - Generate possible causes
   - Rank by likelihood

3. 🔬 **Investigation**
   - Check assumptions
   - Test edge cases
   - Verify data flow

4. 🛠️ **Fix**
   - Provide solution
   - Explain root cause
   - Suggest prevention

**Example:**
```
User: "Getting KeyError: 'user_id'"
↓
Debug Agent:
1. Analyzes: Dictionary access without validation
2. Root cause: API response missing 'user_id' field
3. Fix: Add .get() with default value
4. Prevention: Validate API response schema
```

**Output Format:**
```
🐛 Root Cause:
Dictionary access without key existence check

🔧 Fix:
- user_id = data.get('user_id', None)
+ if user_id is None:
+     raise ValueError("user_id is required")

🛡️ Prevention:
- Add schema validation
- Use Pydantic models
- Add tests for missing fields
```

---

## Agent #4: Documentation Agent

**Role:** 📝 Generates and maintains documentation

**LLM:** DeepSeek Chat (`deepseek/deepseek-chat`)

**When Used:**
- Creating README files
- Writing API documentation
- Generating code comments
- Creating user guides

**Types Generated:**
1. **Code Documentation**
   - Function docstrings
   - Class documentation
   - Module descriptions

2. **API Documentation**
   - Endpoint descriptions
   - Request/response examples
   - Authentication details

3. **Architecture Documentation**
   - System diagrams
   - Component descriptions
   - Data flow

4. **User Documentation**
   - Installation guides
   - Usage examples
   - Tutorials

**Example:**
```
User: "Document this API endpoint"
↓
Documentation Agent:
Generates:
- Endpoint description
- Parameters table
- Request example
- Response example
- Error codes
- Usage notes
```

**Output Format:**
```markdown
## POST /api/users

Creates a new user account.

### Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| email | string | Yes | User email |
| password | string | Yes | User password (min 8 chars) |

### Request Example
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

### Response (201 Created)
...
```

---

## Agent #5: Refactoring Agent

**Role:** ♻️ Improves code quality without changing behavior

**LLM:** DeepSeek Chat (`deepseek/deepseek-chat`)

**When Used:**
- Code smells
- Technical debt
- Performance optimization
- Maintainability improvements

**Refactoring Types:**
1. **Structure**
   - Extract functions
   - Split classes
   - Organize modules

2. **Patterns**
   - Apply design patterns
   - Remove anti-patterns
   - Simplify logic

3. **Performance**
   - Optimize algorithms
   - Reduce complexity
   - Cache results

4. **Readability**
   - Rename variables
   - Simplify expressions
   - Remove duplication

**Example:**
```
User: "Refactor this spaghetti code"
↓
Refactoring Agent:
- Extracts nested logic to functions
- Applies strategy pattern
- Reduces cyclomatic complexity from 15 to 5
- Improves readability
```

**Output Format:**
```
Before: Complexity 15, 200 lines
After:  Complexity 5, 150 lines

Changes:
1. Extracted 3 helper functions
2. Applied Strategy pattern
3. Removed duplicate code (4 instances)
4. Renamed confusing variables

Benefits:
✅ 25% fewer lines
✅ 67% less complex
✅ Easier to test
✅ Better maintainability
```

---

## Agent #6: Security Agent

**Role:** 🔒 Identifies and fixes security vulnerabilities

**LLM:** DeepSeek Chat (`deepseek/deepseek-chat`)

**When Used:**
- Security audits
- Vulnerability scanning
- OWASP compliance
- Penetration testing prep

**Checks:**
1. **OWASP Top 10**
   - Injection attacks
   - Broken authentication
   - Sensitive data exposure
   - XML external entities
   - Broken access control
   - Security misconfiguration
   - XSS
   - Insecure deserialization
   - Known vulnerabilities
   - Insufficient logging

2. **Best Practices**
   - Input validation
   - Output encoding
   - Secure password storage
   - HTTPS usage
   - Token management

3. **Dependency Security**
   - Known CVEs
   - Outdated packages
   - Vulnerable versions

**Example:**
```
User: "Audit this authentication code"
↓
Security Agent:
🔴 Critical: SQL injection vulnerability (line 23)
🟡 Warning: Passwords not hashed (line 45)
🟡 Warning: No rate limiting
🟢 Good: HTTPS enforced
```

**Output Format:**
```
Security Audit Report

🔴 Critical Issues (2):
1. SQL Injection (line 23)
   Severity: 9.8/10
   Fix: Use parameterized queries
   
2. Hardcoded API key (line 67)
   Severity: 9.0/10
   Fix: Use environment variables

🟡 Warnings (3):
1. Weak password policy
2. No CSRF protection
3. Missing rate limiting

Recommendations:
- Add input sanitization
- Implement rate limiting (100 req/min)
- Use bcrypt for passwords
- Add security headers
```

---

## Agent #7: DevOps Agent

**Role:** 🚀 Generates CI/CD and infrastructure code

**LLM:** DeepSeek Chat (`deepseek/deepseek-chat`)

**When Used:**
- Creating CI/CD pipelines
- Infrastructure as Code
- Deployment automation
- Cloud configuration

**Generates:**
1. **CI/CD Pipelines**
   - GitHub Actions
   - GitLab CI
   - Jenkins
   - CircleCI

2. **Infrastructure**
   - Docker/Kubernetes
   - Terraform
   - CloudFormation
   - Ansible

3. **Cloud Config**
   - AWS
   - Azure
   - GCP
   - DigitalOcean

4. **Deployment**
   - Blue-green deployments
   - Canary releases
   - Rollback strategies

**Example:**
```
User: "Create GitHub Actions for Python app"
↓
DevOps Agent:
Generates:
- Workflow YAML
- Test job
- Build job
- Deploy job
- Environment secrets
```

**Output Format:**
```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    ...
```

---

## Agent #8: Architect Agent (Planned)

**Role:** 🏗️ System design and architecture

**LLM:** DeepSeek Reasoner (`deepseek/deepseek-reasoner`)
- Why: Requires high-level reasoning

**When Used:**
- New system design
- Microservices architecture
- Database schema design
- API design

**Responsibilities:**
- System architecture diagrams
- Technology stack recommendations
- Scalability planning
- Design pattern selection
- Trade-off analysis

**Example:**
```
User: "Design a scalable e-commerce system"
↓
Architect Agent:
- Microservices architecture
- Event-driven design
- Database: PostgreSQL + Redis
- Message queue: RabbitMQ
- API Gateway pattern
- CDN for static assets
```

---

## Agent #9: QA Agent (Planned)

**Role:** 🧪 Test generation and quality assurance

**LLM:** DeepSeek Chat (`deepseek/deepseek-chat`)

**When Used:**
- Generating unit tests
- Integration tests
- E2E tests
- Test coverage analysis

**Generates:**
- Unit tests (pytest, jest)
- Integration tests
- Mock objects
- Test fixtures
- Edge case tests
- Performance tests

**Example:**
```
User: "Generate tests for this function"
↓
QA Agent:
Creates:
- Happy path tests
- Edge case tests
- Error handling tests
- Performance tests
- Mock external dependencies
```

---

## How Orchestration Works

### 1. **Single Agent Task**

```
User: "Document this API"
     ↓
Orchestrator: Simple task, one agent
     ↓
Documentation Agent → Response
```

### 2. **Multi-Agent Task (Parallel)**

```
User: "Review code and check security"
     ↓
Orchestrator: Independent tasks
     ↓
┌─────────────┬──────────────┐
│             │              │
Review Agent  Security Agent
│             │              │
└──────┬──────┴──────┬───────┘
       │             │
       └──Aggregate──┘
            ↓
        Response
```

### 3. **Multi-Agent Task (Sequential)**

```
User: "Fix bug and add tests"
     ↓
Orchestrator: Dependent tasks
     ↓
Debug Agent (fixes bug)
     ↓
QA Agent (tests fixed code)
     ↓
Response
```

### 4. **Complex Task (Multi-Stage)**

```
User: "Build user authentication system"
     ↓
Orchestrator: Multi-stage workflow
     ↓
1. Architect Agent (design system)
     ↓
2. Implementation Agent (write code)
     ↓
3. Security Agent (audit)
     ↓
4. QA Agent (generate tests)
     ↓
5. Documentation Agent (docs)
     ↓
Response
```

---

## LLM Model Selection

### DeepSeek Chat (`deepseek/deepseek-chat`)
**Used by:** Implementation, Review, Documentation, Refactoring, Security, DevOps

**Why:**
- Fast response times
- Cost-effective
- Good for straightforward tasks
- Excellent code generation

### DeepSeek Reasoner (`deepseek/deepseek-reasoner`)
**Used by:** Orchestrator, Debug Agent, Architect Agent

**Why:**
- Advanced reasoning
- Better for complex decisions
- Root cause analysis
- System design thinking

### Local Mistral 7B (Llamafile)
**Used by:** Any agent when `USE_LOCAL_FOR_SENSITIVE=true`

**When:**
- Proprietary code
- Sensitive data
- Company secrets
- No internet connection

**Fallback:**
- All agents can use local LLM
- Automatic switching when needed
- Configurable per operation

---

## Agent Configuration

**File:** `backend/core/config.py`

```python
# Model routing
MODEL_IMPLEMENTATION = "deepseek/deepseek-chat"
MODEL_REVIEW = "deepseek/deepseek-chat"
MODEL_ARCHITECT = "deepseek/deepseek-reasoner"
MODEL_DEBUG = "deepseek/deepseek-reasoner"
MODEL_DOCUMENTATION = "deepseek/deepseek-chat"
MODEL_REFACTORING = "deepseek/deepseek-chat"
MODEL_SECURITY = "deepseek/deepseek-chat"
MODEL_DEVOPS = "deepseek/deepseek-chat"
MODEL_QA = "deepseek/deepseek-chat"

# Fallback
MODEL_FALLBACK = "llamafile/mistral-7b-instruct"
USE_LOCAL_FOR_SENSITIVE = True
```

---

## Agent Communication Flow

```
1. User Request (VSCode Extension)
        ↓
2. API Endpoint (/api/agent/query)
        ↓
3. Orchestrator receives request
        ↓
4. Orchestrator analyzes task
        ↓
5. Selects appropriate agent(s)
        ↓
6. Agent processes with LLM
        ↓
7. Agent returns result
        ↓
8. Orchestrator aggregates
        ↓
9. Response to user
```

---

## Privacy & Security

**Sensitive Code Protection:**
```
1. User marks code as sensitive
2. Orchestrator checks: USE_LOCAL_FOR_SENSITIVE
3. Routes to local Mistral (not cloud)
4. No data leaves your machine
```

**Data Flow:**
- **Cloud LLM**: Non-sensitive code, general tasks
- **Local LLM**: Sensitive code, proprietary logic
- **Configurable**: Per-operation basis

---

## Performance Characteristics

| Agent | Avg Response Time | Complexity |
|-------|------------------|------------|
| Implementation | 5-10 sec | Medium |
| Review | 3-7 sec | Low |
| Debug | 8-15 sec | High |
| Documentation | 4-8 sec | Low |
| Refactoring | 6-12 sec | Medium |
| Security | 5-10 sec | Medium |
| DevOps | 4-8 sec | Low |
| Orchestrator | 1-3 sec | High |

**With Local LLM (Mistral 7B):**
- Add 2-5 seconds per request
- Depends on GPU (RTX 4060: ~40 tokens/sec)

---

## Summary

**BREEZER has 9 specialized agents:**
1. **Orchestrator** - Routes tasks (DeepSeek Reasoner)
2. **Implementation** - Writes code (DeepSeek Chat)
3. **Review** - Reviews code (DeepSeek Chat)
4. **Debug** - Fixes bugs (DeepSeek Reasoner)
5. **Documentation** - Writes docs (DeepSeek Chat)
6. **Refactoring** - Improves code (DeepSeek Chat)
7. **Security** - Audits security (DeepSeek Chat)
8. **DevOps** - Creates CI/CD (DeepSeek Chat)
9. **Architect** - Designs systems (Planned)
10. **QA** - Generates tests (Planned)

**Key Features:**
- ✅ Intelligent orchestration
- ✅ Multi-model support (DeepSeek + Local)
- ✅ Privacy-first (local LLM option)
- ✅ GPU-accelerated
- ✅ Extensible architecture

**The Orchestrator (Brain) uses DeepSeek Reasoner to coordinate all agents based on task complexity and requirements.**

---

© 2025 RICHDALE AI - BREEZER Platform
