# Windows 11 + ChatGPT Desktop 实机验证结果

- 验证日期：2026-07-31
- 验证环境：Windows 11，Windows PowerShell 5.1.26100.8972
- Python：3.14.3
- 仓库：`hushiliang2009/cnki-top-journal-search-skill`
- 测试提交：`76651999980bc3f5c9bd283f90002a1efda97851`
- 当前状态：任务 A 已通过；任务 B 的安装、配置、握手与调用已通过，待重启 ChatGPT Desktop 后确认客户端界面可见性。

## 1. Release 附件校验

| 附件 | 字节数 | SHA-256 | 结果 |
| --- | ---: | --- | --- |
| `top-journal-search-lists_Skill.zip` | 716092 | `d6d69a038700ffe51b3c5e49c9130fbbedb1cf170c5f44692f84a749b2105aa8` | 通过 |
| `cnki-search.mcpb` | 322051 | `92b6cc5597cabca874ac6057b2c8e855ce281191b67e29ce1bc5e6ed5263a7ab` | 通过 |
| `top-journal-search-lists-env_Skill.zip` | 421566 | `00aad9c246c61d253259b710b3627b31d96dfe3d6c968650027f2bc1b1f6c915` | 通过 |
| `cnki-search-env.mcpb` | 173558 | `173a01498e5481c1825305ce2d53cb68cdcbd55aab27e225e7f12f9c6fa080e4` | 通过 |

通用版标签 `v0.4.2` 指向 `06e656cd10bd9ede69ef644108badd051116196b`；环境版标签 `top-journal-search-lists-env-v0.2.0` 指向 `85afadef2036dca63161131242c6b8d024746bdb`。

## 2. 任务 A：PowerShell 门控测试

在仓库根目录执行：

```powershell
python -m pytest top-journal-search-lists/tests/test_installers.py top-journal-search-lists-env/tests/test_installers.py -v -rs
```

最终结果：

```text
63 passed in 28.28s
```

- 交接文档列出的9个 Windows PowerShell 测试函数全部通过。
- 环境版回滚测试按有无旧运行时参数化，因此对应10个 Windows 专属测试实例，均为 `PASSED`。
- 首次受限环境运行时，7个 Git Bash 用例因 `CreateFileMapping ... Win32 error 5` 失败；在非沙箱 Windows 进程复跑后63项全部通过，证明首轮异常属于运行环境权限，不是产品缺陷。

## 3. 任务 B：Release 安装与服务验证

### 3.1 安装结果

使用上述已校验 ZIP 中的 `install.ps1`，分别以 `-Codex -PythonExe C:\Python314\python.exe` 安装。

| 项目 | 结果 |
| --- | --- |
| 通用 Skill | 已安装，服务版本 0.4.2 |
| 环境 Skill | 已安装，服务版本 0.2.0 |
| `cnki-search` 运行时 | 179666657 字节 |
| `cnki-search-env` 运行时 | 901665171 字节 |
| 环境版私有 `playwright-browsers` | 721890305 字节 |

安装前 C 盘可用空间为337.4 GiB，满足交接文档的空间要求。

### 3.2 配置与备份

- `config.toml` 可由 Python `tomllib` 正常解析。
- 当前 MCP 条目为 `ai4scholar`、`cnki-search`、`cnki-search-env`、`node_repl`、`stata`、`zotero`。
- 与安装前备份逐项比较，`ai4scholar` 和其他无关 MCP 条目保持不变。
- `config.toml.backup-*` 恰好保留3份。
- 通用 Skill 备份恰好保留3份；环境 Skill 为首次安装，因此没有旧 Skill 备份。

### 3.3 MCP 工具可见性与调用

通过新安装运行时的 stdio MCP 握手，已枚举出四个工具：

```text
cnki_search
cnki_professional_search
cnki_search_env
cnki_professional_search_env
```

调用结果：

- `cnki_search(query="环境污染治理", limit=1)`：`status=challenge_detected`，`record_count=0`。这与交接文档记载的公网知网滑块验证边界一致。
- `cnki_professional_search`：未设置 `CNKI_WEBVPN_HOME` 时返回 `status=configuration_error`，`detail` 包含配置、人工登录和不可用于定时任务的指引。
- `cnki_professional_search_env`：未设置 `CNKI_ENV_WEBVPN_HOME` 时返回同类 `configuration_error` 和环境版配置指引。

`codex mcp list` 同时显示 `cnki-search` 和 `cnki-search-env` 为 `enabled`。

### 3.4 待完成的客户端界面确认

当前 ChatGPT Desktop 进程在安装前已启动，尚未重启。需要退出并重新打开 ChatGPT Desktop，然后确认界面中四个工具同时可见。在此项完成前，任务 B 不标记为最终通过。

## 4. 任务 C

未执行。该项需要机构 WebVPN 人工登录与全程值守，交接文档已标记为可选。

## 5. 与交接文档的差异

1. GitHub 当前返回仓库 `isPrivate=false`，与交接文档中的私有仓库说明不一致，不影响本次验证。
2. 本次环境版私有浏览器缓存实测为721890305字节，高于交接文档的约549 MB估计；但总占用仍低于预留2 GB的要求。
