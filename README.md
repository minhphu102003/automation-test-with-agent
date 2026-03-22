# Browser-Testing with AI Agents

This repository is an automation testing suite powered by [browser-use](https://github.com/browser-use/browser-use) and AI Agents. It is designed to demonstrate how AI can interact with web pages to perform complex testing tasks.

## 🚀 Key Features

- **AI-Driven Automation**: Powered by `browser-use` for high-level browser interaction.
- **Smart Documentation Access**: Uses **Context7 MCP** to ensure the AI always has the latest documentation for rapidly evolving libraries.
- **Optimized for Antigravity**: Modular configuration in the [`.agents/`](.agents/) directory.

## 🛠️ Prerequisites

- [Python](https://www.python.org/) 3.11+
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package & project manager)

## 📦 Getting Started

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd browser-testing
   ```

2. **Sync dependencies**:
   ```bash
   uv sync
   ```

3. **Install Browser Binaries**:
   ```bash
   uv run playwright install chromium
   ```

4. **Configuration**:
   Copy `.env.example` or create a `.env` file with your API keys:
   ```env
   OPENAI_API_KEY=sk-...
   ```

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
