from pathlib import Path

from configurations.logger import get_logger
from server.mcp_server import base_dir

logger = get_logger("configs")

def is_within_roots(path:Path) -> bool:
    
    try:
        path.resolve().relative_to(base_dir.resolve())
        return True
    
    except ValueError:
        return False
        