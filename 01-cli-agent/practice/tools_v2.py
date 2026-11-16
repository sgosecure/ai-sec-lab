import re
import requests

#CVE_PATTERN = re.compile(r"TODO: regex that matches CVE-2021-44228", re.IGNORECASE)
CVE_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)

# 1. MENU CARD: what Claude reads to pick a tool
TOOL_SCHEMAS = [
    {
        "name": "lookup_cve",
        "description": "Look up a CVE in the NIST NVD. Returns description, CVSS score and severity.",
        "input_schema": {
            "type": "object",
            "properties": {"cve_id": {"type": "string", "description": "e.g. CVE-2021-44228"}},
            "required": ["cve_id"],
        },
    },
]

# 2. THE HELPER: does the real work
def lookup_cve(cve_id: str) -> dict:
    cve_id = cve_id.strip().upper()
    # TODO: if it doesn't match CVE_PATTERN, return {"error": ...}
    if not CVE_PATTERN.match(cve_id):  # input validation: never pass raw model output to an API
            return {"error": f"Invalid CVE ID format: {cve_id}"}

    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    # TODO: requests.get(url, params=..., timeout=10), then .json()

    # TODO: if no "vulnerabilities", return {"error": "not found"}
    # TODO: return {"cve_id": ..., "description": ...}

# 3. THE ALLOWLIST: only these can run
REGISTRY = {}  # TODO

# 4. THE FRONT DESK: runs the tool, never crashes
def run_tool(name: str, args: dict) -> dict:
    # TODO: look up name in REGISTRY; unknown -> {"error": ...}
    # TODO: try: call it with **args / except Exception -> {"error": ...}
    pass