from pathlib import Path

from fastmcp import Context
from mcp.types import SamplingMessage, TextContent
from configurations.configs import get_realtive_path, is_within_roots
from configurations.logger import get_logger
from server.mcp_server import server, base_dir

logger = get_logger("server-config")

@server.tool()
async def read_file(filepath:Path, ctx: Context) -> str:
    
    """Read a file from the workspace directory."""
    
    try:
        
        if filepath is None:
            raise ValueError ("filepath is missing")
        
        if not is_within_roots(filepath):
            return f"Error: Access denied: path outside workspace roots: {filepath}"
        
        path = get_realtive_path(filepath)
        text = path.read_text()
        
        await ctx.info(f"file read is successfull: {filepath}")
        return text

    except ValueError as e:
        await ctx.error(f"Value error: {e}")
        raise
        
    except Exception as e:
        await ctx.error(f"Error in {filepath} read file: {e}")
        raise
    
    
@server.tool()
async def write_file(filepath:Path, ctx:Context, content: str) -> str:
    
    """Write content to a file in the workspace directory."""
    
    try:
        
        if content is None:
            raise ValueError("content is missing")
        
        if not is_within_roots(filepath):
            return f"Error: Access denied: path outside workspace roots: {filepath}"
        
        path = get_realtive_path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content)
        await ctx.info(f"Successfully wrote {len(content)} characters to {filepath}")
        return f"Successfully wrote {len(content)} characters to {filepath}"
        
    except ValueError as e:
        await ctx.error(f"Value error: {e}")
        return f"Error writing file: {str(e)}"
    
    except Exception as e:
        await ctx.error(f"Error in write file: {e}")
        return f"Error writing file: {str(e)}"
    
    
@server.tool()    
async def list_files(ctx: Context, directory = ".") -> str:
    
    """List files in a directory within the workspace."""
    
    try:
        
        if not is_within_roots(directory):
            await ctx.warning("Error: Access denied, file/directory outside root directory")
            
        path = get_realtive_path(directory)
        
        if not path.is_dir():
            await ctx.warning(f"Error: {directory} is not a directory")
        
        if not path.exists():
            await ctx.warning(f"Error: {directory} is not exists")
        
        files = []
        
        for item in path.iterdir():
            name = item.name
            relative_path = item.relative_to(base_dir)
            file_type = "Dirdctory" if item.is_dir() else "file"
            size = item.stat().st_size() if item.is_file() else 0
            
            files.append(f"{name}: {file_type}: {relative_path}: ({size} bytes)")
        
        return "\n".join(files) if files else "Directory is empty"
             
    except Exception as e:
        await ctx.error(f"Error in list file: {e}")
        raise
    

@server.tool()
async def analyze_code(code:str, ctx:Context, focus:str = "quality") -> str:
    
    try:
        prompt = f"""Analyze the following code  focusing on {focus}.
        
                    Code:
                    {code}
                    
                """
        
        result = await ctx.session.create_message(
            messages= [ 
            SamplingMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=prompt
                )
            )
            ], 
            max_tokens=1000
        )
        
        if not isinstance(result.content, TextContent):
            raise ValueError(  # noqa: TRY004
            f"Expected text sampling response, "
            f"got {type(result.content).__name__}"
            )
            
        return result.content.text

    except ValueError as e:
        await ctx.error(f"Value error: {e}")
        raise
    
    except Exception as e:
        await ctx.error(f'Error in analyze code: {e}')
        raise
    
@server.resource("file://workspace/{filename}")
async def get_workspace_file(filename:str, ctx:Context) -> str:
    
    "Read a file from workspace as a resource"
    
    try:
        path = (base_dir/filename).resolve()
        path.relative_to(base_dir)
        
        if not path.exists() or not path.is_file():
            await ctx.warning ("File is not found or path isn't a file")
            return "File is not found or path isn't a file"
        
        text = path.read_text()
        await ctx.info(f"file read successfull: {text}")
        
        return text
        
    except Exception as e:
        await ctx.error(f"Error in get_workspace_file {filename}: {e}")
        raise

@server.prompt()
async def review_code(filename:str, ctx:Context):
    
    "generate a prompt to review a code from a file"
    try:
        
        path:Path = (base_dir/filename).resolve()
        path.relative_to(base_dir)
        
        if not path.exists() or not path.is_file():
            await ctx.warning(f"File is not found or path isn't a file: {filename}")
            return f"File is not found or path isn't a file: {filename}"
        
        prompt =f"""You are a helpful code review agent.
                    please review the code in file: {filename} and provide:
                    
                    1. A summary of what the code does
                    2. Potential bugs or issues
                    3. Security concerns
                    4. Suggestions for improvements
                    5. Code quality assessment

                    Focus on readability, maintainability, and best practices.
        """
        
        return prompt
            
    except Exception as e:
        await ctx.error(f"Error in review code {filename}: {e}")
        raise
    

@server.prompt()
async def analyze_security(filename:str, ctx:Context):
    
    """Generate a prompt to analyze security of a file."""
    try:
        
        path:Path = (base_dir/filename).resolve()
        path.relative_to(base_dir)
        
        if not path.exists() or not path.is_file():
            await ctx.warning(f"File is not found or path isn't a file: {filename}")
            return f"File is not found or path isn't a file: {filename}"
        
        prompt =f"""Perform a security analysis of '{filename}' focusing on:

                    1. Input validation and sanitization
                    2. Authentication and authorization checks
                    3. Potential injection vulnerabilities
                    4. Data exposure risks
                    5. Error handling security

                    Provide specific line numbers and remediation suggestions."""
        
        return prompt
            
    except Exception as e:
        await ctx.error(f"Error in analyze_security {filename}: {e}")
        raise
    
    
if __name__ == "__main__":
    print("Starting HTTP MCP Server on http://127.0.0.1:8000")
    print(f"Workspace roots: {base_dir}")
    
    server.run(transport="http",
               host = "127.0.0.1",
               port = 8000)
    
    