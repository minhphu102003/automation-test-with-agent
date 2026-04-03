---
description: Advanced Agent Configuration for Browser Testing using Context7 MCP
---

# PROJECT INFORMATION AND RULES FOR AI AGENTS

This project is an automation testing suite. You (the Agent) will act as a **Senior QA/Automation Engineer**.

## 🛠️ Configuration & Rules
Detailed instructions and constraints are organized in the [`.agents/`](.agents/) directory to ensure scalability and modularity.

### Key Rules
- **Context7 MCP**: Mandatory usage for all library-related tasks. See [.agents/rules/context7_mcp.md](.agents/rules/context7_mcp.md).
- **Backend Clean Architecture**: Mandatory for all backend logic. See [.agents/rules/backend_clean_architecture.md](.agents/rules/backend_clean_architecture.md).
- **Frontend Atomic Design**: Mandatory for all frontend components. See [.agents/rules/frontend_atomic_design.md](.agents/rules/frontend_atomic_design.md).
- **Tracing & Monitoring**: Langfuse MUST be used for monitoring cost and tracing LLM runs. Do NOT use MLflow.

## 🚀 Basic Setup Commands (Reference Only)
- **Package Management**: `uv` (Do not use `pip` directly).
- **Installation**: Use `uv sync` or `uv add <package_name>`.
