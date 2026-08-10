from fastmcp import Context
from pathlib import Path
from server.mcp_server import server
from configurations.logger import get_logger
from configurations.configs import is_within_roots, get_realtive_path


logger = get_logger("server-config")

@server.tool()
async def read_file(filepath:Path, ctx: Context) -> str:
    
    try:
        
        if filepath is None:
            raise ValueError ("filepath is missing")
        
        if not is_within_roots(filepath):
            return f"Error: Access denied: path outside workspace roots: {filepath}"
        
        path = get_realtive_path(filepath)
        text = path.read_text()
        
        return text
        
    
    except ValueError as e:
        await ctx.error(f"Value error: {e}")
        raise
        
    except Exception as e:
        await ctx.error(f"Error in {filepath} read file: {e}")
        raise

