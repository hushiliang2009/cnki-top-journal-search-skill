from __future__ import annotations

import asyncio
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run() -> None:
    skill_root = Path(__file__).resolve().parent.parent
    project = skill_root / "mcpb"
    environment = dict(os.environ)
    environment.pop("PYTHONHOME", None)
    environment.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
    parameters = StdioServerParameters(
        command="uv",
        args=["run", "--directory", str(project), "src/server.py"],
        env=environment,
    )
    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            assert names == ["cnki_search", "cnki_professional_search"]
            print({"tools": names})


if __name__ == "__main__":
    asyncio.run(run())
