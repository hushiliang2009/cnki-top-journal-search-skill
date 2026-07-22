# Top Journal Search Lists 使用指南

## 功能

本 Skill 联合使用中国知网可见浏览器 MCP、ai4scholar MCP 和内置综合期刊目录。它支持知网高级检索与专业检索，并把中英文文献按十级期刊顺序整理，适用于专题查询、文献综述和顶刊定向检索。

CNKI 用于学校授权范围内的中文期刊和精确字段检索；ai4scholar 用于 Google Scholar、Semantic Scholar、PubMed 及引文扩展。两类来源分别记录，互不代替。

## 压缩包内容

```text
top-journal-search-lists/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── scripts/catalog_lookup.py
├── scripts/cnki_search/
├── references/Academic_Journal_Master_Directory_20260715.md
├── references/cnki-search-reference.md
├── installers/
├── mcpb/
└── tests/
```

综合期刊目录随 Skill 提供。压缩包不包含 ai4scholar 配置，也不包含知网账号、密码、Cookie 或浏览器会话文件。

## 环境要求

- Windows、macOS 或 Linux；
- 期刊目录脚本要求 Python 3.10 或更高版本；CNKI MCP 要求 Python 3.11 或更高版本；
- CNKI MCP 使用 `mcp` 与 `playwright`；
- 系统已安装 Chrome、Edge 或 Chromium。没有兼容浏览器时可安装 Playwright Chromium；
- 文件统一使用 UTF-8，CSV 导出使用 UTF-8 BOM。

## 安装

### 自动安装

Windows PowerShell：

```text
powershell -ExecutionPolicy Bypass -File installers/install.ps1
```

macOS 或 Linux：

```text
sh installers/install.sh
```

安装器复制完整 Skill、创建独立 Python 环境，并增量写入 CNKI MCP 配置。修改已有配置前应生成时间戳备份，不得删除 Zotero、ai4scholar 等其他 MCP 服务。

### 手工安装 Skill

把完整的 `top-journal-search-lists` 文件夹复制到以下位置之一：

- Codex Windows：`%USERPROFILE%\.codex\skills\top-journal-search-lists`
- Codex macOS/Linux：`$HOME/.codex/skills/top-journal-search-lists`
- Claude Code：`~/.claude/skills/top-journal-search-lists`

若设置了 `CODEX_HOME` 或 `CLAUDE_CONFIG_DIR`，应使用对应自定义目录。`SKILL.md` 必须直接位于上述文件夹内，不能多套一层同名目录。

### 手工安装 Python 依赖

```text
python -m venv .venv
.venv/Scripts/python -m pip install mcp playwright
```

macOS 和 Linux 将第二行改为 `.venv/bin/python -m pip install mcp playwright`。优先使用系统浏览器；找不到浏览器时再运行 `python -m playwright install chromium`。

### 配置 ai4scholar

ai4scholar 应至少提供 Google Scholar、Semantic Scholar 和 PubMed 检索，以及 Semantic Scholar 的参考文献、被引文献和相似论文工具。安装完成后应执行一次真实查询，不能只依据配置项判断可用。

## 安装验证

在 Skill 根目录运行：

```text
python scripts/catalog_lookup.py validate
python scripts/catalog_lookup.py lookup "American Economic Review" "Nature Human Behaviour" "经济研究"
python -m pytest -p no:cacheprovider tests -q
```

期刊示例的预期层级分别为 1、2、6。检查 MCP 状态时不会打开浏览器：

```text
python -m cnki_search.cli status
```

手工运行时需要把 Skill 的 `scripts` 目录加入 `PYTHONPATH`；自动安装生成的 MCP 配置已包含入口路径。

需要使用更新后的综合目录时，把 `--catalog` 放在子命令之前：

```text
python scripts/catalog_lookup.py --catalog path/to/Academic_Journal_Master_Directory.md validate
```

## CNKI 登录和会话

调用 `cnki_login` 后，程序打开河海大学 WebVPN 登录页。用户在可见浏览器中手工登录，并自行处理验证码。程序不接收账号、密码或验证码。

每次启动只使用临时内存浏览器上下文，不持久化 Cookie，不导入 Chrome、Edge 或其他浏览器的历史会话，也不使用扫描包中的 Local State。关闭会话后需要重新登录。

## CNKI 检索、限流和结果

