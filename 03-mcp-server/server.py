from mcp.server.fastmcp import FastMCP

mcp = FastMCP("security-helper")          # name of your toy box

PORTS = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3389: "RDP", 445: "SMB"}

@mcp.tool()                               # this line turns a function into an MCP tool
def lookup_port(port: int) -> str:
    """Does stuff"""
    return PORTS.get(port, "Unknown port")

if __name__ == "__main__":
    mcp.run()