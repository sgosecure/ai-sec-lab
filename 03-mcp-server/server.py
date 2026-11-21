# Lesson 1: What is MCP?

from mcp.server.fastmcp import FastMCP
import json
import logging
import csv
from collections import Counter
from pathlib import Path


mcp = FastMCP("security-helper")   

audit_log = logging.getLogger("audit")
handler = logging.FileHandler(Path(__file__).parent / "audit.log")   # diary file next to server
handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
audit_log.addHandler(handler)
audit_log.setLevel(logging.INFO)
audit_log.propagate = False             # keep it out of stdout/stderr

def audit(tool, args, outcome):
    """Write one line to the diary."""
    audit_log.info(json.dumps({"tool": tool, "args": args, "outcome": outcome}))




       # name of your toy box

PORTS = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3389: "RDP", 445: "SMB", 31999: "OrcaSecure Lab Service"}

@mcp.tool()                               # this line turns a function into an MCP tool
def lookup_port(port: int) -> str:
    """Does stuff."""
    audit("lookup_port", {}, "OK")
    return PORTS.get(port, "Unknown port")

@mcp.tool()
def my_tool(number: int) -> int:
    """Does other stuff , doubles the number"""
    return number * 2




LOG_FILE = Path(__file__).parent / "auth_log.csv"   # the notebook sits next to this file

@mcp.tool()
def failed_logins_by_user() -> dict:
    """Count failed login attempts per user from the authentication log."""
    audit("failed_logins_by_user", {}, "OK")
    counts = Counter()
    with open(LOG_FILE) as f:
        for row in csv.DictReader(f):          # each row becomes {"time":..., "user":..., ...}
            if row["result"] == "FAIL":
                counts[row["user"]] += 1
    return dict(counts.most_common())          # biggest first


@mcp.tool()
def failed_logins_by_ip() -> dict:
    """Count failed login attempts per source IP address from the authentication log."""
    audit("failed_logins_by_ip", {}, "OK")
    counts = Counter()
    with open(LOG_FILE) as f:
        for row in csv.DictReader(f):
            if row["result"] == "FAIL":
                counts[row["source_ip"]] += 1
    return dict(counts.most_common())


ALLOWED_LOGS = {"auth_log.csv"}                    # the ONLY files this tool may read

@mcp.tool()
def read_log(filename: str) -> str:
    """Read an approved log file and return its contents."""
    if filename not in ALLOWED_LOGS:
        audit("read_log", {"filename": filename}, "DENIED")     # 📝 write it down
        return f"Access denied: '{filename}' is not an approved log file."
    audit("read_log", {"filename": filename}, "ALLOWED")        # 📝 write it down
    return (Path(__file__).parent / filename).read_text()


if __name__ == "__main__":
    mcp.run()