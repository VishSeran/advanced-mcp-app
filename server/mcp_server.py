from fastmcp import FastMCP
from pathlib import Path

from configurations.logger import get_logger

logger = get_logger("mcp-server")
base_dir  = Path(__file__).parent / "workspace"
base_dir.mkdir(exist_ok=True)
class MCPServer:
    
    def __init__(self):
        
        try:
            
            self.mcp_server = FastMCP(
                name="HTTP File Server"
            )
            
            
        except Exception as e:
            logger.error(f"Error in mcp server init: {e}")
            raise