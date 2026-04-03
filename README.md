# Browser-Testing with AI Agents
# Browser-Use Automation & Browser Testing Suite

**Version**: `1.0.0` | **License**: MIT | **Status**: Stable (Clean Architecture)

## 📋 System Requirements (Total)

- **CPU**: 3.0 Cores (Reserved: 1.5)
- **RAM**: 6.0 GB (Reserved: 3.0 GB)
- **Disk**: 2 GB free space
- **Software**: Docker Desktop / Engine with Compose v2+

This project is a professional automation testing suite built with `browser-use`. It is designed to evaluate the feasibility of AI-driven browser automation by tracking execution performance and LLM API costs using Langfuse.

## 🚀 Quick Start with Docker

The easiest way to run the entire suite is using Docker Compose.

1. **Build & Start**:
   ```bash
   docker compose up --build -d
   ```
2. **Access Services**:
   - **Main Dashboard**: [http://localhost:3000](http://localhost:3000)
   - **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Langfuse Tracing**: Cloud Dashboard

For detailed configuration and resource management, see the [Docker Deployment Guide](docs/docker_guide.md).

## 🏗️ Project Architecture

The project follows a modular, layered architecture:

- **`src/core/`**: Centralized logic for initializing the Browser, LLM wrappers, and the `browser-use` Agent.
- **`src/monitoring/`**: Integration with Langfuse to capture token usage, execution time, and computed costs.
- **`config/`**: Shared configuration, including model pricing data for cost calculation.
- **`tests/`**: Dedicated directory for individual automation test scenarios and scripts.
- **`.agents/`**: Modular rules and guidelines for AI agents working in this repository.

## 🚀 Getting Started

### 1. Prerequisites
- [uv](https://github.com/astral-sh/uv) installed.
- Playwright browsers installed: `uv run playwright install`.

### 2. Setup
Clone the repository and sync dependencies:
```powershell
uv sync
```

### 3. Configuration
Create a `.env` file based on `.env.example` and add your API keys:
```env
OPENAI_API_KEY=your_key_here
# Optional: GOOGLE_API_KEY=your_key_here
```

### 4. Running Tests
Run the centralized runner to execute automation scenarios:
```powershell
uv run python main.py
```

## 📊 Monitoring & Cost Tracking

### Viewing Results
To view detailed metrics, including token usage and estimated USD costs:
1. Log into your [Langfuse Cloud](https://langfuse.com) dashboard.
2. Select your project and navigate to **Traces** to view step-by-step executions or **Dashboard** to view aggregate costs.

## 📁 Data-Driven Testing (Google Sheets)

The suite can read tasks from a Google Sheet to perform large-scale automation tests.

### Detailed Guides:
1.  **[Google Sheets Setup Guide](docs/google_sheets_setup.md)**: Steps for API setup, credentials, and sharing.
2.  **[Test Case Template Guide](docs/test_case_template.md)**: How to structure your Google Sheet (13-field format) for the AI Agent.

### Activation:
- Open `main.py`.
- Uncomment: `await run_structured_tests("YourSheetName")`.

## 🛠️ Project Evolution
This structure is built for scalability. To add a new test scenario, create a new file in the `tests/` directory and register it in `main.py`.

## 🤖 AI Agent Setup (CRITICAL)

To get the most out of this project with an AI Agent (like Cursor, Claude Desktop, or Windsurf), you **MUST** configure the **Context7 MCP server**. This tool allows the AI to fetch real-time documentation for `playwright` and `browser-use`.

### Context7 MCP Configuration

Add the following configuration to your AI IDE or Desktop application (e.g., `mcp_config.json`):

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp@latest"
      ],
      "env": {
        "CONTEXT7_API_KEY": "YOUR_UPSTASH_CONTEXT7_TOKEN"
      }
    }
  }
}
```

- **Get an API Key**: Visit the [Upstash Console](https://console.upstash.com/context7) to create a free Context7 token.
- **Why this is needed**: Many libraries in this project update their APIs frequently. This MCP ensures the AI doesn't guess old syntax.

## 📁 Repository Structure

- `main.py`: The entry point for the browser agent.
- `.agents/`: Contains modular rules and instructions for AI agents.
- `.env`: Location for your secret API keys (Git ignored).

## 📄 License
This project is for demonstration purposes. Use it as a boilerplate for your own AI-powered testing!
