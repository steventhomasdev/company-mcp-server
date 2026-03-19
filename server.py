from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP server")

@mcp.tool()
def say_hello(name : str) -> str:
    """Say hello to someone by name"""
    return f"Hello {name} your mcp server is working 🎉"

@mcp.tool()
def add_numbers(a : int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def multiply_numbers(a :int, b :int) -> int:
    "Multiply 2 numbers together"
    return a * b

if __name__ == "__main__":
    mcp.run()

