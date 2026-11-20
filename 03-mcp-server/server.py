# Lesson 1: What is MCP?

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("security-helper")          # name of your toy box

PORTS = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3389: "RDP", 445: "SMB", 31999: "OrcaSecure Lab Service"}

@mcp.tool()                               # this line turns a function into an MCP tool
def lookup_port(port: int) -> str:
    """Does stuff."""
    return PORTS.get(port, "Unknown port")

@mcp.tool()
def my_tool(number: int) -> int:
    """Does other stuff , doubles the number"""
    return number * 2


import csv
from collections import Counter
from pathlib import Path

LOG_FILE = Path(__file__).parent / "auth_log.csv"   # the notebook sits next to this file

@mcp.tool()
def failed_logins_by_user() -> dict:
    """Count failed login attempts per user from the authentication log."""
    counts = Counter()
    with open(LOG_FILE) as f:
        for row in csv.DictReader(f):          # each row becomes {"time":..., "user":..., ...}
            if row["result"] == "FAIL":
                counts[row["user"]] += 1
    return dict(counts.most_common())          # biggest first


@mcp.tool()
def failed_logins_by_ip() -> dict:
    """Count failed login attempts per source IP address from the authentication log."""
    counts = Counter()
    with open(LOG_FILE) as f:
        for row in csv.DictReader(f):
            if row["result"] == "FAIL":
                counts[row["source_ip"]] += 1
    return dict(counts.most_common())



if __name__ == "__main__":
    mcp.run()