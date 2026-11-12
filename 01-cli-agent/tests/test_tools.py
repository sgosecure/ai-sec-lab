import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools import lookup_cve, run_tool
from tools import check_kev

def test_rejects_bad_cve_format():
    assert "error" in lookup_cve("'; DROP TABLE cves;--")


def test_unknown_tool():
    assert run_tool("rm_rf", {}) == {"error": "Unknown tool: rm_rf"}


def test_bad_args_do_not_crash():
    assert "error" in run_tool("get_weather", {"wrong": "x"})

def test_kev_rejects_bad_format():
    assert "error" in check_kev("not-a-cve")