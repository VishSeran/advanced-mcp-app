from langchain_mcp_adapters.tools import load_mcp_tools

from configurations.logger import get_logger
from client.mcp_client import MCPHTTPClient
from agents.llm_agent import LLMAgent

logger = get_logger("http-app")

class MCPHTTPHostApp(MCPHTTPClient):
    
    async def __init__(self, server_url, roots_dir):
        super().__init__(server_url, roots_dir)
        
        self.conversations = []
        self.tools = []
        self.llm_client = None
