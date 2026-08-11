
from contextlib import AsyncExitStack

from mcp.client import streamable_http
from mcp import ClientSession

from configurations.logger import get_logger


logger = get_logger("mcp-client")

class MCPHTTPClient:
    
    def __init__(self, server_url:str, roots_dir:str):
        self.server_url = server_url
        self.roots_dir = roots_dir
        self.session = None
        self.agent = None
        self.exit_stack = AsyncExitStack()
        self.connect = None
        
    
    async def connect_to_server(self):
        
        """Connect to HTTP MCP server via Streamable HTTP. Safe to call multiple times."""
        
        try:
            
            if not self.session is None:
                logger.warning("Session is aleady running")
                return
            
            mcp_url = f"{self.server_url}/mcp"
            
            read, write,_sid = await self.exit_stack.enter_async_context(
                streamable_http(mcp_url)
            )
            
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            await self.session.initialize()
            logger.info("Client has connected to server...")
            self.connect = True
            
            
        except ValueError as e:
            logger.error(f"Value error: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Error in connection: {e}")
            raise