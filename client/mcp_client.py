
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
        
    async def list_tools(self):
        
        try:
            
            result = await self.session.list_tools()
            logger.info(f"Tools listing completed: {result}")
            return result.tools
            
        except Exception as e:
            logger.error(f"Error in list tools: {e}")
            raise
        
        
    async def call_tool(self, tool_name:str, arguments:dict):
        
        try:
            
            if tool_name is None:
                raise ValueError("Tool name is missing")
            
            if arguments is None:
                raise ValueError("arguments are missing")
            
            result = await self.session.call_tool(tool_name, arguments)
            logger.info(f"{tool_name} call successfull")
            
            return result
        
        except ValueError as e:
            logger.error(f"Value Error in call tool: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Error in call tool: {e}")
            raise
        
    
    async def list_resources(self):
        
        try:
            
            result = await self.session.list_resources()
            logger.info(f"resources are listed: {result}")
            
            return result.resources
                    
        except Exception as e:
            logger.error(f"Error in list resources: {e}")
            raise
        
    async def read_resouce(self, uri:str):
        
        try:
            if uri is None:
                raise ValueError("URI is missing")
            
            result = await self.session.read_resource(uri)
            logger.info(f"Resource is fethed: {result}")
            return result
            
        except ValueError as e:
            logger.error(f"Value Error in read resource: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in read resource: {e}")
            raise