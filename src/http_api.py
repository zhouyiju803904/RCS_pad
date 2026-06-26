import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from api import fetch_agv_list


def build_agv_payload() -> list[dict[str, Any]]:
    agvs = fetch_agv_list()
    return [
        {
            "id": agv.id,
            "ip": agv.ip,
            "name": agv.name,
            "state": agv.state,
            "battery": agv.battery,
            "location": agv.location,
            "task": agv.task,
        }
        for agv in agvs
    ]


class AGVRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: list[dict[str, Any]]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/agv/list":
            self._send_json(build_agv_payload())
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/agv/list":
            self._send_json(build_agv_payload())
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def run_server(host: str = "0.0.0.0", port: int = 52000) -> None:
    server = HTTPServer((host, port), AGVRequestHandler)
    print(f"Serving on http://{host}:{port}/api/agv/list")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
