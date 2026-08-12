# Advanced MCP Applications with Streamable HTTP, Roots, and Sampling

An advanced [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) project demonstrating **HTTP transport** for remote connectivity, **filesystem roots** for security boundaries, and **sampling** for server-initiated LLM requests.

The project builds a base HTTP client with full MCP protocol support, then layers two applications on top of it: a **GUI client** for manual interaction and an **AI-powered host app** with full remote MCP capabilities and natural-language tool calling.

This design demonstrates production-ready patterns for remote MCP servers with enterprise-grade security.

## Learning Objectives

- Connect to remote MCP servers using HTTP transport
- Configure filesystem roots for secure file access boundaries
- Implement sampling approval workflows for server-initiated LLM requests
- Build applications that inherit from an HTTP-capable base client
- Understand when to use HTTP vs STDIO transport
- Handle security boundaries and user approval flows

## Prerequisites

- Experience building MCP clients with base/derived class architecture
- Basic Python programming knowledge
- Understanding of HTTP transport
- Familiarity with async/await patterns in Python
- Basic knowledge of object-oriented programming (inheritance)
- Awareness of filesystem security concepts

## Architecture

                     MCP Server
                         │
          ┌──────────────┼──────────────┐
          │              │              │
        Tools         Resources       Prompts
          │              │              │
          ▼              ▼              ▼
   load_mcp_tools()   read_resource()  get_prompt()
          │              │              │
          ▼              ▼              ▼
       Agent           Host            Host

```
mcp_http_server.py          # FastMCP server: tools, resources, prompts, roots enforcement
mcp_http_client_base.py     # Base client: connection, protocol methods (inherited by both apps)
mcp_http_client_app.py      # GUI client (Gradio) — inherits from MCPHTTPClient
mcp_http_host_app.py        # AI host app (OpenAI GPT-4o-mini) — inherits from MCPHTTPClient
workspace/                  # Roots-protected filesystem boundary
```

```
MCPHTTPClient (base)
   ├── connect(), list_tools(), call_tool()
   ├── list_resources(), read_resource()
   └── list_prompts(), get_prompt()
        │
        ├── MCPHTTPClientApp   → Gradio GUI for manual tool/resource/prompt testing
        └── MCPHTTPHostApp     → OpenAI-powered chat with automatic tool calling
```

## Key Concepts

### HTTP Transport
Unlike STDIO (a local subprocess), the server here runs independently over HTTP:
- Multiple clients can connect simultaneously
- Suitable for production, remote/cloud services, and microservice architectures
- Uses **Streamable HTTP**, the modern replacement for the deprecated SSE transport

### Filesystem Roots
A client capability that exposes allowed directories to the server:
1. Client declares which filesystem locations are accessible
2. Server checks all file operations against these roots
3. Prevents path traversal (e.g. `../../../etc/passwd`) and unauthorized access
4. Essential for enterprise deployments with sensitive data

```json
{
  "uri": "file:///home/user/mcp_advanced_lab/workspace",
  "name": "Workspace"
}
```

### Sampling (Server-Initiated LLM Requests)
MCP's `sampling/createMessage` mechanism lets a **server** request an LLM completion **from the client**:
1. Server sends a `sampling/createMessage` request with messages, max tokens, and optional model preferences
2. Client shows a human-in-the-loop approval dialog
3. If approved, client calls the LLM and returns the result to the server
4. Server uses the result to complete its task

Benefits: servers never need their own API keys, clients control cost/model selection, and privacy stays client-side. This project includes a simplified, educational demonstration of the concept (`analyze_code` tool) rather than a full bidirectional implementation, since that requires session-level access not exposed by FastMCP's high-level tool decorators.

## Getting Started

### 1. Set Up the Environment

```bash
python3.11 -m venv mcp_advanced_env
source mcp_advanced_env/bin/activate

pip install mcp==1.16.0 fastmcp==2.12.5 httpx==0.28.1 uvicorn==0.38.0 gradio openai
```

### 2. Create the Project Structure

