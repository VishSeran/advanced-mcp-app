
from contextlib import AsyncExitStack
import json

from fastmcp import Context
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession, GetPromptResult, ListPromptsResult, ListResourcesResult, ListToolsResult, ReadResourceResult
from mcp.types import CreateMessageRequestParams, RequestParams, CreateMessageResult, TextContent

from mcp.client.streamable_http import RequestContext
from agents.llm_agent import LLMAgent
from configurations.logger import get_logger
from configurations.configs import MODEL_NAME


logger = get_logger("mcp-client")

class MCPHTTPClient:
    
    def __init__(self, server_url:str, roots_dir:str, agent:LLMAgent=None):
        self.server_url = server_url
        self.roots_dir = roots_dir
        self.session = None
        self.agent = agent
        self.exit_stack = AsyncExitStack()
        self.connect = False
        
    
    async def connect_to_server(self):
        
        """Connect to HTTP MCP server via Streamable HTTP. Safe to call multiple times."""
        
        try:
            
            if not self.session is None:
                logger.warning("Session is aleady running")
                return
            
            mcp_url = f"{self.server_url}/mcp"
            
            read, write,_sid = await self.exit_stack.enter_async_context(
                streamable_http_client(mcp_url)
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
            logger.error(
                "Error connecting to MCP server: %s",
                e
            )

            await self.exit_stack.aclose()
            self.exit_stack = AsyncExitStack()
            self.session = None
            self.connected = False

            raise
        
    async def list_tools(self):
        
        try:
            
            result:ListToolsResult = await self.session.list_tools()
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
            
            result:ListResourcesResult = await self.session.list_resources()
            logger.info(f"resources are listed: {result}")
            
            return result.resources
                    
        except Exception as e:
            logger.error(f"Error in list resources: {e}")
            raise
        
    async def read_resouce_from_server(self, uri:str):
        
        try:
            if uri is None:
                raise ValueError("URI is missing")
            
            result:ReadResourceResult = await self.session.read_resource(uri)
            logger.info("Resource is fethed")
            return result
            
        except ValueError as e:
            logger.error(f"Value Error in read resource: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in read resource: {e}")
            raise
        
        
    async def list_prompts(self):
        
        try:
                    
            result:ListPromptsResult = await self.session.list_prompts()
            logger.info(f"prompts are listed: {result}")
            
            return result
                    
        except Exception as e:
            logger.error(f"Error in list prompts: {e}")
            raise
        
        
    async def get_prompt(self, name:str, arguments:dict):
    
        try:
            
            if name is None:
                raise ValueError("Prompt name is missing")
            
            if arguments is None:
                raise ValueError("Prompts arguments are missing")
                    
            result:GetPromptResult = await self.session.get_prompt(name, arguments)
            logger.info(f"{name} is fetched")
            
            return result
        
        
        except ValueError as e:
            logger.error(f"Value Error in get prompt: {e}")
            raise
                    
        except Exception as e:
            logger.error(f"Error in get prompt: {e}")
            raise
        
        
    async def sampling_handler(self, 
                               content: RequestContext, 
                               param: CreateMessageRequestParams, ctx:Context) -> CreateMessageResult:
        
        
        try:
            
            if self.agent is None:
                raise RuntimeError("Agent is not running")
            
            if not (content or param):
                raise ValueError("parameters are missing")
            
            messages = []

            for message in param.messages:
                
                if isinstance(message.content, TextContent):
                    
                    messages.append(
                        {
                            "role": message.role,
                            "content": message.content.text
                        }
                    )
                    
            response = await self.agent.get_agent_response(messages)
            
            return CreateMessageResult(
                role="assistant",
                content= TextContent(
                    type="text",
                    text=response
                ),
                model=MODEL_NAME,
                stopReason="endTurn"
            )
            
            
            
        except ValueError as e:
            logger.error(f"Value Error in sampling_handler: {e}")
            raise
                            
        except Exception as e:
            logger.error(f"Error in sampling_handler: {e}")
            raise
        
        
    async def close_connection(self):
        
        try:
            await self.exit_stack.aclose()
            
        finally:
            self.exit_stack = AsyncExitStack()
            self.session = None
            self.agent = None
            self.connect = False

            logger.info("MCP connection closed")
                
                