from pathlib import Path

from configurations.logger import get_logger

from server.mcp_server import base_dir

logger = get_logger("configs")

def is_within_roots(path) -> bool:
    
    try:
        path.resolve().relative_to(base_dir.resolve())
        return True
    
    except ValueError:
        return False
    
    
def get_realtive_path(path):
    
    try:
        
        if path is None:
            raise ValueError("Path is missing")
        
        file_path =  (base_dir/path).resolve()
        path = file_path.relative_to(base_dir)
        
        return path
 
    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Error in get_realtive_path: {e}")
        raise
        