```bash
mkdir mcp_advanced_lab
cd mcp_advanced_lab
mkdir workspace
```

### 3. Seed Some Test Files

```bash
echo "# Test File" > workspace/test.txt
echo "This is a test file in the workspace." >> workspace/test.txt
echo "# README" > workspace/README.md
echo "Welcome to the MCP workspace!" >> workspace/README.md
```

### 4. Start the HTTP MCP Server

```bash
source ../mcp_advanced_env/bin/activate
python mcp_http_server.py
```

You should see:

```
Starting HTTP MCP Server on http://127.0.0.1:8000
Workspace roots: /path/to/mcp_advanced_lab/workspace
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Leave this running — the server listens at `http://127.0.0.1:8000/mcp`.

### 5. Run the GUI Client (new terminal)

```bash
cd mcp_advanced_lab
source ../mcp_advanced_env/bin/activate
python mcp_http_client_app.py http://127.0.0.1:8000 workspace
```

Open `http://127.0.0.1:7861` to explore the **Tools**, **Resources**, and **Prompts** tabs.

### 6. Run the AI Host App (new terminal)

```bash
cd mcp_advanced_lab
source ../mcp_advanced_env/bin/activate
python mcp_http_host_app.py http://127.0.0.1:8000 workspace
```

Open `http://127.0.0.1:7862` for a chat interface powered by GPT-4o-mini that can call all MCP tools, resources, and prompts through natural language.

## What the Server Provides

**Tools**
- `read_file(filepath)` — read a file from the workspace, enforcing roots
- `write_file(filepath, content)` — write a file, enforcing roots
- `list_files(directory=".")` — list directory contents, enforcing roots
- `analyze_code(code, focus="quality")` — demonstrates the MCP sampling protocol conceptually

**Resources**
- `file://workspace/{filename}` — read-only access to workspace files as a resource template

**Prompts**
- `review_code(filename)` — general code review prompt template
- `analyze_security(filename)` — security-focused analysis prompt template

## Testing Roots Security

Try asking the AI host (or the GUI client) to read a file outside the workspace, e.g.:

```
Read the file /etc/passwd
```

Expected result: the server returns an access-denied error, and the roots boundary is respected — files outside `workspace/` are never accessible.

## Testing the AI Host App

Example prompts to try in the chat interface:

- `Create a file called hello.txt with the message: Hello from HTTP MCP!`
- `What resources are available? Then read one of them.`
- `Show me what prompts are available, then get the review_code prompt for test.`
- `Use analyze_code to analyze this code: def add(a, b): return a + b`

## Key Patterns

**HTTP Transport**
```python
# Server
mcp = FastMCP("HTTP Server")
mcp.run(transport="http", host="127.0.0.1", port=8000)

# Client
from mcp.client.streamable_http import streamablehttp_client
mcp_url = f"{server_url}/mcp"
read, write, _ = await streamablehttp_client(mcp_url)
session = ClientSession(read, write)
```

**Roots Security**
```python
def is_within_roots(filepath: str, roots_dir: str) -> bool:
    """Validate file access against roots directory."""
    abs_file = Path(filepath).resolve()
    abs_roots = Path(roots_dir).resolve()
    return abs_file.is_relative_to(abs_roots)
```

**Sampling Concept**
```python
# Server would send sampling request to client
# Client shows approval dialog to user
# If approved, client calls LLM and returns result
# Server uses LLM response to complete task
```

**Synthetic Tools (bridging MCP resources/prompts into OpenAI function calling)**
```python
get_available_tools():
    - Add real MCP tools
    - Add synthetic mcp_list_resources
    - Add synthetic mcp_read_resource
    - Add synthetic mcp_list_prompts
    - Add synthetic mcp_get_prompt
```

## What's Next

- Implement a full sampling approval workflow with real user dialogs
- Add authentication and HTTPS for production deployment
- Create new client apps (CLI, mobile) by inheriting from the base client
- Apply the HTTP transport and roots patterns to your own MCP servers

## License

The content of this project is licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
