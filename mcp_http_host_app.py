from langchain_mcp_adapters.tools import load_mcp_tools

from configurations.logger import get_logger
from client.mcp_client import MCPHTTPClient
from agents.llm_agent import LLMAgent

logger = get_logger("http-app")

class MCPHTTPHostApp(MCPHTTPClient):
    
    def __init__(self, server_url, roots_dir):
        super().__init__(server_url, roots_dir)
        
        self.conversations = []
        self.tools = []
        self.llm_client = None

    async def host_app_initialize(self):
        
        try:
            
            await self.connect_to_server()
            
            self.tools = await load_mcp_tools(self.session)
            
            logger.info(
                "Loaded %d MCP tools",
                len(self.tools)
            )
            
            self.llm_client = LLMAgent(tools=self.tools)
            logger.info("LLM agent initialized")
            
        except Exception:
            logger.exception("Failed to initialize MCP host application")
            await self.close_connection()
            raise
        
    async def get_llm_response(self, query):
        
        try:
        
            response = await self.llm_client.get_agent_response(query)
            logger.info("Response is fetched")
            return response
        
        except Exception as e:
            logger.error(f"Error in get_llm_response: {e}")
            raise
        
    async def conversation(self):
        
        
        print("\nEntering conversation mode. Type 'quit' or 'q' to exit.")
        
        while(True):
            
            query = input("Enter your question here: \n").strip()
            
            if query is None:
                print("\nPlease enter a query")
                continue
            
            if query.lower() in ("quit", "q"):
                print("Exit conversation...")
                break
                
        try:      
            
            response = await self.get_llm_response(query)
            print("\n" + response)  
                
            
        except Exception as e:
            logger.error(f"Error in conversation:{e}")
            raise
        
    async def prompt(self, prompt_name:str):
        
        try:
            
            prompt_list = self.list_prompts()
            
            prompt_obj = next(
                (prompt for prompt in prompt_list if prompt.name == prompt_name), None
            )
            
            if prompt_obj is None:
                logger.info(f"No matching prompt name: {prompt_name}")
            
        except Exception as e:
            logger.error(f"Error in prompt: {e}")
            raise
        
        