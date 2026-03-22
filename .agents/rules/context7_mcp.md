# MANDATORY USE OF CONTEXT7 MCP

## ⚠️ SUPREME RULE
This project utilizes libraries that are frequently updated (e.g., `browser-use`, `playwright`). You ARE NOT PERMITTED to write code, design task plans, or infer syntax based on your internal training data.

## Process
Whenever the user requests work with a library, framework, or API, you MUST strictly follow this process BEFORE generating any code:

1.  **Resolve ID**: Call the `resolve-library-id` tool with the library name to obtain the official Context7-compatible ID.
2.  **Fetch Documentation**: Use the obtained ID to call the `query-docs` tool. You must read the latest documentation and code snippets returned.
3.  **Execute**: Write scripts or respond based **EXACTLY** on the fetched documentation. Do not mix it with legacy syntax from your memory.
4.  **Limit**: If the library documentation cannot be found after 3 calls, **STOP** and request a direct documentation link from the user. Do not guess.
