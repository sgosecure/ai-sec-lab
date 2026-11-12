"""Tools the agent can call. Each returns a JSON-serializable dict."""
import logging
import os
import re

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

log = logging.getLogger("agent.tools")
TIMEOUT = 10
CVE_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
_kev_cache = None  # the file is ~1 MB, so download it once per run


# --- Schemas sent to the model -------------------------------------------
TOOL_SCHEMAS = [
    {
        "name": "get_weather",
        "description": "Get current temperature and wind speed for a city.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. Denver"}},
            "required": ["city"],
        },
    },
    {
        "name": "lookup_cve",
        "description": "Look up a CVE in the NIST NVD. Returns description, CVSS score and severity.",
        "input_schema": {
            "type": "object",
            "properties": {"cve_id": {"type": "string", "description": "e.g. CVE-2021-44228"}},
            "required": ["cve_id"],
        },
    },
    {
        "name": "check_kev",
        "description": (
            "Check if a CVE is in CISA's Known Exploited Vulnerabilities (KEV) catalog, "
            "meaning it is actively exploited in the wild. Returns date added, "
            "remediation due date, and whether ransomware uses it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"cve_id": {"type": "string", "description": "e.g. CVE-2021-44228"}},
            "required": ["cve_id"],
        },
    },
]

_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    reraise=True,
)


@_retry
def _get(url, **kwargs):
    r = requests.get(url, timeout=TIMEOUT, **kwargs)
    r.raise_for_status()
    return r.json()


def get_weather(city: str) -> dict:
    geo = _get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1})
    if not geo.get("results"):
        return {"error": f"City not found: {city}"}
    loc = geo["results"][0]
    wx = _get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "current": "temperature_2m,wind_speed_10m",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
        },
    )
    cur = wx["current"]
    return {"city": loc["name"], "temp_f": cur["temperature_2m"], "wind_mph": cur["wind_speed_10m"]}


def check_kev(cve_id: str) -> dict:
    global _kev_cache
    cve_id = cve_id.strip().upper()
    if not CVE_PATTERN.match(cve_id):          # same bouncer as lookup_cve
        return {"error": f"Invalid CVE ID format: {cve_id}"}
    if _kev_cache is None:
        data = _get(KEV_URL)
        _kev_cache = {v["cveID"]: v for v in data["vulnerabilities"]}
    entry = _kev_cache.get(cve_id)
    if not entry:
        return {"cve_id": cve_id, "in_kev": False}
    return {
        "cve_id": cve_id,
        "in_kev": True,
        "product": f'{entry["vendorProject"]} {entry["product"]}',
        "date_added": entry["dateAdded"],
        "due_date": entry["dueDate"],
        "ransomware_use": entry["knownRansomwareCampaignUse"],
        "required_action": entry["requiredAction"],
    }



def lookup_cve(cve_id: str) -> dict:
    cve_id = cve_id.strip().upper()
    if not CVE_PATTERN.match(cve_id):  # input validation: never pass raw model output to an API
        return {"error": f"Invalid CVE ID format: {cve_id}"}
    headers = {"apiKey": os.environ["NVD_API_KEY"]} if os.getenv("NVD_API_KEY") else {}
    data = _get("https://services.nvd.nist.gov/rest/json/cves/2.0",
                params={"cveId": cve_id}, headers=headers)
    vulns = data.get("vulnerabilities", [])
    if not vulns:
        return {"error": f"{cve_id} not found"}
    cve = vulns[0]["cve"]
    desc = next((d["value"] for d in cve["descriptions"] if d["lang"] == "en"), "")
    score, severity = None, None
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if cve.get("metrics", {}).get(key):
            m = cve["metrics"][key][0]
            score = m["cvssData"]["baseScore"]
            severity = m["cvssData"].get("baseSeverity") or m.get("baseSeverity")
            break
    return {"cve_id": cve_id, "cvss": score, "severity": severity, "description": desc[:500]}


#REGISTRY = {"get_weather": get_weather, "lookup_cve": lookup_cve}
REGISTRY = {"get_weather": get_weather, "lookup_cve": lookup_cve, "check_kev": check_kev}


def run_tool(name: str, args: dict) -> dict:
    """Dispatch a tool call; never let an exception crash the agent loop."""
    log.info("tool_call name=%s args=%s", name, args)
    fn = REGISTRY.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        result = fn(**args)
    except requests.HTTPError as e:
        result = {"error": f"HTTP {e.response.status_code} from upstream API"}
    except Exception as e:  # noqa: BLE001
        log.exception("tool failed")
        result = {"error": f"{type(e).__name__}: {e}"}
    log.info("tool_result name=%s result=%s", name, str(result)[:200])
    return result
