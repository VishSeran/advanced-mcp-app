from fastmcp import Context

from server.mcp_server import server
from configurations.logger import get_logger
from configurations.configs import is_within_roots


logger = get_logger("server-config")

@server.tool()
async def read_file(filepath:str, ctx: Context) -> str:
    
    try:
        
        if filepath is None:
            raise ValueError ("filepath is missing")
        
        if not is_within_roots(filepath):
            return f"Error: Access denied: path outside workspace roots: {filepath}"
        
    
    except ValueError as e:
        await ctx.error(f"Value error: {e}")
        raise
        
    except Exception as e:
        await ctx.error(f"Error in {filepath} read file: {e}")
        raise

