from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run() -> None:
    skill_root = Path(__file__).resolve().parent.parent
    environment = dict(os.environ)
    environment.update(
        {
            "PYTHONPATH": str(skill_root / "scripts"),
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
        }
    )
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "cnki_search.mcp_server"],
        env=environment,
    )
    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            assert names == ["cnki_search"]
            print({"tools": names})


if __name__ == "__main__":
    asyncio.run(run())
