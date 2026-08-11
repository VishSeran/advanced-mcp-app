
from configurations.logger import get_logger
from client.mcp_client import MCPHTTPClient

logger = get_logger("http-app")

class MCPHTTPHostApp(MCPHTTPClient):
    
    def __init__(self, server_url, roots_dir):
        super().__init__(server_url, roots_dir)
        
        self.conversations = []
        