- 高级检索和专业检索均只使用新版 `kns8s/AdvSearch` 页面。当前会话主机为 `webvpn.hhu.edu.cn` 时，使用河海大学 WebVPN 入口 `https://webvpn.hhu.edu.cn/https/77726476706e69737468656265737421fbf952d2243e635930068cb8/kns8s/AdvSearch`；当前会话主机为知网源站时，使用 `https://kns.cnki.net/kns8s/AdvSearch`。程序按当前会话主机选择，不固定 `wrdrecordvisit`，不提供其他入口或回退模式。
- 高级检索在新版页面填写字段化表单；专业检索在同一新版页面切换专业检索标签，并原样填写用户确认的表达式。
- 首选高级检索或专业检索，作者发文检索和句子检索只用于特定任务。
- 程序采用低频串行方式。检索默认 1 页、最多 3 页，每页间隔 4 至 7 秒；详情最多 10 条，每条间隔 3 至 6 秒；下载最多 5 篇，每篇间隔 8 至 15 秒。
- 出现验证码、403、429、权限不足、会话过期或会话失效时立即停止，不自动连续重试，也不切换代理。
- 结果优先按 DOI 去重；没有 DOI 时按规范化题名、第一作者和年份去重。
- 每条结果尽量保留题名、作者、单位、期刊、年份、卷期页码、摘要、关键词、基金、DOI、详情链接和下载状态。
- 结果通过综合目录附加最高期刊层级。未匹配期刊明确标记，不自行指定层级。
- 导出格式包括 JSON、CSV、BibTeX、RIS 和 GB/T 7714。

## 下载规则

检索结果先编号展示。只有用户明确选择具体结果、确认具有访问权限并指定保存目录后，才调用下载工具。每次最多 5 篇，只点击当前知网页面的知网官方全文按钮。

下载后检查 PDF 或 CAJ 文件头。若返回 HTML 登录页或未知格式，程序删除无效文件并停止。不得构造隐藏下载链接或地址，不访问第三方全文站点。

## 检索顺序

1. 经济学 Top 5
2. NCS_PNAS，其中人文、哲学与社会科学交叉期刊优先
3. UTD24
4. FT50
5. Field Top
6. 中文顶尖期刊
7. Top 目录中的其他顶尖期刊
8. SSCI
9. CSSCI
10. SCIE

同一期刊属于多个层级时采用最高层级。第二级内部按 `ncs_internal_rank` 排序。第七级无独立记录时必须明确报告为空层级，不得伪造期刊，也不得从其他层级复制论文。

## 使用示例

```text
使用 $top-journal-search-lists，在中国知网高级检索数字化转型与企业创新，检索 2020 年以来期刊文献，只查看第一页，先不要下载。
```

```text
使用 $top-journal-search-lists，在中国知网专业检索 SU='气候风险' AND KY='企业创新'，返回结果后由我选择需要下载的论文。
```

```text
使用 $top-journal-search-lists 检索人工智能对审计质量影响的中英文文献，并按十级期刊层级整理。
```

## 输出内容

结果包括检索范围和检索式、研究结论、十级论文目录、论文元数据和期刊层级，以及去重口径、空层级、未覆盖范围和缺失字段。摘要不足时只报告可核实信息，不依据题名推测结论。

## 常见问题

### 客户端未识别 Skill

检查最终路径是否为 `<Skills目录>/top-journal-search-lists/SKILL.md`，重新启动客户端或刷新任务。避免形成两层同名目录。

### ai4scholar 不可用

先确认 MCP 已注册并完成一次实际查询。Skill 会报告工具错误，不以普通网络搜索冒充 ai4scholar。

### CNKI 状态一直是 login_required

调用 `cnki_login`，在可见浏览器中完成 WebVPN 登录，再调用 `cnki_status`。若关闭过浏览器，需要重新登录。

### 出现验证码或访问频率提示

当前操作会立即停止。请手工完成验证或稍后再试，不要连续调用工具。若页面返回 403、429 或权限不足，先确认学校授权范围和 WebVPN 状态。

### 是否自动下载论文

不会。只有用户明确选择论文编号并指定保存目录后，才会下载最多 5 篇。

### 综合目录缺失或异常

确认 `references/Academic_Journal_Master_Directory_20260715.md` 未被移动或删除。目录校验失败时停止期刊层级判定。
