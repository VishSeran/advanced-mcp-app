from urllib.parse import quote
import json
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ListPromptsResult

from configurations.logger import get_logger
from client.mcp_client import MCPHTTPClient
from agents.llm_agent import LLMAgent

logger = get_logger("http-app")

class MCPHTTPHostApp:
    
    def __init__(self, server_url, roots_dir):
        self.mcp_client = MCPHTTPClient(server_url, roots_dir)
        
        self.conversations = []
        self.tools = []
        self.agent = None

    async def host_app_initialize(self):
        
        try:
            
            await self.mcp_client.connect_to_server()
            
            self.tools = await load_mcp_tools(self.mcp_client.session)
            
            logger.info(
                "Loaded %d MCP tools",
                len(self.tools)
            )
            
            self.agent = LLMAgent(tools=self.tools)
            logger.info("LLM agent initialized")
            
        except Exception:
            logger.exception("Failed to initialize MCP host application")
            await self.mcp_client.close_connection()
            raise
        
    async def get_llm_response(self, query):
        
        try:
        
            response = await self.agent.get_agent_response(query)
            logger.info("Response is fetched")
            return response
        
        except Exception as e:
            logger.exception("Error in get_llm_response")
            raise
        
    async def conversation(self):
        
        
        print("\nEntering conversation mode. Type 'quit' or 'q' to exit.")
        
        while(True):
            
            query = input("Enter your question here: \n").strip()
            
            if not query:
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
            
            prompt_list:ListPromptsResult = await self.mcp_client.list_prompts()
            prompt_objs = prompt_list.prompts
            
            prompt_obj = next(
                (prompt for prompt in prompt_objs if prompt.name == prompt_name), None
            )
            
            if prompt_obj is None:
                raise ValueError(
                    f"No matching MCP prompt: {prompt_name}"
                )
                
            logger.info(f"{prompt_name} prompt extracted success")
            
            print(prompt_obj)
            
            arguments = {}
            
            if prompt_obj.arguments:
                for argument in prompt_obj.arguments:
                    
                    is_required = "required" if argument.required else "optional"
                    user_input = input(f"\n{argument.name} - {is_required}: ")
                    
                    if not user_input and argument.required:
                        print(f"Error in {argument.name} - {is_required}")
                        return
                    
                    if user_input:
                        arguments[argument.name] = user_input
            
            prompt_result = await self.mcp_client.get_prompt(prompt_name, arguments)
            prompt = prompt_result.messages[0].content.text
            logger.info("prompt is fetched success.")
            
            llm_response = await self.get_llm_response(prompt)
            logger.info(f"llm_response: {llm_response}")
            
            
            return llm_response

        except Exception as e:
            logger.exception("Error in prompt")
            raise
        
    async def read_file(self):
        
        try:
            
            filename = input("Enter the file name you want to read: ")
            encoded_file_name = quote(filename, safe="")
            
            file = await self.mcp_client.read_resouce_from_server(f"file://workspace/{encoded_file_name}")
            return file.contents[0].text
            
        except Exception as e:
            logger.exception("Error in read file")
            raise
        
    
        
    
        
        