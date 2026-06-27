from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Canon MCP Server")

@mcp.tool()
def ping() -> str:
    """
    A simple ping tool to verify the MCP server is reachable.
    """
    return "pong"

if __name__ == "__main__":
    mcp.run()
