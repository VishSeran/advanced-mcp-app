import os
import dotenv

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from configurations.logger import get_logger
from configurations.configs import MODEL_NAME


logger = get_logger("llm-agent")
dotenv.load_dotenv()

class LLMAgent:
    
    def __init__(self, tools, model_name = MODEL_NAME):
        
        try:
            groq_api = os.getenv("groq_api")
            
            if groq_api is None:
                raise ValueError("Groq api is missing")
            
            if model_name is None:
                raise ValueError("Model name is missing")
            
            if tools is None:
                raise ValueError("Tools are missing")
            
            checkpointer = InMemorySaver()
            
            self.configs = {
                "configurable": {
                    "thread_id": "conversational_id"
                }    
            }
            
            self.llm = ChatGroq(
                api_key=groq_api,
                model=model_name,
                temperature=0.5,
                max_tokens=4000,
                model_kwargs={
                    "parallel_tool_calls": False
                }
            )
            
            logger.info(f"Groq llm initiated: {self.llm}")
            
            self.llm_agent = create_agent(
                model=self.llm,
                tools=tools,
                checkpointer=checkpointer,
                system_prompt="""
                            You are a useful AI agent.
                            You have access to the tools that provided.
                            Use the relevant tools if needed when answering the user questions.
                """
            )
            
            logger.info(f"Groq llm agent initiated: {self.llm_agent}")
            
 
        except ValueError as e:
            logger.error(f"Value Error in agent init: {e}")
            raise    
        except Exception as e:
            logger.error(f"Error in agent init: {e}")
            raise
        
    async def get_agent_response(self, query):
        
        try:
            
            if query is None:
                raise ValueError("query is missing")
            
            
            
        except ValueError as e:
            logger.error(f"Value Error in get_agent_response: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Error in get_agent_response: {e}")
            raise