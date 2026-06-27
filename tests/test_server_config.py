import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import api


def test_server_url_is_shared_across_api_helpers():
    api.set_server_base_url("http://127.0.0.1:52000")
    assert api.get_server_base_url() == "http://127.0.0.1:52000"
    assert api.build_api_url("/api/agv/list") == "http://127.0.0.1:52000/api/agv/list"
