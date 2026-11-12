# 01 – CLI agent with tool calling

Terminal chatbot using the Anthropic Messages API with two tools:
`get_weather` (Open-Meteo, no key) and `lookup_cve` (NIST NVD 2.0).

## Security controls
| Control | Where |
|---|---|
| Input validation on tool args (CVE regex) | `tools.lookup_cve` |
| Allowlisted tool registry | `tools.REGISTRY` |
| Errors returned to model, never crash loop | `tools.run_tool` |
| Retries with backoff (network + API) | `tenacity`, `max_retries=3` |
| Max tool rounds per turn | `agent.MAX_TOOL_ROUNDS` |
| Audit log of every tool call | `agent.log` |

## Run
```bash
python agent.py
pytest tests/
```
Try: `Is CVE-2021-44228 critical?` · `Weather in Denver?` · `Compare CVE-2014-0160 and CVE-2017-0144`
