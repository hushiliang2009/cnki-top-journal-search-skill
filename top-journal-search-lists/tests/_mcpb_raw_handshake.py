from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def send(process: subprocess.Popen[str], payload: dict[str, object]) -> None:
    assert process.stdin is not None
    process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
    process.stdin.flush()


def receive(process: subprocess.Popen[str]) -> dict[str, object]:
    assert process.stdout is not None
    line = process.stdout.readline()
    if not line:
        error = process.stderr.read() if process.stderr else ""
        raise RuntimeError(f"MCPB 进程提前退出：{error}")
    return json.loads(line)


def main() -> None:
    skill_root = Path(__file__).resolve().parent.parent
    environment = dict(os.environ)
    environment.pop("PYTHONHOME", None)
    environment.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
    process = subprocess.Popen(
        ["uv", "run", "--directory", str(skill_root / "mcpb"), "src/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    try:
        send(
            process,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "cnki-smoke", "version": "0.1.0"},
                },
            },
        )
        initialized = receive(process)
        send(process, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        send(process, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = receive(process)
        send(
            process,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "cnki_status", "arguments": {}},
            },
        )
        status = receive(process)
        result_text = status["result"]["content"][0]["text"]
        result = json.loads(result_text)
        print(
            json.dumps(
                {
                    "server": initialized["result"]["serverInfo"]["name"],
                    "tools": [tool["name"] for tool in tools["result"]["tools"]],
                    "status": result["status"],
                },
                ensure_ascii=False,
            )
        )
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
