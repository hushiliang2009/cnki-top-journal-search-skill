# 学术期刊综合目录与文献检索优先级（2026年7月15日）

> 本目录整合五份期刊目录，供后续文献检索 Skill 调用 ai4scholar MCP 时确定检索范围和结果排序。目录保留各来源中的完整期刊记录与学科归属；同一期刊可能出现在多个来源或多个学科中，不在目录层面删除重复记录。

## 一、检索顺序

1. 经济学 Top 5 期刊
2. NCS_PNAS_Directory 期刊
3. UTD24 期刊
4. FT50 期刊
5. Field Top 期刊
6. 中文顶尖期刊目录
7. Top 目录中的其他顶尖期刊
8. SSCI 期刊
9. CSSCI 期刊
10. SCIE 期刊

### 经济学 Top 5 期刊

1. American Economic Review
2. Econometrica
3. Journal of Political Economy
4. Quarterly Journal of Economics
5. Review of Economic Studies

### NCS_PNAS_Directory 内部顺序

1. 人文、哲学与社会科学（含交叉研究）期刊
2. NCS 与 PNAS 目录中的其他期刊

其中，人文、哲学与社会科学（含交叉研究）期刊是 NCS_PNAS_Directory 内部的最高优先级。若同一期刊同时属于其他目录，仍按照上述十级检索顺序确定其最终优先级。

## 二、排序与去重规则

1. 文献搜索应覆盖与主题相关的全部层级，检索顺序用于安排查询先后和结果排序，不表示跳过后续层级。
2. 同一期刊同时属于多个目录或多个层级时，以其最高检索层级为准。
3. 同一篇文献被多次检出时，应依据 DOI 优先去重；无 DOI 时，可结合规范化题名、作者和年份去重。
4. 期刊名称匹配应忽略大小写及首尾空格，并兼容常用缩写；输出时使用目录中的规范期刊名称。
5. 结果整理时应保留检索层级、期刊名称、来源目录和学科分类，便于复核。

## 三、机器可读检索配置

```yaml
catalog_version: "2026-07-15"
search_backend: "ai4scholar_mcp"
search_scope: "comprehensive"
priority:
  - level: 1
    group: "economics_top5"
    source: "Top_Academic_Journals_all.md"
  - level: 2
    group: "ncs_pnas"
    source: "NCS_PNAS_Directory.md"
    internal_order:
      - rank: 1
        group: "humanities_philosophy_social_sciences_interdisciplinary"
      - rank: 2
        group: "other_ncs_pnas_journals"
  - level: 3
    group: "utd24"
    source: "Top_Academic_Journals_all.md"
  - level: 4
    group: "ft50"
    source: "Top_Academic_Journals_all.md"
  - level: 5
    group: "field_top"
    source: "Top_Academic_Journals_all.md"
  - level: 6
    group: "chinese_top_journals"
    source: "Top_Academic_Journals_all.md"
  - level: 7
    group: "other_top_journals"
    source: "Top_Academic_Journals_all.md"
  - level: 8
    group: "ssci"
    source: "Social Sciences Citation Index_20260715.md"
  - level: 9
    group: "cssci"
    source: "CSSCI_2025_2026.md"
  - level: 10
    group: "scie"
    source: "Science Citation Index Expanded_20260715.md"
deduplication:
  journal_policy: "highest_priority_wins"
  article_keys:
    - "doi"
    - "normalized_title+authors+year"
output_fields:
  - "priority_level"
  - "priority_group"
  - "journal_title"
  - "source_catalog"
  - "subject_category"
```

## 四、来源概览

| 检索层级 | 来源目录 | 覆盖范围 | 目录规模 |
|---:|---|---|---:|
| 1、3—7 | `Top_Academic_Journals_all.md` | 经济学 Top 5、UTD24、FT50、Field Top、中文及其他顶尖期刊 | 以来源目录为准 |
| 2 | `NCS_PNAS_Directory.md` | 置顶人文社科交叉期刊，以及 Nature、Cell、Science、PNAS 系列期刊 | 以来源目录为准 |
| 8 | `Social Sciences Citation Index_20260715.md` | SSCI 期刊 | 3,538 种，58 个学科类别 |
| 9 | `CSSCI_2025_2026.md` | CSSCI 2025—2026 来源期刊 | 674 种，26 个学科 |
| 10 | `Science Citation Index Expanded_20260715.md` | SCIE 期刊 | 9,430 种，178 个学科类别 |

## 五、完整期刊目录

## 第一检索层级：经济学 Top 5 期刊

1. American Economic Review
2. Econometrica
3. Journal of Political Economy
4. Quarterly Journal of Economics
5. Review of Economic Studies

## 第二检索层级：NCS 与 PNAS 期刊

<!-- SOURCE_BEGIN: NCS_PNAS_Directory.md -->

> **核心说明**：本目录已全面核对并补全。发表过人文、哲学与社会科学（含交叉学科）研究的期刊已被特别提取并置顶。对于涉及经济学、管理学、公共政策、社会学、心理学与数据科学的学者，置顶板块是核心的关注与投稿阵地。

---

### 🌟 置顶板块：人文、哲学与社会科学（含交叉研究）期刊

*以下期刊要么是纯人文社科期刊，要么在常规接收范围内大量发表经济、社会、管理、政策、心理及人类行为方向的实证与交叉研究：*

#### 1. 综合顶刊（含庞大的社科专栏）
* **PNAS (美国科学院院刊)**：极具代表性，其下设极其庞大的 "Social Sciences"（社会科学）专栏，是全球经济学、政治学、人类学、社会学、心理学实证研究的顶级发表阵地。
* **Science** 与 **Nature** (主刊)：两者均常态化发表具有全球影响力的经济学、气候政策、科技政策、人类学等重磅社科论文。
* **Science Advances** (AAAS)：Science 旗下核心 OA 子刊，设有明确且活跃的 "Social and Interdisciplinary Sciences"（社会与交叉科学）板块。
* **PNAS Nexus**：PNAS 开放获取子刊，强力支持涵盖社会科学在内的跨学科与交叉研究。

#### 2. Nature 旗下社科与交叉重磅子刊
* **Nature Human Behaviour** (自然-人类行为)：Nature 旗下最纯正的社会科学顶刊，专注心理学、经济学、社会学、政治学和人类学实证研究。
* **Nature Cities** (自然-城市)：侧重城市科学、城市规划、城市经济学与社会动态。
* **五大政策与环境交叉子刊**：**Nature Climate Change**, **Nature Energy**, **Nature Sustainability**, **Nature Food**, **Nature Water**。这五本期刊高度侧重政策评估、经济分析、人类行为与自然环境的交叉。
* **Humanities and Social Sciences Communications**：Nature 旗下专注于纯人文与社会科学的权威 OA 期刊（前身为 Palgrave Communications）。
* **Nature Reviews Psychology**：专注心理学及行为科学前沿理论的权威综述。
* **Communications Psychology**：Nature 旗下心理学与行为科学期刊。
* **Scientific Data**：极为重视且常发表经济学、社会学、人口学及管理科学的高价值宏微观数据集。
* **部分 npj 系列（合作期刊）**：
  * npj Science of Learning (教育学与心理学交叉)
  * npj Urban Sustainability (城市规划与可持续政策)
  * npj Mental Health Research (心理学与精神卫生)

#### 3. Cell 旗下社科与交叉重点期刊
* **Trends in Cognitive Sciences**：认知科学领域的殿堂级综述，高度交叉心理学、语言学、哲学与人工智能。
* **One Earth**：重点关注环境经济学、社会正义与可持续发展政策。
* **Patterns**：数据科学大刊，常发表计算社会科学、信息资源管理和管理科学中的大数据应用实证。

---

### 第一部分：Nature (自然) 及其全系子刊目录 (Nature Portfolio)

*由 Springer Nature 出版，拥有最庞大的子刊家族。*

#### 1. 顶级主刊
* Nature (创刊于1869年)

#### 2. 生命科学与临床医学类研究子刊 (Research Journals)
* Nature Medicine (医学)
* Nature Biotechnology (生物技术)
* Nature Genetics (遗传学)
* Nature Immunology (免疫学)
* Nature Neuroscience (神经科学)
* Nature Cell Biology (细胞生物学)
* Nature Structural & Molecular Biology (结构与分子生物学)
* Nature Metabolism (代谢)
* Nature Microbiology (微生物学)
* Nature Aging (衰老)
* Nature Cancer (癌症)
* Nature Cardiovascular Research (心血管研究)
* Nature Mental Health (心理健康)
* Nature Biomedical Engineering (生物医学工程)
* Nature Methods (方法学)
* Nature Plants (植物学)
* Nature Health (健康与医疗保障，2026年新刊)

#### 3. 物质科学、计算与地球环境类研究子刊
* Nature Materials (材料学)
* Nature Nanotechnology (纳米技术)
* Nature Photonics (光子学)
* Nature Physics (物理学)
* Nature Chemistry (化学)
* Nature Chemical Engineering (化学工程)
* Nature Catalysis (催化)
* Nature Electronics (电子学)
* Nature Synthesis (合成)
* Nature Geoscience (地球科学)
* Nature Ecology & Evolution (生态学与进化)
* Nature Astronomy (天文学)
* Nature Machine Intelligence (机器智能)
* Nature Computational Science (计算科学)
* Nature Sensors (传感器交叉，2026年新刊)

#### 4. 综述类子刊 (Nature Reviews 系列)
* Nature Reviews Cancer
* Nature Reviews Cardiology
* Nature Reviews Chemistry
* Nature Reviews Clinical Oncology
* Nature Reviews Disease Primers
* Nature Reviews Drug Discovery
* Nature Reviews Earth & Environment
* Nature Reviews Electrical Engineering
* Nature Reviews Endocrinology
* Nature Reviews Gastroenterology & Hepatology
* Nature Reviews Genetics
* Nature Reviews Immunology
* Nature Reviews Materials
* Nature Reviews Methods Primers
* Nature Reviews Microbiology
* Nature Reviews Molecular Cell Biology
* Nature Reviews Nephrology
* Nature Reviews Neurology
* Nature Reviews Neuroscience
* Nature Reviews Physics
* Nature Reviews Rheumatology
* Nature Reviews Urology

#### 5. 综合及开放获取 (Open Access 矩阵)
* Nature Communications (综合性高质量OA巨头)
* Scientific Reports (综合性巨型OA期刊)
* **Communications Biology**
* **Communications Chemistry**
* **Communications Earth & Environment**
* **Communications Engineering**
* **Communications Materials**
* **Communications Medicine**
* **Communications Physics**

---

### 第二部分：Cell (细胞) 及其全系子刊目录 (Cell Press)

*由 Elsevier 出版，生命科学领域的绝对霸主，正向物质科学与数据科学强力扩张。*

#### 1. 顶级主刊
* Cell 

#### 2. 生命科学及医学核心子刊
* Cancer Cell (癌症细胞)
* Immunity (免疫)
* Neuron (神经元)
* Cell Metabolism (细胞代谢)
* Cell Stem Cell (细胞干细胞)
* Molecular Cell (分子细胞)
* Developmental Cell (发育细胞)
* Cell Host & Microbe (细胞宿主与微生物)
* Current Biology (现代生物学综合)
* Structure (结构生物学)
* Med (临床与转化医学)
* American Journal of Human Genetics (人类遗传学，合作出版)
* Biophysical Journal (生物物理学，合作出版)

#### 3. 物质科学及交叉学科子刊
* Chem (化学)
* Joule (能源)
* Matter (材料)
* Device (仪器与设备)
* Chem Catalysis (化学催化)

#### 4. 开放获取及综合类子刊 (Cell Reports 矩阵)
* Cell Reports (生命科学OA)
* Cell Reports Medicine (医学OA)
* Cell Reports Physical Science (物质科学OA)
* Cell Reports Sustainability (可持续性OA)
* Cell Reports Methods (方法学)
* iScience (跨学科综合OA)
* Cell Genomics (基因组学)
* Cell Systems (系统生物学)
* STAR Protocols (实验方法与方案)
* Heliyon (综合性全学科巨型OA期刊)

#### 5. Trends 综述系列期刊 (殿堂级生命科学综述)
* Trends in Biochemical Sciences
* Trends in Biotechnology
* Trends in Cancer
* Trends in Cell Biology
* Trends in Chemistry
* Trends in Ecology & Evolution
* Trends in Endocrinology & Metabolism
* Trends in Genetics
* Trends in Immunology
* Trends in Microbiology
* Trends in Molecular Medicine
* Trends in Neurosciences
* Trends in Parasitology
* Trends in Pharmacological Sciences
* Trends in Plant Science

---

### 第三部分：Science (科学) 及其子刊目录 (AAAS)

*由美国科学促进会 (AAAS) 出版，采取“极少而精”的严苛子刊策略。*

#### 1. 顶级主刊
* Science

#### 2. 核心直系子刊
* Science Translational Medicine (转化医学)
* Science Signaling (细胞信号传导)
* Science Immunology (免疫学)
* Science Robotics (机器人学)

#### 3. 合作期刊 (Science Partner Journals, SPJ)
* Research (与中国科协合作，综合性巨头)
* Plant Phenomics (植物表型组学)
* BME Frontiers (生物医学工程前沿)
* Energy Material Advances (能源材料前沿)
*(注：SPJ 旗下还有数本细分合作期刊，此处仅列代表性顶刊)*

---

### 第四部分：PNAS 及其子刊目录

*由美国国家科学院 (NAS) 出版，被引用次数最多的综合学科文献库。*

#### 1. 顶级主刊
* PNAS (Proceedings of the National Academy of Sciences)

#### 2. 核心子刊
* PNAS Nexus (开放获取综合性子刊，专注极高评价或交叉学科的前沿研究)

<!-- SOURCE_END: NCS_PNAS_Directory.md -->

## 第三至第七检索层级：Top 目录期刊

<!-- SOURCE_BEGIN: Top_Academic_Journals_all.md -->

### 一、 中文顶尖期刊目录
* 管理世界
* 南开管理评论
* 中国软科学
* 经济研究
* 世界经济
* 经济学(季刊)
* 中国工业经济
* 数量经济技术经济研究
* 金融研究
* 会计研究
* 中国社会科学
* 管理科学学报
* 统计研究

---

### 二、 英文综合顶尖期刊目录 (General Top Journals)

#### 1. UTD24 期刊目录 (The UTD Top 24 Business School Research Journals)

**会计学 (Accounting - 3本)**
* The Accounting Review (TAR)
* Journal of Accounting and Economics (JAE)
* Journal of Accounting Research (JAR)

**金融学 (Finance - 3本)**
* The Journal of Finance (JF)
* Journal of Financial Economics (JFE)
* The Review of Financial Studies (RFS)

**信息系统 (Information Systems - 3本)**
* Information Systems Research (ISR)
* INFORMS Journal on Computing (IJOC)
* MIS Quarterly (MISQ)

**市场营销 (Marketing - 4本)**
* Journal of Consumer Research (JCR)
* Journal of Marketing (JM)
* Journal of Marketing Research (JMR)
* Marketing Science (MKS)

**管理科学与运营管理 (MS & OM - 5本)**
* Management Science (MS)
* Operations Research (OR)
* Journal of Operations Management (JOM)
* Manufacturing & Service Operations Management (M&SOM)
* Production and Operations Management (POM)

**综合管理与战略 (General Management - 6本)**
* Academy of Management Journal (AMJ)
* Academy of Management Review (AMR)
* Administrative Science Quarterly (ASQ)
* Organization Science (OS)
* Journal of International Business Studies (JIBS)
* Strategic Management Journal (SMJ)

---

#### 2. 最新 FT50 期刊目录 (Financial Times Top 50 Journals)

**综合管理、战略与创新创业 (15本)**
* Academy of Management Annals 
* Academy of Management Journal
* Academy of Management Review
* Administrative Science Quarterly
* Entrepreneurship Theory and Practice
* Harvard Business Review
* Journal of Business Venturing
* Journal of International Business Studies
* Journal of Management
* Journal of Management Studies
* MIT Sloan Management Review
* Organization Science
* Research Policy
* Strategic Entrepreneurship Journal
* Strategic Management Journal

**会计学 (Accounting - 6本)**
* Accounting, Organizations and Society
* Contemporary Accounting Research
* Journal of Accounting and Economics
* Journal of Accounting Research
* Review of Accounting Studies
* The Accounting Review

**金融学 (Finance - 5本)**
* Journal of Finance
* Journal of Financial and Quantitative Analysis (JFQA)
* Journal of Financial Economics
* Review of Finance
* Review of Financial Studies

**经济学 (Economics - 5本)**
* American Economic Review (AER)
* Econometrica
* Journal of Political Economy (JPE)
* Quarterly Journal of Economics (QJE)
* Review of Economic Studies (REStud)

**市场营销 (Marketing - 6本)**
* Journal of Consumer Psychology
* Journal of Consumer Research
* Journal of Marketing
* Journal of Marketing Research
* Journal of the Academy of Marketing Science (JAMS)
* Marketing Science

**信息系统与运营管理 (IS & OM - 8本)**
* Information Systems Research
* Journal of Management Information Systems (JMIS)
* MIS Quarterly
* Journal of Operations Management
* Management Science
* Manufacturing & Service Operations Management
* Operations Research
* Production and Operations Management

**组织行为、人力资源与心理/社会学 (5本)**
* American Sociological Review 
* Psychological Science 
* Human Resource Management
* Journal of Applied Psychology
* Organizational Behavior and Human Decision Processes (OBHDP)

---

### 三、 经济学各细分领域顶尖期刊（按 JEL 分类系统 / Economics Field Top Journals by JEL Codes）

> 综合顶刊（Top 5：AER、Econometrica、JPE、QJE、REStud）见第二部分 FT50，此处不再重复。以下按 AEA 官方 JEL 分类代码逐学科列出各领域公认 field top 期刊；除标注（ESCI）者外，均经 SSCI/SCIE 2025 年收录清单核验。

#### JEL A：综合经济学 (General Economics)
**Top 5 之后的综合性顶刊 (General-Interest Journals beyond Top 5)**
* Review of Economics and Statistics (REStat)
* Journal of the European Economic Association (JEEA)
* International Economic Review (IER)
* Economic Journal (EJ)
* American Economic Journal: Applied Economics (AEJ: Applied)
* American Economic Review: Insights (AER: Insights)
* Journal of Economic Literature (JEL) - 综述类旗舰
* Journal of Economic Perspectives (JEP) - 综述类旗舰

#### JEL B：经济思想史与方法论 (History of Economic Thought, Methodology, and Heterodox Approaches)
* Cambridge Journal of Economics (CJE) - 非主流经济学旗舰
* History of Political Economy (HOPE)
* Journal of the History of Economic Thought (JHET)
* European Journal of the History of Economic Thought (EJHET)
* Journal of Economic Methodology (JEM)

#### JEL C：数理与数量方法 (Mathematical and Quantitative Methods)
**C1–C5 计量经济学 (Econometrics)**
* Journal of Econometrics (JoE)
* Quantitative Economics (QE)
* Econometric Theory (ET)
* Journal of Business & Economic Statistics (JBES)
* Journal of Applied Econometrics (JAE)
* Econometrics Journal (EctJ)
* Econometric Reviews (ER)

**C7 博弈论 (Game Theory and Bargaining Theory)**
* Games and Economic Behavior (GEB)
* International Journal of Game Theory (IJGT)

**C9 实验经济学 (Design of Experiments)**
* Experimental Economics (ExpEcon)

#### JEL D：微观经济学 (Microeconomics)
**微观经济理论 (Microeconomic Theory)**
* Journal of Economic Theory (JET)
* Theoretical Economics (TE)
* American Economic Journal: Microeconomics (AEJ: Micro)

**D7 集体决策与社会选择 (Analysis of Collective Decision-Making)**
* Social Choice and Welfare (SCW)

**D8 信息、知识与不确定性 (Information, Knowledge, and Uncertainty)**
* Journal of Risk and Uncertainty (JRU)

**D9 行为经济学 (Micro-Based Behavioral Economics)**
* Journal of Economic Behavior & Organization (JEBO)
* Journal of Economic Psychology (JoEP)

#### JEL E：宏观与货币经济学 (Macroeconomics and Monetary Economics)
* Journal of Monetary Economics (JME)
* American Economic Journal: Macroeconomics (AEJ: Macro)
* Review of Economic Dynamics (RED)
* Journal of Money, Credit and Banking (JMCB)
* Journal of Economic Dynamics and Control (JEDC)

#### JEL F：国际经济学 (International Economics)
* Journal of International Economics (JIE) - 领域旗舰
* IMF Economic Review (IMFER)
* Journal of International Money and Finance (JIMF) - 国际金融
* World Economy (WE)
* Review of International Economics (RIE)
* World Trade Review (WTR) - 国际贸易政策

#### JEL G：金融经济学 (Financial Economics)
> 领域综合顶刊（JF、JFE、RFS、RF、JFQA）见第二部分 UTD24/FT50；G22 保险类期刊见第四部分"风险管理与保险"。

**G1 金融市场与资产定价 (General Financial Markets & Asset Pricing)**
* Journal of Financial Markets (JFM) - 市场微观结构
* Review of Asset Pricing Studies (RAPS)（ESCI）
* Journal of Empirical Finance (JEF) - 实证金融
* Journal of Financial Econometrics (JFEC) - 金融计量
* Mathematical Finance (MF) - 数理金融

**G2 金融机构与服务 (Financial Institutions and Services)**
* Journal of Financial Intermediation (JFI)
* Journal of Banking & Finance (JBF)
* Journal of Financial Stability (JFS)

**G3 公司金融与公司治理 (Corporate Finance and Governance)**
* Journal of Corporate Finance (JCF)
* Review of Corporate Finance Studies (RCFS)（ESCI）
* Financial Management (FM)

#### JEL H：公共经济学 (Public Economics)
**公共财政与税收 (Public Finance & Taxation)**
* Journal of Public Economics (JPubE)
* American Economic Journal: Economic Policy (AEJ: Policy)
* International Tax and Public Finance (ITAX)
* National Tax Journal (NTJ)

**H1/D72 公共选择与政治经济学 (Public Choice & Political Economy)**
* Public Choice
* European Journal of Political Economy (EJPE)

#### JEL I：健康、教育与福利经济学 (Health, Education, and Welfare)
**I1 健康经济学 (Health)**
* Journal of Health Economics (JHE)
* Health Economics (HE)
* American Journal of Health Economics (AJHE)

**I2 教育经济学 (Education and Research Institutions)**
* Economics of Education Review (EER)
* Education Finance and Policy (EFP)
* Journal of Human Capital (JHC)

**I3 福利、贫困与不平等 (Welfare, Well-Being, and Poverty)**
* Journal of Economic Inequality (JEI)
* Review of Income and Wealth (RIW)

#### JEL J：劳动与人口经济学 (Labor and Demographic Economics)
* Journal of Labor Economics (JOLE)
* Journal of Human Resources (JHR)
* Labour Economics - 欧洲劳动经济学会会刊
* ILR Review - 劳动关系旗舰
* Journal of Population Economics (JPopE) - 人口经济学
* Demography - 人口学旗舰

#### JEL K：法律与经济学 (Law and Economics)
* Journal of Law and Economics (JLE)
* Journal of Law, Economics, and Organization (JLEO)
* Journal of Legal Studies (JLS)
* American Law and Economics Review (ALER)
* Journal of Empirical Legal Studies (JELS) - 实证法律研究
* International Review of Law and Economics (IRLE)

#### JEL L：产业组织 (Industrial Organization)
* RAND Journal of Economics (RAND)
* Journal of Industrial Economics (JIndE)
* International Journal of Industrial Organization (IJIO)
* Journal of Economics & Management Strategy (JEMS)
* Review of Industrial Organization (RIO)

#### JEL M：工商管理与商业经济学 (Business Administration and Business Economics; Marketing; Accounting; Personnel Economics)
> 工商管理（M1）、市场营销（M31/M37）、会计与审计（M41/M42）、人事经济学（M5）等各学科顶刊详见**第四部分**。

#### JEL N：经济史 (Economic History)
* Journal of Economic History (JEH)
* Economic History Review (EHR)
* Explorations in Economic History (EEH)
* European Review of Economic History (EREH)
* Cliometrica - 计量经济史

#### JEL O：经济发展、创新、技术变迁与增长 (Economic Development, Innovation, Technological Change, and Growth)
**O1 发展经济学 (Economic Development)**
* Journal of Development Economics (JDE)
* World Development (WD)
* World Bank Economic Review (WBER)
* Economic Development and Cultural Change (EDCC)

**O3 创新与技术变迁经济学 (Innovation • Research and Development • Technological Change)**
* Industrial and Corporate Change (ICC)
* Economics of Innovation and New Technology (EINT)
* （创新管理类顶刊 Research Policy、JPIM 等见第四部分"创新与技术管理"）

**O4 经济增长 (Economic Growth and Aggregate Productivity)**
* Journal of Economic Growth (JEG) - 增长领域旗舰

#### JEL P：政治经济学与比较经济体制 (Political Economy and Comparative Economic Systems)
* Journal of Comparative Economics (JCE) - 比较经济学旗舰
* Economics of Transition and Institutional Change - 转型经济学
* China Economic Review (CER) - 中国经济研究旗舰
* Journal of Institutional Economics (JOIE) - 制度经济学

#### JEL Q：农业与自然资源经济学、环境与生态经济学 (Agricultural and Natural Resource Economics; Environmental and Ecological Economics)
**Q1 农业经济学 (Agriculture)**
* American Journal of Agricultural Economics (AJAE)
* Food Policy
* European Review of Agricultural Economics (ERAE)
* Agricultural Economics

**Q2/Q3 资源经济学 (Renewable and Exhaustible Resources)**
* Land Economics
* Resource and Energy Economics (REE)

**Q4 能源经济学 (Energy)**
* Energy Economics (EE)
* Energy Journal (EJ)
* Energy Policy (EP)

**Q5 环境与生态经济学 (Environmental and Ecological Economics)**
* Journal of Environmental Economics and Management (JEEM)
* Journal of the Association of Environmental and Resource Economists (JAERE)
* Environmental and Resource Economics (ERE)
* Review of Environmental Economics and Policy (REEP) - 政策综述旗舰
* Ecological Economics - 生态经济学旗舰

#### JEL R：城市、农村、区域、房地产与交通经济学 (Urban, Rural, Regional, Real Estate, and Transportation Economics)
**R1 城市与区域经济学 (Urban & Regional Economics)**
* Journal of Urban Economics (JUE)
* Regional Science and Urban Economics (RSUE)
* Journal of Economic Geography (JEcG) - 经济地理学
* Economic Geography (EG) - 经济地理学
* Journal of Regional Science (JRS)
* Regional Studies
* Papers in Regional Science (PiRS)

**R2/R3 房地产与住房经济学 (Real Estate & Housing Markets)**
* Real Estate Economics (REE)
* Journal of Real Estate Finance and Economics (JREFE)
* Journal of Housing Economics

**R4 交通经济学 (Transportation Economics)**
* Transportation Research Part B: Methodological (TR-B)
* Transportation Research Part A: Policy and Practice (TR-A)
* Journal of Transport Economics and Policy (JTEP)
* Economics of Transportation

#### JEL Z：其他专题 (Other Special Topics)
* Journal of Cultural Economics - Z1 文化经济学
* Journal of Sports Economics - Z2 体育经济学
* Tourism Economics - Z3 旅游经济学（旅游管理类见第四部分）

---

### 四、 管理学与商学各细分领域顶尖期刊 (Management & Business Field Top Journals)

> 综合顶刊（AMJ、AMR、ASQ、Organization Science、Management Science 等）见第二部分 UTD24/FT50，此处不再重复（v3 已列出者保留）。各节标题标注对应 JEL 分类代码。

#### 1. 综合管理 (General Management) [JEL: M10]
* British Journal of Management (BJM)
* Journal of Business Research (JBR)
* California Management Review (CMR) - 实践导向
* Management and Organization Review (MOR) - 中国与新兴市场管理研究
* Asia Pacific Journal of Management (APJM)

#### 2. 战略管理 (Strategic Management) [JEL: L10/M10]
* Strategic Management Journal (SMJ)
* Global Strategy Journal (GSJ)
* Strategy Science（ESCI）
* Strategic Organization (SO)
* Long Range Planning (LRP)

#### 3. 组织行为与组织研究 (Organizational Behavior & Organization Studies) [JEL: M12/D23]
* Journal of Applied Psychology (JAP)
* Organizational Behavior and Human Decision Processes (OBHDP)
* Journal of Organizational Behavior (JOB)
* Organization Studies
* Human Relations
* Leadership Quarterly (LQ)
* Organizational Research Methods (ORM) - 组织研究方法旗舰
* Journal of Vocational Behavior (JVB)

#### 4. 人力资源管理 (Human Resource Management) [JEL: M50/M12/J50]
* Personnel Psychology (PPsych)
* Human Resource Management (HRM)
* Human Resource Management Journal (HRMJ)
* International Journal of Human Resource Management (IJHRM)
* （劳动关系类 ILR Review 见第三部分 JEL J）

#### 5. 国际商务 (International Business) [JEL: F23/M16]
* Journal of International Business Studies (JIBS)
* Journal of World Business (JWB)
* Management International Review (MIR)
* International Business Review (IBR)
* Journal of International Management (JIM)

#### 6. 创新与技术管理 (Innovation & Technology Management) [JEL: O31/O32]
* Research Policy (RP)
* Journal of Product Innovation Management (JPIM)
* Technovation
* Technological Forecasting and Social Change (TFSC)
* R&D Management (RDM)
* Industry and Innovation (I&I)
* Journal of Technology Transfer (JTT)
* IEEE Transactions on Engineering Management (IEEE TEM)
* （创新经济学类 ICC、EINT 见第三部分 JEL O3）

#### 7. 创业管理 (Entrepreneurship) [JEL: L26/M13]
* Journal of Business Venturing (JBV)
* Entrepreneurship Theory and Practice (ETP)
* Strategic Entrepreneurship Journal (SEJ)
* Small Business Economics (SBE)
* Journal of Small Business Management (JSBM)
* International Small Business Journal (ISBJ)
* Family Business Review (FBR) - 家族企业研究

#### 8. 运营与供应链管理 (Operations & Supply Chain Management) [JEL: M11/L23]
**运筹学与管理科学 (Operations Research & Management Science)**
* European Journal of Operational Research (EJOR)
* Omega - 国际管理科学期刊
* Decision Sciences (DS)
* IISE Transactions - 工业工程旗舰
* Transportation Science (TS)

**生产、物流与供应链 (Production, Logistics & Supply Chain)**
* Journal of Supply Chain Management (JSCM)
* International Journal of Operations & Production Management (IJOPM)
* International Journal of Production Economics (IJPE)
* International Journal of Production Research (IJPR)
* Journal of Business Logistics (JBL)
* Supply Chain Management: An International Journal (SCMIJ)
* Transportation Research Part E: Logistics and Transportation Review (TR-E)

#### 9. 信息系统 (Information Systems) [JEL: M15/L86/O33]
> AIS 高级学者名刊清单（Senior Scholars' List，"Basket of 11"）中的 MISQ、ISR、JMIS 见第二部分 UTD24/FT50，其余 8 本如下。
* Journal of the Association for Information Systems (JAIS)
* European Journal of Information Systems (EJIS)
* Information Systems Journal (ISJ)
* Journal of Information Technology (JIT)
* Journal of Strategic Information Systems (JSIS)
* Decision Support Systems (DSS)
* Information & Management (I&M)
* Information and Organization (I&O)

#### 10. 市场营销 (Marketing) [JEL: M31/M37]
* International Journal of Research in Marketing (IJRM) - 综合营销
* Journal of Retailing (JR) - 零售管理
* Journal of Service Research (JSR) - 服务营销
* Quantitative Marketing and Economics (QME) - 定量营销
* Industrial Marketing Management (IMM) - B2B 营销
* Journal of Advertising (JA) - 广告学
* Journal of International Marketing - 国际营销
* Journal of Interactive Marketing - 数字与互动营销
* Marketing Letters (ML)

#### 11. 会计学 (Accounting) [JEL: M41/M42/M48]
* Auditing: A Journal of Practice & Theory (AJPT) - 审计学
* Journal of Management Accounting Research (JMAR) - 管理会计（ESCI）
* Management Accounting Research (MAR) - 管理会计（欧洲系旗舰）
* The Journal of the American Taxation Association (JATA) - 税务会计（ESCI）
* Journal of Information Systems (JIS) - 会计信息系统
* European Accounting Review (EAR) - 欧洲会计学会会刊
* Journal of Business Finance & Accounting (JBFA)
* Accounting Horizons - AAA 实务导向期刊
* British Accounting Review (BAR)
* Accounting and Business Research (ABR)
* Journal of Accounting and Public Policy (JAPP)

#### 12. 金融学 (Finance) [JEL: G]
> 金融经济学各细分领域顶刊（资产定价、金融机构、公司金融等）已按 JEL 体系整合至**第三部分 JEL G**；综合顶刊 JF、JFE、RFS、RF、JFQA 见第二部分 UTD24/FT50。

#### 13. 公共管理与公共政策 (Public Administration & Public Policy) [JEL: H83/D73]
**公共管理 (Public Administration)**
* Public Administration Review (PAR)
* Journal of Public Administration Research and Theory (JPART)
* Public Management Review (PMR)
* Public Administration - 英国系旗舰
* Governance

**公共政策 (Public Policy)**
* Journal of Policy Analysis and Management (JPAM) - 政策分析旗舰
* Policy Studies Journal (PSJ)
* Regulation & Governance (R&G)

#### 14. 商业伦理、社会责任与公司治理 (Business Ethics, CSR & Governance) [JEL: M14/G34]
* Journal of Business Ethics (JBE)
* Business Ethics Quarterly (BEQ)
* Business & Society (B&S)
* Business Strategy and the Environment (BSE) - ESG 与环境战略
* Corporate Governance: An International Review (CGIR)

#### 15. 旅游与酒店管理 (Hospitality & Tourism Management) [JEL: Z31/Z32/L83]
* Tourism Management (TM)
* Annals of Tourism Research (ATR)
* Journal of Travel Research (JTR)
* Journal of Sustainable Tourism (JOST)
* International Journal of Hospitality Management (IJHM)
* Cornell Hospitality Quarterly (CHQ)

#### 16. 项目管理 (Project Management) [JEL: O22/M11]
* International Journal of Project Management (IJPM)
* Project Management Journal (PMJ)

#### 17. 风险管理与保险 (Risk Management & Insurance) [JEL: G22/D81]
* Journal of Risk and Insurance (JRI)
* Insurance: Mathematics and Economics (IME)
* Geneva Papers on Risk and Insurance: Issues and Practice (GPRI)

#### 18. 知识管理 (Knowledge Management) [JEL: O34/D83]
* Journal of Knowledge Management (JKM)

<!-- SOURCE_END: Top_Academic_Journals_all.md -->

## 第八检索层级：SSCI 期刊

<!-- SOURCE_BEGIN: Social Sciences Citation Index_20260715.md -->

> 数据来源：`Social Sciences Citation Index (SSCI).csv`。期刊按 Web of Science 学科分类整理；同一期刊如属于多个学科，将分别列入相应类别。期刊题名优先依据 ISSN 对应的出版商元数据校正，未匹配部分按标题式规则处理；缩写与正式专名保留规范形式。

- 期刊总数：3,538
- 学科类别：58
- 未分类期刊：2

### SSCI 来源内目录

- [Anthropology](#ssci-anthropology) (92)
- [Area Studies](#ssci-area-studies) (86)
- [Business](#ssci-business) (155)
- [Business, Finance](#ssci-business-finance) (112)
- [Communication](#ssci-communication) (93)
- [Criminology & Penology](#ssci-criminology-penology) (70)
- [Cultural Studies](#ssci-cultural-studies) (44)
- [Demography](#ssci-demography) (29)
- [Development Studies](#ssci-development-studies) (42)
- [Economics](#ssci-economics) (379)
- [Education & Educational Research](#ssci-education-educational-research) (270)
- [Education, Special](#ssci-education-special) (43)
- [Environmental Studies](#ssci-environmental-studies) (129)
- [Ergonomics](#ssci-ergonomics) (15)
- [Ethics](#ssci-ethics) (55)
- [Ethnic Studies](#ssci-ethnic-studies) (20)
- [Family Studies](#ssci-family-studies) (46)
- [Geography](#ssci-geography) (87)
- [Gerontology](#ssci-gerontology) (38)
- [Green & Sustainable Science & Technology](#ssci-green-sustainable-science-technology) (10)
- [Health Policy & Services](#ssci-health-policy-services) (87)
- [History](#ssci-history) (104)
- [History & Philosophy of Science](#ssci-history-philosophy-of-science) (47)
- [History of Social Sciences](#ssci-history-of-social-sciences) (34)
- [Hospitality, Leisure, Sport & Tourism](#ssci-hospitality-leisure-sport-tourism) (58)
- [Industrial Relations & Labor](#ssci-industrial-relations-labor) (32)
- [Information Science & Library Science](#ssci-information-science-library-science) (80)
- [International Relations](#ssci-international-relations) (97)
- [Law](#ssci-law) (156)
- [Linguistics](#ssci-linguistics) (195)
- [Management](#ssci-management) (231)
- [Nursing](#ssci-nursing) (123)
- [Political Science](#ssci-political-science) (188)
- [Psychiatry](#ssci-psychiatry) (144)
- [Psychology, Applied](#ssci-psychology-applied) (84)
- [Psychology, Biological](#ssci-psychology-biological) (14)
- [Psychology, Clinical](#ssci-psychology-clinical) (130)
- [Psychology, Development](#ssci-psychology-development) (77)
- [Psychology, Educational](#ssci-psychology-educational) (60)
- [Psychology, Experimental](#ssci-psychology-experimental) (89)
- [Psychology, Mathematical](#ssci-psychology-mathematical) (13)
- [Psychology, Multidisciplinary](#ssci-psychology-multidisciplinary) (147)
- [Psychology, Psychoanalysis](#ssci-psychology-psychoanalysis) (14)
- [Psychology, Social](#ssci-psychology-social) (63)
- [Public Administration](#ssci-public-administration) (48)
- [Public, Environmental & Occupational Health](#ssci-public-environmental-occupational-health) (178)
- [Regional & Urban Planning](#ssci-regional-urban-planning) (41)
- [Rehabilitation](#ssci-rehabilitation) (74)
- [Social Issues](#ssci-social-issues) (43)
- [Social Sciences, Biomedical](#ssci-social-sciences-biomedical) (45)
- [Social Sciences, Interdisciplinary](#ssci-social-sciences-interdisciplinary) (108)
- [Social Sciences, Mathematical Methods](#ssci-social-sciences-mathematical-methods) (54)
- [Social Work](#ssci-social-work) (44)
- [Sociology](#ssci-sociology) (149)
- [Substance Abuse](#ssci-substance-abuse) (38)
- [Transportation](#ssci-transportation) (38)
- [Urban Studies](#ssci-urban-studies) (45)
- [Women's Studies](#ssci-womens-studies) (46)
- [Unclassified](#ssci-unclassified) (2)

<a id="ssci-anthropology"></a>

### Anthropology

期刊数：92

1. Africa
2. African Archaeological Review
3. AIBR-Revista de Antropologia Iberoamericana
4. American Anthropologist
5. American Antiquity
6. American Ethnologist
7. American Journal of Biological Anthropology
8. American Journal of Human Biology
9. Annals of Human Biology
10. Annual Review of Anthropology
11. Anthropological Forum
12. Anthropological Notebooks
13. Anthropological Quarterly
14. Anthropological Theory
15. Anthropologie
16. Anthropologischer Anzeiger
17. Anthropology & Education Quarterly
18. Anthropology & Medicine
19. Anthropology Southern Africa
20. Anthropos
21. Anthropozoologica
22. Antiquity
23. Archaeological and Anthropological Sciences
24. Archaeology in Oceania
25. Arctic Anthropology
26. Asia Pacific Journal of Anthropology
27. Australian Archaeology
28. Australian Journal of Anthropology
29. Bijdragen tot de Taal- Land- en Volkenkunde
30. Chungara-Revista de Antropologia Chilena
31. Comparative Studies in Society and History
32. Critique of Anthropology
33. Cultural Anthropology
34. Cultural Studies
35. Culture Medicine and Psychiatry
36. Current Anthropology
37. Economic Anthropology
38. Estudios Atacamenos
39. Ethnography
40. Ethnohistory
41. Ethnos
42. Ethos
43. Evolutionary Anthropology
44. Field Methods
45. Focaal-Journal of Global and Historical Anthropology
46. Global Networks-a Journal of Transnational Affairs
47. Hau-Journal of Ethnographic Theory
48. History and Anthropology
49. Homo-Journal of Comparative Human Biology
50. Human Biology
51. Human Ecology
52. Human Nature-an Interdisciplinary Biosocial Perspective
53. Human Organization
54. Inter-Asia Cultural Studies
55. International Journal of Osteoarchaeology
56. Intersecciones en Antropologia
57. Journal of Anthropological Archaeology
58. Journal of Anthropological Research
59. Journal of Anthropological Sciences
60. Journal of Archaeological Method and Theory
61. Journal of Archaeological Research
62. Journal of Archaeological Science
63. Journal of Ethnobiology
64. Journal of Family History
65. Journal of Human Evolution
66. Journal of Latin American and Caribbean Anthropology
67. Journal of Linguistic Anthropology
68. Journal of Material Culture
69. Journal of Peasant Studies
70. Journal of Social Archaeology
71. Journal of the Polynesian Society
72. Journal of the Royal Anthropological Institute
73. Latin American Antiquity
74. Lithic Technology
75. Magallania
76. Medical Anthropology
77. Medical Anthropology Quarterly
78. Oceania
79. PoLAR-Political and Legal Anthropology Review
80. Praehistorische Zeitschrift
81. Public Culture
82. Race & Class
83. Romani Studies
84. Signs and Society
85. Social Analysis
86. Social Anthropology
87. Social Networks
88. Sociologus
89. Sociology Lens
90. Trabajos de Prehistoria
91. Transcultural Psychiatry
92. Zeitschrift fur Ethnologie - Journal of Social and Cultural Anthropology

<a id="ssci-area-studies"></a>

### Area Studies

期刊数：86

1. Africa
2. Africa Spectrum
3. African Affairs
4. African and Asian Studies
5. African Studies
6. African Studies Review
7. Asia & the Pacific Policy Studies
8. Asia Pacific Viewpoint
9. Asian Journal of Social Science
10. Asian Studies Review
11. Asian Survey
12. Bilig
13. British Journal of Middle Eastern Studies
14. Bulletin of Indonesian Economic Studies
15. Bulletin of Latin American Research
16. Central Asian Survey
17. China Information
18. China Journal
19. China Perspectives
20. China Quarterly
21. China Review-an Interdisciplinary Journal on Greater China
22. China-an International Journal
23. Contemporary Pacific
24. Contemporary South Asia
25. Contemporary Southeast Asia
26. Critical Asian Studies
27. East Asian Science Technology and Society-an International Journal
28. East European Politics
29. East European Politics and Societies
30. Economic Development and Cultural Change
31. Eurasian Geography and Economics
32. Europe-Asia Studies
33. European Review
34. European Security
35. German Studies Review
36. IDS Bulletin-Institute of Development Studies
37. India Review
38. International Journal of Middle East Studies
39. Iranian Studies
40. Israel Affairs
41. Journal of Asian and African Studies
42. Journal of Asian Public Policy
43. Journal of Asian Studies
44. Journal of Australian Studies
45. Journal of Balkan and Near Eastern Studies
46. Journal of Baltic Studies
47. Journal of Chinese Political Science
48. Journal of Contemporary Asia
49. Journal of Contemporary China
50. Journal of Contemporary European Studies
51. Journal of Current Southeast Asian Affairs
52. Journal of East Asian Studies
53. Journal of Eastern African Studies
54. Journal of Japanese Studies
55. Journal of Latin American Studies
56. Journal of Modern African Studies
57. Journal of Palestine Studies
58. Journal of Southeast Asian Studies
59. Journal of Southern African Studies
60. Korea Observer
61. Latin American Perspectives
62. Latin American Politics and Society
63. Latin American Research Review
64. London Journal
65. Mediterranean Politics
66. Middle East Critique
67. Middle East Journal
68. Middle East Policy
69. Middle Eastern Studies
70. Modern Asian Studies
71. Modern China
72. Modern Italy
73. Nationalities Papers-the Journal of Nationalism and Ethnicity
74. New Perspectives on Turkey
75. Nwig-New West Indian Guide-Nieuwe West-Indische Gids
76. Pacific Affairs
77. Pacific Focus
78. Pacific Review
79. Post-Soviet Affairs
80. Review of African Political Economy
81. Slavic Review
82. Social Dynamics-a Journal of African Studies
83. Social Science Japan Journal
84. South Asia-Journal of South Asian Studies
85. Southeast European and Black Sea Studies
86. Turkish Studies

<a id="ssci-business"></a>

### Business

期刊数：155

1. Academia-Revista Latinoamericana de Administracion
2. Academy of Management Annals
3. Academy of Management Journal
4. Academy of Management Perspectives
5. Academy of Management Review
6. Administrative Science Quarterly
7. American Business Law Journal
8. Amfiteatru Economic
9. Asia Pacific Business Review
10. Asia Pacific Journal of Marketing and Logistics
11. Asian Business & Management
12. Asian Journal of Technology Innovation
13. Australian Journal of Management
14. Betriebswirtschaftliche Forschung und Praxis
15. British Journal of Management
16. BRQ-Business Research Quarterly
17. Business & Society
18. Business Ethics Quarterly
19. Business Ethics the Environment & Responsibility
20. Business History
21. Business History Review
22. Business Horizons
23. Business Process Management Journal
24. Business Strategy and the Environment
25. California Management Review
26. Canadian Journal of Administrative Sciences-Revue Canadienne des Sciences de l Administration
27. Clothing and Textiles Research Journal
28. Competition & Change
29. Consumption Markets & Culture
30. Corporate Governance-an International Review
31. Corporate Social Responsibility and Environmental Management
32. Custos e Agronegocio on Line
33. Electronic Commerce Research
34. Electronic Commerce Research and Applications
35. Electronic Markets
36. Emerging Markets Finance and Trade
37. Engineering Economist
38. Enterprise & Society
39. Entrepreneurship and Regional Development
40. Entrepreneurship Research Journal
41. Entrepreneurship Theory and Practice
42. Eurasian Business Review
43. European Business Organization Law Review
44. European Journal of Innovation Management
45. European Journal of Marketing
46. European Management Journal
47. European Research on Management and Business Economics
48. Family Business Review
49. Gender in Management
50. Global Strategy Journal
51. Harvard Business Review
52. IEEE Transactions on Engineering Management
53. Industrial and Corporate Change
54. Industrial Marketing Management
55. Information Systems and e-Business Management
56. International Business Review
57. International Entrepreneurship and Management Journal
58. International Journal of Accounting Information Systems
59. International Journal of Advertising
60. International Journal of Bank Marketing
61. International Journal of Business Communication
62. International Journal of Consumer Studies
63. International Journal of Electronic Commerce
64. International Journal of Emerging Markets
65. International Journal of Entrepreneurial Behavior & Research
66. International Journal of Management Education
67. International Journal of Management Reviews
68. International Journal of Managing Projects in Business
69. International Journal of Market Research
70. International Journal of Research in Marketing
71. International Journal of Retail & Distribution Management
72. International Marketing Review
73. International Small Business Journal-Researching Entrepreneurship
74. Internet Research
75. Journal of Advertising
76. Journal of Advertising Research
77. Journal of Brand Management
78. Journal of Business & Industrial Marketing
79. Journal of Business and Psychology
80. Journal of Business and Technical Communication
81. Journal of Business Economics and Management
82. Journal of Business Ethics
83. Journal of Business Research
84. Journal of Business Venturing
85. Journal of Business-to-Business Marketing
86. Journal of Competitiveness
87. Journal of Consumer Affairs
88. Journal of Consumer Behaviour
89. Journal of Consumer Psychology
90. Journal of Consumer Research
91. Journal of Electronic Commerce Research
92. Journal of Engineering and Technology Management
93. Journal of Environmental Economics and Management
94. Journal of Family Business Strategy
95. Journal of Fashion Marketing and Management
96. Journal of Hospitality Marketing & Management
97. Journal of Innovation & Knowledge
98. Journal of Intellectual Capital
99. Journal of Interactive Marketing
100. Journal of International Business Studies
101. Journal of International Marketing
102. Journal of Macromarketing
103. Journal of Management
104. Journal of Management Analytics
105. Journal of Management Studies
106. Journal of Marketing
107. Journal of Marketing for Higher Education
108. Journal of Marketing Management
109. Journal of Marketing Research
110. Journal of Organizational Behavior
111. Journal of Product and Brand Management
112. Journal of Product Innovation Management
113. Journal of Productivity Analysis
114. Journal of Public Policy & Marketing
115. Journal of Research in Interactive Marketing
116. Journal of Retailing
117. Journal of Retailing and Consumer Services
118. Journal of Service Research
119. Journal of Service Theory and Practice
120. Journal of Services Marketing
121. Journal of Social Marketing
122. Journal of the Academy of Marketing Science
123. Journal of Theoretical and Applied Electronic Commerce Research
124. Journal of Vacation Marketing
125. Journal of World Business
126. Journal of World Energy Law & Business
127. Long Range Planning
128. Management Decision
129. Marketing Intelligence & Planning
130. Marketing Letters
131. Marketing Science
132. Marketing Theory
133. MIT Sloan Management Review
134. Multinational Business Review
135. Organizational Dynamics
136. Psychology & Marketing
137. Public Relations Review
138. Qme-Quantitative Marketing and Economics
139. R & d Management
140. RAE-Revista de Administracao de Empresas
141. Rbgn-Revista Brasileira de Gestao de Negocios
142. Research in Transportation Business and Management
143. Research-Technology Management
144. Revista de Historia Industrial
145. Service Business
146. Service Science
147. Small Business Economics
148. South African Journal of Business Management
149. Sport Marketing Quarterly
150. Strategic Entrepreneurship Journal
151. Strategic Management Journal
152. Strategic Organization
153. Supply Chain Management-an International Journal
154. Technological Forecasting and Social Change
155. Transformations in Business & Economics

<a id="ssci-business-finance"></a>

### Business, Finance

期刊数：112

1. Abacus-a Journal of Accounting Finance and Business Studies
2. Accounting and Business Research
3. Accounting and Finance
4. Accounting Auditing & Accountability Journal
5. Accounting Forum
6. Accounting Horizons
7. Accounting Organizations and Society
8. Accounting Review
9. Annual Review of Financial Economics
10. Asia-Pacific Journal of Accounting & Economics
11. Asia-Pacific Journal of Financial Studies
12. Auditing-a Journal of Practice & Theory
13. Australian Accounting Review
14. Borsa Istanbul Review
15. British Accounting Review
16. Comptabilite Controle Audit
17. Contemporary Accounting Research
18. Corporate Governance-an International Review
19. Critical Perspectives on Accounting
20. Emerging Markets Review
21. European Accounting Review
22. European Financial Management
23. European Journal of Finance
24. Federal Reserve Bank of St Louis Review
25. Finance a Uver-Czech Journal of Economics and Finance
26. Finance and Stochastics
27. Finance Research Letters
28. Financial Analysts Journal
29. Financial Innovation
30. Financial Management
31. FinanzArchiv-European Journal of Public Finance
32. Fiscal Studies
33. Geneva Papers on Risk and Insurance-Issues and Practice
34. Geneva Risk and Insurance Review
35. Global Finance Journal
36. IMF Economic Review
37. International Finance
38. International Insolvency Review
39. International Journal of Accounting Information Systems
40. International Journal of Auditing
41. International Journal of Central Banking
42. International Journal of Finance & Economics
43. International Journal of Health  Economics and Management
44. International Journal of Islamic and Middle Eastern Finance and Management
45. International Review of Economics & Finance
46. International Review of Finance
47. International Review of Financial Analysis
48. Investment Analysts Journal
49. Journal of Accounting & Economics
50. Journal of Accounting and Public Policy
51. Journal of Accounting Research
52. Journal of Banking & Finance
53. Journal of Behavioral and Experimental Finance
54. Journal of Behavioral Finance
55. Journal of Business Finance & Accounting
56. Journal of Commodity Markets
57. Journal of Computational Finance
58. Journal of Contemporary Accounting & Economics
59. Journal of Corporate Finance
60. Journal of Credit Risk
61. Journal of Derivatives
62. Journal of Empirical Finance
63. Journal of Finance
64. Journal of Financial and Quantitative Analysis
65. Journal of Financial Econometrics
66. Journal of Financial Economics
67. Journal of Financial Intermediation
68. Journal of Financial Markets
69. Journal of Financial Research
70. Journal of Financial Services Research
71. Journal of Financial Stability
72. Journal of Futures Markets
73. Journal of Industrial Economics
74. Journal of Information Systems
75. Journal of International Financial Management & Accounting
76. Journal of International Financial Markets Institutions & Money
77. Journal of International Money and Finance
78. Journal of Monetary Economics
79. Journal of Money Credit and Banking
80. Journal of Multinational Financial Management
81. Journal of Operational Risk
82. Journal of Pension Economics & Finance
83. Journal of Portfolio Management
84. Journal of Real Estate Finance and Economics
85. Journal of Real Estate Research
86. Journal of Risk
87. Journal of Risk and Insurance
88. Journal of Risk and Uncertainty
89. Journal of Risk Model Validation
90. Management Accounting Research
91. Managerial Auditing Journal
92. Mathematical Finance
93. Mathematics and Financial Economics
94. National Tax Journal
95. North American Journal of Economics and Finance
96. Pacific-Basin Finance Journal
97. Public Money & Management
98. Qualitative Research in Accounting and Management
99. Quantitative Finance
100. Real Estate Economics
101. Research in International Business and Finance
102. Review of Accounting Studies
103. Review of Derivatives Research
104. Review of Finance
105. Review of Financial Studies
106. Revista de Contabilidad-Spanish Accounting Review
107. SIAM Journal on Financial Mathematics
108. Spanish Journal of Finance and Accounting-Revista Espanola de Financiacion y Contabilidad
109. Sustainability Accounting Management and Policy Journal
110. Venture Capital
111. World Bank Economic Review
112. World Economy

<a id="ssci-communication"></a>

### Communication

期刊数：93

1. African Journalism Studies
2. Argumentation
3. Asian Journal of Communication
4. Chinese Journal of Communication
5. Communication & Sport
6. Communication and Critical-Cultural Studies
7. Communication Culture & Critique
8. Communication Methods and Measures
9. Communication Monographs
10. Communication Research
11. Communication Theory
12. Communications-European Journal of Communication Research
13. Continuum-Journal of Media & Cultural Studies
14. Convergence-the International Journal of Research into New Media Technologies
15. Critical Discourse Studies
16. Critical Studies in Media Communication
17. Cyberpsychology-Journal of Psychosocial Research on Cyberspace
18. Digital Journalism
19. Discourse & Communication
20. Discourse & Society
21. Discourse Context & Media
22. Discourse Studies
23. Environmental Communication-a Journal of Nature and Culture
24. European Journal of Communication
25. Feminist Media Studies
26. Games and Culture
27. Health Communication
28. Human Communication Research
29. IEEE Transactions on Professional Communication
30. Information Communication & Society
31. Information Society
32. Interaction Studies
33. International Communication Gazette
34. International Journal of Advertising
35. International Journal of Business Communication
36. International Journal of Communication
37. International Journal of Conflict Management
38. International Journal of Mobile Communications
39. International Journal of Press-Politics
40. International Journal of Public Opinion Research
41. Javnost-the Public
42. Journal of Advertising
43. Journal of Advertising Research
44. Journal of African Media Studies
45. Journal of Applied Communication Research
46. Journal of Broadcasting & Electronic Media
47. Journal of Business and Technical Communication
48. Journal of Children and Media
49. Journal of Communication
50. Journal of Computer-Mediated Communication
51. Journal of Health Communication
52. Journal of Information Technology & Politics
53. Journal of Language and Social Psychology
54. Journal of Media Economics
55. Journal of Media Ethics
56. Journal of Media Psychology-Theories Methods and Applications
57. Journal of Public Relations Research
58. Journal of Social and Personal Relationships
59. Journalism
60. Journalism & Mass Communication Quarterly
61. Journalism Practice
62. Journalism Studies
63. Language & Communication
64. Management Communication Quarterly
65. Mass Communication and Society
66. Media and Communication
67. Media Culture & Society
68. Media International Australia
69. Media Psychology
70. Mobile Media & Communication
71. Narrative Inquiry
72. New Media & Society
73. Personal Relationships
74. Policy and Internet
75. Political Communication
76. Psychology of Popular Media
77. Public Opinion Quarterly
78. Public Relations Review
79. Public Understanding of Science
80. Quarterly Journal of Speech
81. Research on Language and Social Interaction
82. Rhetoric Society Quarterly
83. Science Communication
84. Signs and Society
85. Social Media + Society
86. Social Semiotics
87. Telecommunications Policy
88. Television & New Media
89. Text & Talk
90. Tijdschrift voor Communicatiewetenschap
91. Translator
92. Visual Communication
93. Written Communication

<a id="ssci-criminology-penology"></a>

### Criminology & Penology

期刊数：70

1. Aggression and Violent Behavior
2. American Journal of Criminal Justice
3. Annual Review of Criminology
4. Asian Journal of Criminology
5. British Journal of Criminology
6. Canadian Journal of Criminology and Criminal Justice
7. Crime & Delinquency
8. Crime and Justice-a Review of Research
9. Crime Law and Social Change
10. Crime Media Culture
11. Criminal Behaviour and Mental Health
12. Criminal Justice and Behavior
13. Criminology
14. Criminology & Criminal Justice
15. Criminology & Public Policy
16. Critical Criminology
17. Deviance et Societe
18. Deviant Behavior
19. European Journal of Criminology
20. European Journal on Criminal Policy and Research
21. Feminist Criminology
22. Homicide Studies
23. International Journal of Forensic Mental Health
24. International Journal of Law Crime and Justice
25. International Journal of Offender Therapy and Comparative Criminology
26. International Journal of Speech Language and the Law
27. Journal of Aggression Maltreatment & Trauma
28. Journal of Contemporary Criminal Justice
29. Journal of Crime & Justice
30. Journal of Criminal Justice
31. Journal of Criminal Law & Criminology
32. Journal of Criminology
33. Journal of Developmental and Life-Course Criminology
34. Journal of Experimental Criminology
35. Journal of Forensic Nursing
36. Journal of Forensic Psychiatry & Psychology
37. Journal of Forensic Psychology Research and Practice
38. Journal of Interpersonal Violence
39. Journal of Investigative Psychology and Offender Profiling
40. Journal of Quantitative Criminology
41. Journal of Research in Crime and Delinquency
42. Journal of School Violence
43. Journal of Sexual Aggression
44. Justice Quarterly
45. Legal and Criminological Psychology
46. LGBTQ Family-an Interdisciplinary Journal
47. Monatsschrift für Kriminologie und Strafrechtsreform
48. Police Quarterly
49. Policing & Society
50. Policing-a Journal of Policy and Practice
51. Policing-an International Journal of Police Strategies & Management
52. Prison Journal
53. Psychiatry Psychology and Law
54. Psychology Crime & Law
55. Psychology of Violence
56. Punishment & Society-International Journal of Penology
57. Race and Justice
58. Recht & Psychiatrie
59. Revija za Kriminalistiko in Kriminologijo
60. Security Journal
61. Sexual Abuse-a Journal of Research and Treatment
62. Social & Legal Studies
63. Theoretical Criminology
64. Trauma Violence & Abuse
65. Trends in Organized Crime
66. Victims & Offenders
67. Violence and Victims
68. Women & Criminal Justice
69. Youth Justice-an International Journal
70. Youth Violence and Juvenile Justice

<a id="ssci-cultural-studies"></a>

### Cultural Studies

期刊数：44

1. Asian Studies Review
2. Boundary 2-an International Journal of Literature and Culture
3. Celebrity Studies
4. Communication and Critical-Cultural Studies
5. Continuum-Journal of Media & Cultural Studies
6. Critical Arts-South-North Cultural and Media Studies
7. Critical Inquiry
8. Cultural Critique
9. Cultural Studies
10. Cultural Studies of Science Education
11. Cultural Studies-Critical Methodologies
12. Cultural Trends
13. Differences-a Journal of Feminist Cultural Studies
14. European Journal of Cultural Studies
15. European Journal of English Studies
16. French Cultural Studies
17. Games and Culture
18. Identities-Global Studies in Culture and Power
19. Inter-Asia Cultural Studies
20. International Journal of Cultural Policy
21. International Journal of Cultural Studies
22. Interventions-International Journal of Postcolonial Studies
23. Journal of African Cultural Studies
24. Journal of African Media Studies
25. Journal of Australian Studies
26. Journal of Consumer Culture
27. Journal of Cultural Economy
28. Journal of Latin American Cultural Studies
29. Journal of Material Culture
30. Journal of Popular Culture
31. Journal of Spanish Cultural Studies
32. Journal of Visual Culture
33. Memory Studies
34. Modern Chinese Literature and Culture
35. Parallax
36. Postcolonial Studies
37. Postmedieval-a Journal of Medieval Cultural Studies
38. Public Culture
39. Representations
40. Science as Culture
41. South Atlantic Quarterly
42. Space and Culture
43. Theory Culture & Society
44. Topia-Canadian Journal of Cultural Studies

<a id="ssci-demography"></a>

### Demography

期刊数：29

1. Asian and Pacific Migration Journal
2. Asian Population Studies
3. Biodemography and Social Biology
4. Canadian Studies in Population
5. Comparative Migration Studies
6. Demographic Research
7. Demography
8. European Journal of Migration and Law
9. European Journal of Population-Revue Europeenne de Demographie
10. International Migration
11. International Migration Review
12. Journal of Biosocial Science
13. Journal of Demographic Economics
14. Journal of Ethnic and Migration Studies
15. Journal of Immigrant & Refugee Studies
16. Journal of Population Economics
17. Journal of Refugee Studies
18. Journal of the Economics of Ageing
19. Mathematical Population Studies
20. Migration Studies
21. Papeles de Poblacion
22. Perspectives on Sexual and Reproductive Health
23. Population
24. Population and Development Review
25. Population and Environment
26. Population Research and Policy Review
27. Population Space and Place
28. Population Studies-a Journal of Demography
29. Studies in Family Planning

<a id="ssci-development-studies"></a>

### Development Studies

期刊数：42

1. African Development Review-Revue Africaine de Developpement
2. Cambridge Journal of Regions Economy and Society
3. Canadian Journal of Development Studies-Revue Canadienne d Etudes du Developpement
4. Climate and Development
5. Community Development Journal
6. Developing Economies
7. Development and Change
8. Development Policy Review
9. Development Southern Africa
10. Economic Development and Cultural Change
11. Economic Development Quarterly
12. Entrepreneurship and Regional Development
13. European Journal of Development Research
14. Growth and Change
15. Habitat International
16. Housing Policy Debate
17. IDS Bulletin-Institute of Development Studies
18. Information Technology for Development
19. International Development Planning Review
20. Journal of Agrarian Change
21. Journal of Development Effectiveness
22. Journal of Development Studies
23. Journal of Economic Policy Reform
24. Journal of Environment & Development
25. Journal of Environmental Planning and Management
26. Journal of Environmental Policy & Planning
27. Journal of Human Development and Capabilities
28. Journal of International Development
29. Journal of Peasant Studies
30. Journal of South Asian Development
31. Long Range Planning
32. Progress in Development Studies
33. Public Administration and Development
34. Review of Development Economics
35. Social Policy & Administration
36. Society & Natural Resources
37. Studies in Comparative International Development
38. Sustainable Development
39. Third World Quarterly
40. World Bank Economic Review
41. World Bank Research Observer
42. World Development

<a id="ssci-economics"></a>

### Economics

期刊数：379

1. Acta Oeconomica
2. Agribusiness
3. Agricultural and Food Economics
4. Agricultural Economics
5. Agricultural Economics-Zemedelska Ekonomika
6. American Economic Journal-Applied Economics
7. American Economic Journal-Economic Policy
8. American Economic Journal-Macroeconomics
9. American Economic Journal-Microeconomics
10. American Economic Review
11. American Economic Review-Insights
12. American Journal of Agricultural Economics
13. American Journal of Economics and Sociology
14. American Journal of Health Economics
15. American Law and Economics Review
16. Amfiteatru Economic
17. Annals of Economics and Finance
18. Annals of Public and Cooperative Economics
19. Annals of Regional Science
20. Annual Review of Economics
21. Annual Review of Financial Economics
22. Annual Review of Resource Economics
23. Applied Economic Analysis
24. Applied Economic Perspectives and Policy
25. Applied Economics
26. Applied Economics Letters
27. Applied Health Economics and Health Policy
28. Argumenta Oeconomica
29. Asia-Pacific Economic History Review
30. Asia-Pacific Journal of Accounting & Economics
31. Asian Economic Journal
32. Asian Economic Papers
33. Asian Economic Policy Review
34. Asian Journal of Technology Innovation
35. Asian-Pacific Economic Literature
36. ASTIN Bulletin-the Journal of the International Actuarial Association
37. Australian Economic Papers
38. Australian Economic Review
39. Australian Journal of Agricultural and Resource Economics
40. B e Journal of Economic Analysis & Policy
41. B e Journal of Macroeconomics
42. B e Journal of Theoretical Economics
43. Baltic Journal of Economics
44. Borsa Istanbul Review
45. Brookings Papers on Economic Activity
46. Bulletin of Economic Research
47. Bulletin of Indonesian Economic Studies
48. Cambridge Journal of Economics
49. Cambridge Journal of Regions Economy and Society
50. Canadian Journal of Agricultural Economics-Revue Canadienne d Agroeconomie
51. Canadian Journal of Economics-Revue Canadienne d Economique
52. Canadian Public Policy-Analyse de Politiques
53. CEPAL Review
54. CESifo Economic Studies
55. China & World Economy
56. China Agricultural Economic Review
57. China Economic Review
58. Climate Change Economics
59. Cliometrica
60. Competition & Change
61. Computational Economics
62. Contemporary Economic Policy
63. Custos e Agronegocio on Line
64. Defence and Peace Economics
65. Developing Economies
66. E & M Ekonomie a Management
67. Eastern European Economics
68. Ecological Economics
69. Econ Journal Watch
70. Econometric Reviews
71. Econometric Theory
72. Econometrica
73. Econometrics Journal
74. Economia Politica
75. Economic Analysis and Policy
76. Economic and Labour Relations Review
77. Economic and Social Review
78. Economic Change and Restructuring
79. Economic Computation and Economic Cybernetics Studies and Research
80. Economic Development and Cultural Change
81. Economic Development Quarterly
82. Economic Geography
83. Economic History Review
84. Economic Inquiry
85. Economic Journal
86. Economic Modelling
87. Economic Policy
88. Economic Record
89. Economic Systems
90. Economic Systems Research
91. Economic Theory
92. Economica
93. Economics & Human Biology
94. Economics & Philosophy
95. Economics & Politics
96. Economics Letters
97. Economics of Education Review
98. Economics of Energy & Environmental Policy
99. Economics of Governance
100. Economics of Innovation and New Technology
101. Economics of Transition and Institutional Change
102. Economics of Transportation
103. Economics-the Open Access Open-Assessment e-Journal
104. Economist-Netherlands
105. Economy and Society
106. Education Finance and Policy
107. Ekonomicky Casopis
108. Emerging Markets Finance and Trade
109. Emerging Markets Review
110. Empirica
111. Empirical Economics
112. Energy Economics
113. Energy Journal
114. Energy Policy
115. Environment and Development Economics
116. Environmental & Resource Economics
117. Estudios de Economia
118. Eurasian Business Review
119. Europe-Asia Studies
120. European Economic Review
121. European Journal of Health Economics
122. European Journal of Law and Economics
123. European Journal of Political Economy
124. European Journal of the History of Economic Thought
125. European Research on Management and Business Economics
126. European Review of Agricultural Economics
127. European Review of Economic History
128. Experimental Economics
129. Explorations in Economic History
130. Federal Reserve Bank of St Louis Review
131. Feminist Economics
132. FinanzArchiv-European Journal of Public Finance
133. Fiscal Studies
134. Food Policy
135. Forest Policy and Economics
136. Futures
137. Games and Economic Behavior
138. Geneva Risk and Insurance Review
139. German Economic Review
140. Global Economic Review
141. Hacienda Publica Espanola-Review of Public Economics
142. Health Economics
143. Health Economics Review
144. History of Political Economy
145. Hitotsubashi Journal of Economics
146. IMF Economic Review
147. Independent Review
148. Industrial and Corporate Change
149. Industry and Innovation
150. Information Economics and Policy
151. Insurance Mathematics & Economics
152. International Economic Review
153. International Environmental Agreements-Politics Law and Economics
154. International Finance
155. International Journal of Economic Theory
156. International Journal of Emerging Markets
157. International Journal of Forecasting
158. International Journal of Game Theory
159. International Journal of Health  Economics and Management
160. International Journal of Industrial Organization
161. International Journal of Transport Economics
162. International Labour Review
163. International Review of Economics & Finance
164. International Review of Economics Education
165. International Review of Law and Economics
166. International Tax and Public Finance
167. Investigacion Economica
168. Inzinerine Ekonomika-Engineering Economics
169. Jahrbucher für Nationalokonomie und Statistik
170. Japan and the World Economy
171. Japanese Economic Review
172. JCMS-Journal of Common Market Studies
173. Journal of Accounting & Economics
174. Journal of African Economies
175. Journal of Agrarian Change
176. Journal of Agricultural and Resource Economics
177. Journal of Agricultural Economics
178. Journal of Applied Econometrics
179. Journal of Applied Economics
180. Journal of Asian Economics
181. Journal of Australian Political Economy
182. Journal of Banking & Finance
183. Journal of Behavioral and Experimental Economics
184. Journal of Behavioral and Experimental Finance
185. Journal of Behavioral Finance
186. Journal of Benefit-Cost Analysis
187. Journal of Business & Economic Statistics
188. Journal of Business Economics and Management
189. Journal of Choice Modelling
190. Journal of Commodity Markets
191. Journal of Comparative Economics
192. Journal of Competition Law & Economics
193. Journal of Competitiveness
194. Journal of Consumer Affairs
195. Journal of Contemporary Accounting & Economics
196. Journal of Cultural Economics
197. Journal of Cultural Economy
198. Journal of Demographic Economics
199. Journal of Development Economics
200. Journal of Development Studies
201. Journal of Econometrics
202. Journal of Economic Behavior & Organization
203. Journal of Economic Dynamics & Control
204. Journal of Economic Education
205. Journal of Economic Geography
206. Journal of Economic Growth
207. Journal of Economic History
208. Journal of Economic Inequality
209. Journal of Economic Interaction and Coordination
210. Journal of Economic Issues
211. Journal of Economic Literature
212. Journal of Economic Methodology
213. Journal of Economic Perspectives
214. Journal of Economic Policy Reform
215. Journal of Economic Psychology
216. Journal of Economic Surveys
217. Journal of Economic Theory
218. Journal of Economics
219. Journal of Economics & Management Strategy
220. Journal of Empirical Finance
221. Journal of Environmental Economics and Management
222. Journal of Evolutionary Economics
223. Journal of Family and Economic Issues
224. Journal of Finance
225. Journal of Financial and Quantitative Analysis
226. Journal of Financial Econometrics
227. Journal of Financial Economics
228. Journal of Financial Stability
229. Journal of Forecasting
230. Journal of Forest Economics
231. Journal of Health Economics
232. Journal of Housing Economics
233. Journal of Human Capital
234. Journal of Human Resources
235. Journal of Industrial Economics
236. Journal of Institutional and Theoretical Economics-Zeitschrift fur die Gesamte Staatswissenschaft
237. Journal of Institutional Economics
238. Journal of International Economics
239. Journal of International Financial Markets Institutions & Money
240. Journal of International Trade & Economic Development
241. Journal of Korea Trade
242. Journal of Labor Economics
243. Journal of Law & Economics
244. Journal of Law Economics & Organization
245. Journal of Macroeconomics
246. Journal of Mathematical Economics
247. Journal of Media Economics
248. Journal of Monetary Economics
249. Journal of Money Credit and Banking
250. Journal of Neuroscience Psychology and Economics
251. Journal of Pension Economics & Finance
252. Journal of Policy Analysis and Management
253. Journal of Policy Modeling
254. Journal of Political Economy
255. Journal of Population Economics
256. Journal of Post Keynesian Economics
257. Journal of Productivity Analysis
258. Journal of Public Economic Theory
259. Journal of Public Economics
260. Journal of Real Estate Finance and Economics
261. Journal of Real Estate Research
262. Journal of Regional Science
263. Journal of Regulatory Economics
264. Journal of Risk and Insurance
265. Journal of Risk and Uncertainty
266. Journal of Sports Economics
267. Journal of the Asia Pacific Economy
268. Journal of the Association of Environmental and Resource Economists
269. Journal of the Economics of Ageing
270. Journal of the European Economic Association
271. Journal of the Japanese and International Economies
272. Journal of Transport Economics and Policy
273. Journal of Transport Geography
274. Journal of Urban Economics
275. Journal of Wine Economics
276. Journal of World Trade
277. Korean Economic Review
278. Kyklos
279. Labour Economics
280. Land Economics
281. Latin American Economic Review
282. Macroeconomic Dynamics
283. Managerial and Decision Economics
284. Manchester School
285. Marine Resource Economics
286. Mathematical Finance
287. Mathematical Social Sciences
288. Mathematics and Financial Economics
289. Metroeconomica
290. National Tax Journal
291. NBER Macroeconomics Annual
292. New Political Economy
293. North American Journal of Economics and Finance
294. Oeconomia Copernicana
295. Open Economies Review
296. Oxford Bulletin of Economics and Statistics
297. Oxford Economic Papers-New Series
298. Oxford Review of Economic Policy
299. Pacific Economic Review
300. Panoeconomicus
301. Papers in Regional Science
302. PharmacoEconomics
303. Politicka Ekonomie
304. Portuguese Economic Journal
305. Post-Communist Economies
306. Post-Soviet Affairs
307. Prague Economic Papers
308. Public Choice
309. Qme-Quantitative Marketing and Economics
310. Quantitative Economics
311. Quantitative Finance
312. Quarterly Journal of Economics
313. Quarterly Review of Economics and Finance
314. RAND Journal of Economics
315. Real Estate Economics
316. Regional Science and Urban Economics
317. Regional Studies
318. Research in Transportation Economics
319. Resource and Energy Economics
320. Review of Derivatives Research
321. Review of Development Economics
322. Review of Economic Design
323. Review of Economic Dynamics
324. Review of Economic Studies
325. Review of Economics and Statistics
326. Review of Economics of the Household
327. Review of Environmental Economics and Policy
328. Review of Finance
329. Review of Financial Studies
330. Review of Income and Wealth
331. Review of Industrial Organization
332. Review of International Economics
333. Review of International Organizations
334. Review of International Political Economy
335. Review of Keynesian Economics
336. Review of Network Economics
337. Review of Radical Political Economics
338. Review of World Economics
339. Revista de Economia Mundial
340. Revista de Historia Economica-Journal of Iberian and Latin American Economic History
341. Revista de Historia Industrial
342. Revue d Economie Politique
343. Revue d Etudes Comparatives Est-Ouest
344. Romanian Journal of Economic Forecasting
345. Scandinavian Journal of Economics
346. Scottish Journal of Political Economy
347. SERIEs-Journal of the Spanish Economic Association
348. Singapore Economic Review
349. Small Business Economics
350. Social Choice and Welfare
351. Socio-Economic Planning Sciences
352. Socio-Economic Review
353. South African Journal of Economic and Management Sciences
354. South African Journal of Economics
355. Southern Economic Journal
356. Spatial Economic Analysis
357. Structural Change and Economic Dynamics
358. Studies in Nonlinear Dynamics and Econometrics
359. Technological and Economic Development of Economy
360. Theoretical Economics
361. Theory and Decision
362. Tijdschrift voor Economische en Sociale Geografie
363. Tourism Economics
364. Transformations in Business & Economics
365. Transport Policy
366. Transportation Research Part a-Policy and Practice
367. Transportation Research Part B-Methodological
368. Transportation Research Part e-Logistics and Transportation Review
369. Trimestre Economico
370. Value in Health
371. Water Economics and Policy
372. Water Resources and Economics
373. Work Employment and Society
374. World Bank Economic Review
375. World Bank Research Observer
376. World Development
377. World Economy
378. World Trade Review
379. ZFW-Advances in Economic Geography

<a id="ssci-education-educational-research"></a>

### Education & Educational Research

期刊数：270

1. Academic Psychiatry
2. Academy of Management Learning & Education
3. Active Learning in Higher Education
4. Adult Education Quarterly
5. Advances in Health Sciences Education
6. AERA Open
7. AIDS Education and Prevention
8. American Educational Research Journal
9. American Journal of Education
10. Anthropology & Education Quarterly
11. Applied Measurement in Education
12. Asia Pacific Education Review
13. Asia Pacific Journal of Education
14. Asia-Pacific Education Researcher
15. Asia-Pacific Journal of Teacher Education
16. Assessing Writing
17. Assessment & Evaluation in Higher Education
18. Assessment in Education-Principles Policy & Practice
19. Australasian Journal of Early Childhood
20. Australasian Journal of Educational Technology
21. Australian Educational Researcher
22. Australian Journal of Adult Learning
23. Australian Journal of Education
24. Australian Journal of English Education
25. BMC Medical Education
26. British Educational Research Journal
27. British Journal of Educational Studies
28. British Journal of Educational Technology
29. British Journal of Music Education
30. British Journal of Religious Education
31. British Journal of Sociology of Education
32. Cadmo
33. Cambridge Journal of Education
34. Chemistry Education Research and Practice
35. Comparative Education
36. Comparative Education Review
37. Compare-a Journal of Comparative and International Education
38. Computer Assisted Language Learning
39. Computers & Education
40. Critical Studies in Education
41. Croatian Journal of Education-Hrvatski Casopis za Odgoj i Obrazovanje
42. Cultural Studies of Science Education
43. Culture and Education
44. Current Issues in Language Planning
45. Curriculum Inquiry
46. Curriculum Matters
47. Discourse-Studies in the Cultural Politics of Education
48. Distance Education
49. Early Child Development and Care
50. Early Childhood Education Journal
51. Early Childhood Research Quarterly
52. Early Education and Development
53. Early Years
54. Economics of Education Review
55. Educacion Xx1
56. Education and Information Technologies
57. Education and Training
58. Education and Urban Society
59. Education as Change
60. Education Finance and Policy
61. Educational Administration Quarterly
62. Educational Assessment Evaluation and Accountability
63. Educational Evaluation and Policy Analysis
64. Educational Gerontology
65. Educational Leadership
66. Educational Management Administration & Leadership
67. Educational Measurement-Issues and Practice
68. Educational Philosophy and Theory
69. Educational Policy
70. Educational Psychologist
71. Educational Psychology
72. Educational Research
73. Educational Research Review
74. Educational Researcher
75. Educational Review
76. Educational Studies
77. Educational Studies in Mathematics
78. Educational Technology & Society
79. Egitim ve Bilim-Education and Science
80. Elementary School Journal
81. ELT Journal
82. English in Education
83. English Teaching-Practice and Critique
84. Ensenanza de las Ciencias
85. Environmental Education Research
86. ETR&d-Educational Technology Research and Development
87. European Early Childhood Education Research Journal
88. European Educational Research Journal
89. European Journal of Education
90. European Journal of Teacher Education
91. European Physical Education Review
92. Foreign Language Annals
93. Gender and Education
94. Harvard Educational Review
95. Health Education Journal
96. Health Education Research
97. Higher Education
98. Higher Education Policy
99. Higher Education Research & Development
100. History of Education
101. IEEE Transactions on Learning Technologies
102. Innovation in Language Learning and Teaching
103. Innovations in Education and Teaching International
104. Instructional Science
105. Interactive Learning Environments
106. International Journal for Academic Development
107. International Journal for Educational and Vocational Guidance
108. International Journal for Lesson and Learning Studies
109. International Journal of Applied Linguistics
110. International Journal of Art & Design Education
111. International Journal of Bilingual Education and Bilingualism
112. International Journal of Computer-Supported Collaborative Learning
113. International Journal of Educational Development
114. International Journal of Educational Research
115. International Journal of Educational Technology in Higher Education
116. International Journal of Inclusive Education
117. International Journal of Management Education
118. International Journal of Multilingualism
119. International Journal of Music Education
120. International Journal of Science and Mathematics Education
121. International Journal of Science Education
122. International Journal of STEM Education
123. International Journal of Sustainability in Higher Education
124. International Journal of Technology and Design Education
125. International Multilingual Research Journal
126. International Review of Economics Education
127. International Review of Research in Open and Distributed Learning
128. Internet and Higher Education
129. IRAL-International Review of Applied Linguistics in Language Teaching
130. Irish Educational Studies
131. Journal for Research in Mathematics Education
132. Journal of Adolescent & Adult Literacy
133. Journal of Agricultural Education & Extension
134. Journal of American College Health
135. Journal of Baltic Science Education
136. Journal of Beliefs & Values-Studies in Religion & Education
137. Journal of Biological Education
138. Journal of College Student Development
139. Journal of Computer Assisted Learning
140. Journal of Computing in Higher Education
141. Journal of Curriculum Studies
142. Journal of Diversity in Higher Education
143. Journal of Early Childhood Literacy
144. Journal of Economic Education
145. Journal of Education for Teaching
146. Journal of Education Policy
147. Journal of Educational Administration
148. Journal of Educational and Behavioral Statistics
149. Journal of Educational Change
150. Journal of Educational Computing Research
151. Journal of Educational Research
152. Journal of Engineering Education
153. Journal of English for Academic Purposes
154. Journal of Environmental Education
155. Journal of Experimental Education
156. Journal of Geography in Higher Education
157. Journal of Higher Education
158. Journal of Higher Education Policy and Management
159. Journal of Hospitality Leisure Sport & Tourism Education
160. Journal of Language Identity and Education
161. Journal of Legal Education
162. Journal of Literacy Research
163. Journal of Marketing for Higher Education
164. Journal of Mathematics Teacher Education
165. Journal of Moral Education
166. Journal of Philosophy of Education
167. Journal of Professional Capital and Community
168. Journal of Psychologists and Counsellors in Schools
169. Journal of Research in Music Education
170. Journal of Research in Reading
171. Journal of Research in Science Teaching
172. Journal of Research on Educational Effectiveness
173. Journal of Research on Technology in Education
174. Journal of School Health
175. Journal of School Violence
176. Journal of Science Education and Technology
177. Journal of Social Work Education
178. Journal of Studies in International Education
179. Journal of Teacher Education
180. Journal of Teaching in Physical Education
181. Journal of the Learning Sciences
182. KEDI Journal of Educational Policy
183. Language and Education
184. Language Culture and Curriculum
185. Language Learning
186. Language Learning & Technology
187. Language Policy
188. Language Teaching
189. Language Teaching Research
190. Learning and Instruction
191. Learning Culture and Social Interaction
192. Learning Media and Technology
193. Linguistics and Education
194. Literacy
195. Mathematical Thinking and Learning
196. Measurement in Physical Education and Exercise Science
197. Medical Education Online
198. Metacognition and Learning
199. Mind Brain and Education
200. Mind Culture and Activity
201. Minerva
202. Modern Language Journal
203. Movimento
204. Music Education Research
205. Npj Science of Learning
206. Oxford Review of Education
207. Paedagogica Historica
208. Pedagogische Studien
209. Phi Delta Kappan
210. Physical Education and Sport Pedagogy
211. Physical Review Physics Education Research
212. Porta Linguarum
213. Professional Development in Education
214. Psicologia Educativa
215. Quest
216. Race Ethnicity and Education
217. Reading & Writing Quarterly
218. Reading and Writing
219. Reading Research Quarterly
220. Reading Teacher
221. ReCALL
222. Research in Higher Education
223. Research in Science & Technological Education
224. Research in Science Education
225. Research in the Teaching of English
226. Research Papers in Education
227. Review of Educational Research
228. Review of Higher Education
229. Review of Research in Education
230. Revista de Educacion
231. Revista de Psicodidactica
232. Revista Espanola de Pedagogia
233. Revista Latinoamericana de Investigacion en Matematica Educativa-Relime
234. Ride-the Journal of Applied Theatre and Performance
235. RIED-Revista Iberoamericana de Educacion a Distancia
236. Scandinavian Journal of Educational Research
237. School Effectiveness and School Improvement
238. Science & Education
239. Science Education
240. Scientific Studies of Reading
241. Second Language Research
242. Sex Education-Sexuality Society and Learning
243. Smart Learning Environments
244. Sociology of Education
245. South African Journal of Education
246. Sport Education and Society
247. Studies in Continuing Education
248. Studies in Educational Evaluation
249. Studies in Higher Education
250. Studies in Philosophy and Education
251. Studies in Science Education
252. System
253. Teacher Education and Special Education
254. Teachers and Teaching
255. Teachers College Record
256. Teaching and Teacher Education
257. Teaching in Higher Education
258. Teaching of Psychology
259. Teaching Sociology
260. Technology Pedagogy and Education
261. TESOL Quarterly
262. Theory and Research in Social Education
263. Theory into Practice
264. Thinking Skills and Creativity
265. Urban Education
266. Vocations and Learning
267. ZDM-Mathematics Education
268. Zeitschrift für Erziehungswissenschaft
269. Zeitschrift für Padagogik
270. Zeitschrift für Soziologie der Erziehung und Sozialisation

<a id="ssci-education-special"></a>

### Education, Special

期刊数：43

1. AJIDD-American Journal on Intellectual and Developmental Disabilities
2. American Annals of the Deaf
3. Annals of Dyslexia
4. Behavioral Disorders
5. British Journal of Learning Disabilities
6. Career Development and Transition for Exceptional Individuals
7. Child Language Teaching & Therapy
8. Dyslexia
9. Education and Training in Autism and Developmental Disabilities
10. Education and Treatment of Children
11. European Journal of Special Needs Education
12. Exceptional Children
13. Exceptionality
14. Focus on Autism and Other Developmental Disabilities
15. Gifted Child Quarterly
16. High Ability Studies
17. Infants & Young Children
18. Intellectual and Developmental Disabilities
19. International Journal of Developmental Disabilities
20. International Journal of Disability Development and Education
21. Intervention in School and Clinic
22. Journal of Behavioral Education
23. Journal of Deaf Studies and Deaf Education
24. Journal of Developmental and Physical Disabilities
25. Journal of Early Intervention
26. Journal of Emotional and Behavioral Disorders
27. Journal of Fluency Disorders
28. Journal of Intellectual & Developmental Disability
29. Journal of Intellectual Disabilities
30. Journal of Intellectual Disability Research
31. Journal of Learning Disabilities
32. Journal of Mental Health Research in Intellectual Disabilities
33. Journal of Positive Behavior Interventions
34. Journal of Special Education
35. Journal of Special Education Technology
36. Learning Disabilities Research & Practice
37. Learning Disability Quarterly
38. Reading & Writing Quarterly
39. Remedial and Special Education
40. Research and Practice for Persons with Severe Disabilities
41. Research in Autism
42. Research in Developmental Disabilities
43. Topics in Early Childhood Special Education

<a id="ssci-environmental-studies"></a>

### Environmental Studies

期刊数：129

1. Annals of Regional Science
2. Annual Review of Environment and Resources
3. Annual Review of Resource Economics
4. Anthropocene Review
5. Applied Spatial Analysis and Policy
6. Australasian Journal of Environmental Management
7. Business Strategy and the Environment
8. Carbon Management
9. Climate and Development
10. Climate Change Economics
11. Climate Policy
12. Climate Risk Management
13. Climate Services
14. Coastal Management
15. Computers Environment and Urban Systems
16. Conservation & Society
17. Corporate Social Responsibility and Environmental Management
18. Cultural Geographies
19. Disaster Prevention and Management
20. Disasters
21. Ecological Economics
22. Ecology and Society
23. Ecology Law Quarterly
24. Economics of Energy & Environmental Policy
25. Ecosystem Services
26. Energy & Environment
27. Energy Efficiency
28. Energy Journal
29. Energy Policy
30. Energy Research & Social Science
31. Environment
32. Environment and Behavior
33. Environment and Development Economics
34. Environment and History
35. Environment and Planning a-Economy and Space
36. Environment and Planning B-Urban Analytics and City Science
37. Environment and Planning C-Politics and Space
38. Environment and Planning d-Society & Space
39. Environment and Planning e-Nature and Space
40. Environment and Urbanization
41. Environmental & Resource Economics
42. Environmental Communication-a Journal of Nature and Culture
43. Environmental Education Research
44. Environmental Ethics
45. Environmental Hazards-Human and Policy Dimensions
46. Environmental History
47. Environmental Impact Assessment Review
48. Environmental Innovation and Societal Transitions
49. Environmental Policy and Governance
50. Environmental Politics
51. Environmental Values
52. European Planning Studies
53. European Urban and Regional Studies
54. Extractive Industries and Society
55. Forest Policy and Economics
56. Gaia-Ecological Perspectives for Science and Society
57. Geografisk Tidsskrift-Danish Journal of Geography
58. Global Environmental Change-Human and Policy Dimensions
59. Global Environmental Politics
60. Habitat International
61. Harvard Environmental Law Review
62. Housing Studies
63. Housing Theory & Society
64. Human Ecology
65. Human Ecology Review
66. Impact Assessment and Project Appraisal
67. International Environmental Agreements-Politics Law and Economics
68. International Journal of Climate Change Strategies and Management
69. International Journal of Housing Policy
70. International Journal of Sustainable Transportation
71. International Journal of the Commons
72. International Journal of Urban Sciences
73. International Regional Science Review
74. Journal of Agricultural Education & Extension
75. Journal of Architectural and Planning Research
76. Journal of Energy & Natural Resources Law
77. Journal of Environment & Development
78. Journal of Environmental Economics and Management
79. Journal of Environmental Education
80. Journal of Environmental Law
81. Journal of Environmental Psychology
82. Journal of Housing and the Built Environment
83. Journal of Regional Science
84. Journal of the Association of Environmental and Resource Economists
85. Land
86. Land Economics
87. Land Use Policy
88. Landscape and Urban Planning
89. Landscape Research
90. Local Environment
91. Marine Policy
92. Marine Resource Economics
93. Natural Hazards Review
94. Natural Resources Forum
95. Natural Resources Journal
96. Nature + Culture
97. Nature Climate Change
98. Nature Sustainability
99. Npj Urban Sustainability
100. One Earth
101. Open House International-Sustainable & Smart Architecture and Urban Studies
102. Organization & Environment
103. Papers in Regional Science
104. Population and Environment
105. Problemy Ekorozwoju
106. Progress in Planning
107. Regional Environmental Change
108. Regional Science and Urban Economics
109. Regional Studies
110. Resource and Energy Economics
111. Review of Environmental Economics and Policy
112. Review of European Comparative & International Environmental Law
113. Science and Public Policy
114. Society & Natural Resources
115. Sustainability
116. Sustainability Accounting Management and Policy Journal
117. Sustainable Production and Consumption
118. Tourism Management
119. Transnational Environmental Law
120. Transportation Research Part d-Transport and Environment
121. Urban Forestry & Urban Greening
122. Urban Policy and Research
123. Urban Studies
124. Utilities Policy
125. Water Alternatives-an Interdisciplinary Journal on Water Politics and Development
126. Water Economics and Policy
127. Water Resources and Economics
128. Weather Climate and Society
129. Wiley Interdisciplinary Reviews-Climate Change

<a id="ssci-ergonomics"></a>

### Ergonomics

期刊数：15

1. Accident Analysis and Prevention
2. Applied Ergonomics
3. Behaviour & Information Technology
4. Cognition Technology & Work
5. Ergonomics
6. Human Factors
7. Human Factors and Ergonomics in Manufacturing & Service Industries
8. Interacting with Computers
9. International Journal of Human-Computer Interaction
10. International Journal of Human-Computer Studies
11. International Journal of Industrial Ergonomics
12. International Journal of Occupational Safety and Ergonomics
13. Journal of Safety Research
14. Travail Humain
15. Universal Access in the Information Society

<a id="ssci-ethics"></a>

### Ethics

期刊数：55

1. Acta Bioethica
2. American Journal of Bioethics
3. Bioethics
4. BMC Medical Ethics
5. Business Ethics Quarterly
6. Business Ethics the Environment & Responsibility
7. Developing World Bioethics
8. Economics & Philosophy
9. Environmental Ethics
10. Environmental Values
11. Ethical Perspectives
12. Ethics
13. Ethics & Behavior
14. Ethics & Global Politics
15. Ethics & International Affairs
16. Ethics and Information Technology
17. Etikk i Praksis
18. Hastings Center Report
19. Health Care Analysis
20. HEC Forum
21. Human Studies
22. Inquiry-an Interdisciplinary Journal of Philosophy
23. International Journal of Feminist Approaches to Bioethics
24. Journal of Agricultural & Environmental Ethics
25. Journal of Applied Philosophy
26. Journal of Bioethical Inquiry
27. Journal of Business Ethics
28. Journal of Empirical Research on Human Research Ethics
29. Journal of Law and the Biosciences
30. Journal of Law Medicine & Ethics
31. Journal of Media Ethics
32. Journal of Medical Ethics
33. Journal of Medicine and Philosophy
34. Journal of Moral Philosophy
35. Journal of Responsible Innovation
36. Journal of Social Philosophy
37. Journal of the Philosophy of Sport
38. Journal of Value Inquiry
39. Kennedy Institute of Ethics Journal
40. Law and Philosophy
41. Medicine Health Care and Philosophy
42. Neuroethics
43. Nursing Ethics
44. Philosophical Psychology
45. Philosophy & Public Affairs
46. Philosophy Ethics and Humanities in Medicine
47. Philosophy of the Social Sciences
48. Politics Philosophy & Economics
49. Public Health Ethics
50. Radical Philosophy
51. Research Integrity and Peer Review
52. Science and Engineering Ethics
53. Social Philosophy and Policy
54. Studies in East European Thought
55. Theoretical Medicine and Bioethics

<a id="ssci-ethnic-studies"></a>

### Ethnic Studies

期刊数：20

1. Asian American Journal of Psychology
2. Cultural Diversity & Ethnic Minority Psychology
3. Du Bois Review-Social Science Research on Race
4. Ethnic and Racial Studies
5. Ethnicities
6. Ethnicity & Health
7. Identities-Global Studies in Culture and Power
8. Journal of Black Studies
9. Journal of Ethnic and Migration Studies
10. Journal of Immigrant & Refugee Studies
11. Journal of Refugee Studies
12. Nationalities Papers-the Journal of Nationalism and Ethnicity
13. Nations and Nationalism
14. Patterns of Prejudice
15. Race & Class
16. Race and Justice
17. Race and Social Problems
18. Race Ethnicity and Education
19. Sociology of Race and Ethnicity
20. Souls

<a id="ssci-family-studies"></a>

### Family Studies

期刊数：46

1. American Journal of Family Therapy
2. Australian and New Zealand Journal of Family Therapy
3. BMJ Sexual & Reproductive Health
4. Child & Family Behavior Therapy
5. Child & Family Social Work
6. Child Abuse & Neglect
7. Child Abuse Review
8. Child Maltreatment
9. Child Welfare
10. Children and Youth Services Review
11. Culture Health & Sexuality
12. Emerging Adulthood
13. Families in Society-the Journal of Contemporary Social Services
14. Families Relationships and Societies
15. Families Systems & Health
16. Family & Community Health
17. Family Process
18. Family Relations
19. History of the Family
20. International Journal of Law Policy and the Family
21. Jfr-Journal of Family Research
22. Journal of Aggression Maltreatment & Trauma
23. Journal of Child and Family Studies
24. Journal of Child Sexual Abuse
25. Journal of Comparative Family Studies
26. Journal of Early Adolescence
27. Journal of Family and Economic Issues
28. Journal of Family History
29. Journal of Family Issues
30. Journal of Family Nursing
31. Journal of Family Psychology
32. Journal of Family Studies
33. Journal of Family Theory & Review
34. Journal of Family Therapy
35. Journal of Family Violence
36. Journal of Interpersonal Violence
37. Journal of Marital and Family Therapy
38. Journal of Marriage and Family
39. Journal of Research on Adolescence
40. Journal of Sex & Marital Therapy
41. Journal of Social and Personal Relationships
42. Parenting-Science and Practice
43. Personal Relationships
44. Perspectives on Sexual and Reproductive Health
45. Psychology of Violence
46. Trauma Violence & Abuse

<a id="ssci-geography"></a>

### Geography

期刊数：87

1. Annals of Regional Science
2. Annals of the American Association of Geographers
3. Antipode
4. Applied Geography
5. Applied Spatial Analysis and Policy
6. Area
7. Asia Pacific Viewpoint
8. Australian Geographer
9. Boletin de la Asociacion de Geografos Espanoles
10. Cambridge Journal of Regions Economy and Society
11. Canadian Geographies-Geographies Canadiennes
12. Cartographic Journal
13. Cartography and Geographic Information Science
14. Childrens Geographies
15. Competition & Change
16. Computers Environment and Urban Systems
17. Cultural Geographies
18. Dialogues in Human Geography
19. Economic Geography
20. Emotion Space and Society
21. Environment and Planning a-Economy and Space
22. Environment and Planning B-Urban Analytics and City Science
23. Environment and Planning C-Politics and Space
24. Environment and Planning d-Society & Space
25. Environment and Planning e-Nature and Space
26. Erde
27. Erdkunde
28. Eurasian Geography and Economics
29. European Planning Studies
30. European Urban and Regional Studies
31. Gender Place and Culture
32. Geodetski Vestnik
33. Geoforum
34. Geografie
35. Geografisk Tidsskrift-Danish Journal of Geography
36. Geografiska Annaler Series B-Human Geography
37. Geographical Analysis
38. Geographical Journal
39. Geographical Research
40. Geographical Review
41. Geography
42. Geography Compass
43. Geopolitics
44. Global Environmental Change-Human and Policy Dimensions
45. Global Networks-a Journal of Transnational Affairs
46. Imago Mundi-the International Journal for the History of Cartography
47. International Journal of Geographical Information Science
48. International Journal of Urban and Regional Research
49. Island Studies Journal
50. Journal of Economic Geography
51. Journal of Geographical Systems
52. Journal of Geography
53. Journal of Geography in Higher Education
54. Journal of Historical Geography
55. Journal of Maps
56. Journal of Rural Studies
57. Journal of Transport Geography
58. Landscape and Urban Planning
59. Landscape Research
60. Local Environment
61. Mitteilungen der Osterreichischen Geographischen Gesellschaft
62. Mobilities
63. Moravian Geographical Reports
64. New Zealand Geographer
65. Norsk Geografisk Tidsskrift-Norwegian Journal of Geography
66. Papers in Regional Science
67. Political Geography
68. Population Space and Place
69. Professional Geographer
70. Progress in Human Geography
71. Regional Studies
72. Revista de Geografia Norte Grande
73. Revue de Geographie Alpine-Journal of Alpine Research
74. Scottish Geographical Journal
75. Scripta Nova-Revista Electronica de Geografia y Ciencias Sociales
76. Singapore Journal of Tropical Geography
77. Social & Cultural Geography
78. Sociologia Ruralis
79. South African Geographical Journal
80. Space and Culture
81. Territory Politics Governance
82. Tijdschrift voor Economische en Sociale Geografie
83. Transactions in GIS
84. Transactions of the Institute of British Geographers
85. Urban Geography
86. Urban Policy and Research
87. ZFW-Advances in Economic Geography

<a id="ssci-gerontology"></a>

### Gerontology

期刊数：38

1. Ageing & Society
2. Aging & Mental Health
3. American Journal of Geriatric Psychiatry
4. Australasian Journal on Ageing
5. BMC Geriatrics
6. Canadian Journal on Aging-la Revue Canadienne du Vieillissement
7. Clinical Gerontologist
8. Dementia-International Journal of Social Research and Practice
9. Educational Gerontology
10. European Journal of Ageing
11. Generations
12. Geriatric Nursing
13. Geriatrics & Gerontology International
14. Gerontologist
15. Innovation in Aging
16. International Journal of Aging & Human Development
17. International Journal of Geriatric Psychiatry
18. International Journal of Older People Nursing
19. International Psychogeriatrics
20. JMIR Aging
21. Journal of Aging & Social Policy
22. Journal of Aging and Health
23. Journal of Aging and Physical Activity
24. Journal of Aging Studies
25. Journal of Applied Gerontology
26. Journal of Elder Abuse & Neglect
27. Journal of Gerontological Nursing
28. Journal of Gerontological Social Work
29. Journal of the American Geriatrics Society
30. Journal of the Economics of Ageing
31. Journal of Women & Aging
32. Journals of Gerontology Series a-Biological Sciences and Medical Sciences
33. Journals of Gerontology Series B-Psychological Sciences and Social Sciences
34. Psychology and Aging
35. Research on Aging
36. Topics in Geriatric Rehabilitation
37. Turkish Journal of Geriatrics-Turk Geriatri Dergisi
38. Zeitschrift für Gerontologie und Geriatrie

<a id="ssci-green-sustainable-science-technology"></a>

### Green & Sustainable Science & Technology

期刊数：10

1. Energy Efficiency
2. Energy Research & Social Science
3. International Journal of Sustainability in Higher Education
4. International Journal of Sustainable Transportation
5. Journal of Sustainable Tourism
6. Local Environment
7. Nature Sustainability
8. Sustainability
9. Sustainable Development
10. Sustainable Production and Consumption

<a id="ssci-health-policy-services"></a>

### Health Policy & Services

期刊数：87

1. Administration and Policy in Mental Health and Mental Health Services Research
2. AIDS Care-Psychological and Socio-Medical Aspects of AIDS/HIV
3. American Health and Drug Benefits
4. American Journal of Health Economics
5. American Journal of Managed Care
6. Applied Health Economics and Health Policy
7. Asian Journal of WTO & International Health Law and Policy
8. Australian Health Review
9. Australian Journal of Primary Health
10. BMC Palliative Care
11. BMJ Quality & Safety
12. Cambridge Quarterly of Healthcare Ethics
13. Community Mental Health Journal
14. Cost Effectiveness and Resource Allocation
15. Digital Health
16. Disability and Health Journal
17. Eastern Mediterranean Health Journal
18. European Journal of Health Economics
19. Evaluation & the Health Professions
20. Expert Review of Pharmacoeconomics & Outcomes Research
21. Gaceta Sanitaria
22. Health Affairs
23. Health and Quality of Life Outcomes
24. Health Care Analysis
25. Health Care Management Review
26. Health Care Management Science
27. Health Communication
28. Health Economics
29. Health Economics Policy and Law
30. Health Economics Review
31. Health Expectations
32. Health Information Management Journal
33. Health Policy
34. Health Policy and Planning
35. Health Policy and Technology
36. Health Promotion International
37. Health Research Policy and Systems
38. Health Services Research
39. Health Sociology Review
40. Health Systems & Reform
41. Healthcare
42. Healthcare-the Journal of Delivery Science and Innovation
43. Human Resources for Health
44. Implementation Science
45. Inquiry-the Journal of Health Care Organization Provision and Financing
46. International Journal for Quality in Health Care
47. International Journal of Health  Economics and Management
48. International Journal of Health Planning and Management
49. International Journal of Health Policy and Management
50. International Journal of Integrated Care
51. International Journal of Social Determinants of Health and Health Services
52. Israel Journal of Health Policy Research
53. JAMA Health Forum
54. Journal for Healthcare Quality
55. Journal of Aging and Health
56. Journal of Behavioral Health Services & Research
57. Journal of Community Health
58. Journal of Genetic Counseling
59. Journal of Health Care for the Poor and Underserved
60. Journal of Health Economics
61. Journal of Health Organization and Management
62. Journal of Health Politics Policy and Law
63. Journal of Health Services Research & Policy
64. Journal of Healthcare Management
65. Journal of Interprofessional Care
66. Journal of Mental Health Policy and Economics
67. Journal of Palliative Care
68. Journal of Patient Safety
69. Journal of Pediatric Health Care
70. Journal of Policy and Practice in Intellectual Disabilities
71. Journal of Public Health Policy
72. Journal of Rural Health
73. Medical Care
74. Medical Care Research and Review
75. Medical Decision Making
76. Milbank Quarterly
77. Palliative & Supportive Care
78. Patient-Patient Centered Outcomes Research
79. PharmacoEconomics
80. Psychiatric Services
81. Psychology Public Policy and Law
82. Quality Management in Health Care
83. Quality of Life Research
84. Risk Management and Healthcare Policy
85. SAHARA J-Journal of Social Aspects of HIV-AIDS
86. Sciences Sociales et Sante
87. Value in Health

<a id="ssci-history"></a>

### History

期刊数：104

1. Acta Histriae
2. Agricultural History
3. American Historical Review
4. Americas
5. Australian Journal of Politics and History
6. Austrian History Yearbook
7. Ayer
8. BMGN-the Low Countries Historical Review
9. Britain and the World
10. Canadian Historical Review
11. Central European History
12. Cliometrica
13. Cold War History
14. Comparative Studies in Society and History
15. Contemporary European History
16. Continuity and Change
17. Culture & History Digital Journal
18. Diplomacy & Statecraft
19. Diplomatic History
20. Dutch Crossing-Journal of Low Countries Studies
21. Economic History Review
22. English Historical Review
23. Environment and History
24. Environmental History
25. Estudios Atacamenos
26. Ethnohistory
27. European History Quarterly
28. French History
29. Gender and History
30. German History
31. Hahr-Hispanic American Historical Review
32. Historia Agraria
33. Historia Critica
34. Historia y Politica
35. Historical Journal
36. Historical Methods
37. Historical Social Research-Historische Sozialforschung
38. History and Anthropology
39. History and Theory
40. History Workshop Journal
41. Imago Mundi-the International Journal for the History of Cartography
42. Indian Economic and Social History Review
43. Intelligence and National Security
44. International Journal of the History of Sport
45. International Labor and Working-Class History
46. International Review of Social History
47. Interventions-International Journal of Postcolonial Studies
48. Itinerario-Journal of Imperial and Global Interactions
49. Journal of African History
50. Journal of American History
51. Journal of Australian Studies
52. Journal of British Studies
53. Journal of Cold War Studies
54. Journal of Contemporary History
55. Journal of Early Modern History
56. Journal of Family History
57. Journal of Global History
58. Journal of Interdisciplinary History
59. Journal of Israeli History
60. Journal of Modern European History
61. Journal of Modern History
62. Journal of Modern Italian Studies
63. Journal of Policy History
64. Journal of Social History
65. Journal of the Civil War Era
66. Journal of the Economic and Social History of the Orient
67. Journal of the Gilded Age and Progressive Era
68. Journal of the History of Economic Thought
69. Journal of the History of Sexuality
70. Journal of Victorian Culture
71. Journal of Womens History
72. Labour History
73. Labour-le Travail
74. Law and History Review
75. London Journal
76. Management & Organizational History
77. Mediterranean Historical Review
78. Memory Studies
79. Modern Italy
80. Mouvement Social
81. Nationalities Papers-the Journal of Nationalism and Ethnicity
82. Nations and Nationalism
83. Northern History
84. Oral History Review
85. Past & Present
86. Politics Religion & Ideology
87. Postcolonial Studies
88. Psychoanalysis and History
89. Rassegna Storica del Risorgimento
90. Rethinking History
91. Revista de Historia Economica-Journal of Iberian and Latin American Economic History
92. Revista de Historia Industrial
93. Rural History-Economy Society Culture
94. Scandia
95. Scottish Historical Review
96. Social History of Medicine
97. Social Science History
98. Sociology Lens
99. South African Historical Journal
100. South Asia-Journal of South Asian Studies
101. Tijdschrift voor Rechtsgeschiedenis-Revue d Histoire du Droit-the Legal History Review
102. War & Society
103. War in History
104. Zeitgeschichte

<a id="ssci-history-philosophy-of-science"></a>

### History & Philosophy of Science

期刊数：47

1. Agricultural History
2. Agriculture and Human Values
3. Annals of Science
4. Archives of Natural History
5. Berichte zur Wissenschaftsgeschichte
6. Biology & Philosophy
7. Biosemiotics
8. British Journal for the History of Science
9. British Journal for the Philosophy of Science
10. Bulletin of the History of Medicine
11. Centaurus
12. Dynamis
13. Earth Sciences History
14. East Asian Science Technology and Society-an International Journal
15. Engineering Studies
16. Historia Mathematica
17. Historical Studies in the Natural Sciences
18. History and Philosophy of the Life Sciences
19. History of Geo- and Space Sciences
20. History of Science
21. History of the Human Sciences
22. Imago Mundi-the International Journal for the History of Cartography
23. Isis
24. Journal of Responsible Innovation
25. Journal of the History of Biology
26. Journal of the History of Medicine and Allied Sciences
27. Medical History
28. Medicine Health Care and Philosophy
29. Minerva
30. New Genetics and Society
31. Nuncius-Journal of the History of Science
32. Osiris
33. Philosophy Ethics and Humanities in Medicine
34. Philosophy of Science
35. Physics in Perspective
36. Public Understanding of Science
37. Research Integrity and Peer Review
38. Science & Education
39. Science and Technology Studies
40. Science as Culture
41. Science in Context
42. Social Epistemology
43. Social History of Medicine
44. Social Studies of Science
45. Studies in History and Philosophy of Science
46. Synthese
47. Technology and Culture

<a id="ssci-history-of-social-sciences"></a>

### History of Social Sciences

期刊数：34

1. Asia-Pacific Economic History Review
2. Business History
3. Business History Review
4. Cliometrica
5. Economic History Review
6. Enterprise & Society
7. European Journal of the History of Economic Thought
8. European Review of Economic History
9. Explorations in Economic History
10. Historical Social Research-Historische Sozialforschung
11. History of Education
12. History of Political Economy
13. History of Psychiatry
14. History of Psychology
15. History of the Family
16. History of the Human Sciences
17. Imago Mundi-the International Journal for the History of Cartography
18. Information & Culture
19. Journal of Economic History
20. Journal of Family History
21. Journal of Historical Geography
22. Journal of Philosophy of Education
23. Journal of the History of Economic Thought
24. Journal of the History of the Behavioral Sciences
25. Journal of Urban History
26. Labor History
27. Law and History Review
28. Management & Organizational History
29. Paedagogica Historica
30. Planning Perspectives
31. Psychoanalysis and History
32. Revista de Historia Economica-Journal of Iberian and Latin American Economic History
33. Revista de Historia Industrial
34. Social Science History

<a id="ssci-hospitality-leisure-sport-tourism"></a>

### Hospitality, Leisure, Sport & Tourism

期刊数：58

1. Annals of Tourism Research
2. Asia Pacific Journal of Tourism Research
3. Communication & Sport
4. Cornell Hospitality Quarterly
5. Current Issues in Tourism
6. European Sport Management Quarterly
7. Information Technology & Tourism
8. International Journal of Contemporary Hospitality Management
9. International Journal of Hospitality Management
10. International Journal of Sport and Exercise Psychology
11. International Journal of Sport Finance
12. International Journal of Sport Psychology
13. International Journal of Sports Marketing & Sponsorship
14. International Journal of Sports Science & Coaching
15. International Journal of the History of Sport
16. International Journal of Tourism Research
17. International Review for the Sociology of Sport
18. International Review of Sport and Exercise Psychology
19. Journal of Applied Sport Psychology
20. Journal of Destination Marketing & Management
21. Journal of Hospitality & Tourism Research
22. Journal of Hospitality and Tourism Management
23. Journal of Hospitality and Tourism Technology
24. Journal of Hospitality Leisure Sport & Tourism Education
25. Journal of Hospitality Marketing & Management
26. Journal of Leisure Research
27. Journal of Outdoor Recreation and Tourism-Research Planning and Management
28. Journal of Sport & Exercise Psychology
29. Journal of Sport & Social Issues
30. Journal of Sport and Health Science
31. Journal of Sport Management
32. Journal of Sports Economics
33. Journal of Sustainable Tourism
34. Journal of the Philosophy of Sport
35. Journal of Tourism and Cultural Change
36. Journal of Travel & Tourism Marketing
37. Journal of Travel Research
38. Journal of Vacation Marketing
39. Leisure Sciences
40. Leisure Studies
41. Measurement in Physical Education and Exercise Science
42. Psychology of Sport and Exercise
43. Qualitative Research in Sport Exercise and Health
44. Research Quarterly for Exercise and Sport
45. Scandinavian Journal of Hospitality and Tourism
46. Sociology of Sport Journal
47. Sport Education and Society
48. Sport Exercise and Performance Psychology
49. Sport in Society
50. Sport Management Review
51. Sport Marketing Quarterly
52. Sport Psychologist
53. Tourism Economics
54. Tourism Geographies
55. Tourism Management
56. Tourism Management Perspectives
57. Tourism Review
58. Tourist Studies

<a id="ssci-industrial-relations-labor"></a>

### Industrial Relations & Labor

期刊数：32

1. Asia Pacific Journal of Human Resources
2. British Journal of Industrial Relations
3. Economic and Industrial Democracy
4. Economic and Labour Relations Review
5. Employee Relations
6. European Journal of Industrial Relations
7. German Journal of Human Resource Management-Zeitschrift für Personalforschung
8. Human Resource Development Quarterly
9. Human Resource Management Journal
10. Human Resources for Health
11. ILR Review
12. Industrial Law Journal
13. Industrial Relations
14. International Journal of Manpower
15. International Labor and Working-Class History
16. International Labour Review
17. Journal of Human Resources
18. Journal of Industrial Relations
19. Journal of Labor Economics
20. Journal of Labor Research
21. Labor History
22. Labour History
23. Labour-le Travail
24. Monthly Labor Review
25. New Technology Work and Employment
26. Personnel Review
27. Public Personnel Management
28. Relations Industrielles-Industrial Relations
29. Transfer-European Review of Labour and Research
30. Work Aging and Retirement
31. Work and Occupations
32. Work Employment and Society

<a id="ssci-information-science-library-science"></a>

### Information Science & Library Science

期刊数：80

1. African Journal of Library Archives and Information Science
2. Aslib Journal of Information Management
3. Canadian Journal of Information and Library Science-Revue Canadienne des Sciences de l Information et de Bibliotheconomie
4. College & Research Libraries
5. Data Base for Advances in Information Systems
6. Data Technologies and Applications
7. Electronic Library
8. Ethics and Information Technology
9. European Journal of Information Systems
10. Government Information Quarterly
11. Health Information and Libraries Journal
12. Informacao & Sociedade-Estudos
13. Informacios Tarsadalom
14. Information & Culture
15. Information & Management
16. Information and Organization
17. Information Development
18. Information Processing & Management
19. Information Research-an International Electronic Journal
20. Information Society
21. Information Systems Journal
22. Information Systems Research
23. Information Technology & Management
24. Information Technology & People
25. Information Technology and Libraries
26. Information Technology for Development
27. International Journal of Computer-Supported Collaborative Learning
28. International Journal of Geographical Information Science
29. International Journal of Information Management
30. Investigacion Bibliotecologica
31. Journal of Academic Librarianship
32. Journal of Computer-Mediated Communication
33. Journal of Documentation
34. Journal of Enterprise Information Management
35. Journal of Global Information Management
36. Journal of Global Information Technology Management
37. Journal of Health Communication
38. Journal of Information Science
39. Journal of Information Technology
40. Journal of Informetrics
41. Journal of Knowledge Management
42. Journal of Librarianship and Information Science
43. Journal of Management Information Systems
44. Journal of Organizational and End User Computing
45. Journal of Scholarly Publishing
46. Journal of Strategic Information Systems
47. Journal of the American Medical Informatics Association
48. Journal of the Association for Information Science and Technology
49. Journal of the Association for Information Systems
50. Journal of the Australian Library and Information Association
51. Journal of the Medical Library Association
52. Knowledge Management Research & Practice
53. Knowledge Organization
54. Law Library Journal
55. Learned Publishing
56. Library & Information Science Research
57. Library and Information Science
58. Library Journal
59. Library Quarterly
60. Library Resources & Technical Services
61. Library Trends
62. Libri-International Journal of Libraries and Information Studies
63. Malaysian Journal of Library & Information Science
64. MIS Quarterly
65. MIS Quarterly Executive
66. Online Information Review
67. Portal-Libraries and the Academy
68. Qualitative Health Research
69. Reference Services Review
70. Research Evaluation
71. Revista Espanola de Documentacion Cientifica
72. Scientist
73. Scientometrics
74. Serials Review
75. Social Science Computer Review
76. Social Science Information sur les Sciences Sociales
77. Telecommunications Policy
78. Telematics and Informatics
79. Transinformacao
80. Zeitschrift für Bibliothekswesen und Bibliographie

<a id="ssci-international-relations"></a>

### International Relations

期刊数：97

1. Alternatives
2. American Journal of International Law
3. Asia Europe Journal
4. Asian Journal of WTO & International Health Law and Policy
5. Asian Perspective
6. Australian Journal of International Affairs
7. British Journal of Politics & International Relations
8. Bulletin of the Atomic Scientists
9. Business and Politics
10. Cambridge Review of International Affairs
11. Chinese Journal of International Law
12. Chinese Journal of International Politics
13. Columbia Journal of Transnational Law
14. Common Market Law Review
15. Communist and Post-Communist Studies
16. Conflict Management and Peace Science
17. Contemporary Security Policy
18. Contemporary Southeast Asia
19. Cooperation and Conflict
20. Cornell International Law Journal
21. Current History
22. Diplomacy & Statecraft
23. Emerging Markets Finance and Trade
24. Ethics & International Affairs
25. European Journal of International Law
26. European Journal of International Relations
27. European Security
28. Foreign Affairs
29. Foreign Policy Analysis
30. Global Environmental Politics
31. Global Governance
32. Global Policy
33. Globalizations
34. Human Rights Law Review
35. Intelligence and National Security
36. Internasjonal Politikk
37. International Affairs
38. International Interactions
39. International Journal
40. International Journal of Conflict and Violence
41. International Journal of Transitional Justice
42. International Organization
43. International Peacekeeping
44. International Political Sociology
45. International Politics
46. International Relations
47. International Relations of the Asia-Pacific
48. International Security
49. International Studies Perspectives
50. International Studies Quarterly
51. International Studies Review
52. International Theory
53. JCMS-Journal of Common Market Studies
54. Journal of Cold War Studies
55. Journal of Conflict Resolution
56. Journal of Contemporary European Studies
57. Journal of Current Southeast Asian Affairs
58. Journal of European Integration
59. Journal of Human Rights
60. Journal of International Relations and Development
61. Journal of Intervention and Statebuilding
62. Journal of Peace Research
63. Journal of Strategic Studies
64. Journal of the Japanese and International Economies
65. Journal of World Trade
66. Korea Observer
67. Korean Journal of Defense Analysis
68. Latin American Politics and Society
69. Marine Policy
70. Mediterranean Politics
71. Middle East Policy
72. Millennium-Journal of International Studies
73. New Political Economy
74. Ocean Development and International Law
75. Pacific Focus
76. Pacific Review
77. Peacebuilding
78. Political Studies
79. Politics
80. Review of International Organizations
81. Review of International Political Economy
82. Review of International Studies
83. Review of World Economics
84. Revista Brasileira de Politica Internacional
85. Security Dialogue
86. Security Studies
87. Space Policy
88. Studies in Comparative International Development
89. Studies in Conflict & Terrorism
90. Survival
91. Terrorism and Political Violence
92. Uluslararasi Iliskiler-International Relations
93. War in History
94. Washington Quarterly
95. World Economy
96. World Politics
97. World Trade Review

<a id="ssci-law"></a>

### Law

期刊数：156

1. American Bankruptcy Law Journal
2. American Business Law Journal
3. American Criminal Law Review
4. American Journal of Comparative Law
5. American Journal of International Law
6. American Journal of Law & Medicine
7. American Law and Economics Review
8. Annual Review of Law and Social Science
9. Anuario de Psicologia Juridica
10. Artificial Intelligence and Law
11. Asia Pacific Law Review
12. Asian Journal of WTO & International Health Law and Policy
13. Behavioral Sciences & the Law
14. Boston University Law Review
15. Buffalo Law Review
16. California Law Review
17. Cambridge Law Journal
18. Catholic University Law Review
19. Chinese Journal of International Law
20. Columbia Journal of Law and Social Problems
21. Columbia Journal of Transnational Law
22. Columbia Law Review
23. Common Market Law Review
24. Computer Law & Security Review
25. Cornell International Law Journal
26. Cornell Law Review
27. Current Legal Problems
28. Denver Law Review
29. Duke Law Journal
30. Ecology Law Quarterly
31. European Business Organization Law Review
32. European Constitutional Law Review
33. European Journal of International Law
34. European Journal of Law and Economics
35. European Journal of Migration and Law
36. European Journal of Psychology Applied to Legal Context
37. European Law Journal
38. European Law Review
39. Feminist Legal Studies
40. Food and Drug Law Journal
41. Fordham Law Review
42. George Washington Law Review
43. Georgetown Law Journal
44. Hague Journal on the Rule of Law
45. Harvard Civil Rights-Civil Liberties Law Review
46. Harvard Environmental Law Review
47. Harvard International Law Journal
48. Harvard Journal of Law and Public Policy
49. Harvard Journal on Legislation
50. Harvard Law Review
51. Hastings Law Journal
52. Hong Kong Law Journal
53. Human Rights Law Review
54. Icon-International Journal of Constitutional Law
55. ICSID Review-Foreign Investment Law Journal
56. Indiana Law Journal
57. Industrial Law Journal
58. International & Comparative Law Quarterly
59. International Data Privacy Law
60. International Environmental Agreements-Politics Law and Economics
61. International Insolvency Review
62. International Journal of Evidence & Proof
63. International Journal of Human Rights
64. International Journal of Law and Psychiatry
65. International Journal of Law Crime and Justice
66. International Journal of Law in Context
67. International Journal of Law Policy and the Family
68. International Journal of Marine and Coastal Law
69. International Journal of Transitional Justice
70. International Review of Law and Economics
71. International Review of the Red Cross
72. Iowa Law Review
73. Issues in Law & Medicine
74. Journal of African Law
75. Journal of Competition Law & Economics
76. Journal of Corporate Law Studies
77. Journal of Criminal Law & Criminology
78. Journal of Empirical Legal Studies
79. Journal of Energy & Natural Resources Law
80. Journal of Environmental Law
81. Journal of International Criminal Justice
82. Journal of International Dispute Settlement
83. Journal of International Economic Law
84. Journal of Law & Economics
85. Journal of Law and Society
86. Journal of Law and the Biosciences
87. Journal of Law Economics & Organization
88. Journal of Law Medicine & Ethics
89. Journal of Legal Analysis
90. Journal of Legal Education
91. Journal of Legal Medicine
92. Journal of Legal Studies
93. Journal of the American Academy of Psychiatry and the Law
94. Journal of the Copyright Society of the USA
95. Journal of World Energy Law & Business
96. Journal of World Trade
97. Juvenile and Family Court Journal
98. Law & Policy
99. Law & Social Inquiry
100. Law & Society Review
101. Law and History Review
102. Law and Human Behavior
103. Law and Philosophy
104. Law Library Journal
105. Law Probability & Risk
106. Legal and Criminological Psychology
107. Legal Studies
108. Leiden Journal of International Law
109. Medical Law Review
110. Medicine Science and the Law
111. Melbourne University Law Review
112. Michigan Law Review
113. Minnesota Law Review
114. Modern Law Review
115. Natural Resources Journal
116. Netherlands Quarterly of Human Rights
117. New York University Law Review
118. Northwestern Journal of International Law & Business
119. Northwestern University Law Review
120. Notre Dame Law Review
121. Ocean Development and International Law
122. Oxford Journal of Legal Studies
123. Psychiatry Psychology and Law
124. Psychology Crime & Law
125. Psychology Public Policy and Law
126. Queen Mary Journal of Intellectual Property
127. Regulation & Governance
128. Review of Central and East European Law
129. Review of European Comparative & International Environmental Law
130. Revista Chilena de Derecho
131. Revista Espanola de Derecho Constitucional
132. Rutgers University Law Review
133. Social & Legal Studies
134. South African Journal on Human Rights
135. Southern California Law Review
136. Stanford Law Review
137. Supreme Court Review
138. Texas Law Review
139. Tijdschrift voor Rechtsgeschiedenis-Revue d Histoire du Droit-the Legal History Review
140. Transnational Environmental Law
141. Ucla Law Review
142. University of Chicago Law Review
143. University of Cincinnati Law Review
144. University of Illinois Law Review
145. University of Pennsylvania Journal of International Law
146. University of Pennsylvania Law Review
147. University of Pittsburgh Law Review
148. University of Toronto Law Journal
149. Vanderbilt Law Review
150. Virginia Law Review
151. Washington Law Review
152. Washington Quarterly
153. Wisconsin Law Review
154. World Trade Review
155. Yale Journal on Regulation
156. Yale Law Journal

<a id="ssci-linguistics"></a>

### Linguistics

期刊数：195

1. Across Languages and Cultures
2. Acta Linguistica Academica
3. Africana Linguistica
4. American Journal of Speech-Language Pathology
5. American Speech
6. Annual Review of Applied Linguistics
7. Annual Review of Linguistics
8. Aphasiology
9. Applied Linguistics
10. Applied Linguistics Review
11. Applied Psycholinguistics
12. Argumentation
13. Assessing Writing
14. Atlantis-Journal of the Spanish Association of Anglo-American Studies
15. Australian Journal of Linguistics
16. Babel-Revue Internationale de la Traduction-International Journal of Translation
17. Bilingualism-Language and Cognition
18. Brain and Language
19. Canadian Modern Language Review-Revue Canadienne des Langues Vivantes
20. Child Language Teaching & Therapy
21. Circulo de Linguistica Aplicada a la Comunicacion
22. Clinical Linguistics & Phonetics
23. Cognitive Linguistics
24. Communication Disorders Quarterly
25. Computational Linguistics
26. Computer Assisted Language Learning
27. Corpus Linguistics and Linguistic Theory
28. Current Issues in Language Planning
29. Diachronica
30. Dialectologia et Geolinguistica
31. Digital Scholarship in the Humanities
32. ELT Journal
33. English for Specific Purposes
34. English Language & Linguistics
35. English Teaching-Practice and Critique
36. English Today
37. English World-Wide
38. Estudios Filologicos
39. European Journal of English Studies
40. First Language
41. Folia Linguistica
42. Foreign Language Annals
43. Functions of Language
44. Gender and Language
45. Gesture
46. Glossa-a Journal of General Linguistics
47. Hispania-a Journal Devoted to the Teaching of Spanish and Portuguese
48. Historiographia Linguistica
49. Iberica
50. Indogermanische Forschungen
51. Innovation in Language Learning and Teaching
52. Interaction Studies
53. Intercultural Pragmatics
54. International Journal of American Linguistics
55. International Journal of Applied Linguistics
56. International Journal of Bilingual Education and Bilingualism
57. International Journal of Bilingualism
58. International Journal of Corpus Linguistics
59. International Journal of Language & Communication Disorders
60. International Journal of Lexicography
61. International Journal of Multilingualism
62. International Journal of Speech Language and the Law
63. International Journal of Speech-Language Pathology
64. International Multilingual Research Journal
65. Interpreter and Translator Trainer
66. Interpreting
67. IRAL-International Review of Applied Linguistics in Language Teaching
68. Journal of African Languages and Linguistics
69. Journal of Child Language
70. Journal of Chinese Linguistics
71. Journal of Communication Disorders
72. Journal of Comparative Germanic Linguistics
73. Journal of East Asian Linguistics
74. Journal of English for Academic Purposes
75. Journal of English Linguistics
76. Journal of Fluency Disorders
77. Journal of French Language Studies
78. Journal of Germanic Linguistics
79. Journal of Historical Pragmatics
80. Journal of Language and Politics
81. Journal of Language and Social Psychology
82. Journal of Language Identity and Education
83. Journal of Linguistic Anthropology
84. Journal of Linguistics
85. Journal of Memory and Language
86. Journal of Multilingual and Multicultural Development
87. Journal of Neurolinguistics
88. Journal of Phonetics
89. Journal of Pidgin and Creole Languages
90. Journal of Politeness Research-Language Behaviour Culture
91. Journal of Pragmatics
92. Journal of Psycholinguistic Research
93. Journal of Quantitative Linguistics
94. Journal of Second Language Writing
95. Journal of Semantics
96. Journal of Sociolinguistics
97. Journal of Specialised Translation
98. Journal of Speech Language and Hearing Research
99. Journal of the International Phonetic Association
100. Laboratory Phonology
101. Langages
102. Language
103. Language & Communication
104. Language & History
105. Language Acquisition
106. Language and Cognition
107. Language and Education
108. Language and Intercultural Communication
109. Language and Linguistics
110. Language and Literature
111. Language and Speech
112. Language Assessment Quarterly
113. Language Awareness
114. Language Cognition and Neuroscience
115. Language Culture and Curriculum
116. Language in Society
117. Language Learning
118. Language Learning & Technology
119. Language Learning and Development
120. Language Matters
121. Language Policy
122. Language Problems & Language Planning
123. Language Sciences
124. Language Speech and Hearing Services in Schools
125. Language Teaching
126. Language Teaching Research
127. Language Testing
128. Language Variation and Change
129. Lexikos
130. Lingua
131. Linguistic Approaches to Bilingualism
132. Linguistic Inquiry
133. Linguistic Review
134. Linguistic Typology
135. Linguistica Antverpiensia New Series-Themes in Translation Studies
136. Linguistics
137. Linguistics and Education
138. Linguistics and Philosophy
139. Linguistics Vanguard
140. Literacy
141. Metaphor and Symbol
142. Mind & Language
143. Modern Language Journal
144. Multilingua-Journal of Cross-Cultural and Interlanguage Communication
145. Names-a Journal of Onomastics
146. Narrative Inquiry
147. Natural Language & Linguistic Theory
148. Natural Language Processing
149. Natural Language Semantics
150. Nordic Journal of Linguistics
151. Onomazein
152. Perspectives-Studies in Translation Theory and Practice
153. Phonetica
154. Phonology
155. Porta Linguarum
156. Poznan Studies in Contemporary Linguistics
157. Pragmatics
158. Pragmatics & Cognition
159. Pragmatics and Society
160. Probus
161. ReCALL
162. RELC Journal
163. Research on Language and Social Interaction
164. Review of Cognitive Linguistics
165. Revista Espanola de Linguistica Aplicada
166. Revista Signos
167. Revue Roumaine de Linguistique-Romanian Review of Linguistics
168. Rilce-Revista de Filologia Hispanica
169. RLA-Revista de Linguistica Teorica y Aplicada
170. Second Language Research
171. Signs and Society
172. Sintagma
173. Slovo a Slovesnost
174. Social Semiotics
175. Southern African Linguistics and Applied Language Studies
176. Spanish in Context
177. Studies in Language
178. Studies in Second Language Acquisition
179. Studies in Second Language Learning and Teaching
180. Syntax-a Journal of Theoretical Experimental and Interdisciplinary Research
181. System
182. Target-International Journal of Translation Studies
183. Terminology
184. TESOL Quarterly
185. Text & Talk
186. Theoretical Linguistics
187. Topics in Language Disorders
188. Transactions of the Association for Computational Linguistics
189. Translation and Interpreting Studies
190. Translation Studies
191. Translator
192. Vial-Vigo International Journal of Applied Linguistics
193. World Englishes
194. Zeitschrift für Dialektologie und Linguistik
195. Zeitschrift für Sprachwissenschaft

<a id="ssci-management"></a>

### Management

期刊数：231

1. Academia-Revista Latinoamericana de Administracion
2. Academy of Management Annals
3. Academy of Management Discoveries
4. Academy of Management Journal
5. Academy of Management Learning & Education
6. Academy of Management Perspectives
7. Academy of Management Review
8. Action Research
9. Administrative Science Quarterly
10. Amfiteatru Economic
11. Annual Review of Organizational Psychology and Organizational Behavior
12. Asia Pacific Business Review
13. Asia Pacific Journal of Human Resources
14. Asia Pacific Journal of Management
15. Asian Business & Management
16. Australian Journal of Management
17. Baltic Journal of Management
18. Betriebswirtschaftliche Forschung und Praxis
19. British Journal of Management
20. BRQ-Business Research Quarterly
21. Business Process Management Journal
22. Business Strategy and the Environment
23. California Management Review
24. Canadian Journal of Administrative Sciences-Revue Canadienne des Sciences de l Administration
25. Career Development International
26. Chinese Management Studies
27. Computational Economics
28. Cornell Hospitality Quarterly
29. Corporate Governance-an International Review
30. Corporate Social Responsibility and Environmental Management
31. Creativity and Innovation Management
32. Cross Cultural & Strategic Management
33. Culture and Organization
34. Decision Analysis
35. Decision Sciences
36. Disaster Prevention and Management
37. E & M Ekonomie a Management
38. Electronic Commerce Research
39. Electronic Markets
40. Employee Relations
41. Engineering Construction and Architectural Management
42. Engineering Economist
43. Engineering Management Journal
44. Eurasian Business Review
45. European Journal of Information Systems
46. European Journal of Innovation Management
47. European Journal of International Management
48. European Journal of Work and Organizational Psychology
49. European Management Journal
50. European Management Review
51. European Research on Management and Business Economics
52. European Sport Management Quarterly
53. Gender in Management
54. Gender Work and Organization
55. German Journal of Human Resource Management-Zeitschrift für Personalforschung
56. Global Strategy Journal
57. Group & Organization Management
58. Group Decision and Negotiation
59. Harvard Business Review
60. Human Relations
61. Human Resource Development Quarterly
62. Human Resource Development Review
63. Human Resource Management
64. Human Resource Management Journal
65. Human Resource Management Review
66. IEEE Transactions on Engineering Management
67. IMA Journal of Management Mathematics
68. Industrial and Corporate Change
69. Industrial Marketing Management
70. Industry and Innovation
71. Information & Management
72. Information and Organization
73. Information Systems and e-Business Management
74. Information Systems Research
75. Information Technology & Management
76. INFORMS Journal on Applied Analytics
77. Innovation-Organization & Management
78. International Business Review
79. International Entrepreneurship and Management Journal
80. International Journal of Accounting Information Systems
81. International Journal of Arts Management
82. International Journal of Contemporary Hospitality Management
83. International Journal of Emerging Markets
84. International Journal of Entrepreneurial Behavior & Research
85. International Journal of Forecasting
86. International Journal of Human Resource Management
87. International Journal of Islamic and Middle Eastern Finance and Management
88. International Journal of Lean Six Sigma
89. International Journal of Logistics Management
90. International Journal of Logistics-Research and Applications
91. International Journal of Management Education
92. International Journal of Management Reviews
93. International Journal of Managing Projects in Business
94. International Journal of Manpower
95. International Journal of Operations & Production Management
96. International Journal of Physical Distribution & Logistics Management
97. International Journal of Project Management
98. International Journal of Retail & Distribution Management
99. International Journal of Selection and Assessment
100. International Journal of Shipping and Transport Logistics
101. International Journal of Strategic Property Management
102. International Journal of Technology Management
103. International Small Business Journal-Researching Entrepreneurship
104. International Transactions in Operational Research
105. Journal of Applied Behavioral Science
106. Journal of Applied Psychology
107. Journal of Brand Management
108. Journal of Business Logistics
109. Journal of Competitiveness
110. Journal of Contingencies and Crisis Management
111. Journal of Destination Marketing & Management
112. Journal of East European Management Studies
113. Journal of Economics & Management Strategy
114. Journal of Engineering and Technology Management
115. Journal of Enterprise Information Management
116. Journal of Family Business Strategy
117. Journal of Fashion Marketing and Management
118. Journal of Forecasting
119. Journal of Hospitality and Tourism Management
120. Journal of Hospitality Marketing & Management
121. Journal of Information Technology
122. Journal of Innovation & Knowledge
123. Journal of Intellectual Capital
124. Journal of International Business Studies
125. Journal of International Management
126. Journal of Knowledge Management
127. Journal of Leadership & Organizational Studies
128. Journal of Management
129. Journal of Management & Organization
130. Journal of Management Analytics
131. Journal of Management Information Systems
132. Journal of Management Inquiry
133. Journal of Management Studies
134. Journal of Managerial Psychology
135. Journal of Manufacturing Technology Management
136. Journal of Marketing Management
137. Journal of Nursing Management
138. Journal of Occupational and Organizational Psychology
139. Journal of Operations Management
140. Journal of Organizational and End User Computing
141. Journal of Organizational Behavior
142. Journal of Organizational Behavior Management
143. Journal of Organizational Change Management
144. Journal of Product and Brand Management
145. Journal of Product Innovation Management
146. Journal of Purchasing and Supply Management
147. Journal of Responsible Innovation
148. Journal of Service Management
149. Journal of Service Research
150. Journal of Service Theory and Practice
151. Journal of Small Business Management
152. Journal of Sport Management
153. Journal of Strategic Information Systems
154. Journal of Supply Chain Management
155. Journal of Technology Transfer
156. Journal of the Operational Research Society
157. Knowledge Management Research & Practice
158. Leadership
159. Leadership & Organization Development Journal
160. Leadership Quarterly
161. Long Range Planning
162. M&Som-Manufacturing & Service Operations Management
163. Management & Organizational History
164. Management Accounting Research
165. Management and Organization Review
166. Management Communication Quarterly
167. Management Decision
168. Management International Review
169. Management Learning
170. Management Science
171. Managerial and Decision Economics
172. Managerial Auditing Journal
173. MIS Quarterly
174. MIS Quarterly Executive
175. MIT Sloan Management Review
176. Negotiation and Conflict Management Research
177. Negotiation Journal
178. New Technology Work and Employment
179. Nonprofit Management & Leadership
180. Omega-International Journal of Management Science
181. Operations Management Research
182. Operations Research
183. Organization
184. Organization & Environment
185. Organization Science
186. Organization Studies
187. Organizational Behavior and Human Decision Processes
188. Organizational Dynamics
189. Organizational Psychology Review
190. Organizational Research Methods
191. Personnel Psychology
192. Personnel Review
193. Project Management Journal
194. Public Management Review
195. Qualitative Research in Accounting and Management
196. R & d Management
197. RAE-Revista de Administracao de Empresas
198. Rbgn-Revista Brasileira de Gestao de Negocios
199. Research in Organizational Behavior
200. Research in Transportation Business and Management
201. Research Policy
202. Research-Technology Management
203. Review of Industrial Organization
204. Review of Managerial Science
205. Scandinavian Journal of Management
206. Science and Public Policy
207. Science Technology and Society
208. Service Business
209. Service Industries Journal
210. Service Science
211. Small Business Economics
212. Small Group Research
213. Socio-Economic Planning Sciences
214. South African Journal of Business Management
215. South African Journal of Economic and Management Sciences
216. Sport Management Review
217. Strategic Entrepreneurship Journal
218. Strategic Management Journal
219. Strategic Organization
220. Supply Chain Management-an International Journal
221. Sustainability Accounting Management and Policy Journal
222. System Dynamics Review
223. Systemic Practice and Action Research
224. Systems Research and Behavioral Science
225. Technology Analysis & Strategic Management
226. Technovation
227. Total Quality Management & Business Excellence
228. Tourism Management
229. Tourism Management Perspectives
230. Transportation Journal
231. Work Aging and Retirement

<a id="ssci-nursing"></a>

### Nursing

期刊数：123

1. Acta Paulista de Enfermagem
2. Advances in Neonatal Care
3. Advances in Nursing Science
4. Advances in Skin & Wound Care
5. American Journal of Nursing
6. AORN Journal
7. Applied Nursing Research
8. Archives of Psychiatric Nursing
9. Asia-Pacific Journal of Oncology Nursing
10. Asian Nursing Research
11. Assistenza Infermieristica e Ricerca
12. Australasian Emergency Care
13. Australian Critical Care
14. Australian Journal of Advanced Nursing
15. Australian Journal of Rural Health
16. Bariatric Surgical Practice and Patient Care
17. Birth-Issues in Perinatal Care
18. BMC Nursing
19. Cancer Nursing
20. CIN-Computers Informatics Nursing
21. Clinical Journal of Oncology Nursing
22. Clinical Nurse Specialist
23. Clinical Nursing Research
24. Clinical Simulation in Nursing
25. Collegian
26. Contemporary Nurse
27. Critical Care Nurse
28. Critical Care Nursing Clinics of North America
29. European Journal of Cancer Care
30. European Journal of Cardiovascular Nursing
31. European Journal of Oncology Nursing
32. Gastroenterology Nursing
33. Geriatric Nursing
34. Holistic Nursing Practice
35. Intensive and Critical Care Nursing
36. International Emergency Nursing
37. International Journal of Mental Health Nursing
38. International Journal of Nursing Knowledge
39. International Journal of Nursing Practice
40. International Journal of Nursing Studies
41. International Journal of Older People Nursing
42. International Journal of Qualitative Studies on Health and Well-Being
43. International Nursing Review
44. Issues in Mental Health Nursing
45. JANAC-Journal of the Association of Nurses in AIDS Care
46. Japan Journal of Nursing Science
47. Jnp- the Journal for Nurse Practitioners
48. Jognn-Journal of Obstetric Gynecologic and Neonatal Nursing
49. Journal for Specialists in Pediatric Nursing
50. Journal of Addictions Nursing
51. Journal of Advanced Nursing
52. Journal of Cardiovascular Nursing
53. Journal of Child Health Care
54. Journal of Clinical Nursing
55. Journal of Community Health Nursing
56. Journal of Continuing Education in Nursing
57. Journal of Emergency Nursing
58. Journal of Family Nursing
59. Journal of Forensic Nursing
60. Journal of Gerontological Nursing
61. Journal of Hospice & Palliative Nursing
62. Journal of Korean Academy of Nursing
63. Journal of Midwifery & Womens Health
64. Journal of Neuroscience Nursing
65. Journal of Nursing Administration
66. Journal of Nursing Care Quality
67. Journal of Nursing Education
68. Journal of Nursing Management
69. Journal of Nursing Regulation
70. Journal of Nursing Research
71. Journal of Nursing Scholarship
72. Journal of Pediatric Health Care
73. Journal of Pediatric Hematology-Oncology Nursing
74. Journal of Pediatric Nursing-Nursing Care of Children & Families
75. Journal of PeriAnesthesia Nursing
76. Journal of Perinatal & Neonatal Nursing
77. Journal of Professional Nursing
78. Journal of Psychiatric and Mental Health Nursing
79. Journal of Psychosocial Nursing and Mental Health Services
80. Journal of Renal Care
81. Journal of School Nursing
82. Journal of the American Association of Nurse Practitioners
83. Journal of the American Psychiatric Nurses Association
84. Journal of Tissue Viability
85. Journal of Transcultural Nursing
86. Journal of Trauma Nursing
87. Journal of Wound Ostomy and Continence Nursing
88. MCN-the American Journal of Maternal-Child Nursing
89. Midwifery
90. Nephrology Nursing Journal
91. Nurse Education in Practice
92. Nurse Education Today
93. Nurse Educator
94. Nursing & Health Sciences
95. Nursing Clinics of North America
96. Nursing Economics
97. Nursing Ethics
98. Nursing in Critical Care
99. Nursing Inquiry
100. Nursing Open
101. Nursing Outlook
102. Nursing Philosophy
103. Nursing Research
104. Nursing Science Quarterly
105. Oncology Nursing Forum
106. Orthopaedic Nursing
107. Pain Management Nursing
108. Perspectives in Psychiatric Care
109. Pflege
110. Public Health Nursing
111. Rehabilitation Nursing
112. Research and Theory for Nursing Practice
113. Research in Gerontological Nursing
114. Research in Nursing & Health
115. Revista da Escola de Enfermagem da USP
116. Revista Latino-Americana de Enfermagem
117. Scandinavian Journal of Caring Sciences
118. Seminars in Oncology Nursing
119. Western Journal of Nursing Research
120. Women and Birth
121. Workplace Health & Safety
122. Worldviews on Evidence-Based Nursing
123. Wound Management & Prevention

<a id="ssci-political-science"></a>

### Political Science

期刊数：188

1. Acta Politica
2. African Affairs
3. American Journal of Political Science
4. American Political Science Review
5. American Politics Research
6. Annals of the American Academy of Political and Social Science
7. Annual Review of Political Science
8. Armed Forces & Society
9. Australian Journal of Political Science
10. Australian Journal of Politics and History
11. Austrian Journal of Political Science
12. British Journal of Political Science
13. British Journal of Politics & International Relations
14. British Politics
15. Business and Politics
16. Cambridge Review of International Affairs
17. Canadian Journal of Political Science-Revue Canadienne de Science Politique
18. Citizenship Studies
19. Communist and Post-Communist Studies
20. Comparative European Politics
21. Comparative Political Studies
22. Comparative Politics
23. Contemporary Political Theory
24. Contemporary Politics
25. Contemporary Security Policy
26. Contemporary Southeast Asia
27. Cooperation and Conflict
28. Critical Policy Studies
29. Critical Review
30. Current History
31. Democratization
32. Dissent
33. East European Politics
34. East European Politics and Societies
35. Economics & Politics
36. Electoral Studies
37. Environmental Politics
38. Ethics & Global Politics
39. Ethics & International Affairs
40. Europe-Asia Studies
41. European History Quarterly
42. European Journal of Political Economy
43. European Journal of Political Research
44. European Political Science
45. European Political Science Review
46. European Security
47. European Union Politics
48. Forum-a Journal of Applied Research in Contemporary Politics
49. Geopolitics
50. German Politics
51. Global Environmental Politics
52. Global Policy
53. Governance-an International Journal of Policy Administration and Institutions
54. Government and Opposition
55. Historia y Politica
56. Historical Materialism-Research in Critical Marxist Theory
57. Human Rights Quarterly
58. Independent Review
59. Intelligence and National Security
60. Internasjonal Politikk
61. International Environmental Agreements-Politics Law and Economics
62. International Feminist Journal of Politics
63. International Journal of Conflict and Violence
64. International Journal of Press-Politics
65. International Journal of Public Opinion Research
66. International Journal of the Commons
67. International Journal of Transitional Justice
68. International Organization
69. International Political Science Review
70. International Political Sociology
71. International Politics
72. International Studies Quarterly
73. International Studies Review
74. International Theory
75. Irish Political Studies
76. Japanese Journal of Political Science
77. JCMS-Journal of Common Market Studies
78. Journal of Australian Political Economy
79. Journal of Chinese Governance
80. Journal of Chinese Political Science
81. Journal of Cold War Studies
82. Journal of Conflict Resolution
83. Journal of Contemporary European Studies
84. Journal of Current Southeast Asian Affairs
85. Journal of Democracy
86. Journal of Elections Public Opinion and Parties
87. Journal of European Integration
88. Journal of European Public Policy
89. Journal of Human Rights
90. Journal of Information Technology & Politics
91. Journal of International Relations and Development
92. Journal of Peace Research
93. Journal of Policy History
94. Journal of Political Ideologies
95. Journal of Politics
96. Journal of Public Administration Research and Theory
97. Journal of Public Policy
98. Journal of Strategic Studies
99. Journal of Theoretical Politics
100. Journal of Women Politics & Policy
101. Latin American Perspectives
102. Latin American Politics and Society
103. Legislative Studies Quarterly
104. Local Government Studies
105. Mediterranean Politics
106. Monthly Review-an Independent Socialist Magazine
107. Nation
108. Nationalities Papers-the Journal of Nationalism and Ethnicity
109. Nations and Nationalism
110. New Left Review
111. New Political Economy
112. New Republic
113. Osteuropa
114. Parliamentary Affairs
115. Party Politics
116. Peacebuilding
117. Perspectives on Politics
118. Philosophy & Public Affairs
119. Policy and Internet
120. Policy and Politics
121. Policy and Society
122. Policy Studies
123. Policy Studies Journal
124. Politica y Gobierno
125. Political Analysis
126. Political Behavior
127. Political Communication
128. Political Geography
129. Political Psychology
130. Political Quarterly
131. Political Research Quarterly
132. Political Science
133. Political Science Quarterly
134. Political Science Research and Methods
135. Political Studies
136. Political Studies Review
137. Political Theory
138. Politicka Ekonomie
139. Politics
140. Politics & Gender
141. Politics & Society
142. Politics and Governance
143. Politics and Religion
144. Politics Groups and Identities
145. Politics Philosophy & Economics
146. Politics Religion & Ideology
147. Politikon
148. Politische Vierteljahresschrift
149. Politix
150. Polity
151. Post-Soviet Affairs
152. Presidential Studies Quarterly
153. Problems of Post-Communism
154. PS-Political Science & Politics
155. Public Administration
156. Public Choice
157. Public Opinion Quarterly
158. Publius-the Journal of Federalism
159. Quarterly Journal of Political Science
160. Regulation & Governance
161. Research & Politics
162. Review of African Political Economy
163. Review of International Organizations
164. Review of International Political Economy
165. Review of Policy Research
166. Revista Brasileira de Politica Internacional
167. Revista de Ciencia Politica
168. Revista de Estudios Politicos
169. Revista del CLAD Reforma y Democracia
170. Revue d Economie Politique
171. Romanian Journal of Political Science
172. Scandinavian Political Studies
173. Scottish Journal of Political Economy
174. Social Movement Studies
175. Social Science Quarterly
176. Socio-Economic Review
177. South European Society and Politics
178. State Politics & Policy Quarterly
179. Studies in American Political Development
180. Studies in Comparative International Development
181. Studies in Conflict & Terrorism
182. Survival
183. Swiss Political Science Review
184. Telos
185. Territory Politics Governance
186. Terrorism and Political Violence
187. West European Politics
188. World Politics

<a id="ssci-psychiatry"></a>

### Psychiatry

期刊数：144

1. Academic Psychiatry
2. Acta Psychiatrica Scandinavica
3. Addiction
4. Aging & Mental Health
5. American Journal of Geriatric Psychiatry
6. American Journal of Psychiatry
7. Annals of Clinical Psychiatry
8. Annals of General Psychiatry
9. Anxiety Stress and Coping
10. Archives of Psychiatric Nursing
11. Archives of Suicide Research
12. Asia-Pacific Psychiatry
13. Australasian Psychiatry
14. Australian and New Zealand Journal of Psychiatry
15. Behavior Therapy
16. Behavioral Medicine
17. BioPsychoSocial Medicine
18. Biopsychosocial Science and Medicine
19. BJPsych Open
20. Body Image
21. Brazilian Journal of Psychiatry
22. British Journal of Psychiatry
23. Bulletin of the Menninger Clinic
24. Canadian Journal of Psychiatry-Revue Canadienne de Psychiatrie
25. Child and Adolescent Mental Health
26. Child and Adolescent Psychiatric Clinics of North America
27. Child and Adolescent Psychiatry and Mental Health
28. Child Psychiatry & Human Development
29. Clinical Case Studies
30. Clinical Child Psychology and Psychiatry
31. Clinical Gerontologist
32. Cognitive Neuropsychiatry
33. Community Mental Health Journal
34. Comprehensive Psychiatry
35. Contemporary Psychoanalysis
36. Criminal Behaviour and Mental Health
37. Crisis-the Journal of Crisis Intervention and Suicide Prevention
38. Culture Medicine and Psychiatry
39. Current Opinion in Psychiatry
40. Current Psychiatry Reports
41. Depression and Anxiety
42. Drug and Alcohol Dependence
43. Early Intervention in Psychiatry
44. Eating Behaviors
45. Eating Disorders
46. Epidemiology and Psychiatric Sciences
47. European Addiction Research
48. European Child & Adolescent Psychiatry
49. European Eating Disorders Review
50. European Journal of Psychiatry
51. European Journal of Psychotraumatology
52. European Psychiatry
53. Evolution Psychiatrique
54. Frontiers in Psychiatry
55. General Hospital Psychiatry
56. Harvard Review of Psychiatry
57. History of Psychiatry
58. Indian Journal of Psychiatry
59. International Journal of Clinical and Experimental Hypnosis
60. International Journal of Cognitive Behavioral Therapy
61. International Journal of Eating Disorders
62. International Journal of Forensic Mental Health
63. International Journal of Geriatric Psychiatry
64. International Journal of Law and Psychiatry
65. International Journal of Mental Health and Addiction
66. International Journal of Mental Health Nursing
67. International Journal of Mental Health Promotion
68. International Journal of Mental Health Systems
69. International Journal of Methods in Psychiatric Research
70. International Journal of Psychiatry in Medicine
71. International Journal of Social Psychiatry
72. International Review of Psychiatry
73. Issues in Mental Health Nursing
74. JAMA Psychiatry
75. Journal of Affective Disorders
76. Journal of Aggression Maltreatment & Trauma
77. Journal of Anxiety Disorders
78. Journal of Attention Disorders
79. Journal of Behavior Therapy and Experimental Psychiatry
80. Journal of Behavioral Addictions
81. Journal of Child and Family Studies
82. Journal of Child Psychology and Psychiatry
83. Journal of Clinical Psychiatry
84. Journal of Dual Diagnosis
85. Journal of Ect
86. Journal of Experimental Psychopathology
87. Journal of Forensic Psychiatry & Psychology
88. Journal of Mental Health
89. Journal of Mental Health Policy and Economics
90. Journal of Mental Health Research in Intellectual Disabilities
91. Journal of Nervous and Mental Disease
92. Journal of Obsessive-Compulsive and Related Disorders
93. Journal of Personality Disorders
94. Journal of Psychiatric and Mental Health Nursing
95. Journal of Psychiatric Research
96. Journal of Psychiatry & Neuroscience
97. Journal of Psychopathology and Clinical Science
98. Journal of Psychosomatic Research
99. Journal of the Academy of Consultation-Liaison Psychiatry
100. Journal of the American Academy of Child and Adolescent Psychiatry
101. Journal of the American Academy of Psychiatry and the Law
102. Journal of the American Psychiatric Nurses Association
103. Journal of the American Psychoanalytic Association
104. Journal of Trauma & Dissociation
105. Journal of Traumatic Stress
106. Lancet Psychiatry
107. Mental Health and Physical Activity
108. Mindfulness
109. Nordic Journal of Psychiatry
110. Personality and Mental Health
111. Perspectives in Psychiatric Care
112. Praxis der Kinderpsychologie und Kinderpsychiatrie
113. Psychiatric Annals
114. Psychiatric Clinics of North America
115. Psychiatric Quarterly
116. Psychiatric Rehabilitation Journal
117. Psychiatrie de l Enfant
118. Psychiatrische Praxis
119. Psychiatry Investigation
120. Psychiatry Psychology and Law
121. Psychiatry Research
122. Psychiatry-Interpersonal and Biological Processes
123. Psychoanalytic Study of the Child
124. Psychological Medicine
125. Psychological Trauma-Theory Research Practice and Policy
126. Psychology and Psychotherapy-Theory Research and Practice
127. Psychopathology
128. Psychosis-Psychological Social and Integrative Approaches
129. Psychotherapy and Psychosomatics
130. Recht & Psychiatrie
131. Research in Autism
132. Rivista di Psichiatria
133. Salud Mental
134. Schizophrenia Bulletin
135. Schizophrenia Research
136. Social Psychiatry and Psychiatric Epidemiology
137. South African Journal of Psychiatry
138. Spanish Journal of Psychiatry and Mental Health
139. Stress and Health
140. Suicide and Life-Threatening Behavior
141. Transcultural Psychiatry
142. Turk Psikiyatri Dergisi
143. World Psychiatry
144. Zeitschrift für Kinder-und Jugendpsychiatrie und Psychotherapie

<a id="ssci-psychology-applied"></a>

### Psychology, Applied

期刊数：84

1. Annual Review of Organizational Psychology and Organizational Behavior
2. Applied Ergonomics
3. Applied Psychology-an International Review-Psychologie Appliquee-Revue Internationale
4. Applied Psychology-Health and Well Being
5. Behavioral Sciences & the Law
6. British Journal of Guidance & Counselling
7. Career Development International
8. Career Development Quarterly
9. Counseling Psychologist
10. Ergonomics
11. European Journal of Psychological Assessment
12. European Journal of Work and Organizational Psychology
13. European Review of Applied Psychology-Revue Europeenne de Psychologie Appliquee
14. Gedrag & Organisatie
15. German Journal of Human Resource Management-Zeitschrift für Personalforschung
16. Group & Organization Management
17. Human Factors
18. Human Performance
19. Human Resource Development Quarterly
20. Human Resource Management
21. Industrial and Organizational Psychology
22. International Journal for Educational and Vocational Guidance
23. International Journal of Aerospace Psychology
24. International Journal of Offender Therapy and Comparative Criminology
25. International Journal of Selection and Assessment
26. International Journal of Sport and Exercise Psychology
27. International Journal of Sports Science & Coaching
28. International Journal of Stress Management
29. International Review of Sport and Exercise Psychology
30. Journal of Applied Behavioral Science
31. Journal of Applied Psychology
32. Journal of Applied Sport and Exercise Psychology-Zeitschrift fur Sportpsychologie
33. Journal of Applied Sport Psychology
34. Journal of Behavioral Decision Making
35. Journal of Business and Psychology
36. Journal of Career Assessment
37. Journal of Career Development
38. Journal of Clinical Sport Psychology
39. Journal of College Student Development
40. Journal of Consumer Psychology
41. Journal of Counseling and Development
42. Journal of Counseling Psychology
43. Journal of Educational Measurement
44. Journal of Employment Counseling
45. Journal of Experimental Psychology-Applied
46. Journal of Interpersonal Violence
47. Journal of Investigative Psychology and Offender Profiling
48. Journal of Leadership & Organizational Studies
49. Journal of Management
50. Journal of Managerial Psychology
51. Journal of Multicultural Counseling and Development
52. Journal of Occupational and Organizational Psychology
53. Journal of Occupational Health Psychology
54. Journal of Organizational Behavior
55. Journal of Organizational Behavior Management
56. Journal of Personnel Psychology
57. Journal of Sport & Exercise Psychology
58. Journal of Vocational Behavior
59. Journal of Work and Organizational Psychology-Revista de Psicologia del Trabajo y de las Organizaciones
60. Leadership Quarterly
61. Measurement and Evaluation in Counseling and Development
62. Media Psychology
63. Negotiation and Conflict Management Research
64. Organizational Behavior and Human Decision Processes
65. Organizational Dynamics
66. Organizational Psychology Review
67. Organizational Research Methods
68. Personnel Psychology
69. Personnel Review
70. Psychology & Marketing
71. Psychology of Music
72. Psychology of Sport and Exercise
73. Qualitative Research in Sport Exercise and Health
74. Research in Organizational Behavior
75. Research Quarterly for Exercise and Sport
76. Small Group Research
77. Sport Exercise and Performance Psychology
78. Sport Psychologist
79. Stress and Health
80. Transportation Research Part F-Traffic Psychology and Behaviour
81. Travail Humain
82. Work Aging and Retirement
83. Work and Stress
84. Zeitschrift für Arbeits-und Organisationspsychologie

<a id="ssci-psychology-biological"></a>

### Psychology, Biological

期刊数：14

1. Behavioral and Brain Sciences
2. Behavioural Processes
3. Biological Psychology
4. Evolution and Human Behavior
5. Experimental and Clinical Psychopharmacology
6. Integrative Psychological and Behavioral Science
7. International Journal of Psychophysiology
8. Journal of Experimental Psychology-Animal Learning and Cognition
9. Journal of Psychophysiology
10. Journal of the Experimental Analysis of Behavior
11. Learning & Behavior
12. Learning and Motivation
13. Physiology & Behavior
14. Psychophysiology

<a id="ssci-psychology-clinical"></a>

### Psychology, Clinical

期刊数：130

1. Addictive Behaviors
2. American Behavioral Scientist
3. American Indian and Alaska Native Mental Health Research
4. American Journal of Clinical Hypnosis
5. American Journal of Drug and Alcohol Abuse
6. American Journal of Family Therapy
7. Annual Review of Clinical Psychology
8. Applied Psychophysiology and Biofeedback
9. Archives of Clinical Neuropsychology
10. Archives of Sexual Behavior
11. Arts in Psychotherapy
12. Assessment
13. Behavior Modification
14. Behavior Therapy
15. Behavioral Disorders
16. Behavioral Interventions
17. Behavioral Psychology-Psicologia Conductual
18. Behaviour Research and Therapy
19. Behavioural and Cognitive Psychotherapy
20. Body Image
21. British Journal of Clinical Psychology
22. British Journal of Health Psychology
23. Child & Family Behavior Therapy
24. Child and Adolescent Mental Health
25. Clinica y Salud
26. Clinical Case Studies
27. Clinical Child and Family Psychology Review
28. Clinical Child Psychology and Psychiatry
29. Clinical Neuropsychologist
30. Clinical Psychological Science
31. Clinical Psychologist
32. Clinical Psychology & Psychotherapy
33. Clinical Psychology Review
34. Clinical Psychology-Science and Practice
35. Cognitive and Behavioral Practice
36. Cognitive Behaviour Therapy
37. Cognitive Therapy and Research
38. Criminal Justice and Behavior
39. Depression and Anxiety
40. Diagnostica
41. Eating Behaviors
42. Eating Disorders
43. European Eating Disorders Review
44. European Journal of Health Psychology
45. European Journal of Psychotraumatology
46. Experimental and Clinical Psychopharmacology
47. Family Process
48. Gruppenpsychotherapie und Gruppendynamik
49. Health Psychology
50. Health Psychology Review
51. International Journal of Behavioral Medicine
52. International Journal of Clinical and Experimental Hypnosis
53. International Journal of Clinical and Health Psychology
54. International Journal of Cognitive Behavioral Therapy
55. International Journal of Eating Disorders
56. International Journal of Group Psychotherapy
57. International Journal of Mental Health and Addiction
58. International Journal of Sexual Health
59. International Journal of Transgender Health
60. International Psychogeriatrics
61. Internet Interventions-the Application of Information Technology in Mental and Behavioural Health
62. Journal of Aggression Maltreatment & Trauma
63. Journal of Anxiety Disorders
64. Journal of Applied Behavior Analysis
65. Journal of Behavior Therapy and Experimental Psychiatry
66. Journal of Behavioral Medicine
67. Journal of Child Sexual Abuse
68. Journal of Clinical and Experimental Neuropsychology
69. Journal of Clinical Child and Adolescent Psychology
70. Journal of Clinical Psychiatry
71. Journal of Clinical Psychology
72. Journal of Clinical Psychology in Medical Settings
73. Journal of Cognitive Psychotherapy
74. Journal of Constructivist Psychology
75. Journal of Consulting and Clinical Psychology
76. Journal of Contextual Behavioral Science
77. Journal of Dual Diagnosis
78. Journal of Eating Disorders
79. Journal of Evidence-Based Psychotherapies
80. Journal of Experimental Psychopathology
81. Journal of Family Psychology
82. Journal of Family Therapy
83. Journal of Family Violence
84. Journal of Health Psychology
85. Journal of Latinx Psychology
86. Journal of Marital and Family Therapy
87. Journal of Mental Health
88. Journal of Personality Assessment
89. Journal of Positive Behavior Interventions
90. Journal of Psychoactive Drugs
91. Journal of Psychopathology and Behavioral Assessment
92. Journal of Psychopathology and Clinical Science
93. Journal of Psychosomatic Obstetrics & Gynecology
94. Journal of Rational-Emotive and Cognitive-Behavior Therapy
95. Journal of Sex & Marital Therapy
96. Journal of Sex Research
97. Journal of Social and Clinical Psychology
98. Journal of Substance Use & Addiction Treatment
99. Journal of Trauma & Dissociation
100. Journal of Traumatic Stress
101. Mental Health and Physical Activity
102. Mindfulness
103. Neuropsychology
104. Neuropsychology Review
105. Personality Disorders-Theory Research and Treatment
106. Perspectives on Behavior Science
107. Psychoanalytic Psychology
108. Psychological Assessment
109. Psychological Medicine
110. Psychological Services
111. Psychological Trauma-Theory Research Practice and Policy
112. Psychology and Psychotherapy-Theory Research and Practice
113. Psychology of Violence
114. Psychology Research and Behavior Management
115. Psychosis-Psychological Social and Integrative Approaches
116. Psychotherapie
117. Psychotherapie Psychosomatik Medizinische Psychologie
118. Psychotherapy
119. Psychotherapy Research
120. Rehabilitation Psychology
121. Research on Child and Adolescent Psychopathology
122. Revista Iberoamericana de Diagnostico y Evaluacion-e Avaliacao Psicologica
123. Sexual Abuse-a Journal of Research and Treatment
124. Sexual and Relationship Therapy
125. Terapia Psicologica
126. Transgender Health
127. Verhaltenstherapie
128. Zeitschrift für Klinische Psychologie und Psychotherapie
129. Zeitschrift für Psychosomatische Medizin und Psychotherapie
130. Zeitschrift für Sexualforschung

<a id="ssci-psychology-development"></a>

### Psychology, Development

期刊数：77

1. Adolescent Research Review
2. Aging Neuropsychology and Cognition
3. Applied Developmental Science
4. Attachment & Human Development
5. Autism
6. Autism in Adulthood
7. Autism Research
8. British Journal of Developmental Psychology
9. Child & Youth Care Forum
10. Child Care Health and Development
11. Child Development
12. Child Development Perspectives
13. Child Psychiatry & Human Development
14. Clinical Child Psychology and Psychiatry
15. Cognitive Development
16. Development and Psychopathology
17. Developmental Cognitive Neuroscience
18. Developmental Neuropsychology
19. Developmental Psychology
20. Developmental Review
21. Developmental Science
22. Early Child Development and Care
23. Early Childhood Research Quarterly
24. Early Education and Development
25. Emerging Adulthood
26. European Child & Adolescent Psychiatry
27. European Journal of Developmental Psychology
28. First Language
29. Focus on Autism and Other Developmental Disabilities
30. Human Development
31. Infancy
32. Infant and Child Development
33. Infant Behavior & Development
34. Infant Mental Health Journal-Infancy and Early Childhood
35. Infants & Young Children
36. International Journal of Aging & Human Development
37. International Journal of Behavioral Development
38. Journal for the Study of Education and Development
39. Journal of Adolescence
40. Journal of Adolescent Health
41. Journal of Adolescent Research
42. Journal of Adult Development
43. Journal of Applied Developmental Psychology
44. Journal of Attention Disorders
45. Journal of Autism and Developmental Disorders
46. Journal of Child and Family Studies
47. Journal of Child Language
48. Journal of Child Psychology and Psychiatry
49. Journal of Clinical Child and Adolescent Psychology
50. Journal of Cognition and Development
51. Journal of Developmental and Behavioral Pediatrics
52. Journal of Developmental and Physical Disabilities
53. Journal of Early Adolescence
54. Journal of Experimental Child Psychology
55. Journal of Genetic Psychology
56. Journal of Latinx Psychology
57. Journal of Pediatric Psychology
58. Journal of Research on Adolescence
59. Journal of School Violence
60. Journal of the American Academy of Child and Adolescent Psychiatry
61. Journal of Youth and Adolescence
62. Kindheit und Entwicklung
63. Language Learning and Development
64. Merrill-Palmer Quarterly-Journal of Developmental Psychology
65. Mind Brain and Education
66. Monographs of the Society for Research in Child Development
67. New Directions for Child and Adolescent Development
68. Parenting-Science and Practice
69. Praxis der Kinderpsychologie und Kinderpsychiatrie
70. Psychology and Aging
71. Research in Autism
72. Research in Human Development
73. Research on Child and Adolescent Psychopathology
74. Review Journal of Autism and Developmental Disorders
75. School Mental Health
76. Sex Roles
77. Social Development

<a id="ssci-psychology-educational"></a>

### Psychology, Educational

期刊数：60

1. Applied Measurement in Education
2. Behavioral Disorders
3. British Journal of Educational Psychology
4. Canadian Journal of School Psychology
5. Child Development
6. Cognition and Instruction
7. Contemporary Educational Psychology
8. Creativity Research Journal
9. Discourse Processes
10. Dyslexia
11. Early Education and Development
12. Educational and Psychological Measurement
13. Educational Measurement-Issues and Practice
14. Educational Psychologist
15. Educational Psychology
16. Educational Psychology Review
17. European Journal of Psychology of Education
18. Gifted Child Quarterly
19. High Ability Studies
20. Instructional Science
21. Journal for the Study of Education and Development
22. Journal of Applied Research in Intellectual Disabilities
23. Journal of Counseling Psychology
24. Journal of Creative Behavior
25. Journal of Diversity in Higher Education
26. Journal of Early Intervention
27. Journal of Educational and Psychological Consultation
28. Journal of Educational Measurement
29. Journal of Educational Psychology
30. Journal of Emotional and Behavioral Disorders
31. Journal of Experimental Education
32. Journal of Literacy Research
33. Journal of Psychoeducational Assessment
34. Journal of Research in Reading
35. Journal of School Psychology
36. Journal of School Violence
37. Journal of the Learning Sciences
38. Language Assessment Quarterly
39. Learning and Individual Differences
40. Learning and Instruction
41. Measurement and Evaluation in Counseling and Development
42. Metacognition and Learning
43. Psicologia Educativa
44. Psychologie in Erziehung und Unterricht
45. Psychology in the Schools
46. Psychology of Music
47. Reading and Writing
48. Reading Research Quarterly
49. Revista de Psicodidactica
50. School Mental Health
51. School Psychology
52. School Psychology International
53. School Psychology Review
54. Scientific Studies of Reading
55. Social Psychology of Education
56. Studies in Educational Evaluation
57. Training and Education in Professional Psychology
58. Voprosy Psikhologii
59. Zeitschrift für Entwicklungspsychologie und Padagogische Psychologie
60. Zeitschrift für Padagogische Psychologie

<a id="ssci-psychology-experimental"></a>

### Psychology, Experimental

期刊数：89

1. Acta Psychologica
2. Adaptive Behavior
3. Advances in Cognitive Psychology
4. Aging Neuropsychology and Cognition
5. Applied Cognitive Psychology
6. Applied Psycholinguistics
7. Attention Perception & Psychophysics
8. Behavior Research Methods
9. Bilingualism-Language and Cognition
10. Biological Psychology
11. Brain and Cognition
12. Brain and Language
13. British Journal of Mathematical & Statistical Psychology
14. Canadian Journal of Experimental Psychology-Revue Canadienne de Psychologie Experimentale
15. Cognition
16. Cognition & Emotion
17. Cognition and Instruction
18. Cognitive Development
19. Cognitive Neuropsychology
20. Cognitive Processing
21. Cognitive Psychology
22. Cognitive Research-Principles and Implications
23. Cognitive Science
24. Cognitive Systems Research
25. Computers in Human Behavior
26. Consciousness and Cognition
27. Cortex
28. Current Opinion in Behavioral Sciences
29. Developmental Neuropsychology
30. Developmental Science
31. Discourse Processes
32. Ecological Psychology
33. Emotion
34. Evolutionary Psychology
35. Experimental Psychology
36. Human Movement Science
37. I-Perception
38. International Journal of Psychophysiology
39. Journal of Applied Research in Memory and Cognition
40. Journal of Child Language
41. Journal of Cognition and Development
42. Journal of Cognitive Neuroscience
43. Journal of Cognitive Psychology
44. Journal of Experimental Child Psychology
45. Journal of Experimental Psychology-Animal Learning and Cognition
46. Journal of Experimental Psychology-General
47. Journal of Experimental Psychology-Human Perception and Performance
48. Journal of Experimental Psychology-Learning Memory and Cognition
49. Journal of Memory and Language
50. Journal of Motor Behavior
51. Journal of Neurolinguistics
52. Journal of Neuropsychology
53. Journal of Psycholinguistic Research
54. Journal of the Experimental Analysis of Behavior
55. Language and Cognition
56. Language and Speech
57. Language Cognition and Neuroscience
58. Language Learning and Development
59. Laterality
60. Learning & Behavior
61. Learning and Motivation
62. Memory
63. Memory & Cognition
64. Mind & Language
65. Motivation and Emotion
66. Multisensory Research
67. Multivariate Behavioral Research
68. Music Perception
69. Musicae Scientiae
70. Nature Human Behaviour
71. Neuropsychologia
72. New Ideas in Psychology
73. Npj Science of Learning
74. Perception
75. Perceptual and Motor Skills
76. Psicologica
77. Psychological Research-Psychologische Forschung
78. Psychology of Aesthetics Creativity and the Arts
79. Psychology of Music
80. Psychonomic Bulletin & Review
81. Psychophysiology
82. Quarterly Journal of Experimental Psychology
83. Social Cognitive and Affective Neuroscience
84. Spatial Cognition and Computation
85. Thinking & Reasoning
86. Topics in Cognitive Science
87. Trends in Cognitive Sciences
88. Visual Cognition
89. Wiley Interdisciplinary Reviews-Cognitive Science

<a id="ssci-psychology-mathematical"></a>

### Psychology, Mathematical

期刊数：13

1. Applied Measurement in Education
2. Applied Psychological Measurement
3. Behavior Research Methods
4. British Journal of Mathematical & Statistical Psychology
5. Educational and Psychological Measurement
6. Journal of Classification
7. Journal of Educational and Behavioral Statistics
8. Journal of Educational Measurement
9. Journal of Mathematical Psychology
10. Methodology-European Journal of Research Methods for the Behavioral and Social Sciences
11. Nonlinear Dynamics Psychology and Life Sciences
12. Psychometrika
13. Psychonomic Bulletin & Review

<a id="ssci-psychology-multidisciplinary"></a>

### Psychology, Multidisciplinary

期刊数：147

1. Advances in Methods and Practices in Psychological Science
2. Aggression and Violent Behavior
3. Aggressive Behavior
4. AIDS Care-Psychological and Socio-Medical Aspects of AIDS/HIV
5. American Journal of Community Psychology
6. American Journal of Psychology
7. American Psychologist
8. Anales de Psicologia
9. Annals of Behavioral Medicine
10. Annee Psychologique
11. Annual Review of Psychology
12. Anuario de Psicologia Juridica
13. Anxiety Stress and Coping
14. Archive for the Psychology of Religion-Archiv fur Religionspsychologie
15. Archives of Suicide Research
16. Asian American Journal of Psychology
17. Australian Journal of Psychology
18. Australian Psychologist
19. Behavior Genetics
20. Behavioral Sciences
21. BioPsychoSocial Medicine
22. Biopsychosocial Science and Medicine
23. BMC Psychology
24. Body Image
25. British Journal of Psychology
26. Canadian Journal of Behavioural Science-Revue Canadienne des Sciences du Comportement
27. Canadian Psychology-Psychologie Canadienne
28. Ceskoslovenska Psychologie
29. Collabra-Psychology
30. Computers in Human Behavior
31. Creativity Research Journal
32. Crisis-the Journal of Crisis Intervention and Suicide Prevention
33. Culture & Psychology
34. Current Directions in Psychological Science
35. Current Opinion in Psychology
36. Current Psychology
37. Cyberpsychology-Journal of Psychosocial Research on Cyberspace
38. Death Studies
39. Discourse & Society
40. Dreaming
41. Emotion Review
42. Empirical Studies of the Arts
43. Environment and Behavior
44. Ethics & Behavior
45. Ethos
46. European Journal of Psychology Applied to Legal Context
47. European Journal of Psychology Open
48. European Psychologist
49. Feminism & Psychology
50. Frontiers in Psychology
51. Hispanic Journal of Behavioral Sciences
52. History of Psychology
53. Humor-International Journal of Humor Research
54. Intelligence
55. International Journal for the Psychology of Religion
56. International Journal of Human-Computer Studies
57. International Journal of Psychological Research
58. International Journal of Psychology
59. International Journal of Sport Psychology
60. Japanese Psychological Research
61. Journal of Black Psychology
62. Journal of Community Psychology
63. Journal of Comparative Psychology
64. Journal of Economic Psychology
65. Journal of Emotional and Behavioral Disorders
66. Journal of Environmental Psychology
67. Journal of Forensic Psychology Research and Practice
68. Journal of Gambling Studies
69. Journal of General Psychology
70. Journal of Genetic Psychology
71. Journal of Happiness Studies
72. Journal of Homosexuality
73. Journal of Humanistic Psychology
74. Journal of Intelligence
75. Journal of Latinx Psychology
76. Journal of Media Psychology-Theories Methods and Applications
77. Journal of Neuroscience Psychology and Economics
78. Journal of Pacific Rim Psychology
79. Journal of Positive Psychology
80. Journal of Psychology
81. Journal of Psychology and Theology
82. Journal of Psychology in Africa
83. Journal of Reproductive and Infant Psychology
84. Journals of Gerontology Series B-Psychological Sciences and Social Sciences
85. Judgment and Decision Making
86. Laterality
87. Legal and Criminological Psychology
88. Military Psychology
89. Motivation Science
90. Nature Reviews Psychology
91. Neurobiology of Learning and Memory
92. New Ideas in Psychology
93. Nordic Psychology
94. Omega-Journal of Death and Dying
95. Perspectives on Psychological Science
96. Philosophical Psychology
97. Pratiques Psychologiques
98. Professional Psychology-Research and Practice
99. Psicologia Educativa
100. Psicologia-Reflexao e Critica
101. Psicothema
102. Psihologija
103. Psikhologicheskii Zhurnal
104. PsyCh Journal
105. Psychiatry Psychology and Law
106. Psycho-Oncology
107. Psychologia
108. Psychologica Belgica
109. Psychological Bulletin
110. Psychological Inquiry
111. Psychological Methods
112. Psychological Record
113. Psychological Reports
114. Psychological Review
115. Psychological Science
116. Psychological Science in the Public Interest
117. Psychologie Francaise
118. Psychologische Rundschau
119. Psychologist
120. Psychology & Health
121. Psychology & Sexuality
122. Psychology Crime & Law
123. Psychology of Addictive Behaviors
124. Psychology of Popular Media
125. Psychology of Religion and Spirituality
126. Psychology of Sexual Orientation and Gender Diversity
127. Psychology of Women Quarterly
128. Psychology Public Policy and Law
129. Psychology Research and Behavior Management
130. Psychosocial Intervention
131. Qualitative Research in Psychology
132. Review of General Psychology
133. Revista Latinoamericana de Psicologia
134. Revista Mexicana de Psicologia
135. Scandinavian Journal of Psychology
136. South African Journal of Psychology
137. Spanish Journal of Psychology
138. Studia Psychologica
139. Studies in Psychology
140. Suicide and Life-Threatening Behavior
141. Teaching of Psychology
142. Theory & Psychology
143. Turk Psikoloji Dergisi
144. Universitas Psychologica
145. Women & Therapy
146. Zeitschrift für Psychologie-Journal of Psychology
147. Zeitschrift für Psychosomatische Medizin und Psychotherapie

<a id="ssci-psychology-psychoanalysis"></a>

### Psychology, Psychoanalysis

期刊数：14

1. Bulletin of the Menninger Clinic
2. Contemporary Psychoanalysis
3. Forum der Psychoanalyse
4. International Journal of Psychoanalysis
5. Journal of the American Psychoanalytic Association
6. Psyche-Zeitschrift fur Psychoanalyse und Ihre Anwendungen
7. Psychoanalysis and History
8. Psychoanalytic Dialogues
9. Psychoanalytic Inquiry
10. Psychoanalytic Psychology
11. Psychoanalytic Quarterly
12. Psychoanalytic Study of the Child
13. Psychotherapie
14. Zeitschrift für Psychosomatische Medizin und Psychotherapie

<a id="ssci-psychology-social"></a>

### Psychology, Social

期刊数：63

1. Analyses of Social Issues and Public Policy
2. Asian Journal of Social Psychology
3. Basic and Applied Social Psychology
4. British Journal of Social Psychology
5. Child Abuse & Neglect
6. Cultural Diversity & Ethnic Minority Psychology
7. Cyberpsychology Behavior and Social Networking
8. Deviant Behavior
9. Emerging Adulthood
10. European Journal of Personality
11. European Journal of Social Psychology
12. European Review of Social Psychology
13. Gedrag & Organisatie
14. Group Dynamics-Theory Research and Practice
15. Group Processes & Intergroup Relations
16. International Journal of Intercultural Relations
17. International Journal of Social Psychology
18. International Review of Social Psychology
19. Journal for the Theory of Social Behaviour
20. Journal of Applied Social Psychology
21. Journal of Community & Applied Social Psychology
22. Journal of Cross-Cultural Psychology
23. Journal of Diversity in Higher Education
24. Journal of Experimental Social Psychology
25. Journal of Health and Social Behavior
26. Journal of Individual Differences
27. Journal of Language and Social Psychology
28. Journal of Latinx Psychology
29. Journal of Loss & Trauma
30. Journal of Nonverbal Behavior
31. Journal of Personality
32. Journal of Personality and Social Psychology
33. Journal of Personality Assessment
34. Journal of Psychosocial Oncology
35. Journal of Research in Personality
36. Journal of Social and Clinical Psychology
37. Journal of Social and Personal Relationships
38. Journal of Social Issues
39. Journal of Social Psychology
40. Kolner Zeitschrift für Soziologie und Sozialpsychologie
41. Law and Human Behavior
42. Motivation and Emotion
43. Organizational Behavior and Human Decision Processes
44. Personal Relationships
45. Personality and Individual Differences
46. Personality and Mental Health
47. Personality and Social Psychology Bulletin
48. Personality and Social Psychology Review
49. Political Psychology
50. Psychology of Men & Masculinities
51. Research on Language and Social Interaction
52. Self and Identity
53. Sex Roles
54. Small Group Research
55. Social and Personality Psychology Compass
56. Social Behavior and Personality
57. Social Cognition
58. Social Influence
59. Social Issues and Policy Review
60. Social Justice Research
61. Social Psychological and Personality Science
62. Social Psychology
63. Social Psychology Quarterly

<a id="ssci-public-administration"></a>

### Public Administration

期刊数：48

1. Administration & Society
2. American Review of Public Administration
3. Amme Idaresi Dergisi
4. Australian Journal of Public Administration
5. Canadian Public Administration-Administration Publique du Canada
6. Canadian Public Policy-Analyse de Politiques
7. Civil Szemle
8. Climate Policy
9. Contemporary Economic Policy
10. Critical Policy Studies
11. Environment and Planning C-Politics and Space
12. Gestion y Politica Publica
13. Governance-an International Journal of Policy Administration and Institutions
14. Human Service Organizations Management Leadership & Governance
15. International Public Management Journal
16. International Review of Administrative Sciences
17. Journal of Accounting and Public Policy
18. Journal of Chinese Governance
19. Journal of Comparative Policy Analysis
20. Journal of European Public Policy
21. Journal of European Social Policy
22. Journal of Homeland Security and Emergency Management
23. Journal of Policy Analysis and Management
24. Journal of Public Administration Research and Theory
25. Journal of Public Policy
26. Journal of Social Policy
27. Local Government Studies
28. Nonprofit Management & Leadership
29. Policy and Politics
30. Policy and Society
31. Policy Sciences
32. Policy Studies
33. Policy Studies Journal
34. Public Administration
35. Public Administration and Development
36. Public Administration Review
37. Public Management Review
38. Public Money & Management
39. Public Performance & Management Review
40. Public Personnel Management
41. Public Policy and Administration
42. Regulation & Governance
43. Review of Policy Research
44. Review of Public Personnel Administration
45. Revista del CLAD Reforma y Democracia
46. Science and Public Policy
47. Social Policy & Administration
48. Transylvanian Review of Administrative Sciences

<a id="ssci-public-environmental-occupational-health"></a>

### Public, Environmental & Occupational Health

期刊数：178

1. Accident Analysis and Prevention
2. Administration and Policy in Mental Health and Mental Health Services Research
3. African Journal of Reproductive Health
4. AIDS and Behavior
5. AIDS Care-Psychological and Socio-Medical Aspects of AIDS/HIV
6. AIDS Education and Prevention
7. AIDS Patient Care and STDs
8. AJAR-African Journal of AIDS Research
9. American Journal of Community Psychology
10. American Journal of Health Promotion
11. American Journal of Mens Health
12. American Journal of Preventive Medicine
13. American Journal of Public Health
14. Anales del Sistema Sanitario de Navarra
15. Analytic Methods in Accident Research
16. Annals of Human Biology
17. Annual Review of Public Health
18. Anthropology & Medicine
19. Archives of Public Health
20. Arts & Health
21. Asia-Pacific Journal of Public Health
22. Australian and New Zealand Journal of Public Health
23. Australian Journal of Primary Health
24. Australian Journal of Rural Health
25. BMC Womens Health
26. BMJ Global Health
27. Cadernos de Saude Publica
28. Canadian Journal of Public Health-Revue Canadienne de Sante Publique
29. Central European Journal of Public Health
30. Childrens Health Care
31. China CDC Weekly
32. Chronic Illness
33. Ciencia & Saude Coletiva
34. Community Mental Health Journal
35. Conflict and Health
36. Critical Public Health
37. Current Environmental Health Reports
38. Digital Health
39. Disability and Health Journal
40. Disaster Medicine and Public Health Preparedness
41. Disaster Prevention and Management
42. Economics & Human Biology
43. Environmental Health and Preventive Medicine
44. Epidemiologia & Prevenzione
45. Epidemiology
46. Ethiopian Journal of Health Development
47. European Journal of Public Health
48. Families Systems & Health
49. Family & Community Health
50. Frontiers in Public Health
51. Gaceta Sanitaria
52. Games for Health Journal
53. Gesundheitswesen
54. Global Health Action
55. Global Health Promotion
56. Global Health-Science and Practice
57. Global Public Health
58. Globalization and Health
59. Health
60. Health & Place
61. Health & Social Care in the Community
62. Health and Human Rights
63. Health Care for Women International
64. Health Education & Behavior
65. Health Education Journal
66. Health Education Research
67. Health Expectations
68. Health Promotion International
69. Health Promotion Journal of Australia
70. Health Reports
71. Health Risk & Society
72. Health Security
73. Health Systems & Reform
74. HERD-Health Environments Research & Design Journal
75. Indian Journal of Public Health
76. Injury Epidemiology
77. Injury Prevention
78. International Health
79. International Journal for Equity in Health
80. International Journal of Circumpolar Health
81. International Journal of Health Geographics
82. International Journal of Health Planning and Management
83. International Journal of Injury Control and Safety Promotion
84. International Journal of Mental Health Promotion
85. International Journal of Occupational Safety and Ergonomics
86. International Journal of Public Health
87. International Journal of Qualitative Studies on Health and Well-Being
88. International Journal of Sexual Health
89. International Journal of Transgender Health
90. Iranian Journal of Public Health
91. Israel Journal of Health Policy Research
92. JAMA Health Forum
93. JANAC-Journal of the Association of Nurses in AIDS Care
94. JMIR Public Health and Surveillance
95. Journal of Adolescent Health
96. Journal of American College Health
97. Journal of Behavioral Health Services & Research
98. Journal of Community Health
99. Journal of Community Psychology
100. Journal of Correctional Health Care
101. Journal of Epidemiology and Community Health
102. Journal of Epidemiology and Global Health
103. Journal of Global Health
104. Journal of Health and Social Behavior
105. Journal of Health Care for the Poor and Underserved
106. Journal of Immigrant and Minority Health
107. Journal of Mens Health
108. Journal of Occupational Health Psychology
109. Journal of Palliative Care
110. Journal of Physical Activity & Health
111. Journal of Prevention
112. Journal of Public Health
113. Journal of Public Health Management and Practice
114. Journal of Public Health Policy
115. Journal of Racial and Ethnic Health Disparities
116. Journal of Religion & Health
117. Journal of Rural Health
118. Journal of Safety Research
119. Journal of School Health
120. Journal of Transport & Health
121. Journal of Womens Health
122. Lancet Global Health
123. Lancet Planetary Health
124. Lancet Public Health
125. Lancet Regional Health-Europe
126. Lancet Regional Health-Western Pacific
127. LGBT Health
128. Longitudinal and Life Course Studies
129. Maternal and Child Health Journal
130. Medical Anthropology Quarterly
131. Nicotine & Tobacco Research
132. Perspectives in Public Health
133. Population Health Metrics
134. Preventing Chronic Disease
135. Prevention Science
136. Progress in Community Health Partnerships-Research Education and Action
137. Psychiatric Services
138. Psychology & Health
139. Psychology Health & Medicine
140. Public Health
141. Public Health Ethics
142. Public Health Genomics
143. Public Health Nursing
144. Public Health Reports
145. Quality of Life Research
146. Reproductive Health
147. Research in Social & Administrative Pharmacy
148. Revista de Saude Publica
149. Revista Espanola de Salud Publica
150. Revista Panamericana de Salud Publica-Pan American Journal of Public Health
151. Risk Analysis
152. Rural and Remote Health
153. Safety and Health at Work
154. SAHARA J-Journal of Social Aspects of HIV-AIDS
155. Salud Colectiva
156. Salud Publica de Mexico
157. Saude e Sociedade
158. Scandinavian Journal of Public Health
159. Scandinavian Journal of Work Environment & Health
160. Science of Diabetes Self-Management and Care
161. Sex Education-Sexuality Society and Learning
162. Sexual & Reproductive Healthcare
163. Sexual and Reproductive Health Matters
164. Sexual Health
165. Slovenian Journal of Public Health
166. Social Science & Medicine
167. Social Work in Public Health
168. Sociology of Health & Illness
169. SSM-Population Health
170. Studies in Family Planning
171. Tobacco Control
172. Tobacco Induced Diseases
173. Traffic Injury Prevention
174. Transgender Health
175. Translational Behavioral Medicine
176. Women & Health
177. Womens Health Issues
178. Work-a Journal of Prevention Assessment & Rehabilitation

<a id="ssci-regional-urban-planning"></a>

### Regional & Urban Planning

期刊数：41

1. Annals of Regional Science
2. Applied Spatial Analysis and Policy
3. Computers Environment and Urban Systems
4. disP
5. Environment and Planning B-Urban Analytics and City Science
6. Environment and Planning C-Politics and Space
7. European Planning Studies
8. European Urban and Regional Studies
9. Futures
10. Growth and Change
11. Habitat International
12. Housing Studies
13. Housing Theory & Society
14. International Development Planning Review
15. International Journal of Housing Policy
16. International Journal of Urban and Regional Research
17. International Regional Science Review
18. Journal of Architectural and Planning Research
19. Journal of Environment & Development
20. Journal of Environmental Planning and Management
21. Journal of Environmental Policy & Planning
22. Journal of Housing and the Built Environment
23. Journal of Planning Education and Research
24. Journal of Planning Literature
25. Journal of Regional Science
26. Journal of Rural Studies
27. Journal of the American Planning Association
28. Journal of Urban Planning and Development
29. Landscape and Urban Planning
30. Local Environment
31. Local Government Studies
32. Papers in Regional Science
33. Planning Theory
34. Planning Theory & Practice
35. Progress in Planning
36. Regional Studies
37. Society & Natural Resources
38. Sustainable Development
39. Technological Forecasting and Social Change
40. Urban Design International
41. Urban Policy and Research

<a id="ssci-rehabilitation"></a>

### Rehabilitation

期刊数：74

1. AJIDD-American Journal on Intellectual and Developmental Disabilities
2. American Annals of the Deaf
3. American Journal of Occupational Therapy
4. American Journal of Speech-Language Pathology
5. Annals of Dyslexia
6. Aphasiology
7. Arts in Psychotherapy
8. Assistive Technology
9. Augmentative and Alternative Communication
10. Autism in Adulthood
11. Brain Injury
12. British Journal of Occupational Therapy
13. Canadian Journal of Occupational Therapy-Revue Canadienne d Ergotherapie
14. Career Development and Transition for Exceptional Individuals
15. Clinical Linguistics & Phonetics
16. Communication Disorders Quarterly
17. Disability & Society
18. Disability and Health Journal
19. Disability and Rehabilitation
20. Disability and Rehabilitation-Assistive Technology
21. Dyslexia
22. Education and Training in Autism and Developmental Disabilities
23. Education and Treatment of Children
24. European Journal of Cancer Care
25. Exceptional Children
26. Focus on Autism and Other Developmental Disabilities
27. Folia Phoniatrica et Logopaedica
28. Games for Health Journal
29. Infants & Young Children
30. Intellectual and Developmental Disabilities
31. International Journal of Developmental Disabilities
32. International Journal of Disability Development and Education
33. International Journal of Language & Communication Disorders
34. International Journal of Rehabilitation Research
35. International Journal of Speech-Language Pathology
36. Journal of Applied Research in Intellectual Disabilities
37. Journal of Communication Disorders
38. Journal of Deaf Studies and Deaf Education
39. Journal of Developmental and Physical Disabilities
40. Journal of Disability Policy Studies
41. Journal of Early Intervention
42. Journal of Fluency Disorders
43. Journal of Head Trauma Rehabilitation
44. Journal of Intellectual & Developmental Disability
45. Journal of Intellectual Disabilities
46. Journal of Intellectual Disability Research
47. Journal of Learning Disabilities
48. Journal of Mental Health Research in Intellectual Disabilities
49. Journal of Music Therapy
50. Journal of Occupational Rehabilitation
51. Journal of Policy and Practice in Intellectual Disabilities
52. Journal of Special Education Technology
53. Journal of Speech Language and Hearing Research
54. Journal of Visual Impairment & Blindness
55. Kinesiology
56. Language Speech and Hearing Services in Schools
57. Learning Disabilities Research & Practice
58. Learning Disability Quarterly
59. NeuroRehabilitation
60. Nordic Journal of Music Therapy
61. Occupational Therapy International
62. OTJR-Occupational Therapy Journal of Research
63. Physical & Occupational Therapy in Pediatrics
64. Psychiatric Rehabilitation Journal
65. Rehabilitation Counseling Bulletin
66. Rehabilitation Nursing
67. Rehabilitation Psychology
68. Research and Practice for Persons with Severe Disabilities
69. Research in Autism
70. Research in Developmental Disabilities
71. Scandinavian Journal of Occupational Therapy
72. Sexuality and Disability
73. Topics in Geriatric Rehabilitation
74. Topics in Language Disorders

<a id="ssci-social-issues"></a>

### Social Issues

期刊数：43

1. Addiction Research & Theory
2. American Journal of Bioethics
3. Analyses of Social Issues and Public Policy
4. Australian Journal of Social Issues
5. Bioethics
6. Bulletin of the Atomic Scientists
7. Columbia Journal of Law and Social Problems
8. Critical Social Policy
9. Death Studies
10. Dissent
11. Drustvena Istrazivanja
12. Human Rights Quarterly
13. Issues in Science and Technology
14. Journal of Bioethical Inquiry
15. Journal of European Social Policy
16. Journal of Gender Studies
17. Journal of Health Politics Policy and Law
18. Journal of Medical Ethics
19. Journal of Occupational Rehabilitation
20. Journal of Poverty and Social Justice
21. Journal of Responsible Innovation
22. Journal of Social Issues
23. Journal of Social Philosophy
24. Journal of Social Policy
25. Kennedy Institute of Ethics Journal
26. New Genetics and Society
27. Nonprofit and Voluntary Sector Quarterly
28. Politics & Society
29. Race & Class
30. Revija za Socijalnu Politiku
31. Revista de Estudios Sociales
32. Science Technology & Human Values
33. Social Issues and Policy Review
34. Social Policy & Administration
35. Social Policy and Society
36. Social Politics
37. South European Society and Politics
38. Technology in Society
39. Theoretical Medicine and Bioethics
40. Tydskrif Vir Geesteswetenskappe
41. Voluntas
42. Youth & Society
43. Zygon

<a id="ssci-social-sciences-biomedical"></a>

### Social Sciences, Biomedical

期刊数：45

1. Acta Bioethica
2. AIDS and Behavior
3. AIDS Care-Psychological and Socio-Medical Aspects of AIDS/HIV
4. American Journal of Bioethics
5. Anthropology & Medicine
6. Biodemography and Social Biology
7. Bioethics
8. BioSocieties
9. BMC Medical Ethics
10. BMJ Sexual & Reproductive Health
11. Cambridge Quarterly of Healthcare Ethics
12. Critical Public Health
13. Culture Health & Sexuality
14. Culture Medicine and Psychiatry
15. Death Studies
16. Evolution and Human Behavior
17. Hastings Center Report
18. Health
19. Health Care Analysis
20. Health Risk & Society
21. Human Nature-an Interdisciplinary Biosocial Perspective
22. International Journal of Feminist Approaches to Bioethics
23. International Journal of Qualitative Studies on Health and Well-Being
24. International Journal of Transgender Health
25. Journal of Bioethical Inquiry
26. Journal of Biosocial Science
27. Journal of Cancer Survivorship
28. Journal of Genetic Counseling
29. Journal of Health and Social Behavior
30. Journal of Health Politics Policy and Law
31. Journal of Legal Medicine
32. Journal of Medical Ethics
33. Journal of Medicine and Philosophy
34. Medical Anthropology
35. Medical Anthropology Quarterly
36. Neuroethics
37. New Genetics and Society
38. Omega-Journal of Death and Dying
39. Psycho-Oncology
40. Qualitative Health Research
41. Social Science & Medicine
42. Social Theory & Health
43. Sociology of Health & Illness
44. Theoretical Medicine and Bioethics
45. Transgender Health

<a id="ssci-social-sciences-interdisciplinary"></a>

### Social Sciences, Interdisciplinary

期刊数：108

1. Accident Analysis and Prevention
2. Actes de la Recherche en Sciences Sociales
3. Action Research
4. Adaptive Behavior
5. Adolescent Research Review
6. Advances in Life Course Research
7. American Behavioral Scientist
8. American Journal of Evaluation
9. Andamios
10. Annals of the American Academy of Political and Social Science
11. Applied Research in Quality of Life
12. Archives of Sexual Behavior
13. Asian Journal of Social Science
14. Big Data & Society
15. Child Indicators Research
16. Childhood-a Global Journal of Child Research
17. Clothing and Textiles Research Journal
18. Crime Law and Social Change
19. Critical Social Policy
20. Cross-Cultural Research
21. Cultural Trends
22. Dados-Revista de Ciencias Sociais
23. Daedalus
24. Disability & Society
25. Disasters
26. Emotion Space and Society
27. European Journal of Futures Research
28. Evaluation
29. Evaluation and Program Planning
30. Evaluation Review
31. Evidence & Policy
32. Field Methods
33. Globalizations
34. GLQ-a Journal of Lesbian and Gay Studies
35. Group Decision and Negotiation
36. Historical Social Research-Historische Sozialforschung
37. Human Organization
38. Human Relations
39. Humanities & Social Sciences Communications
40. Interdisciplinary Science Reviews
41. International Journal of Design
42. International Journal of Heritage Studies
43. International Journal of Intercultural Relations
44. International Journal of Qualitative Methods
45. International Journal of Sexual Health
46. International Journal of Social Research Methodology
47. International Journal of Transgender Health
48. Island Studies Journal
49. Jasss-the Journal of Artificial Societies and Social Simulation
50. Journal of Black Studies
51. Journal of Children and Media
52. Journal of Consciousness Studies
53. Journal of Gender Studies
54. Journal of Happiness Studies
55. Journal of Homosexuality
56. Journal of Mixed Methods Research
57. Journal of Poverty and Social Justice
58. Journal of Risk Research
59. Journal of Safety Research
60. Journal of Sex Research
61. Journal of Youth Studies
62. Longitudinal and Life Course Studies
63. Minerva
64. Movimento
65. Negotiation Journal
66. New Left Review
67. New Perspectives on Turkey
68. Patient Education and Counseling
69. Perfiles Latinoamericanos
70. Policy Sciences
71. Public Opinion Quarterly
72. Qualitative Health Research
73. Qualitative Inquiry
74. Qualitative Research
75. Race & Class
76. Race and Social Problems
77. Revista de Estudios Sociales
78. Risk Management-an International Journal
79. RSF-the Russell SAGE Journal of the Social Sciences
80. SAGE Open
81. Science & Society
82. Sciences Sociales et Sante
83. Semiotica
84. Sexuality Research and Social Policy
85. Social & Legal Studies
86. Social Epistemology
87. Social Inclusion
88. Social Indicators Research
89. Social Philosophy and Policy
90. Social Research
91. Social Science Computer Review
92. Social Science Information sur les Sciences Sociales
93. Social Science Japan Journal
94. Social Science Journal
95. Society
96. South African Journal for Research in Sport Physical Education and Recreation
97. Space Policy
98. Systems
99. Systems Research and Behavioral Science
100. Technology in Society
101. Tidsskrift for Samfunnsforskning
102. Time & Society
103. Trames-Journal of the Humanities and Social Sciences
104. Travail Genre et Societes
105. Young
106. Youth & Society
107. Zeitschrift für Evaluation
108. Zeitschrift für Sexualforschung

<a id="ssci-social-sciences-mathematical-methods"></a>

### Social Sciences, Mathematical Methods

期刊数：54

1. Applied Psychological Measurement
2. ASTIN Bulletin-the Journal of the International Actuarial Association
3. Computational and Mathematical Organization Theory
4. Econometric Reviews
5. Econometric Theory
6. Econometrica
7. Econometrics Journal
8. Empirical Economics
9. EPJ Data Science
10. Finance and Stochastics
11. Financial Innovation
12. IMA Journal of Management Mathematics
13. Insurance Mathematics & Economics
14. International Journal of Game Theory
15. Jahrbucher für Nationalokonomie und Statistik
16. Journal of Applied Econometrics
17. Journal of Business & Economic Statistics
18. Journal of Causal Inference
19. Journal of Econometrics
20. Journal of Educational and Behavioral Statistics
21. Journal of Management Analytics
22. Journal of Mathematical Economics
23. Journal of Mathematical Psychology
24. Journal of Mathematical Sociology
25. Journal of Official Statistics
26. Journal of Productivity Analysis
27. Journal of Survey Statistics and Methodology
28. Journal of the Royal Statistical Society Series a-Statistics in Society
29. Law Probability & Risk
30. Mathematical Finance
31. Mathematical Population Studies
32. Mathematical Social Sciences
33. Mathematics and Financial Economics
34. Methodology-European Journal of Research Methods for the Behavioral and Social Sciences
35. Multivariate Behavioral Research
36. Nonlinear Dynamics Psychology and Life Sciences
37. Oxford Bulletin of Economics and Statistics
38. Political Analysis
39. Psychometrika
40. Qme-Quantitative Marketing and Economics
41. Quantitative Finance
42. Review of Economics and Statistics
43. Risk Analysis
44. Scandinavian Actuarial Journal
45. SIAM Journal on Financial Mathematics
46. Social Choice and Welfare
47. Sociological Methods & Research
48. Stata Journal
49. Structural Equation Modeling-a Multidisciplinary Journal
50. Studies in Nonlinear Dynamics and Econometrics
51. Survey Methodology
52. Survey Research Methods
53. System Dynamics Review
54. Theory and Decision

<a id="ssci-social-work"></a>

### Social Work

期刊数：44

1. Affilia-Feminist Inquiry in Social Work
2. American Journal of Community Psychology
3. American Journal of Orthopsychiatry
4. Asia Pacific Journal of Social Work and Development
5. Australian Social Work
6. British Journal of Social Work
7. Child & Family Social Work
8. Child Abuse & Neglect
9. Child Abuse Review
10. Child and Adolescent Social Work Journal
11. Child Maltreatment
12. Child Welfare
13. Children & Society
14. Children and Youth Services Review
15. Clinical Social Work Journal
16. European Journal of Social Work
17. Families in Society-the Journal of Contemporary Social Services
18. Family Relations
19. Health & Social Care in the Community
20. Health & Social Work
21. Human Service Organizations Management Leadership & Governance
22. International Journal of Social Welfare
23. International Social Work
24. Journal of Community Psychology
25. Journal of Gerontological Social Work
26. Journal of Psychologists and Counsellors in Schools
27. Journal of Public Child Welfare
28. Journal of Social Policy
29. Journal of Social Service Research
30. Journal of Social Work
31. Journal of Social Work Education
32. Journal of Social Work Practice
33. Journal of the Society for Social Work and Research
34. Ljetopis Socijalnog Rada
35. Qualitative Social Work
36. Research on Social Work Practice
37. Social Policy & Administration
38. Social Policy and Society
39. Social Service Review
40. Social Work
41. Social Work in Health Care
42. Social Work in Public Health
43. Social Work Research
44. Trauma Violence & Abuse

<a id="ssci-sociology"></a>

### Sociology

期刊数：149

1. Acta Sociologica
2. Agriculture and Human Values
3. American Journal of Cultural Sociology
4. American Journal of Economics and Sociology
5. American Journal of Sociology
6. American Sociological Review
7. Annals of Tourism Research
8. Annual Review of Law and Social Science
9. Annual Review of Sociology
10. Anthrozoos
11. Armed Forces & Society
12. Berliner Journal für Soziologie
13. Biodemography and Social Biology
14. Body & Society
15. British Journal of Sociology
16. British Journal of Sociology of Education
17. Canadian Review of Sociology-Revue Canadienne de Sociologie
18. Chinese Sociological Review
19. City & Community
20. Comparative Studies in Society and History
21. Contemporary Sociology-a Journal of Reviews
22. Contributions to Indian Sociology
23. Convergencia-Revista de Ciencias Sociales
24. Cornell Hospitality Quarterly
25. Crime Media Culture
26. Critical Sociology
27. Cultural Sociology
28. Current Sociology
29. Deviance et Societe
30. Deviant Behavior
31. Discourse & Society
32. Drustvena Istrazivanja
33. Du Bois Review-Social Science Research on Race
34. Eastern European Countryside
35. Economic and Social Review
36. Economy and Society
37. Ethnic and Racial Studies
38. Ethnography
39. European Journal of Social Theory
40. European Journal of Sociology-Archives Europeennes de Sociologie
41. European Societies
42. European Sociological Review
43. Filosofija-Sociologija
44. Food Culture & Society
45. Gender & Society
46. Global Networks-a Journal of Transnational Affairs
47. Health Sociology Review
48. Human Ecology
49. Human Ecology Review
50. Human Studies
51. Information Communication & Society
52. Innovation-the European Journal of Social Science Research
53. International Journal of Comparative Sociology
54. International Journal of Intercultural Relations
55. International Political Sociology
56. International Review for the Sociology of Sport
57. International Sociology
58. Journal for the Scientific Study of Religion
59. Journal of Consumer Culture
60. Journal of Contemporary Ethnography
61. Journal of Cultural Economy
62. Journal of Health and Social Behavior
63. Journal of Immigrant & Refugee Studies
64. Journal of Law and Society
65. Journal of Leisure Research
66. Journal of Marriage and Family
67. Journal of Mathematical Sociology
68. Journal of Sociology
69. Journal of Sport & Social Issues
70. Journal of the History of Sexuality
71. Kolner Zeitschrift für Soziologie und Sozialpsychologie
72. Language in Society
73. Law & Society Review
74. Leisure Sciences
75. Media Culture & Society
76. Men and Masculinities
77. Mobilization
78. Nations and Nationalism
79. New Directions for Child and Adolescent Development
80. Poetics
81. Polish Sociological Review
82. Politics & Society
83. Population and Development Review
84. Qualitative Research
85. Qualitative Sociology
86. Race & Class
87. Race and Social Problems
88. Rationality and Society
89. Research in Social Stratification and Mobility
90. Review of Religious Research
91. Revista Espanola de Investigaciones Sociologicas
92. Revista Internacional de Sociologia
93. Revue Francaise de Sociologie
94. Rural Sociology
95. Scandinavian Journal of Hospitality and Tourism
96. Sexualities
97. Social Compass
98. Social Forces
99. Social Indicators Research
100. Social Justice Research
101. Social Movement Studies
102. Social Networks
103. Social Problems
104. Social Psychology Quarterly
105. Social Science Quarterly
106. Social Science Research
107. Society
108. Society & Animals
109. Society & Natural Resources
110. Society and Mental Health
111. Socio-Economic Review
112. Sociologia
113. Sociologia Ruralis
114. Sociological Forum
115. Sociological Inquiry
116. Sociological Methodology
117. Sociological Methods & Research
118. Sociological Perspectives
119. Sociological Quarterly
120. Sociological Research Online
121. Sociological Review
122. Sociological Science
123. Sociological Spectrum
124. Sociological Theory
125. Sociologicky Casopis-Czech Sociological Review
126. Sociologie du Travail
127. Sociologisk Forskning
128. Sociologus
129. Sociology Compass
130. Sociology Lens
131. Sociology of Education
132. Sociology of Health & Illness
133. Sociology of Race and Ethnicity
134. Sociology of Religion
135. Sociology of Sport Journal
136. Sociology-the Journal of the British Sociological Association
137. Sotsiologicheskie Issledovaniya
138. Soziale Welt-Zeitschrift fur Sozialwissenschaftliche Forschung und Praxis
139. Sport in Society
140. Symbolic Interaction
141. Teaching Sociology
142. Telos
143. Tempo Social
144. Theory and Society
145. Work and Occupations
146. Work Employment and Society
147. Young
148. Youth & Society
149. Zeitschrift für Soziologie

<a id="ssci-substance-abuse"></a>

### Substance Abuse

期刊数：38

1. Addiction
2. Addiction Research & Theory
3. Addiction Science & Clinical Practice
4. Addictive Behaviors
5. Adicciones
6. Alcohol and Alcoholism
7. Alcohol Research-Current Reviews
8. American Journal of Drug and Alcohol Abuse
9. American Journal on Addictions
10. Current Addiction Reports
11. Drug and Alcohol Dependence
12. Drug and Alcohol Review
13. Drugs-Education Prevention and Policy
14. European Addiction Research
15. Harm Reduction Journal
16. Heroin Addiction and Related Clinical Problems
17. International Gambling Studies
18. International Journal of Drug Policy
19. International Journal of Mental Health and Addiction
20. Journal of Addictions Nursing
21. Journal of Addictive Diseases
22. Journal of Child & Adolescent Substance Use
23. Journal of Drug Issues
24. Journal of Dual Diagnosis
25. Journal of Ethnicity in Substance Abuse
26. Journal of Gambling Studies
27. Journal of Psychoactive Drugs
28. Journal of Studies on Alcohol and Drugs
29. Journal of Substance Use
30. Journal of Substance Use & Addiction Treatment
31. Nicotine & Tobacco Research
32. Nordic Studies on Alcohol and Drugs
33. Psychology of Addictive Behaviors
34. Substance Abuse Treatment Prevention and Policy
35. Substance Use & Addiction Journal
36. Substance Use & Misuse
37. Tobacco Control
38. Tobacco Induced Diseases

<a id="ssci-transportation"></a>

### Transportation

期刊数：38

1. Accident Analysis and Prevention
2. Analytic Methods in Accident Research
3. Communications in Transportation Research
4. Economics of Transportation
5. European Journal of Transport and Infrastructure Research
6. European Transport Research Review
7. International Journal of Shipping and Transport Logistics
8. International Journal of Sustainable Transportation
9. International Journal of Transport Economics
10. Journal of Air Transport Management
11. Journal of Intelligent Transportation Systems
12. Journal of Public Transportation
13. Journal of Safety Research
14. Journal of Transport & Health
15. Journal of Transport and Land Use
16. Journal of Transport Economics and Policy
17. Journal of Transport Geography
18. Journal of Transportation Safety & Security
19. Maritime Economics & Logistics
20. Maritime Policy & Management
21. Mobilities
22. Research in Transportation Business and Management
23. Research in Transportation Economics
24. Traffic Injury Prevention
25. Transport Policy
26. Transport Reviews
27. Transportation
28. Transportation Journal
29. Transportation Letters-the International Journal of Transportation Research
30. Transportation Research Part a-Policy and Practice
31. Transportation Research Part B-Methodological
32. Transportation Research Part d-Transport and Environment
33. Transportation Research Part e-Logistics and Transportation Review
34. Transportation Research Part F-Traffic Psychology and Behaviour
35. Transportation Science
36. Transportmetrica a-Transport Science
37. Transportmetrica B-Transport Dynamics
38. Travel Behaviour and Society

<a id="ssci-urban-studies"></a>

### Urban Studies

期刊数：45

1. Cities
2. City & Community
3. Economic Development Quarterly
4. Education and Urban Society
5. Environment and Planning B-Urban Analytics and City Science
6. Environment and Urbanization
7. EURE-Revista Latinoamericana de Estudios Urbano Regionales
8. European Planning Studies
9. European Urban and Regional Studies
10. Habitat International
11. Housing Policy Debate
12. Housing Studies
13. Housing Theory & Society
14. International Journal of Housing Policy
15. International Journal of Urban and Regional Research
16. International Journal of Urban Sciences
17. International Regional Science Review
18. Journal of Architectural and Planning Research
19. Journal of Contemporary Ethnography
20. Journal of Housing and the Built Environment
21. Journal of Housing Economics
22. Journal of Planning Education and Research
23. Journal of Planning Literature
24. Journal of Real Estate Finance and Economics
25. Journal of the American Planning Association
26. Journal of Urban Affairs
27. Journal of Urban Economics
28. Journal of Urban History
29. Journal of Urban Planning and Development
30. Journal of Urban Technology
31. Landscape and Urban Planning
32. Local Environment
33. Npj Urban Sustainability
34. Open House International-Sustainable & Smart Architecture and Urban Studies
35. Planning Theory & Practice
36. Real Estate Economics
37. Regional Science and Urban Economics
38. Urban Affairs Review
39. Urban Design International
40. Urban Education
41. Urban Forestry & Urban Greening
42. Urban Geography
43. Urban Policy and Research
44. Urban Research & Practice
45. Urban Studies

<a id="ssci-womens-studies"></a>

### Women's Studies

期刊数：46

1. Affilia-Feminist Inquiry in Social Work
2. Asian Journal of Womens Studies
3. Asian Women
4. Australian Feminist Studies
5. Differences-a Journal of Feminist Cultural Studies
6. European Journal of Womens Studies
7. Feminism & Psychology
8. Feminist Economics
9. Feminist Legal Studies
10. Feminist Media Studies
11. Feminist Review
12. Feminist Studies
13. Feminist Theory
14. Feministische Studien
15. Frontiers-a Journal of Women Studies
16. Gender & Society
17. Gender and History
18. Gender and Language
19. Gender in Management
20. Gender Place and Culture
21. Gender Work and Organization
22. Health Care for Women International
23. Hypatia-a Journal of Feminist Philosophy
24. Indian Journal of Gender Studies
25. International Feminist Journal of Politics
26. International Journal of Feminist Approaches to Bioethics
27. Journal of Gender Studies
28. Journal of Middle East Womens Studies
29. Journal of Women & Aging
30. Journal of Women Politics & Policy
31. Journal of Womens Health
32. Journal of Womens History
33. LGBTQ Family-an Interdisciplinary Journal
34. Politics & Gender
35. Psychology of Women Quarterly
36. Radical Philosophy
37. Sex Roles
38. Signs
39. Social Politics
40. Travail Genre et Societes
41. Violence Against Women
42. Women & Criminal Justice
43. Women & Health
44. Women & Therapy
45. Womens Health Issues
46. Womens Studies International Forum

<a id="ssci-unclassified"></a>

### Unclassified

期刊数：2

1. Ethics and Society
2. Journal for the Preservation of Library and Archival Material

<!-- SOURCE_END: Social Sciences Citation Index_20260715.md -->

## 第九检索层级：CSSCI 期刊

<!-- SOURCE_BEGIN: CSSCI_2025_2026.md -->

> 南京大学中国社会科学研究评价中心编制。本目录仅供数据库用户参考，不作其他用途。

| 序号 | 期刊名称 | 学科名称 |
|---|---|---|
| 1 | 安徽大学学报（哲学社会科学版） | 高校学报 |
| 2 | 安徽师范大学学报（社会科学版） | 高校学报 |
| 3 | 安徽史学 | 历史学 |
| 4 | 澳门理工学报（人文社会科学版） | 高校学报 |
| 5 | 保险研究 | 经济学 |
| 6 | 北方民族大学学报（哲学社会科学版） | 民族学与文化学 |
| 7 | 北京大学教育评论 | 教育学 |
| 8 | 北京大学学报（哲学社会科学版） | 高校学报 |
| 9 | 北京电影学院学报 | 艺术学 |
| 10 | 北京工商大学学报（社会科学版） | 经济学 |
| 11 | 北京工业大学学报（社会科学版） | 高校学报 |
| 12 | 北京联合大学学报（人文社会科学版） | 高校学报 |
| 13 | 北京师范大学学报（社会科学版） | 高校学报 |
| 14 | 北京体育大学学报 | 体育学 |
| 15 | 北京舞蹈学院学报 | 艺术学 |
| 16 | 北京行政学院学报 | 政治学 |
| 17 | 比较法研究 | 法学 |
| 18 | 比较教育研究 | 教育学 |
| 19 | 编辑学报 | 新闻学与传播学 |
| 20 | 编辑之友 | 新闻学与传播学 |
| 21 | 财经法学 | 法学 |
| 22 | 财经科学 | 经济学 |
| 23 | 财经理论与实践 | 经济学 |
| 24 | 财经论丛（浙江财经大学学报） | 经济学 |
| 25 | 财经问题研究 | 经济学 |
| 26 | 财经研究 | 经济学 |
| 27 | 财贸经济 | 经济学 |
| 28 | 财贸研究 | 经济学 |
| 29 | 财政研究 | 经济学 |
| 30 | 残疾人研究 | 社会学 |
| 31 | 产业经济研究 | 经济学 |
| 32 | 长江流域资源与环境 | 自然资源与环境科学 |
| 33 | 成都体育学院学报 | 体育学 |
| 34 | 城市发展研究 | 人文经济地理 |
| 35 | 城市规划 | 人文经济地理 |
| 36 | 城市规划学刊 | 人文经济地理 |
| 37 | 城市问题 | 人文经济地理 |
| 38 | 重庆大学学报（社会科学版） | 高校学报 |
| 39 | 重庆社会科学 | 综合性社会科学 |
| 40 | 出版发行研究 | 新闻学与传播学 |
| 41 | 出版科学 | 新闻学与传播学 |
| 42 | 出土文献 | 中华传统文化 |
| 43 | 传媒观察 | 新闻学与传播学 |
| 44 | 大连理工大学学报（社会科学版） | 高校学报 |
| 45 | 大学教育科学 | 教育学 |
| 46 | 大学图书馆学报 | 信息资源管理 |
| 47 | 当代财经 | 经济学 |
| 48 | 当代传播 | 新闻学与传播学 |
| 49 | 当代电影 | 艺术学 |
| 50 | 当代法学 | 法学 |
| 51 | 当代经济管理 | 管理学 |
| 52 | 当代经济科学 | 经济学 |
| 53 | 当代经济研究 | 经济学 |
| 54 | 当代美国评论 | 政治学 |
| 55 | 当代世界 | 政治学 |
| 56 | 当代世界社会主义问题 | 马克思主义理论 |
| 57 | 当代世界与社会主义 | 马克思主义理论 |
| 58 | 当代外国文学 | 外国文学 |
| 59 | 当代外语研究 | 语言学 |
| 60 | 当代文坛 | 中国文学 |
| 61 | 当代修辞学 | 语言学 |
| 62 | 当代亚太 | 政治学 |
| 63 | 当代语言学 | 语言学 |
| 64 | 当代中国史研究 | 历史学 |
| 65 | 当代作家评论 | 中国文学 |
| 66 | 党的文献 | 马克思主义理论 |
| 67 | 党建 | 马克思主义理论 |
| 68 | 党史研究与教学 | 马克思主义理论 |
| 69 | 档案学通讯 | 信息资源管理 |
| 70 | 档案学研究 | 信息资源管理 |
| 71 | 道德与文明 | 哲学 |
| 72 | 德国研究 | 政治学 |
| 73 | 地理科学 | 人文经济地理 |
| 74 | 地理科学进展 | 人文经济地理 |
| 75 | 地理学报（北京） | 人文经济地理 |
| 76 | 地理学报（台湾） | 人文经济地理 |
| 77 | 地理研究 | 人文经济地理 |
| 78 | 电化教育研究 | 教育学 |
| 79 | 电视研究 | 艺术学 |
| 80 | 电影艺术 | 艺术学 |
| 81 | 电子政务 | 管理学 |
| 82 | 东北大学学报（社会科学版） | 高校学报 |
| 83 | 东北师大学报（哲学社会科学版） | 高校学报 |
| 84 | 东北亚论坛 | 政治学 |
| 85 | 东方法学 | 法学 |
| 86 | 东南大学学报（哲学社会科学版） | 高校学报 |
| 87 | 东南文化 | 历史学 |
| 88 | 东南学术 | 综合性社会科学 |
| 89 | 东南亚研究 | 政治学 |
| 90 | 东岳论丛 | 综合性社会科学 |
| 91 | 读书 | 综合性社会科学 |
| 92 | 敦煌学辑刊 | 中华传统文化 |
| 93 | 敦煌研究 | 中华传统文化 |
| 94 | 法律科学（西北政法大学学报） | 法学 |
| 95 | 法律适用 | 法学 |
| 96 | 法商研究 | 法学 |
| 97 | 法学 | 法学 |
| 98 | 法学家 | 法学 |
| 99 | 法学论坛 | 法学 |
| 100 | 法学评论 | 法学 |
| 101 | 法学研究 | 法学 |
| 102 | 法学杂志 | 法学 |
| 103 | 法制与社会发展 | 法学 |
| 104 | 法治研究 | 法学 |
| 105 | 方言 | 语言学 |
| 106 | 福建论坛（人文社会科学版） | 综合性社会科学 |
| 107 | 福建师范大学学报（哲学社会科学版） | 高校学报 |
| 108 | 妇女研究论丛 | 社会学 |
| 109 | 复旦教育论坛 | 教育学 |
| 110 | 复旦学报（社会科学版） | 高校学报 |
| 111 | 改革 | 经济学 |
| 112 | 甘肃社会科学 | 综合性社会科学 |
| 113 | 甘肃行政学院学报 | 政治学 |
| 114 | 港澳研究 | 政治学 |
| 115 | 高等工程教育研究 | 教育学 |
| 116 | 高等教育研究 | 教育学 |
| 117 | 高校教育管理 | 教育学 |
| 118 | 工程管理科技前沿 | 管理学 |
| 119 | 公共管理评论 | 管理学 |
| 120 | 公共管理学报 | 管理学 |
| 121 | 公共管理与政能评论 | 管理学 |
| 122 | 公共行政评论 | 政治学 |
| 123 | 公共行政学报 | 政治学 |
| 124 | 古代文明 | 历史学 |
| 125 | 古汉语研究 | 语言学 |
| 126 | 故宫博物院院刊 | 考古学 |
| 127 | 管理工程学报 | 管理学 |
| 128 | 管理科学 | 管理学 |
| 129 | 管理科学学报 | 管理学 |
| 130 | 管理评论 | 管理学 |
| 131 | 管理世界 | 管理学 |
| 132 | 管理学报（湖北） | 管理学 |
| 133 | 管理学报（台湾） | 管理学 |
| 134 | 管理学刊 | 管理学 |
| 135 | 光明日报·理论版 | 马克思主义理论 |
| 136 | 广东财经大学学报 | 经济学 |
| 137 | 广东社会科学 | 综合性社会科学 |
| 138 | 广西大学学报（哲学社会科学版） | 高校学报 |
| 139 | 广西民族研究 | 民族学与文化学 |
| 140 | 广州大学学报（社会科学版） | 高校学报 |
| 141 | 贵州财经大学学报 | 经济学 |
| 142 | 贵州民族研究 | 民族学与文化学 |
| 143 | 贵州社会科学 | 综合性社会科学 |
| 144 | 国际安全研究 | 政治学 |
| 145 | 国际关系研究 | 政治学 |
| 146 | 国际观察 | 政治学 |
| 147 | 国际汉学 | 中华传统文化 |
| 148 | 国际金融研究 | 经济学 |
| 149 | 国际经济合作 | 经济学 |
| 150 | 国际经济评论 | 经济学 |
| 151 | 国际经贸探索 | 经济学 |
| 152 | 国际论坛 | 政治学 |
| 153 | 国际贸易 | 经济学 |
| 154 | 国际贸易问题 | 经济学 |
| 155 | 国际商务（对外经济贸易大学学报） | 经济学 |
| 156 | 国际税收 | 经济学 |
| 157 | 国际问题研究 | 政治学 |
| 158 | 国际新闻界 | 新闻学与传播学 |
| 159 | 国际展望 | 政治学 |
| 160 | 国际政治科学 | 政治学 |
| 161 | 国际政治研究 | 政治学 |
| 162 | 国家检察官学院学报 | 法学 |
| 163 | 国家教育行政学院学报 | 教育学 |
| 164 | 国家图书馆学刊 | 信息资源管理 |
| 165 | 国外理论动态 | 马克思主义理论 |
| 166 | 国外文学 | 外国文学 |
| 167 | 海南大学学报（人文社会科学版） | 高校学报 |
| 168 | 汉语学报 | 语言学 |
| 169 | 汉语学习 | 语言学 |
| 170 | 和平与发展 | 政治学 |
| 171 | 河北学刊 | 综合性社会科学 |
| 172 | 河海大学学报（哲学社会科学版） | 高校学报 |
| 173 | 河南大学学报（社会科学版） | 高校学报 |
| 174 | 河南师范大学学报（哲学社会科学版） | 高校学报 |
| 175 | 红旗文稿 | 马克思主义理论 |
| 176 | 宏观经济研究 | 经济学 |
| 177 | 宏观质量研究 | 管理学 |
| 178 | 湖北大学学报（哲学社会科学版） | 高校学报 |
| 179 | 湖北民族大学学报（哲学社会科学版） | 民族学与文化学 |
| 180 | 湖南大学学报（社会科学版） | 高校学报 |
| 181 | 湖南科技大学学报（社会科学版） | 高校学报 |
| 182 | 湖南师范大学教育科学学报 | 教育学 |
| 183 | 湖南师范大学社会科学学报 | 高校学报 |
| 184 | 华东经济管理 | 管理学 |
| 185 | 华东师范大学学报（教育科学版） | 教育学 |
| 186 | 华东师范大学学报（哲学社会科学版） | 高校学报 |
| 187 | 华东政法大学学报 | 法学 |
| 188 | 华南农业大学学报（社会科学版） | 高校学报 |
| 189 | 华南师范大学学报（社会科学版） | 高校学报 |
| 190 | 华侨华人历史研究 | 历史学 |
| 191 | 华文教学与研究 | 教育学 |
| 192 | 华中科技大学学报（社会科学版） | 高校学报 |
| 193 | 华中农业大学学报（社会科学版） | 高校学报 |
| 194 | 华中师范大学学报（人文社会科学版） | 高校学报 |
| 195 | 环球法律评论 | 法学 |
| 196 | 会计评论 | 管理学 |
| 197 | 会计研究 | 管理学 |
| 198 | 会计与经济研究 | 管理学 |
| 199 | 基础教育 | 教育学 |
| 200 | 吉林大学社会科学学报 | 高校学报 |
| 201 | 吉首大学学报（社会科学版） | 高校学报 |
| 202 | 济南大学学报（社会科学版） | 高校学报 |
| 203 | 暨南学报（哲学社会科学版） | 高校学报 |
| 204 | 建筑学报 | 艺术学 |
| 205 | 江海学刊 | 综合性社会科学 |
| 206 | 江汉考古 | 考古学 |
| 207 | 江汉论坛 | 综合性社会科学 |
| 208 | 江淮论坛 | 综合性社会科学 |
| 209 | 江苏高教 | 教育学 |
| 210 | 江苏社会科学 | 综合性社会科学 |
| 211 | 江苏行政学院学报 | 政治学 |
| 212 | 江西社会科学 | 综合性社会科学 |
| 213 | 江西师范大学学报（哲学社会科学版） | 高校学报 |
| 214 | 教师教育研究 | 教育学 |
| 215 | 教学与研究 | 马克思主义理论 |
| 216 | 教育发展研究 | 教育学 |
| 217 | 教育科学 | 教育学 |
| 218 | 教育科学研究期刊 | 教育学 |
| 219 | 教育实践与研究 | 教育学 |
| 220 | 教育学报 | 教育学 |
| 221 | 教育研究 | 教育学 |
| 222 | 教育研究与实验 | 教育学 |
| 223 | 教育与经济 | 教育学 |
| 224 | 金融经济学研究 | 经济学 |
| 225 | 金融评论 | 经济学 |
| 226 | 金融研究 | 经济学 |
| 227 | 近代史研究 | 历史学 |
| 228 | 经济地理 | 人文经济地理 |
| 229 | 经济管理 | 管理学 |
| 230 | 经济经纬 | 经济学 |
| 231 | 经济科学 | 经济学 |
| 232 | 经济理论与经济管理 | 经济学 |
| 233 | 经济论文 | 经济学 |
| 234 | 经济论文丛刊 | 经济学 |
| 235 | 经济评论 | 经济学 |
| 236 | 经济社会史评论 | 历史学 |
| 237 | 经济社会体制比较 | 经济学 |
| 238 | 经济体制改革 | 管理学 |
| 239 | 经济问题 | 经济学 |
| 240 | 经济问题探索 | 经济学 |
| 241 | 经济学（季刊） | 经济学 |
| 242 | 经济学报 | 经济学 |
| 243 | 经济学动态 | 经济学 |
| 244 | 经济学家 | 经济学 |
| 245 | 经济研究 | 经济学 |
| 246 | 经济与管理评论 | 经济学 |
| 247 | 经济与管理研究 | 经济学 |
| 248 | 经济纵横 | 经济学 |
| 249 | 开放教育研究 | 教育学 |
| 250 | 开放时代 | 综合性社会科学 |
| 251 | 抗日战争研究 | 历史学 |
| 252 | 考古 | 考古学 |
| 253 | 考古学报 | 考古学 |
| 254 | 考古与文物 | 考古学 |
| 255 | 科技进步与对能 | 管理学 |
| 256 | 科技与出版 | 新闻学与传播学 |
| 257 | 科学技术哲学研究 | 哲学 |
| 258 | 科学社会主义 | 马克思主义理论 |
| 259 | 科学学研究 | 管理学 |
| 260 | 科学学与科学技术管理 | 管理学 |
| 261 | 科研管理 | 管理学 |
| 262 | 课程教材教法 | 教育学 |
| 263 | 孔子研究 | 中华传统文化 |
| 264 | 兰州大学学报（社会科学版） | 高校学报 |
| 265 | 劳动经济研究 | 经济学 |
| 266 | 理论视野 | 马克思主义理论 |
| 267 | 理论探索 | 政治学 |
| 268 | 理论探讨 | 政治学 |
| 269 | 理论学刊 | 政治学 |
| 270 | 理论与改革 | 政治学 |
| 271 | 历史档案 | 历史学 |
| 272 | 历史地理研究 | 中华传统文化 |
| 273 | 历史人类学学刊 | 历史学 |
| 274 | 历史研究 | 历史学 |
| 275 | 历史语言研究所集刊 | 历史学 |
| 276 | 岭南学报 | 中国文学 |
| 277 | 鲁迅研究月刊 | 中国文学 |
| 278 | 伦理学研究 | 哲学 |
| 279 | 逻辑学研究 | 哲学 |
| 280 | 旅游科学 | 人文经济地理 |
| 281 | 旅游学刊 | 人文经济地理 |
| 282 | 马克思主义理论学科研究 | 马克思主义理论 |
| 283 | 马克思主义研究 | 马克思主义理论 |
| 284 | 马克思主义与现实 | 马克思主义理论 |
| 285 | 毛泽东邓小平理论研究 | 马克思主义理论 |
| 286 | 美国研究 | 政治学 |
| 287 | 美术 | 艺术学 |
| 288 | 美术研究 | 艺术学 |
| 289 | 民国档案 | 历史学 |
| 290 | 民俗研究 | 中华传统文化 |
| 291 | 民族教育研究 | 民族学与文化学 |
| 292 | 民族文学研究 | 中国文学 |
| 293 | 民族学刊 | 民族学与文化学 |
| 294 | 民族研究 | 民族学与文化学 |
| 295 | 民族艺术 | 艺术学 |
| 296 | 民族艺术研究 | 艺术学 |
| 297 | 民族语文 | 语言学 |
| 298 | 南昌大学学报（人文社会科学版） | 高校学报 |
| 299 | 南大法学 | 法学 |
| 300 | 南方经济 | 经济学 |
| 301 | 南方文坛 | 中国文学 |
| 302 | 南国学术 | 综合性社会科学 |
| 303 | 南京大学学报（哲学·人文科学．社会科学） | 高校学报 |
| 304 | 南京农业大学学报（社会科学版） | 高校学报 |
| 305 | 南京社会科学 | 综合性社会科学 |
| 306 | 南京师大学报（社会科学版） | 高校学报 |
| 307 | 南京艺术学院学报（美术与设计） | 艺术学 |
| 308 | 南开管理评论 | 管理学 |
| 309 | 南开经济研究 | 经济学 |
| 310 | 南开学报（哲学社会科学版） | 高校学报 |
| 311 | 南通大学学报（社会科学版） | 高校学报 |
| 312 | 南洋问题研究 | 政治学 |
| 313 | 内蒙古社会科学 | 综合性社会科学 |
| 314 | 宁夏社会科学 | 综合性社会科学 |
| 315 | 农村经济 | 经济学 |
| 316 | 农业技术经济 | 经济学 |
| 317 | 农业经济问题 | 经济学 |
| 318 | 欧洲研究 | 政治学 |
| 319 | 齐鲁学刊 | 高校学报 |
| 320 | 青海民族研究 | 民族学与文化学 |
| 321 | 青海社会科学 | 综合性社会科学 |
| 322 | 青年研究 | 社会学 |
| 323 | 清华大学教育研究 | 教育学 |
| 324 | 清华大学学报（哲学社会科学版） | 高校学报 |
| 325 | 清华法学 | 法学 |
| 326 | 清华中文学报 | 中国文学 |
| 327 | 清史研究 | 历史学 |
| 328 | 情报科学 | 信息资源管理 |
| 329 | 情报理论与实践 | 信息资源管理 |
| 330 | 情报学报 | 信息资源管理 |
| 331 | 情报杂志 | 信息资源管理 |
| 332 | 情报资料工作 | 信息资源管理 |
| 333 | 求实 | 政治学 |
| 334 | 求是 | 马克思主义理论 |
| 335 | 求是学刊 | 综合性社会科学 |
| 336 | 求索 | 综合性社会科学 |
| 337 | 全球传媒学刊 | 新闻学与传播学 |
| 338 | 全球教育展望 | 教育学 |
| 339 | 人口学刊 | 社会学 |
| 340 | 丿廴口石开究 | 社会学 |
| 341 | 人口与发展 | 社会学 |
| 342 | 人口与经济 | 社会学 |
| 343 | 人民论坛 | 综合性社会科学 |
| 344 | 人民日报·理论版 | 马克思主义理论 |
| 345 | 人权 | 政治学 |
| 346 | 人文地理 | 人文经济地理 |
| 347 | 人文杂志 | 综合性社会科学 |
| 348 | 人文中国学报 | 中国文学 |
| 349 | 日本侵华南京大屠杀研究 | 历史学 |
| 350 | 日本学刊 | 政治学 |
| 351 | 软科学 | 管理学 |
| 352 | 山东大学学报（哲学社会科学版） | 高校学报 |
| 353 | 山东社会科学 | 综合性社会科学 |
| 354 | 山东师范大学学报（社会科学版） | 高校学报 |
| 355 | 山西财经大学学报 | 经济学 |
| 356 | 山西大学学报（哲学社会科学版） | 高校学报 |
| 357 | 陕西师范大学学报（哲学社会科学版） | 高校学报 |
| 358 | 上海财经大学学报 | 经济学 |
| 359 | 上海大学学报（社会科学版） | 高校学报 |
| 360 | 上海翻译（中英文） | 语言学 |
| 361 | 上海交通大学学报（哲学社会科学版） | 高校学报 |
| 362 | 上海经济研究 | 经济学 |
| 363 | 上海师范大学学报（哲学社会科学版） | 高校学报 |
| 364 | 上海体育大学学报 | 体育学 |
| 365 | 上海行政学院学报 | 政治学 |
| 366 | 设计学报 | 艺术学 |
| 367 | 社会 | 社会学 |
| 368 | 社会保障评论 | 管理学 |
| 369 | 社会发展研究 | 社会学 |
| 370 | 社会建设 | 社会学 |
| 371 | 社会科学 | 综合性社会科学 |
| 372 | 社会科学辑刊 | 综合性社会科学 |
| 373 | 社会科学研究 | 综合性社会科学 |
| 374 | 社会科学战线 | 综合性社会科学 |
| 375 | 社会学评论 | 社会学 |
| 376 | 社会学研究 | 社会学 |
| 377 | 社会主义研究 | 马克思主义理论 |
| 378 | 深圳大学学报队文社会科学版） | 高校学报 |
| 379 | 沈阳体育学院学报 | 体育学 |
| 380 | 审计研究 | 管理学 |
| 381 | 审计与经济研究 | 管理学 |
| 382 | 生态文明研究 | 自然资源与环境科学 |
| 383 | 史林 | 历史学 |
| 384 | 史学集刊 | 历史学 |
| 385 | 史学理论研究 | 历史学 |
| 386 | 史学史研究 | 历史学 |
| 387 | 史学月刊 | 历史学 |
| 388 | 世界汉语教学 | 语言学 |
| 389 | 世界经济 | 经济学 |
| 390 | 世界经济文汇 | 经济学 |
| 391 | 世界经济研究 | 经济学 |
| 392 | 世界经济与政治 | 政治学 |
| 393 | 世界经济与政治论坛 | 经济学 |
| 394 | 世界历史 | 历史学 |
| 395 | 世界历史评论 | 历史学 |
| 396 | 世界社会科学 | 综合性社会科学 |
| 397 | 世界社会主义研究 | 马克思主义理论 |
| 398 | 世界哲学 | 哲学 |
| 399 | 世界宗教文化 | 宗教学 |
| 400 | 世界宗教研究 | 宗教学 |
| 401 | 首都师范大学学报（社会科学版） | 高校学报 |
| 402 | 书法研究 | 艺术学 |
| 403 | 数据分析与知识发现 | 信息资源管理 |
| 404 | 数理统计与管理 | 统计学 |
| 405 | 数量经济技术经济研究 | 经济学 |
| 406 | 税务研究 | 经济学 |
| 407 | 思想教育研究 | 马克思主义理论 |
| 408 | 思想理论教育 | 马克思主义理论 |
| 409 | 思想理论教育导刊 | 马克思主义理论 |
| 410 | 思想战线 | 综合性社会科学 |
| 411 | 四川大学学报（哲学社会科学版） | 高校学报 |
| 412 | 四川师范大学学报（社会科学版） | 高校学报 |
| 413 | 苏州大学学报（教育科学版） | 教育学 |
| 414 | 苏州大学学报（哲学社会科学版） | 高校学报 |
| 415 | 台大社会工作学刊 | 社会学 |
| 416 | 台大中文学报 | 中国文学 |
| 417 | 台湾大学美术史研究集刊 | 艺术学 |
| 418 | 台湾经济预测与政能 | 经济学 |
| 419 | 台湾研究 | 政治学 |
| 420 | 太平洋学报 | 政治学 |
| 421 | 探索 | 政治学 |
| 422 | 探索与争鸣 | 综合性社会科学 |
| 423 | 特殊教育研究学刊 | 教育学 |
| 424 | 体育科学 | 体育学 |
| 425 | 体育学报 | 体育学 |
| 426 | 体育学刊 | 体育学 |
| 427 | 体育学研究 | 体育学 |
| 428 | 体育与科学 | 体育学 |
| 429 | 天津社会科学 | 综合性社会科学 |
| 430 | 天津体育学院学报 | 体育学 |
| 431 | 同济大学学报（社会科学版） | 高校学报 |
| 432 | 统计研究 | 统计学 |
| 433 | 统计与决策 | 统计学 |
| 434 | 统计与信息论坛 | 统计学 |
| 435 | 统一战线学研究 | 马克思主义理论 |
| 436 | 图书馆 | 信息资源管理 |
| 437 | 图书馆建设 | 信息资源管理 |
| 438 | 图书馆论坛 | 信息资源管理 |
| 439 | 图书馆学研究 | 信息资源管理 |
| 440 | 图书馆杂志 | 信息资源管理 |
| 441 | 图书情报工作 | 信息资源管理 |
| 442 | 图书情报知识 | 信息资源管理 |
| 443 | 图书与情报 | 信息资源管理 |
| 444 | 图书资讯学刊 | 信息资源管理 |
| 445 | 外国经济与管理 | 管理学 |
| 446 | 外国文学 | 外国文学 |
| 447 | 外国文学动态研究 | 外国文学 |
| 448 | 外国文学评论 | 外国文学 |
| 449 | 外国文学研究 | 外国文学 |
| 450 | 外国语（上海外国语大学学报） | 语言学 |
| 451 | 外交评论 | 政治学 |
| 452 | 外语导刊 | 语言学 |
| 453 | 外语电化教学 | 语言学 |
| 454 | 外语教学 | 语言学 |
| 455 | 外语教学理论与实践 | 语言学 |
| 456 | 外语教学与研究 | 语言学 |
| 457 | 外语教育研究前沿 | 语言学 |
| 458 | 外语界 | 语言学 |
| 459 | 外语与外语教学 | 语言学 |
| 460 | 文化遗产 | 中华传统文化 |
| 461 | 文化杂志 | 中华传统文化 |
| 462 | 文化纵横 | 综合性社会科学 |
| 463 | 文史 | 历史学 |
| 464 | 文史哲 | 综合性社会科学 |
| 465 | 文物 | 考古学 |
| 466 | 文献 | 历史学 |
| 467 | 文学评论 | 中国文学 |
| 468 | 文学遗产 | 中国文学 |
| 469 | 文艺理论研究 | 中国文学 |
| 470 | 文艺理论与批评 | 中国文学 |
| 471 | 文艺研究 | 艺术学 |
| 472 | 文艺争鸣 | 中国文学 |
| 473 | 文与哲 | 中国文学 |
| 474 | 武汉大学学报（哲学社会科学版） | 高校学报 |
| 475 | 武汉体育学院学报 | 体育学 |
| 476 | 西安财经大学学报 | 经济学 |
| 477 | 西安交通大学学报（社会科学版） | 高校学报 |
| 478 | 西安体育学院学报 | 体育学 |
| 479 | 西北大学学报（哲学社会科学版） | 高校学报 |
| 480 | 西北民族研究 | 民族学与文化学 |
| 481 | 西北农林科技大学学报（社会科学版） | 高校学报 |
| 482 | 西北师大学报（社会科学版） | 高校学报 |
| 483 | 西南大学学报（社会科学版） | 高校学报 |
| 484 | 西南民族大学学报（人文社会科学版） | 民族学与文化学 |
| 485 | 西亚非洲 | 政治学 |
| 486 | 西域研究 | 中华传统文化 |
| 487 | 西藏大学学报（藏文版） | 高校学报 |
| 488 | 西藏大学学报（社会科学版） | 高校学报 |
| 489 | 西藏研究（藏文） | 民族学与文化学 |
| 490 | 戏剧忡央戏剧学院学报） | 艺术学 |
| 491 | 戏剧艺术（上海戏剧学院学报） | 艺术学 |
| 492 | 戏曲艺术 | 艺术学 |
| 493 | 系统工程理论与实践 | 管理学 |
| 494 | 系统管理学报 | 管理学 |
| 495 | 厦门大学学报（哲学社会科学版） | 高校学报 |
| 496 | 现代财经（天津财经大学学报） | 经济学 |
| 497 | 现代出版 | 新闻学与传播学 |
| 498 | 现代传播（中国传媒大学学报） | 新闻学与传播学 |
| 499 | 现代大学教育 | 教育学 |
| 500 | 现代法学 | 法学 |
| 501 | 现代国际关系 | 政治学 |
| 502 | 现代教育管理 | 教育学 |
| 503 | 现代教育技术 | 教育学 |
| 504 | 现代金融研究 | 经济学 |
| 505 | 现代经济探讨 | 经济学 |
| 506 | 现代情报 | 信息资源管理 |
| 507 | 现代外语 | 语言学 |
| 508 | 现代远程教育研究 | 教育学 |
| 509 | 现代远距离教育 | 教育学 |
| 510 | 现代哲学 | 哲学 |
| 511 | 现代中文学刊 | 中国文学 |
| 512 | 湘潭大学学报（哲学社会科学版） | 高校学报 |
| 513 | 小说评论 | 中国文学 |
| 514 | 心理发展与教育 | 心理学 |
| 515 | 心理科学 | 心理学 |
| 516 | 心理科学进展 | 心理学 |
| 517 | 心理学报 | 心理学 |
| 518 | 理与行为研究 | 心理学 |
| 519 | 新疆社会科学 | 综合性社会科学 |
| 520 | 新疆师范大学学报（哲学社会科学版） | 高校学报 |
| 521 | 新美术 | 艺术学 |
| 522 | 新文学史料 | 中国文学 |
| 523 | 新闻大学 | 新闻学与传播学 |
| 524 | 新闻记者 | 新闻学与传播学 |
| 525 | 新闻界 | 新闻学与传播学 |
| 526 | 新闻与传播评论 | 新闻学与传播学 |
| 527 | 新闻与传播研究 | 新闻学与传播学 |
| 528 | 新闻与写作 | 新闻学与传播学 |
| 529 | 信息资源管理学报 | 信息资源管理 |
| 530 | 行政法学研究 | 法学 |
| 531 | 行政管理改革 | 管理学 |
| 532 | 行政论坛 | 政治学 |
| 533 | 学海 | 综合性社会科学 |
| 534 | 学前教育研究 | 教育学 |
| 535 | 学术界 | 综合性社会科学 |
| 536 | 学术论坛 | 综合性社会科学 |
| 537 | 学术前沿 | 综合性社会科学 |
| 538 | 学术研究 | 综合性社会科学 |
| 539 | 学术月刊 | 综合性社会科学 |
| 540 | 学位与研究生教育 | 教育学 |
| 541 | 学习与实践 | 综合性社会科学 |
| 542 | 学习与探索 | 综合性社会科学 |
| 543 | 亚太安全与海洋研究 | 政治学 |
| 544 | 亚太经济 | 经济学 |
| 545 | 研究生教育研究 | 教育学 |
| 546 | 研究与发展管理 | 管理学 |
| 547 | 扬子江文学评论 | 中国文学 |
| 548 | 艺术设计研究（中英文） | 艺术学 |
| 549 | 音乐研究 | 艺术学 |
| 550 | 音乐艺术（上海音乐学院学报） | 艺术学 |
| 551 | 应用心理学 | 心理学 |
| 552 | 语文研究 | 语言学 |
| 553 | 语言教学与研究 | 语言学 |
| 554 | 语言科学 | 语言学 |
| 555 | 语言文字应用 | 语言学 |
| 556 | 语言研究 | 语言学 |
| 557 | 语言战略研究 | 语言学 |
| 558 | 远程教育杂志 | 教育学 |
| 559 | 月旦法学 | 法学 |
| 560 | 云南民族大学学报（哲学社会科学版） | 民族学与文化学 |
| 561 | 云南社会科学 | 综合性社会科学 |
| 562 | 云南师范大学学报（哲学社会科学版） | 高校学报 |
| 563 | 哲学动态 | 哲学 |
| 564 | 哲学分析 | 哲学 |
| 565 | 哲学研究 | 哲学 |
| 566 | 哲学与文化 | 哲学 |
| 567 | 浙江大学学报队文社会科学版） | 高校学报 |
| 568 | 浙江工商大学学报 | 高校学报 |
| 569 | 浙江社会科学 | 综合性社会科学 |
| 570 | 浙江学刊 | 综合性社会科学 |
| 571 | 证券市场导报 | 经济学 |
| 572 | 证券市场发展李刊 | 管理学 |
| 573 | 郑州大学学报（哲学社会科学版） | 高校学报 |
| 574 | 政大法学评论 | 法学 |
| 575 | 政法论丛 | 法学 |
| 576 | 政法论坛 | 法学 |
| 577 | 政治大学哲学学报 | 哲学 |
| 578 | 政治经济学评论 | 经济学 |
| 579 | 政治学研究 | 政治学 |
| 580 | 政治与法律 | 法学 |
| 581 | 知识产权 | 法学 |
| 582 | 治理研究 | 管理学 |
| 583 | 中共党史研究 | 马克思主义理论 |
| 584 | 中共中央党校（国家行政学院）学报 | 政治学 |
| 585 | 中国比较文学 | 中国文学 |
| 586 | 中国边疆史地研究 | 中华传统文化 |
| 587 | 中国编辑 | 新闻学与传播学 |
| 588 | 中国出版 | 新闻学与传播学 |
| 589 | 中国大学教学 | 教育学 |
| 590 | 中国当代文学研究 | 中国文学 |
| 591 | 中国地质大学学报（社会科学版） | 高校学报 |
| 592 | 中国电化教育 | 教育学 |
| 593 | 中国电视 | 艺术学 |
| 594 | 中国法律评论 | 法学 |
| 595 | 中国法学 | 法学 |
| 596 | 中国翻译 | 语言学 |
| 597 | 中国高等教育 | 教育学 |
| 598 | 中国高教研究 | 教育学 |
| 599 | 中国高校社会科学 | 综合性社会科学 |
| 600 | 中国工业经济 | 经济学 |
| 601 | 中国管理科学 | 管理学 |
| 602 | 中国环境管理 | 自然资源与环境科学 |
| 603 | 中国教育学刊 | 教育学 |
| 604 | 中国经济史研究 | 历史学 |
| 605 | 中国经济问题 | 经济学 |
| 606 | 中国科技论坛 | 管理学 |
| 607 | 中国科技期刊研究 | 新闻学与传播学 |
| 608 | 中国科技史杂志 | 历史学 |
| 609 | 中国科学院院刊 | 管理学 |
| 610 | 中国矿业大学学报（社会科学版） | 高校学报 |
| 611 | 中国历史地理论丛 | 中华传统文化 |
| 612 | 中国临床心理学杂志 | 心理学 |
| 613 | 中国流通经济 | 经济学 |
| 614 | 中国农村观察 | 经济学 |
| 615 | 中国农村经济 | 经济学 |
| 616 | 中国农史 | 历史学 |
| 617 | 中国农业大学学报（社会科学版） | 高校学报 |
| 618 | 中国评论 | 政治学 |
| 619 | 中国青年研究 | 社会学 |
| 620 | 中国人口·资源与环境 | 自然资源与环境科学 |
| 621 | 中国人口科学 | 社会学 |
| 622 | 中国人力资源开发 | 管理学 |
| 623 | 中国人民大学学报 | 高校学报 |
| 624 | 中国人民公安大学学报（社会科学版） | 政治学 |
| 625 | 中国软科学 | 管理学 |
| 626 | 中国社会经济史研究 | 历史学 |
| 627 | 中国社会科学 | 综合性社会科学 |
| 628 | 中国社会科学评价 | 综合性社会科学 |
| 629 | 中国社会科学院大学学报 | 高校学报 |
| 630 | 中国史研究 | 历史学 |
| 631 | 中国史研究动态 | 历史学 |
| 632 | 中国书法 | 艺术学 |
| 633 | 中国特色社会主义研究 | 马克思主义理论 |
| 634 | 中国特殊教育 | 教育学 |
| 635 | 中国体育科技 | 体育学 |
| 636 | 中国图书馆学报 | 信息资源管理 |
| 637 | 中国土地科学 | 自然资源与环境科学 |
| 638 | 中国外语 | 语言学 |
| 639 | 中国文化研究所学报 | 综合性社会科学 |
| 640 | 中国文学批评 | 中国文学 |
| 641 | 中国文学研究 | 中国文学 |
| 642 | 中国文艺评论 | 艺术学 |
| 643 | 中国现代文学研究丛刊 | 中国文学 |
| 644 | 中国刑事法杂志 | 法学 |
| 645 | 中国行政管理 | 管理学 |
| 646 | 中国音乐 | 艺术学 |
| 647 | 中国音乐学 | 艺术学 |
| 648 | 中国应用法学 | 法学 |
| 649 | 中国语文 | 语言学 |
| 650 | 中国语文通讯 | 语言学 |
| 651 | 中国语文研究 | 语言学 |
| 652 | 中国远程教育 | 教育学 |
| 653 | 中国藏学 | 民族学与文化学 |
| 654 | 中国藏学（藏文） | 民族学与文化学 |
| 655 | 中国哲学史 | 哲学 |
| 656 | 中华文史论丛 | 历史学 |
| 657 | 中南财经政法大学学报 | 经济学 |
| 658 | 中南大学学报（社会科学版） | 高校学报 |
| 659 | 中南民族大学学报（人文社会科学版） | 民族学与文化学 |
| 660 | 中山大学学报（社会科学版） | 高校学报 |
| 661 | 中外法学 | 法学 |
| 662 | 中央财经大学学报 | 经济学 |
| 663 | 中央民族大学学报（哲学社会科学版） | 民族学与文化学 |
| 664 | 中央音乐学院学报 | 艺术学 |
| 665 | 中原文物 | 考古学 |
| 666 | 中州学刊 | 综合性社会科学 |
| 667 | 周易研究 | 中华传统文化 |
| 668 | 装饰 | 艺术学 |
| 669 | 资源科学 | 自然资源与环境科学 |
| 670 | 自然辩证法通讯 | 哲学 |
| 671 | 自然辩证法研究 | 哲学 |
| 672 | 自然资源学报 | 自然资源与环境科学 |
| 673 | 宗教学研究 | 宗教学 |
| 674 | 组织与管理 | 管理学 |

<!-- SOURCE_END: CSSCI_2025_2026.md -->

## 第十检索层级：SCIE 期刊

<!-- SOURCE_BEGIN: Science Citation Index Expanded_20260715.md -->

> 数据来源：`Science Citation Index Expanded (SCIE).csv`。期刊按 Web of Science 学科分类整理；同一期刊如属于多个学科，将分别列入相应类别。期刊题名优先依据 ISSN 对应的出版商元数据校正，未匹配部分按标题式规则处理；缩写与正式专名保留规范形式。

- 期刊总数：9,430
- 学科类别：178
- 未分类期刊：2

### SCIE 来源内目录

- [Acoustics](#scie-acoustics) (31)
- [Agricultural Economics & Policy](#scie-agricultural-economics-policy) (22)
- [Agricultural Engineering](#scie-agricultural-engineering) (14)
- [Agriculture, Dairy & Animal Science](#scie-agriculture-dairy-animal-science) (62)
- [Agriculture, Multidisciplinary](#scie-agriculture-multidisciplinary) (59)
- [Agronomy](#scie-agronomy) (87)
- [Allergy](#scie-allergy) (27)
- [Anatomy & Morphology](#scie-anatomy-morphology) (20)
- [Andrology](#scie-andrology) (8)
- [Anesthesiology](#scie-anesthesiology) (34)
- [Astronomy & Astrophysics](#scie-astronomy-astrophysics) (70)
- [Audiology & Speech-Language Pathology](#scie-audiology-speech-language-pathology) (27)
- [Automation & Control Systems](#scie-automation-control-systems) (64)
- [Behavioral Sciences](#scie-behavioral-sciences) (52)
- [Biochemical Research Methods](#scie-biochemical-research-methods) (76)
- [Biochemistry & Molecular Biology](#scie-biochemistry-molecular-biology) (281)
- [Biodiversity Conservation](#scie-biodiversity-conservation) (64)
- [Biology](#scie-biology) (88)
- [Biophysics](#scie-biophysics) (70)
- [Biotechnology & Applied Microbiology](#scie-biotechnology-applied-microbiology) (157)
- [Cardiac & Cardiovascular System](#scie-cardiac-cardiovascular-system) (143)
- [Cell & Tissue Engineering](#scie-cell-tissue-engineering) (28)
- [Cell Biology](#scie-cell-biology) (189)
- [Chemistry, Analytical](#scie-chemistry-analytical) (87)
- [Chemistry, Applied](#scie-chemistry-applied) (72)
- [Chemistry, Inorganic & Nuclear](#scie-chemistry-inorganic-nuclear) (42)
- [Chemistry, Medicinal](#scie-chemistry-medicinal) (60)
- [Chemistry, Multidisciplinary](#scie-chemistry-multidisciplinary) (176)
- [Chemistry, Organic](#scie-chemistry-organic) (51)
- [Chemistry, Physical](#scie-chemistry-physical) (162)
- [Clinical Neurology](#scie-clinical-neurology) (213)
- [Computer Science, Artificial Intelligence](#scie-computer-science-artificial-intelligence) (143)
- [Computer Science, Cybernetics](#scie-computer-science-cybernetics) (24)
- [Computer Science, Hardware & Architecture](#scie-computer-science-hardware-architecture) (51)
- [Computer Science, Information Systems](#scie-computer-science-information-systems) (155)
- [Computer Science, Interdisciplinary Applications](#scie-computer-science-interdisciplinary-applications) (112)
- [Computer Science, Software Engineering](#scie-computer-science-software-engineering) (106)
- [Computer Science, Theory & Methods](#scie-computer-science-theory-methods) (110)
- [Construction & Building Technology](#scie-construction-building-technology) (68)
- [Critical Care Medicine](#scie-critical-care-medicine) (37)
- [Crystallography](#scie-crystallography) (26)
- [Dentistry, Oral Surgery & Medicine](#scie-dentistry-oral-surgery-medicine) (91)
- [Dermatology](#scie-dermatology) (69)
- [Developmental Biology](#scie-developmental-biology) (38)
- [Ecology](#scie-ecology) (171)
- [Education, Scientific Disciplines](#scie-education-scientific-disciplines) (44)
- [Electrochemistry](#scie-electrochemistry) (31)
- [Emergency Medicine](#scie-emergency-medicine) (31)
- [Endocrinology & Metabolism](#scie-endocrinology-metabolism) (142)
- [Energy & Fuels](#scie-energy-fuels) (119)
- [Engineering, Aerospace](#scie-engineering-aerospace) (36)
- [Engineering, Biomedical](#scie-engineering-biomedical) (99)
- [Engineering, Chemical](#scie-engineering-chemical) (142)
- [Engineering, Civil](#scie-engineering-civil) (139)
- [Engineering, Electrical & Electronic](#scie-engineering-electrical-electronic) (268)
- [Engineering, Environmental](#scie-engineering-environmental) (54)
- [Engineering, Geological](#scie-engineering-geological) (41)
- [Engineering, Industrial](#scie-engineering-industrial) (50)
- [Engineering, Manufacturing](#scie-engineering-manufacturing) (50)
- [Engineering, Marine](#scie-engineering-marine) (16)
- [Engineering, Mechanical](#scie-engineering-mechanical) (136)
- [Engineering, Multidisciplinary](#scie-engineering-multidisciplinary) (90)
- [Engineering, Ocean](#scie-engineering-ocean) (15)
- [Engineering, Petroleum](#scie-engineering-petroleum) (17)
- [Entomology](#scie-entomology) (100)
- [Environmental Sciences](#scie-environmental-sciences) (273)
- [Evolutionary Biology](#scie-evolutionary-biology) (51)
- [Fisheries](#scie-fisheries) (54)
- [Food Science & Technology](#scie-food-science-technology) (137)
- [Forestry](#scie-forestry) (69)
- [Gastroenterology & Hepatology](#scie-gastroenterology-hepatology) (93)
- [Genetics & Heredity](#scie-genetics-heredity) (169)
- [Geochemistry & Geophysics](#scie-geochemistry-geophysics) (87)
- [Geography, Physical](#scie-geography-physical) (50)
- [Geology](#scie-geology) (49)
- [Geosciences, Multidisciplinary](#scie-geosciences-multidisciplinary) (199)
- [Geriatrics & Gerontology](#scie-geriatrics-gerontology) (56)
- [Green & Sustainable Science & Technology](#scie-green-sustainable-science-technology) (47)
- [Health Care Sciences & Services](#scie-health-care-sciences-services) (107)
- [Hematology](#scie-hematology) (78)
- [History & Philosophy of Science](#scie-history-philosophy-of-science) (60)
- [Horticulture](#scie-horticulture) (37)
- [Imaging Science & Photographic Technology](#scie-imaging-science-photographic-technology) (27)
- [Immunology](#scie-immunology) (157)
- [Infectious Diseases](#scie-infectious-diseases) (94)
- [Instruments & Instrumentation](#scie-instruments-instrumentation) (62)
- [Integrative & Complementary Medicine](#scie-integrative-complementary-medicine) (28)
- [Limnology](#scie-limnology) (21)
- [Logic](#scie-logic) (21)
- [Marine & Freshwater Biology](#scie-marine-freshwater-biology) (109)
- [Materials Science, Biomaterials](#scie-materials-science-biomaterials) (44)
- [Materials Science, Ceramics](#scie-materials-science-ceramics) (29)
- [Materials Science, Characterization, Testing](#scie-materials-science-characterization-testing) (31)
- [Materials Science, Coatings & Films](#scie-materials-science-coatings-films) (21)
- [Materials Science, Composites](#scie-materials-science-composites) (26)
- [Materials Science, Multidisciplinary](#scie-materials-science-multidisciplinary) (341)
- [Materials Science, Paper & Wood](#scie-materials-science-paper-wood) (21)
- [Materials Science, Textiles](#scie-materials-science-textiles) (26)
- [Mathematical & Computational Biology](#scie-mathematical-computational-biology) (53)
- [Mathematics](#scie-mathematics) (334)
- [Mathematics, Applied](#scie-mathematics-applied) (267)
- [Mathematics, Interdisciplinary Applications](#scie-mathematics-interdisciplinary-applications) (106)
- [Mechanics](#scie-mechanics) (137)
- [Medical Ethics](#scie-medical-ethics) (16)
- [Medical Informatics](#scie-medical-informatics) (32)
- [Medical Laboratory Technology](#scie-medical-laboratory-technology) (29)
- [Medicine, General & Internal](#scie-medicine-general-internal) (162)
- [Medicine, Legal](#scie-medicine-legal) (17)
- [Medicine, Research & Experimental](#scie-medicine-research-experimental) (134)
- [Metallurgy & Metallurgical Engineering](#scie-metallurgy-metallurgical-engineering) (80)
- [Meteorology & Atmospheric Sciences](#scie-meteorology-atmospheric-sciences) (95)
- [Microbiology](#scie-microbiology) (134)
- [Microscopy](#scie-microscopy) (8)
- [Mineralogy](#scie-mineralogy) (29)
- [Mining & Mineral Processing](#scie-mining-mineral-processing) (21)
- [Multidisciplinary Sciences](#scie-multidisciplinary-sciences) (76)
- [Mycology](#scie-mycology) (29)
- [Nanoscience & Nanotechnology](#scie-nanoscience-nanotechnology) (107)
- [Neuroimaging](#scie-neuroimaging) (14)
- [Neurosciences](#scie-neurosciences) (271)
- [Nuclear Science & Technology](#scie-nuclear-science-technology) (34)
- [Nursing](#scie-nursing) (125)
- [Nutrition & Dietetics](#scie-nutrition-dietetics) (87)
- [Obstetrics & Gynecology](#scie-obstetrics-gynecology) (84)
- [Oceanography](#scie-oceanography) (63)
- [Oncology](#scie-oncology) (240)
- [Operations Research & Management Science](#scie-operations-research-management-science) (86)
- [Ophthalmology](#scie-ophthalmology) (62)
- [Optics](#scie-optics) (100)
- [Ornithology](#scie-ornithology) (27)
- [Orthopedics](#scie-orthopedics) (86)
- [Otorhinolaryngology](#scie-otorhinolaryngology) (43)
- [Paleontology](#scie-paleontology) (54)
- [Parasitology](#scie-parasitology) (38)
- [Pathology](#scie-pathology) (75)
- [Pediatrics](#scie-pediatrics) (129)
- [Peripheral Vascular Diseases](#scie-peripheral-vascular-diseases) (67)
- [Pharmacology & Pharmacy](#scie-pharmacology-pharmacy) (270)
- [Physics, Applied](#scie-physics-applied) (160)
- [Physics, Atomic, Molecular & Chemical](#scie-physics-atomic-molecular-chemical) (33)
- [Physics, Condensed Matter](#scie-physics-condensed-matter) (67)
- [Physics, Fluids & Plasmas](#scie-physics-fluids-plasmas) (34)
- [Physics, Mathematical](#scie-physics-mathematical) (56)
- [Physics, Multidisciplinary](#scie-physics-multidisciplinary) (84)
- [Physics, Nuclear](#scie-physics-nuclear) (19)
- [Physics, Particles & Fields](#scie-physics-particles-fields) (29)
- [Physiology](#scie-physiology) (79)
- [Plant Sciences](#scie-plant-sciences) (238)
- [Polymer Science](#scie-polymer-science) (86)
- [Primary Health Care](#scie-primary-health-care) (18)
- [Psychiatry](#scie-psychiatry) (153)
- [Psychology](#scie-psychology) (80)
- [Public, Environmental & Occupational Health](#scie-public-environmental-occupational-health) (208)
- [Quantum Science & Technology](#scie-quantum-science-technology) (18)
- [Radiology, Nuclear Medicine & Medical Imaging](#scie-radiology-nuclear-medicine-medical-imaging) (136)
- [Rehabilitation](#scie-rehabilitation) (68)
- [Remote Sensing](#scie-remote-sensing) (36)
- [Reproductive Biology](#scie-reproductive-biology) (31)
- [Respiratory System](#scie-respiratory-system) (66)
- [Rheumatology](#scie-rheumatology) (34)
- [Robotics](#scie-robotics) (31)
- [Soil Science](#scie-soil-science) (38)
- [Spectroscopy](#scie-spectroscopy) (40)
- [Sport Sciences](#scie-sport-sciences) (86)
- [Statistics & Probability](#scie-statistics-probability) (126)
- [Substance Abuse](#scie-substance-abuse) (21)
- [Surgery](#scie-surgery) (212)
- [Telecommunications](#scie-telecommunications) (90)
- [Thermodynamics](#scie-thermodynamics) (63)
- [Toxicology](#scie-toxicology) (94)
- [Transplantation](#scie-transplantation) (25)
- [Transportation Science & Technology](#scie-transportation-science-technology) (42)
- [Tropical Medicine](#scie-tropical-medicine) (25)
- [Urology & Nephrology](#scie-urology-nephrology) (88)
- [Veterinary Sciences](#scie-veterinary-sciences) (142)
- [Virology](#scie-virology) (36)
- [Water Resources](#scie-water-resources) (99)
- [Zoology](#scie-zoology) (175)
- [Unclassified](#scie-unclassified) (2)

<a id="scie-acoustics"></a>

### Acoustics

期刊数：31

1. Acoustical Physics
2. Acoustics Australia
3. Acta Acustica
4. Applied Acoustics
5. Archives of Acoustics
6. IEEE Transactions on Audio Speech and Language Processing
7. IEEE Transactions on Ultrasonics Ferroelectrics and Frequency Control
8. International Journal of Acoustics and Vibration
9. International Journal of Aeroacoustics
10. Journal of Clinical Ultrasound
11. Journal of Low Frequency Noise Vibration and Active Control
12. Journal of Sound and Vibration
13. Journal of the Acoustical Society of America
14. Journal of the Audio Engineering Society
15. Journal of Theoretical and Computational Acoustics
16. Journal of Ultrasound in Medicine
17. Journal of Vibration and Acoustics-Transactions of the ASME
18. Journal of Vibration and Control
19. Journal on Audio Speech and Music Processing
20. Medical Ultrasonography
21. Noise Control Engineering Journal
22. Phonetica
23. Shock and Vibration
24. Speech Communication
25. Ultraschall in der Medizin
26. Ultrasonic Imaging
27. Ultrasonics
28. Ultrasonics Sonochemistry
29. Ultrasound in Medicine and Biology
30. Ultrasound in Obstetrics & Gynecology
31. Wave Motion

<a id="scie-agricultural-economics-policy"></a>

### Agricultural Economics & Policy

期刊数：22

1. Agrekon
2. Agribusiness
3. Agricultural and Food Economics
4. Agricultural Economics
5. Agricultural Economics-Zemedelska Ekonomika
6. American Journal of Agricultural Economics
7. Annual Review of Resource Economics
8. Applied Economic Perspectives and Policy
9. Aquaculture Economics & Management
10. Australian Journal of Agricultural and Resource Economics
11. British Food Journal
12. Canadian Journal of Agricultural Economics-Revue Canadienne d Agroeconomie
13. China Agricultural Economic Review
14. Custos e Agronegocio on Line
15. European Review of Agricultural Economics
16. Food Policy
17. German Journal of Agricultural Economics
18. International Food and Agribusiness Management Review
19. Journal of Agricultural and Resource Economics
20. Journal of Agricultural Economics
21. Journal of Wine Economics
22. New Medit

<a id="scie-agricultural-engineering"></a>

### Agricultural Engineering

期刊数：14

1. Ama-Agricultural Mechanization in Asia Africa and Latin America
2. Applied Engineering in Agriculture
3. Aquacultural Engineering
4. Biomass & Bioenergy
5. Bioresource Technology
6. Biosystems Engineering
7. Engenharia Agricola
8. Industrial Crops and Products
9. International Journal of Agricultural and Biological Engineering
10. Journal of Agricultural Engineering
11. Journal of Irrigation and Drainage Engineering
12. Journal of the ASABE
13. Paddy and Water Environment
14. Revista Brasileira de Engenharia Agricola e Ambiental

<a id="scie-agriculture-dairy-animal-science"></a>

### Agriculture, Dairy & Animal Science

期刊数：62

1. Acta Agriculturae Scandinavica Section A-Animal Science
2. Animal
3. Animal Bioscience
4. Animal Biotechnology
5. Animal Feed Science and Technology
6. Animal Frontiers
7. Animal Genetics
8. Animal Nutrition
9. Animal Production Science
10. Animal Reproduction
11. Animal Reproduction Science
12. Animal Science Journal
13. Animal Science Papers and Reports
14. Animals
15. Annals of Animal Science
16. Annual Review of Animal Biosciences
17. Applied Animal Behaviour Science
18. Archives Animal Breeding
19. Archives of Animal Nutrition
20. Avian Biology Research
21. Brazilian Journal of Poultry Science
22. British Poultry Science
23. Buffalo Bulletin
24. Canadian Journal of Animal Science
25. Czech Journal of Animal Science
26. Domestic Animal Endocrinology
27. European Poultry Science
28. Fourrages
29. Genetics Selection Evolution
30. Indian Journal of Animal Research
31. Indian Journal of Animal Sciences
32. INRAE Productions Animales
33. Italian Journal of Animal Science
34. Itea-Informacion Tecnica Economica Agraria
35. Journal of Animal and Feed Sciences
36. Journal of Animal Breeding and Genetics
37. Journal of Animal Physiology and Animal Nutrition
38. Journal of Animal Science
39. Journal of Animal Science and Biotechnology
40. Journal of Animal Science and Technology
41. Journal of Applied Animal Research
42. Journal of Applied Poultry Research
43. Journal of Dairy Research
44. Journal of Dairy Science
45. Journal of Poultry Science
46. Journal of Reproduction and Development
47. Large Animal Review
48. Livestock Science
49. Mljekarstvo
50. Poultry Science
51. Reproduction in Domestic Animals
52. Revista Brasileira de Zootecnia-Brazilian Journal of Animal Science
53. Revista Colombiana de Ciencias Pecuarias
54. Revista Mexicana de Ciencias Pecuarias
55. Revista Mvz Cordoba
56. Small Ruminant Research
57. South African Journal of Animal Science
58. Tropical Animal Health and Production
59. Tropical Grasslands-Forrajes Tropicales
60. World Rabbit Science
61. Worlds Poultry Science Journal
62. Zuchtungskunde

<a id="scie-agriculture-multidisciplinary"></a>

### Agriculture, Multidisciplinary

期刊数：59

1. Agrarforschung Schweiz
2. Agricultural & Environmental Letters
3. Agricultural and Food Science
4. Agricultural Systems
5. Agriculture and Human Values
6. Agriculture Ecosystems & Environment
7. Agrociencia
8. Agroecology and Sustainable Food Systems
9. Annals of Agricultural Sciences
10. Annals of Applied Biology
11. Artificial Intelligence in Agriculture
12. Berichte Uber Landwirtschaft
13. Bioscience Journal
14. Biosystems Engineering
15. Bragantia
16. Cahiers Agricultures
17. California Agriculture
18. Chemical and Biological Technologies in Agriculture
19. Chilean Journal of Agricultural Research
20. Ciencia e Agrotecnologia
21. Cogent Food & Agriculture
22. Computers and Electronics in Agriculture
23. Crop & Pasture Science
24. Cuadernos de Desarrollo Rural
25. Grassland Science
26. Icelandic Agricultural Sciences
27. Indian Journal of Agricultural Sciences
28. Information Processing in Agriculture
29. International Journal of Agricultural Sustainability
30. International Journal of Agriculture and Natural Resources
31. Irish Journal of Agricultural and Food Research
32. JARQ-Japan Agricultural Research Quarterly
33. Journal of Agricultural & Environmental Ethics
34. Journal of Agricultural and Food Chemistry
35. Journal of Agricultural Meteorology
36. Journal of Agricultural Science
37. Journal of Agricultural Science and Technology
38. Journal of Agricultural Sciences-Tarim Bilimleri Dergisi
39. Journal of Animal and Plant Sciences-Japs
40. Journal of Integrative Agriculture
41. Journal of Land Use Science
42. Journal of Plant Diseases and Protection
43. Journal of the Faculty of Agriculture Kyushu University
44. Journal of the Science of Food and Agriculture
45. Landbauforschung-Journal of Sustainable and Organic Agricultural Systems
46. New Medit
47. New Zealand Journal of Agricultural Research
48. NJAS-Impact in Agricultural and Life Sciences
49. Outlook on Agriculture
50. Pakistan Journal of Agricultural Sciences
51. Pesquisa Agropecuaria Brasileira
52. Philippine Agricultural Scientist
53. Precision Agriculture
54. Renewable Agriculture and Food Systems
55. Revista Ciencia Agronomica
56. Revista de la Facultad de Ciencias Agrarias
57. Scientia Agricola
58. Semina-Ciencias Agrarias
59. Spanish Journal of Agricultural Research

<a id="scie-agronomy"></a>

### Agronomy

期刊数：87

1. Acta Agriculturae Scandinavica Section B-Soil and Plant Science
2. Acta Scientiarum-Agronomy
3. Advances in Weed Science
4. Agricultural and Forest Meteorology
5. Agricultural Water Management
6. Agriculture-Basel
7. Agroforestry Systems
8. Agronomy for Sustainable Development
9. Agronomy Journal
10. Agronomy-Basel
11. American Journal of Potato Research
12. Archives of Agronomy and Soil Science
13. Bioagro
14. Biological Agriculture & Horticulture
15. Bioscience Journal
16. Biotechnologie Agronomie Societe et Environnement
17. Breeding Science
18. Cahiers Agricultures
19. Canadian Journal of Plant Science
20. Cereal Research Communications
21. Chilean Journal of Agricultural Research
22. Ciencia Rural
23. Communications in Soil Science and Plant Analysis
24. Crop Breeding and Applied Biotechnology
25. Crop Journal
26. Crop Protection
27. Crop Science
28. Czech Journal of Genetics and Plant Breeding
29. Emirates Journal of Food and Agriculture
30. Euphytica
31. European Journal of Agronomy
32. European Journal of Plant Pathology
33. Experimental Agriculture
34. Field Crops Research
35. Genetic Resources and Crop Evolution
36. Grass and Forage Science
37. Grassland Science
38. Industrial Crops and Products
39. International Agrophysics
40. International Journal of Plant Production
41. Irrigation and Drainage
42. Irrigation Science
43. Italian Journal of Agrometeorology-Rivista Italiana di Agrometeorologia
44. Italian Journal of Agronomy
45. Itea-Informacion Tecnica Economica Agraria
46. Journal of Agronomy and Crop Science
47. Journal of Crop Health
48. Journal of Plant Nutrition and Soil Science
49. Journal of Plant Registrations
50. Journal of Seed Science
51. Journal of the American Pomological Society
52. Legume Research
53. Maydica
54. Molecular Breeding
55. Mycobiology
56. New Zealand Journal of Crop and Horticultural Science
57. Paddy and Water Environment
58. Pest Management Science
59. Philippine Journal of Crop Science
60. Phytoparasitica
61. Phytopathologia Mediterranea
62. Plant and Soil
63. Plant Breeding
64. Plant Pathology
65. Plant Phenomics
66. Plant Production Science
67. Plant Protection Science
68. Plant Soil and Environment
69. Postharvest Biology and Technology
70. Potato Research
71. Range Management and Agroforestry
72. Revista Caatinga
73. Revista de la Facultad de Agronomia de la Universidad del Zulia
74. Revista Fitotecnia Mexicana
75. Rice
76. Rice Science
77. Romanian Agricultural Research
78. Seed Science and Technology
79. Sugar Tech
80. Theoretical and Applied Genetics
81. Tropical Grasslands-Forrajes Tropicales
82. Turkish Journal of Agriculture and Forestry
83. Turkish Journal of Field Crops
84. Weed Biology and Management
85. Weed Research
86. Weed Science
87. Weed Technology

<a id="scie-allergy"></a>

### Allergy

期刊数：27

1. Allergologie
2. Allergology International
3. Allergy
4. Allergy and Asthma Proceedings
5. Allergy Asthma & Immunology Research
6. Allergy Asthma and Clinical Immunology
7. Annals of Allergy Asthma & Immunology
8. Asian Pacific Journal of Allergy and Immunology
9. Clinical and Experimental Allergy
10. Clinical and Translational Allergy
11. Clinical Reviews in Allergy & Immunology
12. Contact Dermatitis
13. Current Allergy and Asthma Reports
14. Current Opinion in Allergy and Clinical Immunology
15. Immunology and Allergy Clinics of North America
16. International Archives of Allergy and Immunology
17. Iranian Journal of Allergy Asthma and Immunology
18. Journal of Allergy and Clinical Immunology
19. Journal of Allergy and Clinical Immunology-in Practice
20. Journal of Asthma
21. Journal of Asthma and Allergy
22. Journal of Investigational Allergology and Clinical Immunology
23. Pediatric Allergy and Immunology
24. Pediatric Allergy Immunology and Pulmonology
25. Postepy Dermatologii i Alergologii
26. Revue Francaise d Allergologie
27. World Allergy Organization Journal

<a id="scie-anatomy-morphology"></a>

### Anatomy & Morphology

期刊数：20

1. Acta Zoologica
2. Anatomia Histologia Embryologia
3. Anatomical Record-Advances in Integrative Anatomy and Evolutionary Biology
4. Anatomical Science International
5. Annals of Anatomy-Anatomischer Anzeiger
6. Applied Immunohistochemistry & Molecular Morphology
7. Brain Structure & Function
8. Cells Tissues Organs
9. Clinical Anatomy
10. Developmental Dynamics
11. Folia Morphologica
12. Frontiers in Neuroanatomy
13. International Journal of Morphology
14. Journal of Anatomy
15. Journal of Morphology
16. Journal of the Anatomical Society of India
17. Microscopy Research and Technique
18. Surgical and Radiologic Anatomy
19. Tissue & Cell
20. Zoomorphology

<a id="scie-andrology"></a>

### Andrology

期刊数：8

1. Andrologia
2. Andrology
3. Asian Journal of Andrology
4. Basic and Clinical Andrology
5. Revista Internacional de Andrologia
6. Systems Biology in Reproductive Medicine
7. Translational Andrology and Urology
8. World Journal of Mens Health

<a id="scie-anesthesiology"></a>

### Anesthesiology

期刊数：34

1. Acta Anaesthesiologica Scandinavica
2. Anaesthesia
3. Anaesthesia and Intensive Care
4. Anaesthesia Critical Care & Pain Medicine
5. Anaesthesiologie
6. Anasthesiologie & Intensivmedizin
7. Anasthesiologie Intensivmedizin Notfallmedizin Schmerztherapie
8. Anesthesia and Analgesia
9. Anesthesiology
10. Best Practice & Research-Clinical Anaesthesiology
11. BMC Anesthesiology
12. Brazilian Journal of Anesthesiology
13. British Journal of Anaesthesia
14. Canadian Journal of Anesthesia-Journal Canadien d Anesthesie
15. Clinical Journal of Pain
16. Current Opinion in Anesthesiology
17. European Journal of Anaesthesiology
18. European Journal of Pain
19. International Journal of Obstetric Anesthesia
20. Journal of Anesthesia
21. Journal of Cardiothoracic and Vascular Anesthesia
22. Journal of Clinical Anesthesia
23. Journal of Clinical Monitoring and Computing
24. Journal of Neurosurgical Anesthesiology
25. Korean Journal of Anesthesiology
26. Minerva Anestesiologica
27. Pain
28. Pain Medicine
29. Pain Physician
30. Pain Practice
31. Pediatric Anesthesia
32. Perioperative Medicine
33. Regional Anesthesia and Pain Medicine
34. Schmerz

<a id="scie-astronomy-astrophysics"></a>

### Astronomy & Astrophysics

期刊数：70

1. Acta Astronomica
2. Advances in Astronomy
3. Advances in Space Research
4. Annales Geophysicae
5. Annual Review of Astronomy and Astrophysics
6. Annual Review of Earth and Planetary Sciences
7. Astrobiology
8. Astronomical Journal
9. Astronomische Nachrichten
10. Astronomy & Astrophysics
11. Astronomy & Geophysics
12. Astronomy and Astrophysics Review
13. Astronomy and Computing
14. Astronomy Letters-a Journal of Astronomy and Space Astrophysics
15. Astronomy Reports
16. Astroparticle Physics
17. Astrophysical Bulletin
18. Astrophysical Journal
19. Astrophysical Journal Letters
20. Astrophysical Journal Supplement Series
21. Astrophysics
22. Astrophysics and Space Science
23. Celestial Mechanics & Dynamical Astronomy
24. Classical and Quantum Gravity
25. Comptes Rendus Physique
26. Contributions of the Astronomical Observatory Skalnate Pleso
27. Cosmic Research
28. Discover Space
29. Earth and Space Science
30. Experimental Astronomy
31. Frontiers in Astronomy and Space Sciences
32. General Relativity and Gravitation
33. Geophysical and Astrophysical Fluid Dynamics
34. Gravitation & Cosmology
35. Icarus
36. International Journal of Astrobiology
37. International Journal of Modern Physics D
38. Journal of Astrophysics and Astronomy
39. Journal of Cosmology and Astroparticle Physics
40. Journal of Geophysical Research-Space Physics
41. Journal of High Energy Astrophysics
42. Journal of Space Weather and Space Climate
43. Journal of the Korean Astronomical Society
44. Kinematics and Physics of Celestial Bodies
45. Life Sciences in Space Research
46. Living Reviews in Solar Physics
47. Modern Physics Letters A
48. Monthly Notices of the Royal Astronomical Society
49. Nature Astronomy
50. New Astronomy
51. New Astronomy Reviews
52. Observatory
53. Open Astronomy
54. Physical Review D
55. Physics Letters B
56. Physics of the Dark Universe
57. Planetary and Space Science
58. Publications of the Astronomical Society of Australia
59. Publications of the Astronomical Society of Japan
60. Publications of the Astronomical Society of the Pacific
61. Radio Science
62. Research in Astronomy and Astrophysics
63. Revista Mexicana de Astronomia y Astrofisica
64. Serbian Astronomical Journal
65. Solar Physics
66. Solar System Research
67. Space Science Reviews
68. Space Weather-the International Journal of Research and Applications
69. Space-Science & Technology
70. Universe

<a id="scie-audiology-speech-language-pathology"></a>

### Audiology & Speech-Language Pathology

期刊数：27

1. American Journal of Audiology
2. American Journal of Speech-Language Pathology
3. Aphasiology
4. Audiology and Neurotology
5. Augmentative and Alternative Communication
6. Brain and Language
7. Clinical Linguistics & Phonetics
8. Ear and Hearing
9. Folia Phoniatrica et Logopaedica
10. Hearing Research
11. International Journal of Audiology
12. International Journal of Language & Communication Disorders
13. International Journal of Speech-Language Pathology
14. Journal of Communication Disorders
15. Journal of Fluency Disorders
16. Journal of Speech Language and Hearing Research
17. Journal of the Acoustical Society of America
18. Journal of the American Academy of Audiology
19. Journal of Voice
20. Language and Speech
21. Language Cognition and Neuroscience
22. Language Speech and Hearing Services in Schools
23. Logopedics Phoniatrics Vocology
24. Noise & Health
25. Phonetica
26. Seminars in Speech and Language
27. Trends in Hearing

<a id="scie-automation-control-systems"></a>

### Automation & Control Systems

期刊数：64

1. Advanced Intelligent Systems
2. Annual Review of Control Robotics and Autonomous Systems
3. Annual Reviews in Control
4. Archives of Control Sciences
5. Asian Journal of Control
6. At-Automatisierungstechnik
7. Automatica
8. Automatika
9. Automation and Remote Control
10. Autonomous Agents and Multi-Agent Systems
11. Chemometrics and Intelligent Laboratory Systems
12. Control Engineering and Applied Informatics
13. Control Engineering Practice
14. Discrete Event Dynamic Systems-Theory and Applications
15. Engineering Applications of Artificial Intelligence
16. ESAIM-Control Optimisation and Calculus of Variations
17. European Journal of Control
18. IEEE Control Systems Magazine
19. IEEE Robotics & Automation Magazine
20. IEEE Transactions on Automatic Control
21. IEEE Transactions on Automation Science and Engineering
22. IEEE Transactions on Control of Network Systems
23. IEEE Transactions on Control Systems Technology
24. IEEE Transactions on Cybernetics
25. IEEE Transactions on Industrial Electronics
26. IEEE Transactions on Industrial Informatics
27. IEEE Transactions on Systems Man Cybernetics-Systems
28. IEEE-ASME Transactions on Mechatronics
29. IEEE-CAA Journal of Automatica Sinica
30. IET Control Theory and Applications
31. IMA Journal of Mathematical Control and Information
32. Information Technology and Control
33. International Journal of Adaptive Control and Signal Processing
34. International Journal of Advanced Manufacturing Technology
35. International Journal of Applied Mathematics and Computer Science
36. International Journal of Computers Communications & Control
37. International Journal of Control
38. International Journal of Control Automation and Systems
39. International Journal of Fuzzy Systems
40. International Journal of Robotics & Automation
41. International Journal of Robust and Nonlinear Control
42. International Journal of Systems Science
43. ISA Transactions
44. Journal of Chemometrics
45. Journal of Dynamic Systems Measurement and Control-Transactions of the ASME
46. Journal of Dynamical and Control Systems
47. Journal of Machine Learning Research
48. Journal of Process Control
49. Journal of Systems Engineering and Electronics
50. Journal of the Franklin Institute
51. Mathematics of Control Signals and Systems
52. Measurement & Control
53. Mechatronics
54. Modeling Identification and Control
55. Nonlinear Analysis-Hybrid Systems
56. Optimal Control Applications & Methods
57. Proceedings of the Institution of Mechanical Engineers Part I-Journal of Systems and Control Engineering
58. Revista Iberoamericana de Automatica e Informatica Industrial
59. Robotic Intelligence and Automation
60. Robotics and Autonomous Systems
61. SIAM Journal on Control and Optimization
62. Studies in Informatics and Control
63. Systems & Control Letters
64. Transactions of the Institute of Measurement and Control

<a id="scie-behavioral-sciences"></a>

### Behavioral Sciences

期刊数：52

1. Acta Ethologica
2. Aggressive Behavior
3. Animal Behaviour
4. Animal Cognition
5. Appetite
6. Applied Animal Behaviour Science
7. Autism Research
8. Behavior Genetics
9. Behavioral and Brain Functions
10. Behavioral and Brain Sciences
11. Behavioral Ecology
12. Behavioral Ecology and Sociobiology
13. Behavioral Medicine
14. Behavioral Neuroscience
15. Behaviour
16. Behavioural Brain Research
17. Behavioural Pharmacology
18. Behavioural Processes
19. Biological Psychology
20. Brain and Behavior
21. Brain Behavior and Evolution
22. Chemical Senses
23. Cognitive Affective & Behavioral Neuroscience
24. Cognitive and Behavioral Neurology
25. Cortex
26. Current Opinion in Behavioral Sciences
27. Epilepsy & Behavior
28. Ethology
29. Ethology Ecology & Evolution
30. Evolution and Human Behavior
31. Frontiers in Behavioral Neuroscience
32. Frontiers in Integrative Neuroscience
33. Genes Brain and Behavior
34. Hormones and Behavior
35. Human Factors
36. Journal of Comparative Physiology A-Neuroethology Sensory Neural and Behavioral Physiology
37. Journal of Comparative Psychology
38. Journal of Developmental and Behavioral Pediatrics
39. Journal of Ect
40. Journal of Ethology
41. Journal of Experimental Psychology-Animal Learning and Cognition
42. Journal of the Experimental Analysis of Behavior
43. Journal of Veterinary Behavior-Clinical Applications and Research
44. Language Cognition and Neuroscience
45. Learning & Behavior
46. Neurobiology of Learning and Memory
47. Neuropsychologia
48. Neuroscience and Biobehavioral Reviews
49. Pharmacology Biochemistry and Behavior
50. Physiology & Behavior
51. Stress-the International Journal on the Biology of Stress
52. Trends in Cognitive Sciences

<a id="scie-biochemical-research-methods"></a>

### Biochemical Research Methods

期刊数：76

1. ACS Synthetic Biology
2. Acta Crystallographica Section D-Structural Biology
3. Acta Crystallographica Section F-Structural Biology Communications
4. Algorithms for Molecular Biology
5. Analytical and Bioanalytical Chemistry
6. Analytical Biochemistry
7. Assay and Drug Development Technologies
8. Bioanalysis
9. BioChip Journal
10. Bioconjugate Chemistry
11. Bioinformatics
12. Biological Procedures Online
13. Biologicals
14. Biomedical Chromatography
15. Biomedical Optics Express
16. Biomicrofluidics
17. BioTechniques
18. Biotechnology Journal
19. BMC Bioinformatics
20. Briefings in Bioinformatics
21. Chromatographia
22. Clinical Proteomics
23. Combinatorial Chemistry & High Throughput Screening
24. Current Bioinformatics
25. Current Opinion in Biotechnology
26. Current Proteomics
27. Cytometry Part A
28. Drug Testing and Analysis
29. Electrophoresis
30. Expert Review of Proteomics
31. IEEE Transactions on Computational Biology and Bioinformatics
32. IEEE Transactions on NanoBioscience
33. IET Nanobiotechnology
34. Journal of Biological Engineering
35. Journal of Biomedical Optics
36. Journal of Biophotonics
37. Journal of Breath Research
38. Journal of Chromatographic Science
39. Journal of Chromatography A
40. Journal of Chromatography B-Analytical Technologies in the Biomedical and Life Sciences
41. Journal of Computational Biology
42. Journal of Fluorescence
43. Journal of Immunological Methods
44. Journal of Labelled Compounds & Radiopharmaceuticals
45. Journal of Liquid Chromatography & Related Technologies
46. Journal of Magnetic Resonance
47. Journal of Mass Spectrometry
48. Journal of Microbiological Methods
49. Journal of Molecular Graphics & Modelling
50. Journal of Neuroscience Methods
51. Journal of Proteome Research
52. Journal of Proteomics
53. Journal of Spectroscopy
54. Journal of the American Society for Mass Spectrometry
55. Journal of Virological Methods
56. Lab on a Chip
57. Methods
58. Molecular & Cellular Proteomics
59. Molecular and Cellular Probes
60. Molecular Imaging
61. Nature Methods
62. Nature Protocols
63. New Biotechnology
64. Phytochemical Analysis
65. Plant Methods
66. Plant Molecular Biology Reporter
67. PLOS Computational Biology
68. Preparative Biochemistry & Biotechnology
69. Protein Expression and Purification
70. Proteomics
71. Proteomics Clinical Applications
72. Rapid Communications in Mass Spectrometry
73. Slas Discovery
74. Slas Technology
75. Synthetic Biology
76. Transgenic Research

<a id="scie-biochemistry-molecular-biology"></a>

### Biochemistry & Molecular Biology

期刊数：281

1. ACS Chemical Biology
2. ACS Chemical Neuroscience
3. Acta Biochimica et Biophysica Sinica
4. Acta Biochimica Polonica
5. Acta Crystallographica Section D-Structural Biology
6. Acta Crystallographica Section F-Structural Biology Communications
7. Addiction Biology
8. American Journal of Respiratory Cell and Molecular Biology
9. Amino Acids
10. Amyloid-Journal of Protein Folding Disorders
11. Analytical Biochemistry
12. Annual Review of Biochemistry
13. Antioxidants
14. Antioxidants & Redox Signaling
15. Apoptosis
16. Applied Biochemistry and Biotechnology
17. Archives of Biochemistry and Biophysics
18. Archives of Insect Biochemistry and Physiology
19. Biocatalysis and Biotransformation
20. Biochemical and Biophysical Research Communications
21. Biochemical Genetics
22. Biochemical Journal
23. Biochemical Society Transactions
24. Biochemical Systematics and Ecology
25. Biochemistry
26. Biochemistry and Cell Biology
27. Biochemistry and Molecular Biology Education
28. Biochemistry-Moscow
29. Biochimica et Biophysica Acta-Bioenergetics
30. Biochimica et Biophysica Acta-Biomembranes
31. Biochimica et Biophysica Acta-Gene Regulatory Mechanisms
32. Biochimica et Biophysica Acta-General Subjects
33. Biochimica et Biophysica Acta-Molecular and Cell Biology of Lipids
34. Biochimica et Biophysica Acta-Molecular Basis of Disease
35. Biochimica et Biophysica Acta-Molecular Cell Research
36. Biochimica et Biophysica Acta-Proteins and Proteomics
37. Biochimica et Biophysica Acta-Reviews on Cancer
38. Biochimie
39. Bioconjugate Chemistry
40. Bioelectrochemistry
41. BioEssays
42. BioFactors
43. Bioinorganic Chemistry and Applications
44. Biological Chemistry
45. Biological Trace Element Research
46. Biomacromolecules
47. Biomedical Chromatography
48. Biomedical Journal
49. Biomedicines
50. BioMetals
51. Biomolecules
52. Bioorganic & Medicinal Chemistry
53. Bioorganic Chemistry
54. Biophysical Chemistry
55. Biopolymers
56. Bioscience Biotechnology and Biochemistry
57. Bioscience Reports
58. BioTechniques
59. Biotechnology and Applied Biochemistry
60. BMB Reports
61. Brain Mechanisms
62. Carbohydrate Research
63. Cell
64. Cell and Bioscience
65. Cell Biochemistry and Biophysics
66. Cell Biochemistry and Function
67. Cell Chemical Biology
68. Cell Death and Differentiation
69. Cell Systems
70. Cellular & Molecular Biology Letters
71. Cellular and Molecular Life Sciences
72. Channels
73. ChemBioChem
74. Chemical Biology & Drug Design
75. Chemico-Biological Interactions
76. Chemistry & Biodiversity
77. Chemistry and Physics of Lipids
78. Chromosome Research-Biology of the Nucleus
79. Comparative Biochemistry and Physiology A-Molecular & Integrative Physiology
80. Comparative Biochemistry and Physiology B-Biochemistry & Molecular Biology
81. Comparative Biochemistry and Physiology C-Toxicology & Pharmacology
82. Comparative Biochemistry and Physiology D-Genomics & Proteomics
83. Computational and Structural Biotechnology Journal
84. Critical Reviews in Biochemistry and Molecular Biology
85. Current Biology
86. Current Drug Metabolism
87. Current Genomics
88. Current Issues in Molecular Biology
89. Current Medicinal Chemistry
90. Current Molecular Pharmacology
91. Current Opinion in Chemical Biology
92. Current Opinion in Lipidology
93. Current Opinion in Structural Biology
94. Current Pharmaceutical Biotechnology
95. Current Protein & Peptide Science
96. Current Proteomics
97. Cytokine
98. Cytokine & Growth Factor Reviews
99. DNA and Cell Biology
100. Doklady Biochemistry and Biophysics
101. EMBO Journal
102. EMBO Reports
103. Environmental Pollutants and Bioavailability
104. Epigenetics
105. Essays in Biochemistry
106. European Cytokine Network
107. European Journal of Human Genetics
108. Experimental and Molecular Medicine
109. Expert Opinion on Drug Metabolism & Toxicology
110. Expert Reviews in Molecular Medicine
111. Extremophiles
112. FASEB Journal
113. FEBS Journal
114. FEBS Letters
115. FEBS Open Bio
116. Fish Physiology and Biochemistry
117. Fly
118. Folia Histochemica et Cytobiologica
119. Food & Function
120. Free Radical Biology and Medicine
121. Free Radical Research
122. Frontiers in Bioscience-Landmark
123. Frontiers in Molecular Biosciences
124. Gene Therapy
125. General Physiology and Biophysics
126. Genes & Diseases
127. Genes & Genetic Systems
128. Genes & Genomics
129. Genetics and Molecular Biology
130. Genome Research
131. Glycobiology
132. Glycoconjugate Journal
133. Hemoglobin
134. Human Molecular Genetics
135. Indian Journal of Biochemistry & Biophysics
136. Innate Immunity
137. Insect Biochemistry and Molecular Biology
138. Insect Molecular Biology
139. International Journal of Biochemistry & Cell Biology
140. International Journal of Biological Macromolecules
141. International Journal of Biological Sciences
142. International Journal of Genomics
143. International Journal of Molecular Sciences
144. International Journal of Peptide Research and Therapeutics
145. IUBMB Life
146. Journal of Biochemical and Molecular Toxicology
147. Journal of Biochemistry
148. Journal of Biological Chemistry
149. Journal of Biological Inorganic Chemistry
150. Journal of Biomolecular NMR
151. Journal of Biomolecular Structure & Dynamics
152. Journal of Carbohydrate Chemistry
153. Journal of Cellular Biochemistry
154. Journal of Chemical Ecology
155. Journal of Computer-Aided Molecular Design
156. Journal of Enzyme Inhibition and Medicinal Chemistry
157. Journal of Evolutionary Biochemistry and Physiology
158. Journal of Food Biochemistry
159. Journal of Genetics and Genomics
160. Journal of Inorganic Biochemistry
161. Journal of Integrative Plant Biology
162. Journal of Interferon and Cytokine Research
163. Journal of Lipid Research
164. Journal of Liposome Research
165. Journal of Medical Biochemistry
166. Journal of Membrane Biology
167. Journal of Molecular Biology
168. Journal of Molecular Evolution
169. Journal of Molecular Graphics & Modelling
170. Journal of Molecular Modeling
171. Journal of Molecular Neuroscience
172. Journal of Molecular Recognition
173. Journal of Neurochemistry
174. Journal of Nutritional Biochemistry
175. Journal of Peptide Science
176. Journal of Photochemistry and Photobiology B-Biology
177. Journal of Physiology and Biochemistry
178. Journal of Plant Biochemistry and Biotechnology
179. Journal of Receptors and Signal Transduction
180. Journal of Steroid Biochemistry and Molecular Biology
181. Journal of Structural Biology
182. Journal of Trace Elements in Medicine and Biology
183. Journal of Zhejiang University-Science B
184. Lipids
185. Lipids in Health and Disease
186. Macromolecular Bioscience
187. Magnesium Research
188. Mammalian Genome
189. Matrix Biology
190. Metabolites
191. Metallomics
192. Methods
193. Molecular and Biochemical Parasitology
194. Molecular and Cellular Biology
195. Molecular and Cellular Probes
196. Molecular Aspects of Medicine
197. Molecular Biology
198. Molecular Biology and Evolution
199. Molecular Biology Reports
200. Molecular Biotechnology
201. Molecular Cancer
202. Molecular Carcinogenesis
203. Molecular Cell
204. Molecular Ecology
205. Molecular Ecology Resources
206. Molecular Genetics and Genomics
207. Molecular Genetics Microbiology and Virology
208. Molecular Immunology
209. Molecular Medicine
210. Molecular Microbiology
211. Molecular Omics
212. Molecular Phylogenetics and Evolution
213. Molecular Plant
214. Molecular Plant-Microbe Interactions
215. Molecular Psychiatry
216. Molecular Reproduction and Development
217. Molecular Systems Biology
218. Molecular Vision
219. Molecules
220. Molecules and Cells
221. Natural Product Reports
222. Nature Chemical Biology
223. Nature Medicine
224. Nature Structural & Molecular Biology
225. Neurochemical Research
226. Neurochemistry International
227. Nitric Oxide-Biology and Chemistry
228. Nucleic Acid Therapeutics
229. Nucleic Acids Research
230. Nucleosides Nucleotides & Nucleic Acids
231. Oncogene
232. Open Biology
233. Organogenesis
234. Peptide Science
235. Peptides
236. Pesticide Biochemistry and Physiology
237. Photochemical & Photobiological Sciences
238. Photochemistry and Photobiology
239. Physical Biology
240. Phytochemistry
241. Plant Cell
242. Plant Communications
243. Plant Molecular Biology
244. Plant Science
245. Plant Signaling & Behavior
246. PLOS Biology
247. Preparative Biochemistry & Biotechnology
248. Prion
249. Process Biochemistry
250. Progress in Biochemistry and Biophysics
251. Progress in Biophysics & Molecular Biology
252. Progress in Lipid Research
253. Prostaglandins & Other Lipid Mediators
254. Prostaglandins Leukotrienes and Essential Fatty Acids
255. Protein and Peptide Letters
256. Protein Engineering Design & Selection
257. Protein Expression and Purification
258. Protein Journal
259. Protein Science
260. Proteins-Structure Function and Bioinformatics
261. Proteomics
262. Redox Biology
263. Redox Report
264. RNA
265. RNA Biology
266. RSC Medicinal Chemistry
267. Russian Journal of Bioorganic Chemistry
268. Science Signaling
269. Signal Transduction and Targeted Therapy
270. Statistical Applications in Genetics and Molecular Biology
271. Steroids
272. Structure
273. Trace Elements and Electrolytes
274. Transgenic Research
275. Trends in Biochemical Sciences
276. Trends in Glycoscience and Glycotechnology
277. Trends in Microbiology
278. Trends in Molecular Medicine
279. Turkish Journal of Biochemistry-Turk Biyokimya Dergisi
280. Yeast
281. Zeitschrift für Naturforschung Section C-a Journal of Biosciences

<a id="scie-biodiversity-conservation"></a>

### Biodiversity Conservation

期刊数：64

1. American Museum Novitates
2. Animal Biodiversity and Conservation
3. Animal Biotelemetry
4. Animal Conservation
5. Avian Conservation and Ecology
6. Biodiversity and Conservation
7. Biodiversity Data Journal
8. BioInvasions Records
9. Biological Conservation
10. Biological Invasions
11. Biota Neotropica
12. Bird Conservation International
13. Bulletin of the American Museum of Natural History
14. Bulletin of the Peabody Museum of Natural History
15. Caribbean Journal of Science
16. Conservation Biology
17. Conservation Genetics
18. Conservation Genetics Resources
19. Conservation Letters
20. Conservation Physiology
21. Conservation Science and Practice
22. Diversity and Distributions
23. Diversity-Basel
24. Eco Mont-Journal on Protected Mountain Areas Research
25. Ecography
26. Endangered Species Research
27. Environmental Conservation
28. Food Webs
29. Global Change Biology
30. Global Ecology and Conservation
31. Human Dimensions of Wildlife
32. Human-Wildlife Interactions
33. Journal for Nature Conservation
34. Journal of Applied Ecology
35. Journal of Ethnobiology and Ethnomedicine
36. Journal of Fish and Wildlife Management
37. Journal of Natural History
38. Koedoe
39. Landscape and Ecological Engineering
40. Management of Biological Invasions
41. Marine Biodiversity
42. Natural History
43. Nature Conservation-Bulgaria
44. NeoBiota
45. Northeastern Naturalist
46. Oryx
47. Pachyderm
48. Palaeobiodiversity and Palaeoenvironments
49. Paleobiology
50. People and Nature
51. Perspectives in Ecology and Conservation
52. Plants People Planet
53. Polar Biology
54. Proceedings of the Academy of Natural Sciences of Philadelphia
55. Proceedings of the Linnean Society of New South Wales
56. Revista Chilena de Historia Natural
57. Revista Mexicana de Biodiversidad
58. Southeastern Naturalist
59. Southwestern Naturalist
60. Systematics and Biodiversity
61. Tropical Conservation Science
62. Urban Ecosystems
63. Western North American Naturalist
64. Wildlife Society Bulletin

<a id="scie-biology"></a>

### Biology

期刊数：88

1. Aerobiologia
2. American Biology Teacher
3. American Journal of Human Biology
4. Annals of Human Biology
5. Archives of Biological Sciences
6. Astrobiology
7. Biocell
8. Bioelectrochemistry
9. Bioelectromagnetics
10. BioEssays
11. Biologia
12. Biologia Futura
13. Biological Bulletin
14. Biological Research
15. Biological Reviews
16. Biological Rhythm Research
17. Biology Bulletin
18. Biology Direct
19. Biology Letters
20. Biology Open
21. Biology-Basel
22. Biometrics
23. Biometrika
24. BioScience
25. Bioscience Journal
26. BioScience Trends
27. Biosystems
28. BMC Biology
29. Brazilian Archives of Biology and Technology
30. Brazilian Journal of Medical and Biological Research
31. Bulletin de la Societe Linneenne de Lyon
32. Bulletin of Mathematical Biology
33. Chronobiology International
34. Communications Biology
35. Comptes Rendus Biologies
36. Computational Biology and Chemistry
37. Cryobiology
38. Cryoletters
39. Current Biology
40. Current Opinion in Insect Science
41. Discover Life
42. Electromagnetic Biology and Medicine
43. Excli Journal
44. FASEB Journal
45. Folia Biologica
46. Folia Biologica-Krakow
47. Geobiology
48. Human Biology
49. Indian Journal of Experimental Biology
50. Integrative Organismal Biology
51. Interface Focus
52. International Journal of Astrobiology
53. International Journal of Radiation Biology
54. Journal of Agricultural Biological and Environmental Statistics
55. Journal of Biological Education
56. Journal of Biological Research-Thessaloniki
57. Journal of Biological Rhythms
58. Journal of Biological Systems
59. Journal of Biosciences
60. Journal of Ethnobiology
61. Journal of Mathematical Biology
62. Journal of Radiation Research
63. Journal of the History of Biology
64. Journal of Theoretical Biology
65. Journal of Thermal Biology
66. Life Science Alliance
67. Life Sciences in Space Research
68. Life-Basel
69. Mathematical Biosciences
70. Mathematical Medicine and Biology-A Journal of the IMA
71. Microscopy Research and Technique
72. Open Life Sciences
73. Periodicum Biologorum
74. Philosophical Transactions of the Royal Society B-Biological Sciences
75. Physics of Life Reviews
76. PLOS Biology
77. Proceedings of the Royal Society B-Biological Sciences
78. Quarterly Review of Biology
79. Radiation and Environmental Biophysics
80. Radiation Research
81. Revista de Biologia Tropical
82. Science China-Life Sciences
83. Synthetic Biology
84. Theoretical Biology Forum
85. Theory in Biosciences
86. Turkish Journal of Biology
87. Yale Journal of Biology and Medicine
88. Zhurnal Obshchei Biologii

<a id="scie-biophysics"></a>

### Biophysics

期刊数：70

1. Acta Biochimica et Biophysica Sinica
2. Acta Crystallographica Section D-Structural Biology
3. Acta Crystallographica Section F-Structural Biology Communications
4. Acta of Bioengineering and Biomechanics
5. Aerospace Medicine and Human Performance
6. Annual Review of Biophysics
7. Archives of Biochemistry and Biophysics
8. Biochemical and Biophysical Research Communications
9. Biochimica et Biophysica Acta-Bioenergetics
10. Biochimica et Biophysica Acta-Biomembranes
11. Biochimica et Biophysica Acta-Gene Regulatory Mechanisms
12. Biochimica et Biophysica Acta-General Subjects
13. Biochimica et Biophysica Acta-Molecular and Cell Biology of Lipids
14. Biochimica et Biophysica Acta-Molecular Basis of Disease
15. Biochimica et Biophysica Acta-Proteins and Proteomics
16. Biochimica et Biophysica Acta-Reviews on Cancer
17. Bioelectrochemistry
18. Bioelectromagnetics
19. Biointerphases
20. Biomechanics and Modeling in Mechanobiology
21. Biomicrofluidics
22. Biomolecular NMR Assignments
23. Biophysical Chemistry
24. Biophysical Journal
25. Biopolymers
26. Biorheology
27. Biosensors & Bioelectronics
28. Cell Biochemistry and Biophysics
29. Cellular and Molecular Bioengineering
30. Chemistry and Physics of Lipids
31. Colloids and Surfaces B-Biointerfaces
32. Current Opinion in Chemical Biology
33. Doklady Biochemistry and Biophysics
34. Electromagnetic Biology and Medicine
35. European Biophysics Journal
36. FEBS Letters
37. General Physiology and Biophysics
38. High Altitude Medicine & Biology
39. Indian Journal of Biochemistry & Biophysics
40. International Journal of Biometeorology
41. Journal of Applied Biomaterials & Functional Materials
42. Journal of Bioenergetics and Biomembranes
43. Journal of Biological Physics
44. Journal of Biomechanical Engineering-Transactions of the ASME
45. Journal of Biomechanics
46. Journal of Biomolecular Structure & Dynamics
47. Journal of Biophotonics
48. Journal of Computer-Aided Molecular Design
49. Journal of Mechanics in Medicine and Biology
50. Journal of Molecular Modeling
51. Journal of Molecular Recognition
52. Journal of Photochemistry and Photobiology B-Biology
53. Journal of Physical Chemistry B
54. Journal of Structural Biology
55. Multisensory Research
56. Nature Structural & Molecular Biology
57. NMR in Biomedicine
58. Peptide Science
59. Photochemical & Photobiological Sciences
60. Photochemistry and Photobiology
61. Physical Biology
62. Physics of Life Reviews
63. Physiological Measurement
64. Progress in Biochemistry and Biophysics
65. Progress in Biophysics & Molecular Biology
66. Proteins-Structure Function and Bioinformatics
67. Quarterly Reviews of Biophysics
68. Radiation and Environmental Biophysics
69. Radiation Research
70. Structure

<a id="scie-biotechnology-applied-microbiology"></a>

### Biotechnology & Applied Microbiology

期刊数：157

1. 3 Biotech
2. Algal Research-Biomass Biofuels and Bioproducts
3. Algorithms for Molecular Biology
4. AMB Express
5. American Journal of Enology and Viticulture
6. Animal Biotechnology
7. Annals of Microbiology
8. Annual Review of Animal Biosciences
9. Applied and Environmental Microbiology
10. Applied Biochemistry and Biotechnology
11. Applied Biochemistry and Microbiology
12. Applied Microbiology and Biotechnology
13. Artificial Cells Nanomedicine and Biotechnology
14. Biocatalysis and Biotransformation
15. Biochemical Engineering Journal
16. Biocontrol Science and Technology
17. Biodegradation
18. Biofouling
19. Biofuels Bioproducts & Biorefining-Biofpr
20. Bioinformatics
21. Biological Control
22. Biologicals
23. Biomarkers
24. Biomass & Bioenergy
25. Biopharm International
26. Bioprocess and Biosystems Engineering
27. Bioresource Technology
28. Bioresources and Bioprocessing
29. Bioscience Biotechnology and Biochemistry
30. Biosensors & Bioelectronics
31. Biotechnic & Histochemistry
32. Biotechnology & Biotechnological Equipment
33. Biotechnology Advances
34. Biotechnology and Applied Biochemistry
35. Biotechnology and Bioengineering
36. Biotechnology and Bioprocess Engineering
37. Biotechnology and Genetic Engineering Reviews
38. Biotechnology for Biofuels and Bioproducts
39. Biotechnology Journal
40. Biotechnology Law Report
41. Biotechnology Letters
42. Biotechnology Progress
43. BMC Bioinformatics
44. BMC Biotechnology
45. BMC Genomics
46. Briefings in Functional Genomics
47. Canadian Journal of Microbiology
48. Cancer Gene Therapy
49. Cellular Reprogramming
50. Chemical and Biochemical Engineering Quarterly
51. Critical Reviews in Biotechnology
52. Critical Reviews in Eukaryotic Gene Expression
53. Crop Breeding and Applied Biotechnology
54. Current Nanoscience
55. Current Opinion in Biotechnology
56. Current Opinion in Chemical Engineering
57. Cytotechnology
58. Cytotherapy
59. Electronic Journal of Biotechnology
60. Engineering in Life Sciences
61. Environmental Technology & Innovation
62. Enzyme and Microbial Technology
63. Expert Opinion on Biological Therapy
64. FEMS Yeast Research
65. Fermentation-Basel
66. Folia Microbiologica
67. Food and Bioproducts Processing
68. Food Biotechnology
69. Food Microbiology
70. Food Technology and Biotechnology
71. Frontiers in Bioengineering and Biotechnology
72. Gene Therapy
73. Genes & Genomics
74. Genome
75. Genome Biology
76. Genome Research
77. Genomics
78. Global Change Biology Bioenergy
79. GM Crops & Food-Biotechnology in Agriculture and the Food Chain
80. Human Gene Therapy
81. Human Vaccines & Immunotherapeutics
82. Indian Journal of Microbiology
83. International Biodeterioration & Biodegradation
84. International Journal of Biological Markers
85. International Journal of Genomics
86. International Microbiology
87. Iranian Journal of Biotechnology
88. Journal of Antibiotics
89. Journal of Applied Genetics
90. Journal of Applied Microbiology
91. Journal of Applied Phycology
92. Journal of Bioactive and Compatible Polymers
93. Journal of Biological Engineering
94. Journal of Bioscience and Bioengineering
95. Journal of Biotechnology
96. Journal of Chemical Technology and Biotechnology
97. Journal of Computational Biology
98. Journal of Food Protection
99. Journal of Food Safety
100. Journal of Gene Medicine
101. Journal of General and Applied Microbiology
102. Journal of General Virology
103. Journal of Industrial Microbiology & Biotechnology
104. Journal of Microbiology and Biotechnology
105. Journal of Microorganism Control
106. Journal of Nanobiotechnology
107. Journal of the American Society of Brewing Chemists
108. Journal of Tissue Engineering and Regenerative Medicine
109. Journal of Virological Methods
110. Journal of Zhejiang University-Science B
111. Letters in Applied Microbiology
112. Mammalian Genome
113. Marine Biotechnology
114. Metabolic Engineering
115. Microbes and Environments
116. Microbial Biotechnology
117. Microbial Cell Factories
118. Microbial Physiology
119. Minerva Biotechnology and Biomolecular Research
120. Molecular and Cellular Probes
121. Molecular Biotechnology
122. Molecular Plant-Microbe Interactions
123. Molecular Therapy
124. Mutation Research-Fundamental and Molecular Mechanisms of Mutagenesis
125. Mutation Research-Genetic Toxicology and Environmental Mutagenesis
126. Mutation Research-Reviews in Mutation Research
127. Nanomedicine
128. Nature Biotechnology
129. Nature Reviews Drug Discovery
130. New Biotechnology
131. New Genetics and Society
132. Npj Biofilms and Microbiomes
133. Omics-A Journal of Integrative Biology
134. OncoTargets and Therapy
135. Pharmacogenetics and Genomics
136. Plant Biotechnology
137. Plant Biotechnology Journal
138. Plant Biotechnology Reports
139. Plant Breeding
140. Plant Cell Tissue and Organ Culture
141. Preparative Biochemistry & Biotechnology
142. Probiotics and Antimicrobial Proteins
143. Process Biochemistry
144. Protein Engineering Design & Selection
145. Protein Expression and Purification
146. Reviews in Environmental Science and Bio-Technology
147. Sensors and Actuators Reports
148. Slas Discovery
149. STEM Cell Research
150. STEM Cells
151. Synthetic and Systems Biotechnology
152. Synthetic Biology
153. Systematic and Applied Microbiology
154. Transgenic Research
155. Trends in Biotechnology
156. World Journal of Microbiology & Biotechnology
157. Yeast

<a id="scie-cardiac-cardiovascular-system"></a>

### Cardiac & Cardiovascular System

期刊数：143

1. Acta Cardiologica
2. Acta Cardiologica Sinica
3. American Heart Journal
4. American Journal of Cardiology
5. American Journal of Cardiovascular Drugs
6. American Journal of Physiology-Heart and Circulatory Physiology
7. Anatolian Journal of Cardiology
8. Annals of Cardiothoracic Surgery
9. Annals of Noninvasive Electrocardiology
10. Annals of Thoracic and Cardiovascular Surgery
11. Annals of Thoracic Medicine
12. Annals of Thoracic Surgery
13. Archives of Cardiovascular Diseases
14. Arquivos Brasileiros de Cardiologia
15. Atherosclerosis
16. Basic Research in Cardiology
17. BMC Cardiovascular Disorders
18. Brazilian Journal of Cardiovascular Surgery
19. Canadian Journal of Cardiology
20. Cardiology
21. Cardiology Clinics
22. Cardiology in Review
23. Cardiology in the Young
24. Cardiology Journal
25. Cardiology Research and Practice
26. Cardiorenal Medicine
27. CardioVascular and Interventional Radiology
28. Cardiovascular Diabetology
29. Cardiovascular Diagnosis and Therapy
30. Cardiovascular Drugs and Therapy
31. Cardiovascular Engineering and Technology
32. CardioVascular Journal of Africa
33. Cardiovascular Pathology
34. Cardiovascular Research
35. Cardiovascular Therapeutics
36. Cardiovascular Toxicology
37. Cardiovascular Ultrasound
38. Catheterization and Cardiovascular Interventions
39. Circulation
40. Circulation Journal
41. Circulation Research
42. Circulation-Arrhythmia and Electrophysiology
43. Circulation-Cardiovascular Imaging
44. Circulation-Cardiovascular Interventions
45. Circulation-Genomic and Precision Medicine
46. Circulation-Heart Failure
47. Circulation-Population Health and Outcomes
48. Clinical Cardiology
49. Clinical Research in Cardiology
50. Coronary Artery Disease
51. Current Cardiology Reports
52. Current Opinion in Cardiology
53. Current Problems in Cardiology
54. Echocardiography-a Journal of Cardiovascular Ultrasound and Allied Techniques
55. ESC Heart Failure
56. EuroIntervention
57. Europace
58. European Heart Journal
59. European Heart Journal Supplements
60. European Heart Journal-Acute Cardiovascular Care
61. European Heart Journal-Cardiovascular Imaging
62. European Heart Journal-Cardiovascular Pharmacotherapy
63. European Heart Journal-Quality of Care and Clinical Outcomes
64. European Journal of Cardio-Thoracic Surgery
65. European Journal of Cardiovascular Nursing
66. European Journal of Heart Failure
67. European Journal of Preventive Cardiology
68. Frontiers in Cardiovascular Medicine
69. General Thoracic and Cardiovascular Surgery
70. Global Heart
71. Heart
72. Heart & Lung
73. Heart and Vessels
74. Heart Failure Clinics
75. Heart Failure Reviews
76. Heart Lung and Circulation
77. Heart Rhythm
78. Heart Surgery Forum
79. Hellenic Journal of Cardiology
80. Herz
81. Interdisciplinary CardioVascular and Thoracic Surgery
82. International Heart Journal
83. International Journal of Cardiology
84. International Journal of Cardiovascular Imaging
85. JACC-Basic to Translational Science
86. JACC-Cardiovascular Imaging
87. JACC-Cardiovascular Interventions
88. JACC-Clinical Electrophysiology
89. JACC-Heart Failure
90. JACC-Journal of the American College of Cardiology
91. JACC: CardioOncology
92. JAMA Cardiology
93. Journal of Cardiac Failure
94. Journal of Cardiac Surgery
95. Journal of Cardiology
96. Journal of Cardiopulmonary Rehabilitation and Prevention
97. Journal of Cardiothoracic and Vascular Anesthesia
98. Journal of Cardiothoracic Surgery
99. Journal of Cardiovascular Computed Tomography
100. Journal of Cardiovascular Development and Disease
101. Journal of Cardiovascular Electrophysiology
102. Journal of Cardiovascular Magnetic Resonance
103. Journal of Cardiovascular Medicine
104. Journal of Cardiovascular Nursing
105. Journal of Cardiovascular Pharmacology
106. Journal of Cardiovascular Pharmacology and Therapeutics
107. Journal of Cardiovascular Surgery
108. Journal of Cardiovascular Translational Research
109. Journal of Electrocardiology
110. Journal of Geriatric Cardiology
111. Journal of Heart and Lung Transplantation
112. Journal of Interventional Cardiac Electrophysiology
113. Journal of Interventional Cardiology
114. Journal of Invasive Cardiology
115. Journal of Molecular and Cellular Cardiology
116. Journal of Nuclear Cardiology
117. Journal of the American Heart Association
118. Journal of the American Society of Echocardiography
119. Journal of Thoracic and Cardiovascular Surgery
120. Journal of Thrombosis and Thrombolysis
121. Kardiologiya
122. Korean Circulation Journal
123. Minerva Cardiology and Angiology
124. Nature Reviews Cardiology
125. Netherlands Heart Journal
126. Nutrition Metabolism and Cardiovascular Diseases
127. Pace-Pacing and Clinical Electrophysiology
128. Pediatric Cardiology
129. Perfusion-UK
130. Polish Heart Journal-Kardiologia Polska
131. Postepy w Kardiologii Interwencyjnej
132. Progress in Cardiovascular Diseases
133. Pulmonary Circulation
134. Respiratory Medicine
135. Reviews in Cardiovascular Medicine
136. Revista Espanola de Cardiologia
137. Revista Portuguesa de Cardiologia
138. Scandinavian Cardiovascular Journal
139. Seminars in Thoracic and Cardiovascular Surgery
140. Structural and Congenital Heart Disease
141. Texas Heart Institute Journal
142. Thoracic and Cardiovascular Surgeon
143. Trends in Cardiovascular Medicine

<a id="scie-cell-tissue-engineering"></a>

### Cell & Tissue Engineering

期刊数：28

1. Bone & Joint Research
2. Bone Research
3. Cell STEM Cell
4. Cell Transplantation
5. Cellular and Molecular Bioengineering
6. Cellular Reprogramming
7. Current STEM Cell Research & Therapy
8. Cytotherapy
9. European Cells & Materials
10. International Journal of STEM Cells
11. Journal of Tissue Engineering
12. Journal of Tissue Engineering and Regenerative Medicine
13. Npj Regenerative Medicine
14. Regenerative Medicine
15. Regenerative Therapy
16. STEM Cell Reports
17. STEM Cell Research
18. STEM Cell Research & Therapy
19. STEM Cell Reviews and Reports
20. STEM Cells
21. STEM Cells and Development
22. STEM Cells International
23. STEM Cells Translational Medicine
24. Tissue Engineering and Regenerative Medicine
25. Tissue Engineering Part A
26. Tissue Engineering Part B-Reviews
27. Tissue Engineering Part C-Methods
28. World Journal of STEM Cells

<a id="scie-cell-biology"></a>

### Cell Biology

期刊数：189

1. Acta Histochemica
2. Acta Histochemica et Cytochemica
3. Acta Naturae
4. Ageing Research Reviews
5. Aging Cell
6. American Journal of Physiology-Cell Physiology
7. American Journal of Respiratory Cell and Molecular Biology
8. Analytical Cellular Pathology
9. Animal Cells and Systems
10. Annual Review of Cell and Developmental Biology
11. Apoptosis
12. Autophagy
13. Biochemistry and Cell Biology
14. Biochimica et Biophysica Acta-Molecular and Cell Biology of Lipids
15. Biochimica et Biophysica Acta-Molecular Cell Research
16. Biologicheskie Membrany
17. Biology of the Cell
18. Biopreservation and Biobanking
19. Bioscience Reports
20. Biotechnic & Histochemistry
21. BMC Molecular and Cell Biology
22. Cancer & Metabolism
23. Cancer Cell
24. Cell
25. Cell Adhesion & Migration
26. Cell and Tissue Banking
27. Cell and Tissue Research
28. Cell Biochemistry and Biophysics
29. Cell Biochemistry and Function
30. Cell Biology and Toxicology
31. Cell Biology International
32. Cell Calcium
33. Cell Communication and Signaling
34. Cell Cycle
35. Cell Death & Disease
36. Cell Death and Differentiation
37. Cell Death Discovery
38. Cell Discovery
39. Cell Division
40. Cell Journal
41. Cell Metabolism
42. Cell Proliferation
43. Cell Reports
44. Cell Reports Medicine
45. Cell Research
46. Cell STEM Cell
47. Cell Stress & Chaperones
48. Cell Structure and Function
49. Cell Systems
50. Cells
51. Cells Tissues Organs
52. Cellular & Molecular Biology Letters
53. Cellular and Molecular Bioengineering
54. Cellular and Molecular Life Sciences
55. Cellular and Molecular Neurobiology
56. Cellular Immunology
57. Cellular Microbiology
58. Cellular Oncology
59. Cellular Signalling
60. Cold Spring Harbor Perspectives in Biology
61. Connective Tissue Research
62. Current Biology
63. Current Opinion in Cell Biology
64. Current Opinion in Genetics & Development
65. Current Opinion in Structural Biology
66. Current STEM Cell Research & Therapy
67. Cytogenetic and Genome Research
68. Cytokine
69. Cytokine & Growth Factor Reviews
70. Cytologia
71. Cytometry Part A
72. Cytopathology
73. Cytoskeleton
74. Cytotechnology
75. Cytotherapy
76. Development Growth & Differentiation
77. Developmental Cell
78. Differentiation
79. Discover Developmental Biology
80. Disease Models & Mechanisms
81. DNA and Cell Biology
82. EMBO Journal
83. EMBO Reports
84. European Cytokine Network
85. European Journal of Cell Biology
86. European Journal of Histochemistry
87. Experimental Cell Research
88. FASEB Journal
89. FEBS Letters
90. Folia Histochemica et Cytobiologica
91. Frontiers in Bioscience-Landmark
92. Frontiers in Cell and Developmental Biology
93. Genes & Development
94. Genes to Cells
95. Growth Factors
96. Growth Hormone & IGF Research
97. Histochemistry and Cell Biology
98. Histology and Histopathology
99. Histopathology
100. HLA
101. Human Cell
102. IET Systems Biology
103. Immunology and Cell Biology
104. In Vitro Cellular & Developmental Biology-Animal
105. In Vitro Cellular & Developmental Biology-Plant
106. Inflammation
107. Inflammation Research
108. Integrative Biology
109. International Journal of Biochemistry & Cell Biology
110. International Journal of STEM Cells
111. IUBMB Life
112. Journal of Bioenergetics and Biomembranes
113. Journal of Biomedical Science
114. Journal of Cell Biology
115. Journal of Cell Communication and Signaling
116. Journal of Cell Science
117. Journal of Cellular and Molecular Medicine
118. Journal of Cellular Biochemistry
119. Journal of Cellular Physiology
120. Journal of Extracellular Vesicles
121. Journal of Histochemistry & Cytochemistry
122. Journal of Histotechnology
123. Journal of Interferon and Cytokine Research
124. Journal of Leukocyte Biology
125. Journal of Membrane Biology
126. Journal of Molecular and Cellular Cardiology
127. Journal of Molecular Cell Biology
128. Journal of Molecular Histology
129. Journal of Muscle Research and Cell Motility
130. Journal of Receptors and Signal Transduction
131. Journal of Structural Biology
132. Journal of Tissue Engineering and Regenerative Medicine
133. Matrix Biology
134. Mechanisms of Ageing and Development
135. Mediators of Inflammation
136. Microbial Cell
137. Mitochondrion
138. Molecular and Cellular Biochemistry
139. Molecular and Cellular Biology
140. Molecular and Cellular Endocrinology
141. Molecular and Cellular Probes
142. Molecular Biology of the Cell
143. Molecular Cancer Research
144. Molecular Cell
145. Molecular Medicine
146. Molecular Reproduction and Development
147. Molecules and Cells
148. Nature Aging
149. Nature Cell Biology
150. Nature Medicine
151. Nature Reviews Molecular Cell Biology
152. Nature Structural & Molecular Biology
153. Neural Regeneration Research
154. Nitric Oxide-Biology and Chemistry
155. Nucleus
156. Oncogene
157. Pathobiology
158. Physiological Genomics
159. Pigment Cell & Melanoma Research
160. Plant and Cell Physiology
161. Plant Cell
162. Platelets
163. Postepy Biologii Komorki
164. Prostaglandins & Other Lipid Mediators
165. Prostaglandins Leukotrienes and Essential Fatty Acids
166. Protein & Cell
167. Protoplasma
168. Science Signaling
169. Science Translational Medicine
170. Seminars in Cell & Developmental Biology
171. Signal Transduction and Targeted Therapy
172. Skeletal Muscle
173. STEM Cell Reports
174. STEM Cell Research
175. STEM Cell Research & Therapy
176. STEM Cell Reviews and Reports
177. STEM Cells
178. Structure
179. Tissue & Cell
180. Tissue Engineering Part A
181. Tissue Engineering Part B-Reviews
182. Tissue Engineering Part C-Methods
183. Traffic
184. Trends in Cell Biology
185. Trends in Molecular Medicine
186. Wiley Interdisciplinary Reviews-RNA
187. World Journal of STEM Cells
188. Wound Repair and Regeneration
189. Zygote

<a id="scie-chemistry-analytical"></a>

### Chemistry, Analytical

期刊数：87

1. Accreditation and Quality Assurance
2. ACS Sensors
3. Acta Chromatographica
4. Analyst
5. Analytica Chimica Acta
6. Analytical and Bioanalytical Chemistry
7. Analytical Biochemistry
8. Analytical Chemistry
9. Analytical Letters
10. Analytical Methods
11. Analytical Sciences
12. Annual Review of Analytical Chemistry
13. Archaeometry
14. ArchéoSciences-Revue d Archeometrie
15. Bioanalysis
16. BioChip Journal
17. Biomedical Chromatography
18. Biosensors & Bioelectronics
19. Biosensors-Basel
20. Bunseki Kagaku
21. Chemometrics and Intelligent Laboratory Systems
22. Chemosensors
23. Chinese Journal of Analytical Chemistry
24. Chirality
25. Chromatographia
26. Communications in Soil Science and Plant Analysis
27. Critical Reviews in Analytical Chemistry
28. Current Analytical Chemistry
29. Drug Testing and Analysis
30. Electroanalysis
31. Electrophoresis
32. Environmental Chemistry
33. Environmental Science-Processes & Impacts
34. Forensic Chemistry
35. Instrumentation Science & Technology
36. International Journal of Analytical Chemistry
37. International Journal of Environmental Analytical Chemistry
38. Journal of Analytical and Applied Pyrolysis
39. Journal of Analytical Atomic Spectrometry
40. Journal of Analytical Chemistry
41. Journal of Analytical Methods in Chemistry
42. Journal of Analytical Science and Technology
43. Journal of Analytical Toxicology
44. Journal of AOAC International
45. Journal of Chemometrics
46. Journal of Chromatographic Science
47. Journal of Chromatography A
48. Journal of Chromatography B-Analytical Technologies in the Biomedical and Life Sciences
49. Journal of Cultural Heritage
50. Journal of Electroanalytical Chemistry
51. Journal of Fluorescence
52. Journal of Labelled Compounds & Radiopharmaceuticals
53. Journal of Liquid Chromatography & Related Technologies
54. Journal of Mass Spectrometry
55. Journal of Peptide Science
56. Journal of Pharmaceutical and Biomedical Analysis
57. Journal of Radioanalytical and Nuclear Chemistry
58. Journal of Separation Science
59. Journal of the American Society for Mass Spectrometry
60. Journal of Thermal Analysis and Calorimetry
61. Journal of Water Chemistry and Technology
62. JPC-Journal of Planar Chromatography-Modern TLC
63. Lab on a Chip
64. LCGC Europe
65. LCGC North America
66. Luminescence
67. Methods and Applications in Fluorescence
68. Microchemical Journal
69. Microchimica Acta
70. Micromachines
71. Npj Heritage Science
72. Phytochemical Analysis
73. Rapid Communications in Mass Spectrometry
74. Reviews in Analytical Chemistry
75. Sensors
76. Sensors and Actuators B-Chemical
77. Sensors and Actuators Reports
78. Separation and Purification Reviews
79. Separations
80. Slas Discovery
81. Slas Technology
82. Studies in Conservation
83. Talanta
84. Thermochimica Acta
85. TrAC-Trends in Analytical Chemistry
86. Trends in Environmental Analytical Chemistry
87. Vibrational Spectroscopy

<a id="scie-chemistry-applied"></a>

### Chemistry, Applied

期刊数：72

1. AATCC Review
2. Adsorption Science & Technology
3. Advanced Synthesis & Catalysis
4. Agrochimica
5. Annual Review of Chemical and Biomolecular Engineering
6. Applied Organometallic Chemistry
7. Bioscience Biotechnology and Biochemistry
8. Carbohydrate Polymers
9. Carbohydrate Research
10. Catalysis Today
11. Central European Journal of Energetic Materials
12. Cereal Chemistry
13. Chemical Industry & Chemical Engineering Quarterly
14. Chemistry & Industry
15. Chinese Journal of Catalysis
16. Coatingstech
17. Color Research and Application
18. Coloration Technology
19. Combinatorial Chemistry & High Throughput Screening
20. Dyes and Pigments
21. Flavour and Fragrance Journal
22. Food Additives & Contaminants Part B-Surveillance
23. Food Additives and Contaminants Part A-Chemistry Analysis Control Exposure & Risk Assessment
24. Food and Agricultural Immunology
25. Food Chemistry
26. Food Chemistry-X
27. Food Hydrocolloids
28. Food Science and Technology International
29. Fuel Processing Technology
30. Grasas y Aceites
31. Green Sciences
32. Indian Journal of Chemical Technology
33. International Journal of Biological Macromolecules
34. Journal of Agricultural and Food Chemistry
35. Journal of Asian Natural Products Research
36. Journal of Cellular Plastics
37. Journal of Coatings Technology and Research
38. Journal of Cosmetic Science
39. Journal of Energetic Materials
40. Journal of Energy Chemistry
41. Journal of Essential Oil Research
42. Journal of Food Composition and Analysis
43. Journal of Food Safety and Food Quality-Archiv für Lebensmittelhygiene
44. Journal of Microencapsulation
45. Journal of Near Infrared Spectroscopy
46. Journal of Oleo Science
47. Journal of Porous Materials
48. Journal of Rare Earths
49. Journal of Surfactants and Detergents
50. Journal of the American Leather Chemists Association
51. Journal of the American Oil Chemists Society
52. Journal of the Science of Food and Agriculture
53. Journal of Vinyl & Additive Technology
54. Journal of Water Chemistry and Technology
55. Microporous and Mesoporous Materials
56. Molecular Diversity
57. Natural Product Research
58. Organic Process Research & Development
59. Pigment & Resin Technology
60. Plant Foods for Human Nutrition
61. Progress in Organic Coatings
62. Propellants Explosives Pyrotechnics
63. Reactive & Functional Polymers
64. Records of Natural Products
65. Revista Mexicana de Ingenieria Quimica
66. Russian Journal of Applied Chemistry
67. Science and Technology of Energetic Materials
68. Separation and Purification Reviews
69. Studies in Conservation
70. Surface Coatings International
71. Tenside Surfactants Detergents
72. Topics in Catalysis

<a id="scie-chemistry-inorganic-nuclear"></a>

### Chemistry, Inorganic & Nuclear

期刊数：42

1. Applied Organometallic Chemistry
2. Applied Radiation and Isotopes
3. Archaeometry
4. Bioinorganic Chemistry and Applications
5. Chinese Journal of Inorganic Chemistry
6. Chinese Journal of Structural Chemistry
7. Comments on Inorganic Chemistry
8. Coordination Chemistry Reviews
9. Dalton Transactions
10. Discover Metals
11. European Journal of Inorganic Chemistry
12. Inorganic and Nano-Metal Chemistry
13. Inorganic Chemistry
14. Inorganic Chemistry Communications
15. Inorganic Chemistry Frontiers
16. Inorganica Chimica Acta
17. Inorganics
18. Isotopes in Environmental and Health Studies
19. Journal of Biological Inorganic Chemistry
20. Journal of Cluster Science
21. Journal of Coordination Chemistry
22. Journal of Fluorine Chemistry
23. Journal of Inorganic Biochemistry
24. Journal of Organometallic Chemistry
25. Journal of Radioanalytical and Nuclear Chemistry
26. Journal of Solid State Chemistry
27. Journal of Structural Chemistry
28. Magnetochemistry
29. Main Group Metal Chemistry
30. Nukleonika
31. Organometallics
32. Phosphorus Sulfur and Silicon and the Related Elements
33. Polyhedron
34. Progress in Solid State Chemistry
35. Radiochimica Acta
36. Reviews in Inorganic Chemistry
37. Russian Journal of Coordination Chemistry
38. Russian Journal of Inorganic Chemistry
39. Solid State Sciences
40. Transition Metal Chemistry
41. Zeitschrift für Anorganische und Allgemeine Chemie
42. Zeitschrift für Naturforschung Section B-a Journal of Chemical Sciences

<a id="scie-chemistry-medicinal"></a>

### Chemistry, Medicinal

期刊数：60

1. ACS Chemical Neuroscience
2. ACS Infectious Diseases
3. ACS Medicinal Chemistry Letters
4. Anti-Cancer Agents in Medicinal Chemistry
5. Antioxidants
6. Archiv der Pharmazie
7. Archives of Pharmacal Research
8. Bioorganic & Medicinal Chemistry
9. Bioorganic & Medicinal Chemistry Letters
10. ChemBioChem
11. Chemical & Pharmaceutical Bulletin
12. Chemical Biology & Drug Design
13. Chemical Research in Toxicology
14. Chemistry of Natural Compounds
15. ChemMedChem
16. Chirality
17. Current Computer-Aided Drug Design
18. Current Medicinal Chemistry
19. Current Topics in Medicinal Chemistry
20. Drug Design Development and Therapy
21. Drug Development and Industrial Pharmacy
22. Drug Development Research
23. European Journal of Medicinal Chemistry
24. Expert Opinion on Therapeutic Patents
25. Fitoterapia
26. Future Medicinal Chemistry
27. Journal of Asian Natural Products Research
28. Journal of Chemical Information and Modeling
29. Journal of Enzyme Inhibition and Medicinal Chemistry
30. Journal of Ethnopharmacology
31. Journal of Ginseng Research
32. Journal of Labelled Compounds & Radiopharmaceuticals
33. Journal of Medicinal Chemistry
34. Journal of Medicinal Food
35. Journal of Natural Medicines
36. Journal of Natural Products
37. Journal of Pharmaceutical Sciences
38. Letters in Drug Design & Discovery
39. Marine Drugs
40. Medicinal Chemistry
41. Medicinal Chemistry Research
42. Medicinal Research Reviews
43. Mini-Reviews in Medicinal Chemistry
44. Molecular Diversity
45. Molecular Informatics
46. Natural Product Communications
47. Natural Product Reports
48. Natural Product Research
49. Nucleic Acid Therapeutics
50. Pharmaceutical Chemistry Journal
51. Pharmaceuticals
52. Pharmacognosy Magazine
53. Pharmazie
54. Phytochemistry Letters
55. Phytomedicine
56. Phytotherapy Research
57. Planta Medica
58. Records of Natural Products
59. Revista Brasileira de Farmacognosia-Brazilian Journal of Pharmacognosy
60. RSC Medicinal Chemistry

<a id="scie-chemistry-multidisciplinary"></a>

### Chemistry, Multidisciplinary

期刊数：176

1. Accounts of Chemical Research
2. ACS Central Science
3. ACS Earth and Space Chemistry
4. ACS Nano
5. ACS Omega
6. ACS Sensors
7. ACS Sustainable Chemistry & Engineering
8. Acta Chimica Sinica
9. Acta Chimica Slovenica
10. Acta Crystallographica A-Foundation and Advances
11. Acta Crystallographica Section B-Structural Science Crystal Engineering and Materials
12. Acta Crystallographica Section C-Structural Chemistry
13. Acta Pharmacologica Sinica
14. Advanced Functional Materials
15. Advanced Materials
16. Advanced Materials Interfaces
17. Advanced Science
18. Afinidad
19. Angewandte Chemie-International Edition
20. Applied Sciences-Basel
21. Arabian Journal of Chemistry
22. Archiv der Pharmazie
23. Australian Journal of Chemistry
24. Bioconjugate Chemistry
25. BMC Chemistry
26. Bulletin of the Chemical Society of Ethiopia
27. Bulletin of the Chemical Society of Japan
28. Bulletin of the Korean Chemical Society
29. C&en Global Enterprise
30. Canadian Journal of Chemistry
31. Carbon Letters
32. Cell Reports Physical Science
33. Chem
34. Chemical & Pharmaceutical Bulletin
35. Chemical Communications
36. Chemical Journal of Chinese Universities-Chinese
37. Chemical Papers
38. Chemical Record
39. Chemical Research in Chinese Universities
40. Chemical Research in Toxicology
41. Chemical Reviews
42. Chemical Science
43. Chemical Society Reviews
44. Chemicke Listy
45. Chemie in Unserer Zeit
46. Chemija
47. Chemistry & Biodiversity
48. Chemistry Letters
49. Chemistry-A European Journal
50. Chemistry-an Asian Journal
51. ChemistryOpen
52. ChemistrySelect
53. ChemNanoMat
54. ChemPlusChem
55. ChemSusChem
56. Chimia
57. Chinese Chemical Letters
58. Chinese Journal of Chemistry
59. Communications Chemistry
60. Comptes Rendus Chimie
61. Croatica Chemica Acta
62. Crystal Growth & Design
63. CrystEngComm
64. Current Opinion in Green and Sustainable Chemistry
65. Doklady Chemistry
66. Drug and Chemical Toxicology
67. Energy & Environmental Science
68. Environmental Chemistry Letters
69. Environmental Science-Nano
70. Fibre Chemistry
71. Frontiers in Chemistry
72. Green Chemistry
73. Green Chemistry Letters and Reviews
74. Green Processing and Synthesis
75. Helvetica Chimica Acta
76. Heteroatom Chemistry
77. International Journal of Molecular Sciences
78. Iranian Journal of Chemistry & Chemical Engineering-International English Edition
79. Israel Journal of Chemistry
80. IUCrJ
81. Journal of Applied Crystallography
82. Journal of Chemical and Engineering Data
83. Journal of Chemical Education
84. Journal of Chemical Information and Modeling
85. Journal of Chemical Research
86. Journal of Chemical Sciences
87. Journal of Chemical Technology and Biotechnology
88. Journal of Cheminformatics
89. Journal of Chemistry
90. Journal of CO2 Utilization
91. Journal of Computational Biophysics and Chemistry
92. Journal of Computational Chemistry
93. Journal of Controlled Release
94. Journal of Experimental Nanoscience
95. Journal of Flow Chemistry
96. Journal of Inclusion Phenomena and Macrocyclic Chemistry
97. Journal of Industrial and Engineering Chemistry
98. Journal of Mathematical Chemistry
99. Journal of Molecular Modeling
100. Journal of Nanoparticle Research
101. Journal of Nanostructure in Chemistry
102. Journal of Pharmaceutical Sciences
103. Journal of Physical and Chemical Reference Data
104. Journal of Physics and Chemistry of Solids
105. Journal of Porphyrins and Phthalocyanines
106. Journal of Saudi Chemical Society
107. Journal of Sulfur Chemistry
108. Journal of the American Chemical Society
109. Journal of the Brazilian Chemical Society
110. Journal of the Chemical Society of Pakistan
111. Journal of the Chilean Chemical Society
112. Journal of the Chinese Chemical Society
113. Journal of the Indian Chemical Society
114. Journal of the Iranian Chemical Society
115. Journal of the Mexican Chemical Society
116. Journal of the Serbian Chemical Society
117. Korean Journal of Chemical Engineering
118. Lab on a Chip
119. Langmuir
120. Liquid Crystals
121. Macedonian Journal of Chemistry and Chemical Engineering
122. Macroheterocycles
123. Magnetic Resonance in Chemistry
124. Main Group Chemistry
125. Marine Chemistry
126. Match-Communications in Mathematical and in Computer Chemistry
127. Materials Chemistry Frontiers
128. Materials Horizons
129. Materials Today Chemistry
130. Mendeleev Communications
131. Molecular Crystals and Liquid Crystals
132. Molecular Diversity
133. Molecules
134. Monatshefte für Chemie
135. Nano Letters
136. Nano Today
137. Nanomaterials
138. Nanoscale
139. Nanoscale Advances
140. Nanotechnology Reviews
141. Nature Chemistry
142. Nature Reviews Chemistry
143. New Journal of Chemistry
144. Open Chemistry
145. Pharmaceutical Research
146. Pharmazie
147. Progress in Chemistry
148. Przemysl Chemiczny
149. Pure and Applied Chemistry
150. Quimica Nova
151. Reaction Chemistry & Engineering
152. Research on Chemical Intermediates
153. Revue Roumaine de Chimie
154. RSC Advances
155. Russian Chemical Bulletin
156. Russian Chemical Reviews
157. Russian Journal of General Chemistry
158. SAR and QSAR in Environmental Research
159. Science China-Chemistry
160. Separation Science and Technology
161. Small
162. Solid Fuel Chemistry
163. Solvent Extraction and Ion Exchange
164. Solvent Extraction Research and Development-Japan
165. South African Journal of Chemistry-Suid-Afrikaanse Tydskrif Vir Chemie
166. Structural Chemistry
167. Studia Universitatis Babes-Bolyai Chemia
168. Supramolecular Chemistry
169. SusMat
170. Sustainable Chemistry and Pharmacy
171. Theoretical and Experimental Chemistry
172. Topics in Current Chemistry
173. Trends in Chemistry
174. Turkish Journal of Chemistry
175. Ultrasonics Sonochemistry
176. Wiley Interdisciplinary Reviews-Computational Molecular Science

<a id="scie-chemistry-organic"></a>

### Chemistry, Organic

期刊数：51

1. Advanced Synthesis & Catalysis
2. Aldrichimica Acta
3. Arkivoc
4. Asian Journal of Organic Chemistry
5. Beilstein Journal of Organic Chemistry
6. Bioconjugate Chemistry
7. Bioinorganic Chemistry and Applications
8. Biomacromolecules
9. Bioorganic & Medicinal Chemistry
10. Bioorganic & Medicinal Chemistry Letters
11. Bioorganic Chemistry
12. Carbohydrate Polymers
13. Carbohydrate Research
14. Chemistry of Heterocyclic Compounds
15. Chemistry of Natural Compounds
16. Chinese Journal of Organic Chemistry
17. Chirality
18. Current Organic Chemistry
19. Current Organic Synthesis
20. European Journal of Organic Chemistry
21. Heterocyclic Communications
22. Indian Journal of Chemistry
23. Indian Journal of Heterocyclic Chemistry
24. Journal of Carbohydrate Chemistry
25. Journal of Fluorine Chemistry
26. Journal of Heterocyclic Chemistry
27. Journal of Organic Chemistry
28. Journal of Organometallic Chemistry
29. Journal of Physical Organic Chemistry
30. Journal of Synthetic Organic Chemistry Japan
31. Letters in Organic Chemistry
32. Main Group Metal Chemistry
33. Mini-Reviews in Organic Chemistry
34. Natural Product Reports
35. Organic & Biomolecular Chemistry
36. Organic Chemistry Frontiers
37. Organic Letters
38. Organic Preparations and Procedures International
39. Organic Process Research & Development
40. Organometallics
41. Petroleum Chemistry
42. Phosphorus Sulfur and Silicon and the Related Elements
43. Polycyclic Aromatic Compounds
44. Russian Journal of Bioorganic Chemistry
45. Russian Journal of Organic Chemistry
46. Synlett
47. Synthesis-Stuttgart
48. Synthetic Communications
49. Tetrahedron
50. Tetrahedron Letters
51. Zeitschrift für Naturforschung Section B-a Journal of Chemical Sciences

<a id="scie-chemistry-physical"></a>

### Chemistry, Physical

期刊数：162

1. ACS Applied Energy Materials
2. ACS Catalysis
3. ACS Energy Letters
4. ACS Nano
5. Acta Physico-Chimica Sinica
6. Adsorption Science & Technology
7. Adsorption-Journal of the International Adsorption Society
8. Advanced Energy Materials
9. Advanced Functional Materials
10. Advanced Materials
11. Advances in Colloid and Interface Science
12. Annual Review of Physical Chemistry
13. Applied Catalysis A-General
14. Applied Catalysis B-Environment and Energy
15. Applied Catalysis O: Open
16. Applied Clay Science
17. Applied Surface Science
18. Biophysical Chemistry
19. Calphad-Computer Coupling of Phase Diagrams and Thermochemistry
20. Carbon
21. Carbon Energy
22. Catalysis Letters
23. Catalysis Reviews-Science and Engineering
24. Catalysis Science & Technology
25. Catalysis Surveys from Asia
26. Catalysis Today
27. Catalysts
28. ChemCatChem
29. Chemical Physics
30. Chemical Physics Letters
31. Chemical Physics Reviews
32. Chemistry of Materials
33. ChemPhotoChem
34. ChemPhysChem
35. Chinese Journal of Catalysis
36. Clay Minerals
37. Clays and Clay Minerals
38. Colloid and Interface Science Communications
39. Colloid and Polymer Science
40. Colloid Journal
41. Colloids and Surfaces A-Physicochemical and Engineering Aspects
42. Colloids and Surfaces B-Biointerfaces
43. Computational and Theoretical Chemistry
44. Concepts in Magnetic Resonance Part A
45. Current Opinion in Colloid & Interface Science
46. Current Opinion in Electrochemistry
47. Discover Metals
48. Doklady Physical Chemistry
49. EcoMat
50. Electrocatalysis
51. Energy & Environmental Materials
52. Energy Storage Materials
53. European Physical Journal E
54. Faraday Discussions
55. FlatChem
56. Fluid Phase Equilibria
57. Fullerenes Nanotubes and Carbon Nanostructures
58. Green Energy & Environment
59. High Energy Chemistry
60. Intermetallics
61. International Journal of Chemical Kinetics
62. International Journal of Hydrogen Energy
63. International Journal of Photoenergy
64. International Journal of Quantum Chemistry
65. International Journal of Thermophysics
66. International Reviews in Physical Chemistry
67. Ionics
68. Johnson Matthey Technology Review
69. Joule
70. Journal of Alloys and Compounds
71. Journal of Catalysis
72. Journal of Chemical Physics
73. Journal of Chemical Theory and Computation
74. Journal of Chemical Thermodynamics
75. Journal of Colloid and Interface Science
76. Journal of Dispersion Science and Technology
77. Journal of Energetic Materials
78. Journal of Energy Chemistry
79. Journal of Fluorescence
80. Journal of Materials Chemistry A
81. Journal of Materiomics
82. Journal of Molecular Structure
83. Journal of Phase Equilibria and Diffusion
84. Journal of Photochemistry and Photobiology a-Chemistry
85. Journal of Photochemistry and Photobiology C-Photochemistry Reviews
86. Journal of Physical and Chemical Reference Data
87. Journal of Physical Chemistry A
88. Journal of Physical Chemistry B
89. Journal of Physical Chemistry C
90. Journal of Physical Chemistry Letters
91. Journal of Physical Organic Chemistry
92. Journal of Physics-Energy
93. Journal of Porous Materials
94. Journal of Power Sources
95. Journal of Solid State Chemistry
96. Journal of Solution Chemistry
97. Journal of Structural Chemistry
98. Journal of Supercritical Fluids
99. Journal of Surfactants and Detergents
100. Journal of the American Society for Mass Spectrometry
101. Journal of Thermal Analysis and Calorimetry
102. Journal of Water Chemistry and Technology
103. Kinetics and Catalysis
104. Langmuir
105. Liquid Crystals Reviews
106. Magnetic Resonance in Chemistry
107. Magnetochemistry
108. Materials
109. Materials Today Energy
110. Membranes
111. Methods and Applications in Fluorescence
112. Microporous and Mesoporous Materials
113. Molecular Catalysis
114. Molecular Physics
115. Molecular Simulation
116. Molecular Systems Design & Engineering
117. Nano Energy
118. Nano Letters
119. Nano Research
120. Nanoscale Horizons
121. Nature Catalysis
122. Nature Materials
123. Npj Computational Materials
124. Particle & Particle Systems Characterization
125. Petroleum Chemistry
126. Photochemical & Photobiological Sciences
127. Physical Chemistry Chemical Physics
128. Physicochemical Problems of Mineral Processing
129. Physics and Chemistry of Glasses-European Journal of Glass Science and Technology Part B
130. Physics and Chemistry of Liquids
131. Plasmonics
132. Progress in Nuclear Magnetic Resonance Spectroscopy
133. Progress in Reaction Kinetics and Mechanism
134. Progress in Surface Science
135. Radiation Physics and Chemistry
136. Reaction Kinetics Mechanisms and Catalysis
137. Russian Journal of Physical Chemistry A
138. Science and Technology of Energetic Materials
139. Silicon
140. Small
141. Small Methods
142. Small Structures
143. Soft Matter
144. Solid State Ionics
145. Solid State Nuclear Magnetic Resonance
146. Solid State Sciences
147. Structural Chemistry
148. Structural Dynamics-US
149. Surface and Interface Analysis
150. Surface Innovations
151. Surface Review and Letters
152. Surface Science
153. Surface Science Reports
154. Surfaces and Interfaces
155. Sustainable Energy & Fuels
156. Tenside Surfactants Detergents
157. Theoretical Chemistry Accounts
158. Thermochimica Acta
159. Topics in Catalysis
160. Vibrational Spectroscopy
161. Zeitschrift für Naturforschung Section A-a Journal of Physical Sciences
162. Zeitschrift für Physikalische Chemie-International Journal of Research in Physical Chemistry & Chemical Physics

<a id="scie-clinical-neurology"></a>

### Clinical Neurology

期刊数：213

1. Acta Neurochirurgica
2. Acta Neurologica Belgica
3. Acta Neurologica Scandinavica
4. Acta Neuropathologica
5. Alzheimer Disease & Associated Disorders
6. Alzheimers & Dementia
7. Alzheimers Research & Therapy
8. American Journal of Alzheimers Disease and Other Dementias
9. American Journal of Neuroradiology
10. Amyotrophic Lateral Sclerosis and Frontotemporal Degeneration
11. Annals of Clinical and Translational Neurology
12. Annals of Indian Academy of Neurology
13. Annals of Neurology
14. Aphasiology
15. Applied Neuropsychology-Adult
16. Applied Neuropsychology-Child
17. Behavioral Sleep Medicine
18. Behavioural Neurology
19. Bipolar Disorders
20. BMC Neurology
21. Brain
22. Brain & Development
23. Brain Impairment
24. Brain Pathology
25. Brain Sciences
26. Brain Stimulation
27. Brain Topography
28. Brain Tumor Pathology
29. British Journal of Neurosurgery
30. Canadian Journal of Neurological Sciences
31. Cephalalgia
32. Cerebrovascular Diseases
33. Child Neuropsychology
34. Childs Nervous System
35. Clinical Autonomic Research
36. Clinical EEG and Neuroscience
37. Clinical Journal of Pain
38. Clinical Neurology and Neurosurgery
39. Clinical Neuropathology
40. Clinical Neuropharmacology
41. Clinical Neurophysiology
42. Clinical Neuropsychologist
43. Clinical Neuroradiology
44. Clinical Spine Surgery
45. CNS Drugs
46. CNS Spectrums
47. Cognitive and Behavioral Neurology
48. Current Alzheimer Research
49. Current Neurology and Neuroscience Reports
50. Current Neurovascular Research
51. Current Opinion in Neurology
52. Current Pain and Headache Reports
53. Current Treatment Options in Neurology
54. Dementia and Geriatric Cognitive Disorders
55. Developmental Medicine and Child Neurology
56. Developmental Neurorehabilitation
57. Epilepsia
58. Epilepsia Open
59. Epilepsy & Behavior
60. Epilepsy Currents
61. Epilepsy Research
62. Epileptic Disorders
63. European Archives of Psychiatry and Clinical Neuroscience
64. European Journal of Neurology
65. European Journal of Paediatric Neurology
66. European Journal of Pain
67. European Neurology
68. European Neuropsychopharmacology
69. European Spine Journal
70. European Stroke Journal
71. Expert Review of Neurotherapeutics
72. Fortschritte der Neurologie Psychiatrie
73. Frontiers in Neurology
74. Global Spine Journal
75. Headache
76. Human Psychopharmacology-Clinical and Experimental
77. Ideggyogyaszati Szemle-Clinical Neuroscience
78. International Journal of Neuropsychopharmacology
79. International Journal of Stroke
80. Interventional Neuroradiology
81. JAMA Neurology
82. Journal of Affective Disorders
83. Journal of Child Neurology
84. Journal of Clinical and Experimental Neuropsychology
85. Journal of Clinical Neurology
86. Journal of Clinical Neurophysiology
87. Journal of Clinical Neuroscience
88. Journal of Clinical Sleep Medicine
89. Journal of Geriatric Psychiatry and Neurology
90. Journal of Head Trauma Rehabilitation
91. Journal of Headache and Pain
92. Journal of Korean Neurosurgical Society
93. Journal of Movement Disorders
94. Journal of Nervous and Mental Disease
95. Journal of Neural Transmission
96. Journal of Neuro-Oncology
97. Journal of Neuro-Ophthalmology
98. Journal of Neurodevelopmental Disorders
99. Journal of Neurogastroenterology and Motility
100. Journal of Neuroimaging
101. Journal of Neurologic Physical Therapy
102. Journal of Neurological Surgery Part A-Central European Neurosurgery
103. Journal of Neurological Surgery Part B-Skull Base
104. Journal of Neurology
105. Journal of Neurology Neurosurgery and Psychiatry
106. Journal of Neuromuscular Diseases
107. Journal of Neuropathology and Experimental Neurology
108. Journal of Neuropsychiatry and Clinical Neurosciences
109. Journal of Neuroradiology
110. Journal of Neuroscience Nursing
111. Journal of Neurosurgery
112. Journal of Neurosurgery-Pediatrics
113. Journal of Neurosurgery-Spine
114. Journal of Neurosurgical Anesthesiology
115. Journal of Neurosurgical Sciences
116. Journal of Neurotrauma
117. Journal of Pain
118. Journal of Pain and Symptom Management
119. Journal of Pain Research
120. Journal of Psychopharmacology
121. Journal of Sleep Research
122. Journal of Spinal Cord Medicine
123. Journal of Stroke
124. Journal of the International Neuropsychological Society
125. Journal of the Neurological Sciences
126. Journal of the Peripheral Nervous System
127. Jpad-Journal of Prevention of Alzheimers Disease
128. Klinische Neurophysiologie
129. Korean Journal of Pain
130. Lancet Neurology
131. Movement Disorders
132. Movement Disorders Clinical Practice
133. Multiple Sclerosis and Related Disorders
134. Multiple Sclerosis Journal
135. Muscle & Nerve
136. Nature and Science of Sleep
137. Nature Reviews Neurology
138. Nervenarzt
139. Neuro-Oncology
140. Neurocase
141. Neurochirurgie
142. Neurocritical Care
143. Neurodegenerative Diseases
144. Neuroepidemiology
145. Neurogastroenterology and Motility
146. Neurogenetics
147. Neurologia
148. Neurologia i Neurochirurgia Polska
149. Neurologia Medico-Chirurgica
150. Neurologic Clinics
151. Neurological Research
152. Neurological Sciences
153. Neurologist
154. Neurology
155. Neurology and Therapy
156. Neurology Asia
157. Neurology-Genetics
158. Neurology-Neuroimmunology & Neuroinflammation
159. Neuromodulation
160. Neuromuscular Disorders
161. Neuropathology
162. Neuropathology and Applied Neurobiology
163. Neuropediatrics
164. Neurophysiologie Clinique-Clinical Neurophysiology
165. Neuropsychiatric Disease and Treatment
166. Neuroradiology
167. NeuroRehabilitation
168. Neurorehabilitation and Neural Repair
169. Neurosciences
170. Neuroscientist
171. Neurospine
172. Neurosurgery
173. Neurosurgery Clinics of North America
174. Neurosurgical Focus
175. Neurosurgical Review
176. Neurotherapeutics
177. Noropsikiyatri Arsivi-Archives of Neuropsychiatry
178. Operative Neurosurgery
179. Otology & Neurotology
180. Pain
181. Pain and Therapy
182. Pain Physician
183. Pain Practice
184. Pain Research & Management
185. Parkinsonism & Related Disorders
186. Parkinsons Disease
187. Pediatric Neurology
188. Pediatric Neurosurgery
189. Progress in Neuro-Psychopharmacology & Biological Psychiatry
190. Psychiatry and Clinical Neurosciences
191. Psychiatry Research-Neuroimaging
192. Revista de Neurologia
193. Revue Neurologique
194. Schmerz
195. Seizure-European Journal of Epilepsy
196. Seminars in Neurology
197. Seminars in Pediatric Neurology
198. Sleep
199. Sleep and Biological Rhythms
200. Sleep and Breathing
201. Sleep Health
202. Sleep Medicine
203. Sleep Medicine Reviews
204. Spinal Cord
205. Spine
206. Spine Journal
207. Stroke
208. Stroke and Vascular Neurology
209. Therapeutic Advances in Neurological Disorders
210. Translational Stroke Research
211. Turkish Neurosurgery
212. World Neurosurgery
213. Zeitschrift für Neuropsychologie

<a id="scie-computer-science-artificial-intelligence"></a>

### Computer Science, Artificial Intelligence

期刊数：143

1. ACM Transactions on Asian and Low-Resource Language Information Processing
2. ACM Transactions on Autonomous and Adaptive Systems
3. ACM Transactions on Intelligent Systems and Technology
4. ACM Transactions on Interactive Intelligent Systems
5. Adaptive Behavior
6. Advanced Engineering Informatics
7. Advanced Intelligent Systems
8. Advances in Electrical and Computer Engineering
9. AI Edam-Artificial Intelligence for Engineering Design Analysis and Manufacturing
10. AI Magazine
11. Annals of Mathematics and Artificial Intelligence
12. Applied Artificial Intelligence
13. Applied Intelligence
14. Applied Ontology
15. Applied Soft Computing
16. Artificial Intelligence
17. Artificial Intelligence and Law
18. Artificial Intelligence in Agriculture
19. Artificial Intelligence in Medicine
20. Artificial Intelligence Review
21. Artificial Life
22. Autonomous Agents and Multi-Agent Systems
23. Autonomous Robots
24. Big Data Research
25. CAAI Transactions on Intelligence Technology
26. Chemometrics and Intelligent Laboratory Systems
27. Cognitive Computation
28. Cognitive Systems Research
29. Complex & Intelligent Systems
30. Computational Intelligence
31. Computational Linguistics
32. Computer Speech and Language
33. Computer Vision and Image Understanding
34. Computing and Informatics
35. Connection Science
36. Constraints
37. Data & Knowledge Engineering
38. Data Mining and Knowledge Discovery
39. Decision Support Systems
40. Egyptian Informatics Journal
41. Engineering Applications of Artificial Intelligence
42. European Journal on Artificial Intelligence
43. Evolutionary Computation
44. Evolving Systems
45. Expert Systems
46. Expert Systems with Applications
47. Frontiers in Neurorobotics
48. Fuzzy Optimization and Decision Making
49. Genetic Programming and Evolvable Machines
50. IEEE Computational Intelligence Magazine
51. IEEE Intelligent Systems
52. IEEE Transactions on Affective Computing
53. IEEE Transactions on Cognitive and Developmental Systems
54. IEEE Transactions on Cybernetics
55. IEEE Transactions on Emerging Topics in Computational Intelligence
56. IEEE Transactions on Evolutionary Computation
57. IEEE Transactions on Fuzzy Systems
58. IEEE Transactions on Games
59. IEEE Transactions on Human-Machine Systems
60. IEEE Transactions on Image Processing
61. IEEE Transactions on Intelligent Vehicles
62. IEEE Transactions on Knowledge and Data Engineering
63. IEEE Transactions on Neural Networks and Learning Systems
64. IEEE Transactions on Pattern Analysis and Machine Intelligence
65. IET Biometrics
66. IET Computer Vision
67. IET Image Processing
68. Image and Vision Computing
69. Information Fusion
70. Information Technology and Control
71. Integrated Computer-Aided Engineering
72. Intelligent Data Analysis
73. International Arab Journal of Information Technology
74. International Journal of Applied Mathematics and Computer Science
75. International Journal of Approximate Reasoning
76. International Journal of Bio-Inspired Computation
77. International Journal of Computational Intelligence Systems
78. International Journal of Computer Vision
79. International Journal of Fuzzy Systems
80. International Journal of Information Technology & Decision Making
81. International Journal of Intelligent Systems
82. International Journal of Interactive Multimedia and Artificial Intelligence
83. International Journal of Machine Learning and Cybernetics
84. International Journal of Multimedia Information Retrieval
85. International Journal of Neural Systems
86. International Journal of Pattern Recognition and Artificial Intelligence
87. International Journal of Software Engineering and Knowledge Engineering
88. International Journal of Uncertainty Fuzziness and Knowledge-Based Systems
89. International Journal on Artificial Intelligence Tools
90. International Journal on Document Analysis and Recognition
91. Journal of Ambient Intelligence and Smart Environments
92. Journal of Artificial Intelligence and Soft Computing Research
93. Journal of Artificial Intelligence Research
94. Journal of Automated Reasoning
95. Journal of Chemometrics
96. Journal of Computer and Systems Sciences International
97. Journal of Experimental & Theoretical Artificial Intelligence
98. Journal of Heuristics
99. Journal of Intelligent & Fuzzy Systems
100. Journal of Intelligent & Robotic Systems
101. Journal of Intelligent Information Systems
102. Journal of Intelligent Manufacturing
103. Journal of Logic Language and Information
104. Journal of Machine Learning Research
105. Journal of Mathematical Imaging and Vision
106. Journal of Multiple-Valued Logic and Soft Computing
107. Journal of Real-Time Image Processing
108. Journal of Web Semantics
109. Journal on Multimodal User Interfaces
110. Knowledge and Information Systems
111. Knowledge Engineering Review
112. Knowledge-Based Systems
113. Machine Learning
114. Machine Learning-Science and Technology
115. Machine Vision and Applications
116. Malaysian Journal of Computer Science
117. Medical Image Analysis
118. Memetic Computing
119. Minds and Machines
120. Natural Computing
121. Natural Language Processing
122. Nature Machine Intelligence
123. Network-Computation in Neural Systems
124. Neural Computation
125. Neural Network World
126. Neural Networks
127. Neural Processing Letters
128. Neurocomputing
129. Pattern Analysis and Applications
130. Pattern Recognition
131. Pattern Recognition Letters
132. PeerJ Computer Science
133. Radiology-Artificial Intelligence
134. Robotics and Autonomous Systems
135. Semantic Web
136. SIAM Journal on Imaging Sciences
137. Soft Computing
138. Statistical Analysis and Data Mining-an ASA Data Science Journal
139. Swarm and Evolutionary Computation
140. Swarm Intelligence
141. Transactions of the Association for Computational Linguistics
142. Turkish Journal of Electrical Engineering and Computer Sciences
143. Wiley Interdisciplinary Reviews-Data Mining and Knowledge Discovery

<a id="scie-computer-science-cybernetics"></a>

### Computer Science, Cybernetics

期刊数：24

1. ACM Transactions on Computer-Human Interaction
2. Behaviour & Information Technology
3. Biological Cybernetics
4. Cybernetics and Systems
5. Entertainment Computing
6. Human-Computer Interaction
7. IEEE Transactions on Affective Computing
8. IEEE Transactions on Computational Social Systems
9. IEEE Transactions on Cybernetics
10. IEEE Transactions on Haptics
11. IEEE Transactions on Human-Machine Systems
12. IEEE Transactions on Systems Man Cybernetics-Systems
13. Interacting with Computers
14. International Journal of Human-Computer Interaction
15. International Journal of Human-Computer Studies
16. Journal of Computer and Systems Sciences International
17. Journal on Multimodal User Interfaces
18. Kybernetes
19. Kybernetika
20. Machine Vision and Applications
21. Modeling Identification and Control
22. Presence-Virtual and Augmented Reality
23. Universal Access in the Information Society
24. User Modeling and User-Adapted Interaction

<a id="scie-computer-science-hardware-architecture"></a>

### Computer Science, Hardware & Architecture

期刊数：51

1. ACM Journal on Emerging Technologies in Computing Systems
2. ACM Transactions on Architecture and Code Optimization
3. ACM Transactions on Design Automation of Electronic Systems
4. ACM Transactions on Embedded Computing Systems
5. ACM Transactions on Reconfigurable Technology and Systems
6. ACM Transactions on Storage
7. Analog Integrated Circuits and Signal Processing
8. Communications of the ACM
9. Computer
10. Computer Journal
11. Computer Networks
12. Computer Standards & Interfaces
13. Computers & Electrical Engineering
14. Design Automation for Embedded Systems
15. Displays
16. IEEE Canadian Journal of Electrical and Computer Engineering
17. IEEE Computer Architecture Letters
18. IEEE Consumer Electronics Magazine
19. IEEE Design & Test
20. IEEE Embedded Systems Letters
21. IEEE Micro
22. IEEE Multimedia
23. IEEE Network
24. IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems
25. IEEE Transactions on Computers
26. IEEE Transactions on Dependable and Secure Computing
27. IEEE Transactions on Networking
28. IEEE Transactions on Neural Networks and Learning Systems
29. IEEE Transactions on Reliability
30. IEEE Transactions on Sustainable Computing
31. IEEE Transactions on Very Large Scale Integration (VLSI) Systems
32. IEEE Wireless Communications
33. IEICE Transactions on Fundamentals of Electronics Communications and Computer Sciences
34. IET Computers and Digital Techniques
35. Integration-the VLSI Journal
36. International Journal of High Performance Computing Applications
37. Journal of Circuits Systems and Computers
38. Journal of Computer and System Sciences
39. Journal of Computer Science and Technology
40. Journal of Network and Computer Applications
41. Journal of Optical Communications and Networking
42. Journal of Supercomputing
43. Journal of Systems Architecture
44. Journal of the ACM
45. Microprocessors and Microsystems
46. Mobile Networks & Applications
47. Networks
48. New Generation Computing
49. Performance Evaluation
50. Sustainable Computing-Informatics & Systems
51. VLDB Journal

<a id="scie-computer-science-information-systems"></a>

### Computer Science, Information Systems

期刊数：155

1. ACM SIGCOMM Computer Communication Review
2. ACM Transactions on Autonomous and Adaptive Systems
3. ACM Transactions on Computer-Human Interaction
4. ACM Transactions on Database Systems
5. ACM Transactions on Information Systems
6. ACM Transactions on Intelligent Systems and Technology
7. ACM Transactions on Internet Technology
8. ACM Transactions on Knowledge Discovery from Data
9. ACM Transactions on Multimedia Computing Communications and Applications
10. ACM Transactions on Privacy and Security
11. ACM Transactions on Sensor Networks
12. ACM Transactions on the Web
13. Acta Informatica
14. Ad Hoc & Sensor Wireless Networks
15. Ad Hoc Networks
16. Applied Ontology
17. Aslib Journal of Information Management
18. Big Data Research
19. Business & Information Systems Engineering
20. Cluster Computing-the Journal of Networks Software Tools and Applications
21. Cmc-Computers Materials & Continua
22. Computer Communications
23. Computer Journal
24. Computer Networks
25. Computer Science and Information Systems
26. Computer Science Review
27. Computers & Security
28. Data & Knowledge Engineering
29. Data Mining and Knowledge Discovery
30. Data Technologies and Applications
31. Decision Support Systems
32. Discover Computing
33. Distributed and Parallel Databases
34. Egyptian Informatics Journal
35. Electronic Commerce Research and Applications
36. Electronics
37. Engineering Information Technology & Electronic Engineering
38. Enterprise Information Systems
39. European Journal of Information Systems
40. Forensic Science International-Digital Investigation
41. Foundations and Trends in Information Retrieval
42. Frontiers of Computer Science
43. GeoInformatica
44. Human-Centric Computing and Information Sciences
45. ICT Express
46. IEEE Access
47. IEEE Communications Surveys and Tutorials
48. IEEE Internet of Things Journal
49. IEEE Journal of Biomedical and Health Informatics
50. IEEE Latin America Transactions
51. IEEE Multimedia
52. IEEE Network
53. IEEE Pervasive Computing
54. IEEE Security & Privacy
55. IEEE Systems Journal
56. IEEE Transactions on Big Data
57. IEEE Transactions on Cloud Computing
58. IEEE Transactions on Computational Social Systems
59. IEEE Transactions on Control of Network Systems
60. IEEE Transactions on Dependable and Secure Computing
61. IEEE Transactions on Emerging Topics in Computing
62. IEEE Transactions on Information Theory
63. IEEE Transactions on Knowledge and Data Engineering
64. IEEE Transactions on Mobile Computing
65. IEEE Transactions on Multimedia
66. IEEE Transactions on Network and Service Management
67. IEEE Transactions on Services Computing
68. IEEE Transactions on Sustainable Computing
69. IEEE Wireless Communications
70. IEEE Wireless Communications Letters
71. IEICE Transactions on Fundamentals of Electronics Communications and Computer Sciences
72. IEICE Transactions on Information and Systems
73. IET Information Security
74. INFOR
75. Informatica
76. Information & Management
77. Information and Software Technology
78. Information Processing & Management
79. Information Processing Letters
80. Information Sciences
81. Information Systems
82. Information Systems Frontiers
83. Information Systems Management
84. Information Technology and Control
85. Information Technology and Libraries
86. International Arab Journal of Information Technology
87. International Journal of ad Hoc and Ubiquitous Computing
88. International Journal of Computers Communications & Control
89. International Journal of Cooperative Information Systems
90. International Journal of Critical Infrastructure Protection
91. International Journal of Distributed Sensor Networks
92. International Journal of Fuzzy Systems
93. International Journal of Geographical Information Science
94. International Journal of Information Security
95. International Journal of Information Technology & Decision Making
96. International Journal of Medical Informatics
97. International Journal of Network Management
98. International Journal of Sensor Networks
99. International Journal of Web and Grid Services
100. International Journal of Web Services Research
101. Internet of Things
102. Internet Research
103. ISPRS International Journal of Geo-Information
104. IT Professional
105. Journal of Ambient Intelligence and Smart Environments
106. Journal of Chemical Information and Modeling
107. Journal of Cheminformatics
108. Journal of Cloud Computing-Advances Systems and Applications
109. Journal of Communications and Networks
110. Journal of Computer Information Systems
111. Journal of Database Management
112. Journal of Grid Computing
113. Journal of Information Science
114. Journal of Information Science and Engineering
115. Journal of Information Security and Applications
116. Journal of Information Technology
117. Journal of Intelligent Information Systems
118. Journal of Internet Technology
119. Journal of King Saud University Computer and Information Sciences
120. Journal of Management Information Systems
121. Journal of Network and Systems Management
122. Journal of Optical Communications and Networking
123. Journal of Organizational and End User Computing
124. Journal of Organizational Computing and Electronic Commerce
125. Journal of Signal Processing Systems for Signal Image and Video Technology
126. Journal of Strategic Information Systems
127. Journal of the ACM
128. Journal of the American Medical Informatics Association
129. Journal of the Association for Information Science and Technology
130. Journal of the Association for Information Systems
131. Journal of Visual Communication and Image Representation
132. Journal of Web Semantics
133. Knowledge and Information Systems
134. KSII Transactions on Internet and Information Systems
135. Methods of Information in Medicine
136. MIS Quarterly
137. Mobile Networks & Applications
138. Multimedia Systems
139. New Review of Hypermedia and Multimedia
140. Online Information Review
141. Optical Switching and Networking
142. Peer-to-Peer Networking and Applications
143. PeerJ Computer Science
144. Pervasive and Mobile Computing
145. Photonic Network Communications
146. Proceedings of the VLDB Endowment
147. Requirements Engineering
148. Science China-Information Sciences
149. Semantic Web
150. SIGMOD Record
151. Sustainable Computing-Informatics & Systems
152. Tsinghua Science and Technology
153. VLDB Journal
154. Wireless Networks
155. World Wide Web-Internet and Web Information Systems

<a id="scie-computer-science-interdisciplinary-applications"></a>

### Computer Science, Interdisciplinary Applications

期刊数：112

1. ACM Journal on Computing and Cultural Heritage
2. ACM Transactions on Modeling and Computer Simulation
3. Advances in Engineering Software
4. AI Edam-Artificial Intelligence for Engineering Design Analysis and Manufacturing
5. Applicable Algebra in Engineering Communication and Computing
6. Applied Soft Computing
7. Archives of Computational Methods in Engineering
8. Artificial Intelligence and Law
9. Astronomy and Computing
10. Big Data
11. CIN-Computers Informatics Nursing
12. COMPEL-the International Journal for Computation and Mathematics in Electrical and Electronic Engineering
13. Computational and Mathematical Organization Theory
14. Computational Biology and Chemistry
15. Computational Geosciences
16. Computational Linguistics
17. Computational Statistics & Data Analysis
18. Computer Applications in Engineering Education
19. Computer Methods and Programs in Biomedicine
20. Computer Methods in Biomechanics and Biomedical Engineering
21. Computer Music Journal
22. Computer Physics Communications
23. Computer Supported Cooperative Work-the Journal of Collaborative Computing and Work Practices
24. Computer-Aided Civil and Infrastructure Engineering
25. Computers & Chemical Engineering
26. Computers & Education
27. Computers & Electrical Engineering
28. Computers & Fluids
29. Computers & Geosciences
30. Computers & Industrial Engineering
31. Computers & Operations Research
32. Computers & Structures
33. Computers and Concrete
34. Computers and Electronics in Agriculture
35. Computers and Geotechnics
36. Computers in Industry
37. Computing in Science & Engineering
38. Current Computer-Aided Drug Design
39. Earth Science Informatics
40. Electronic Commerce Research and Applications
41. Engineering Computations
42. Engineering with Computers
43. Entertainment Computing
44. Environmental Modelling & Software
45. Forensic Science International-Digital Investigation
46. IEEE Journal of Biomedical and Health Informatics
47. IEEE Transactions on Computational Biology and Bioinformatics
48. IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems
49. IEEE Transactions on Industrial Informatics
50. IEEE Transactions on Learning Technologies
51. IEEE Transactions on Medical Imaging
52. Industrial Management & Data Systems
53. Information Processing in Agriculture
54. INFORMS Journal on Computing
55. Integrated Computer-Aided Engineering
56. International Journal for Numerical Methods in Fluids
57. International Journal of Computational Intelligence Systems
58. International Journal of Computer Integrated Manufacturing
59. International Journal of High Performance Computing Applications
60. International Journal of Information Technology & Decision Making
61. International Journal of Interactive Multimedia and Artificial Intelligence
62. International Journal of Modern Physics C
63. International Journal of RF and Microwave Computer-Aided Engineering
64. International Journal on Artificial Intelligence Tools
65. Journal of Biomedical Informatics
66. Journal of Chemical Information and Modeling
67. Journal of Cheminformatics
68. Journal of Combinatorial Optimization
69. Journal of Computational Biology
70. Journal of Computational Design and Engineering
71. Journal of Computational Physics
72. Journal of Computational Science
73. Journal of Computer-Aided Molecular Design
74. Journal of Computing and Information Science in Engineering
75. Journal of Computing in Civil Engineering
76. Journal of Hydroinformatics
77. Journal of Industrial Information Integration
78. Journal of Informetrics
79. Journal of Molecular Graphics & Modelling
80. Journal of Molecular Modeling
81. Journal of Network and Computer Applications
82. Journal of New Music Research
83. Journal of Organizational Computing and Electronic Commerce
84. Journal of Simulation
85. Journal of Statistical Computation and Simulation
86. Journal of Statistical Software
87. Journal of the American Medical Informatics Association
88. Journal of Visualization
89. Language Resources and Evaluation
90. Machine Learning-Science and Technology
91. Match-Communications in Mathematical and in Computer Chemistry
92. Mathematical and Computer Modelling of Dynamical Systems
93. Mathematics and Computers in Simulation
94. Medical & Biological Engineering & Computing
95. Medical Image Analysis
96. Molecular Informatics
97. Nature Computational Science
98. Nature Machine Intelligence
99. Neuroinformatics
100. Queueing Systems
101. R Journal
102. Robotics and Computer-Integrated Manufacturing
103. SAR and QSAR in Environmental Research
104. Scientometrics
105. Simulation Modelling Practice and Theory
106. Simulation-Transactions of the Society for Modeling and Simulation International
107. Social Science Computer Review
108. Soft Computing
109. Speech Communication
110. Statistical Analysis and Data Mining-an ASA Data Science Journal
111. Structural and Multidisciplinary Optimization
112. Virtual Reality

<a id="scie-computer-science-software-engineering"></a>

### Computer Science, Software Engineering

期刊数：106

1. ACM Transactions on Applied Perception
2. ACM Transactions on Database Systems
3. ACM Transactions on Design Automation of Electronic Systems
4. ACM Transactions on Embedded Computing Systems
5. ACM Transactions on Graphics
6. ACM Transactions on Internet Technology
7. ACM Transactions on Knowledge Discovery from Data
8. ACM Transactions on Mathematical Software
9. ACM Transactions on Multimedia Computing Communications and Applications
10. ACM Transactions on Programming Languages and Systems
11. ACM Transactions on Software Engineering and Methodology
12. ACM Transactions on Storage
13. ACM Transactions on the Web
14. Advances in Engineering Software
15. Algorithmica
16. Automated Software Engineering
17. BIT Numerical Mathematics
18. Communications of the ACM
19. Computational Visual Media
20. Computer
21. Computer Aided Geometric Design
22. Computer Animation and Virtual Worlds
23. Computer Graphics Forum
24. Computer Journal
25. Computer Science and Information Systems
26. Computer Science Review
27. Computer Standards & Interfaces
28. Computer-Aided Design
29. Computers & Graphics-UK
30. Concurrency and Computation-Practice & Experience
31. Design Automation for Embedded Systems
32. Discrete Mathematics and Theoretical Computer Science
33. Empirical Software Engineering
34. Engineering Information Technology & Electronic Engineering
35. Entertainment Computing
36. Formal Aspects of Computing
37. Frontiers of Computer Science
38. Fundamenta Informaticae
39. Graphical Models
40. ICGA Journal
41. IEEE Computer Graphics and Applications
42. IEEE Embedded Systems Letters
43. IEEE Internet Computing
44. IEEE Micro
45. IEEE Multimedia
46. IEEE Security & Privacy
47. IEEE Software
48. IEEE Transactions on Dependable and Secure Computing
49. IEEE Transactions on Games
50. IEEE Transactions on Multimedia
51. IEEE Transactions on Reliability
52. IEEE Transactions on Services Computing
53. IEEE Transactions on Software Engineering
54. IEEE Transactions on Visualization and Computer Graphics
55. IEICE Transactions on Information and Systems
56. IET Software
57. Image and Vision Computing
58. Information and Software Technology
59. Information Visualization
60. International Journal of Data Warehousing and Mining
61. International Journal of Electronic Commerce
62. International Journal of Information Security
63. International Journal of Multimedia Information Retrieval
64. International Journal of Software Engineering and Knowledge Engineering
65. International Journal of Wavelets Multiresolution and Information Processing
66. International Journal of Web and Grid Services
67. International Journal of Web Services Research
68. International Journal on Software Tools for Technology Transfer
69. IT Professional
70. Journal of Computer Languages
71. Journal of Computer Science and Technology
72. Journal of Database Management
73. Journal of Functional Programming
74. Journal of Mathematical Imaging and Vision
75. Journal of Network and Computer Applications
76. Journal of Software-Evolution and Process
77. Journal of Systems and Software
78. Journal of Systems Architecture
79. Journal of the ACM
80. Journal of Universal Computer Science
81. Journal of Visual Communication and Image Representation
82. Journal of Web Engineering
83. Journal of Web Semantics
84. Mathematical Programming
85. Mathematical Programming Computation
86. Mathematics and Computers in Simulation
87. Optimization Methods & Software
88. Presence-Virtual and Augmented Reality
89. Programming and Computer Software
90. Random Structures & Algorithms
91. Requirements Engineering
92. Science of Computer Programming
93. SIAM Journal on Imaging Sciences
94. SIGMOD Record
95. Simulation Modelling Practice and Theory
96. Simulation-Transactions of the Society for Modeling and Simulation International
97. Software and Systems Modeling
98. Software Quality Journal
99. Software Testing Verification & Reliability
100. Software-Practice & Experience
101. SoftwareX
102. Theory and Practice of Logic Programming
103. Tsinghua Science and Technology
104. Virtual Reality
105. Visual Computer
106. World Wide Web-Internet and Web Information Systems

<a id="scie-computer-science-theory-methods"></a>

### Computer Science, Theory & Methods

期刊数：110

1. ACM Computing Surveys
2. ACM Transactions on Algorithms
3. ACM Transactions on Architecture and Code Optimization
4. ACM Transactions on Autonomous and Adaptive Systems
5. ACM Transactions on Computational Logic
6. ACM Transactions on Computer Systems
7. ACM Transactions on Multimedia Computing Communications and Applications
8. Advances in Mathematics of Communications
9. Applicable Algebra in Engineering Communication and Computing
10. Applied Ontology
11. Artificial Life
12. Big Data
13. Big Data Research
14. Cluster Computing-the Journal of Networks Software Tools and Applications
15. Combinatorics Probability and Computing
16. Communications of the ACM
17. Computational Complexity
18. Computer Journal
19. Computer Methods and Programs in Biomedicine
20. Computer Science Review
21. Computing
22. Concurrency and Computation-Practice & Experience
23. Connection Science
24. Constraints
25. Cryptography and Communications-Discrete-Structures Boolean Functions and Sequences
26. Cryptologia
27. Designs Codes and Cryptography
28. Discrete & Computational Geometry
29. Distributed and Parallel Databases
30. Distributed Computing
31. Evolutionary Computation
32. Expert Systems
33. Formal Methods in System Design
34. Foundations of Computational Mathematics
35. Frontiers of Computer Science
36. Future Generation Computer Systems-the International Journal of Escience
37. Fuzzy Sets and Systems
38. Genetic Programming and Evolvable Machines
39. Human-Computer Interaction
40. IEEE Annals of the History of Computing
41. IEEE Multimedia
42. IEEE Transactions on Big Data
43. IEEE Transactions on Cloud Computing
44. IEEE Transactions on Evolutionary Computation
45. IEEE Transactions on Information Forensics and Security
46. IEEE Transactions on Information Theory
47. IEEE Transactions on Networking
48. IEEE Transactions on Neural Networks and Learning Systems
49. IEEE Transactions on Parallel and Distributed Systems
50. IET Computers and Digital Techniques
51. IET Information Security
52. Image and Vision Computing
53. Information and Computation
54. Information Fusion
55. Information Systems Frontiers
56. International Journal of Bio-Inspired Computation
57. International Journal of Foundations of Computer Science
58. International Journal of General Systems
59. International Journal of High Performance Computing Applications
60. International Journal of Information Security
61. International Journal of Parallel Programming
62. International Journal of Quantum Information
63. International Journal of Systems Science
64. International Journal of Unconventional Computing
65. Journal of Big Data
66. Journal of Cellular Automata
67. Journal of Computational Science
68. Journal of Computer and System Sciences
69. Journal of Computer and Systems Sciences International
70. Journal of Cryptographic Engineering
71. Journal of Cryptology
72. Journal of Grid Computing
73. Journal of Heuristics
74. Journal of Logic and Computation
75. Journal of Logical and Algebraic Methods in Programming
76. Journal of Multiple-Valued Logic and Soft Computing
77. Journal of Parallel and Distributed Computing
78. Journal of Supercomputing
79. Journal of Symbolic Computation
80. Journal of Systems and Software
81. Journal of the ACM
82. Journal of Universal Computer Science
83. Journal of Web Engineering
84. Logical Methods in Computer Science
85. Malaysian Journal of Computer Science
86. Mathematical Structures in Computer Science
87. Microprocessors and Microsystems
88. Multidimensional Systems and Signal Processing
89. Multimedia Systems
90. Natural Computing
91. Nature Computational Science
92. New Generation Computing
93. Parallel Computing
94. PeerJ Computer Science
95. Performance Evaluation
96. Problems of Information Transmission
97. Proceedings of the VLDB Endowment
98. Quantum Information & Computation
99. RAIRO-Theoretical Informatics and Applications
100. Real-Time Systems
101. Romanian Journal of Information Science and Technology
102. Semantic Web
103. SIAM Journal on Computing
104. Statistics and Computing
105. Swarm and Evolutionary Computation
106. Theoretical Computer Science
107. Theory and Practice of Logic Programming
108. Theory of Computing
109. Theory of Computing Systems
110. Wiley Interdisciplinary Reviews-Data Mining and Knowledge Discovery

<a id="scie-construction-building-technology"></a>

### Construction & Building Technology

期刊数：68

1. ACI Materials Journal
2. ACI Structural Journal
3. Advanced Steel Construction
4. Advances in Cement Research
5. Advances in Civil Engineering
6. Advances in Concrete Construction
7. Advances in Structural Engineering
8. Architectural Engineering and Design Management
9. Ashrae Journal
10. Automation in Construction
11. Bauingenieur
12. Bauphysik
13. Beton- und Stahlbetonbau
14. Building and Environment
15. Building Research and Information
16. Building Services Engineering Research & Technology
17. Building Simulation
18. Buildings
19. Case Studies in Construction Materials
20. Cement & Concrete Composites
21. Cement and Concrete Research
22. Cement Wapno Beton
23. Computer-Aided Civil and Infrastructure Engineering
24. Computers and Concrete
25. Construction and Building Materials
26. Developments in the Built Environment
27. Energy and Buildings
28. Engineering Journal-American Institute of Steel Construction
29. Indoor Air
30. Indoor and Built Environment
31. Informes de la Construccion
32. International Journal of Architectural Heritage
33. International Journal of Concrete Structures and Materials
34. International Journal of Pavement Engineering
35. International Journal of Steel Structures
36. International Journal of Ventilation
37. Journal of Advanced Concrete Technology
38. Journal of Asian Architecture and Building Engineering
39. Journal of Building Engineering
40. Journal of Building Performance Simulation
41. Journal of Building Physics
42. Journal of Construction Engineering and Management
43. Journal of Constructional Steel Research
44. Journal of Materials in Civil Engineering
45. Journal of Performance of Constructed Facilities
46. Journal of Structural Engineering
47. Journal of Sustainable Cement-Based Materials
48. Leukos
49. Lighting Research & Technology
50. Magazine of Concrete Research
51. Materiales de Construccion
52. Materials and Structures
53. PCI Journal
54. Proceedings of the Institution of Civil Engineers-Structures and Buildings
55. Revista de la Construccion
56. Revista Romana de Materiale-Romanian Journal of Materials
57. Road Materials and Pavement Design
58. Science and Technology for the Built Environment
59. Stahlbau
60. Steel and Composite Structures
61. Structural Concrete
62. Structural Control & Health Monitoring
63. Structural Design of Tall and Special Buildings
64. Structural Engineering International
65. Sustainable Cities and Society
66. Tunnelling and Underground Space Technology
67. Wind and Structures
68. ZKG International

<a id="scie-critical-care-medicine"></a>

### Critical Care Medicine

期刊数：37

1. American Journal of Critical Care
2. American Journal of Respiratory and Critical Care Medicine
3. Anaesthesia and Intensive Care
4. Anaesthesia Critical Care & Pain Medicine
5. Anasthesiologie & Intensivmedizin
6. Anasthesiologie Intensivmedizin Notfallmedizin Schmerztherapie
7. Annals of Intensive Care
8. Australian Critical Care
9. Burns
10. Chest
11. Critical Care
12. Critical Care and Resuscitation
13. Critical Care Clinics
14. Critical Care Medicine
15. Critical Care Nurse
16. Current Opinion in Critical Care
17. European Heart Journal-Acute Cardiovascular Care
18. Injury-International Journal of the Care of the Injured
19. Intensive and Critical Care Nursing
20. Intensive Care Medicine
21. Journal of Burn Care & Research
22. Journal of Critical Care
23. Journal of Intensive Care
24. Journal of Intensive Care Medicine
25. Journal of Neurotrauma
26. Journal of Trauma and Acute Care Surgery
27. Journal of Trauma Nursing
28. Lancet Respiratory Medicine
29. Medicina Intensiva
30. Minerva Anestesiologica
31. Neurocritical Care
32. Pediatric Critical Care Medicine
33. Respiratory Care
34. Resuscitation
35. Seminars in Respiratory and Critical Care Medicine
36. Shock
37. Therapeutic Hypothermia and Temperature Management

<a id="scie-crystallography"></a>

### Crystallography

期刊数：26

1. Acta Crystallographica A-Foundation and Advances
2. Acta Crystallographica Section B-Structural Science Crystal Engineering and Materials
3. Acta Crystallographica Section C-Structural Chemistry
4. Acta Crystallographica Section D-Structural Biology
5. Acta Crystallographica Section F-Structural Biology Communications
6. Chinese Journal of Structural Chemistry
7. Crystal Growth & Design
8. Crystal Research and Technology
9. Crystallography Reports
10. Crystallography Reviews
11. Crystals
12. CrystEngComm
13. IUCrJ
14. Journal of Applied Crystallography
15. Journal of Chemical Crystallography
16. Journal of Crystal Growth
17. Journal of Molecular Graphics & Modelling
18. Liquid Crystals
19. Liquid Crystals Reviews
20. Molecular Crystals and Liquid Crystals
21. Phase Transitions
22. Polyhedron
23. Progress in Crystal Growth and Characterization of Materials
24. Structural Chemistry
25. Zeitschrift für Kristallographie-Crystalline Materials
26. Zeitschrift für Kristallographie-New Crystal Structures

<a id="scie-dentistry-oral-surgery-medicine"></a>

### Dentistry, Oral Surgery & Medicine

期刊数：91

1. Acta Odontologica Scandinavica
2. American Journal of Dentistry
3. American Journal of Orthodontics and Dentofacial Orthopedics
4. Angle Orthodontist
5. Archives of Oral Biology
6. Australasian Orthodontic Journal
7. Australian Dental Journal
8. Australian Endodontic Journal
9. BMC Oral Health
10. Brazilian Oral Research
11. British Dental Journal
12. British Journal of Oral & Maxillofacial Surgery
13. Caries Research
14. Cleft Palate Craniofacial Journal
15. Clinical Implant Dentistry and Related Research
16. Clinical Oral Implants Research
17. Clinical Oral Investigations
18. Community Dental Health
19. Community Dentistry and Oral Epidemiology
20. Cranio-the Journal of Craniomandibular & Sleep Practice
21. Dental Materials
22. Dental Materials Journal
23. Dental Traumatology
24. Dentomaxillofacial Radiology
25. European Journal of Dental Education
26. European Journal of Oral Sciences
27. European Journal of Orthodontics
28. European Journal of Paediatric Dentistry
29. Gerodontology
30. Head & Face Medicine
31. Implantologie
32. International Dental Journal
33. International Endodontic Journal
34. International Journal of Computerized Dentistry
35. International Journal of Dental Hygiene
36. International Journal of Implant Dentistry
37. International Journal of Oral & Maxillofacial Implants
38. International Journal of Oral and Maxillofacial Surgery
39. International Journal of Oral Implantology
40. International Journal of Oral Science
41. International Journal of Paediatric Dentistry
42. International Journal of Periodontics & Restorative Dentistry
43. International Journal of Prosthodontics
44. Japanese Dental Science Review
45. Journal of Adhesive Dentistry
46. Journal of Advanced Prosthodontics
47. Journal of Applied Oral Science
48. Journal of Clinical Pediatric Dentistry
49. Journal of Clinical Periodontology
50. Journal of Cranio-Maxillofacial Surgery
51. Journal of Dental Education
52. Journal of Dental Research
53. Journal of Dental Sciences
54. Journal of Dentistry
55. Journal of Endodontics
56. Journal of Esthetic and Restorative Dentistry
57. Journal of Evidence-Based Dental Practice
58. Journal of Oral & Facial Pain and Headache
59. Journal of Oral and Maxillofacial Surgery
60. Journal of Oral Implantology
61. Journal of Oral Pathology & Medicine
62. Journal of Oral Rehabilitation
63. Journal of Oral Science
64. Journal of Orofacial Orthopedics-Fortschritte der Kieferorthopadie
65. Journal of Periodontal and Implant Science
66. Journal of Periodontal Research
67. Journal of Periodontology
68. Journal of Prosthetic Dentistry
69. Journal of Prosthodontic Research
70. Journal of Prosthodontics-Implant Esthetic and Reconstructive Dentistry
71. Journal of Public Health Dentistry
72. Journal of Stomatology Oral and Maxillofacial Surgery
73. Journal of the American Dental Association
74. Journal of the Canadian Dental Association
75. Korean Journal of Orthodontics
76. Medicina Oral Patologia Oral y Cirugia Bucal
77. Molecular Oral Microbiology
78. Odontology
79. Operative Dentistry
80. Oral and Maxillofacial Surgery Clinics of North America
81. Oral Diseases
82. Oral Health & Preventive Dentistry
83. Oral Oncology
84. Oral Radiology
85. Oral Surgery Oral Medicine Oral Pathology Oral Radiology
86. Orthodontics & Craniofacial Research
87. Pediatric Dentistry
88. Periodontology 2000
89. Progress in Orthodontics
90. Quintessence International
91. Seminars in Orthodontics

<a id="scie-dermatology"></a>

### Dermatology

期刊数：69

1. Acta Dermato-Venereologica
2. Acta Dermatovenerologica Croatica
3. Advances in Skin & Wound Care
4. Advances in Wound Care
5. American Journal of Clinical Dermatology
6. American Journal of Dermatopathology
7. Anais Brasileiros de Dermatologia
8. Annales de Dermatologie et de Venereologie
9. Annals of Dermatology
10. Archives of Dermatological Research
11. Australasian Journal of Dermatology
12. British Journal of Dermatology
13. Burns
14. Burns & Trauma
15. Clinical and Experimental Dermatology
16. Clinical Cosmetic and Investigational Dermatology
17. Clinics in Dermatology
18. Contact Dermatitis
19. Cutis
20. Dermatitis
21. Dermatologic Clinics
22. Dermatologic Surgery
23. Dermatologic Therapy
24. Dermatologica Sinica
25. Dermatologie
26. Dermatology
27. Dermatology and Therapy
28. Dermatology Practical & Conceptual
29. European Journal of Dermatology
30. Experimental Dermatology
31. Hong Kong Journal of Dermatology & Venereology
32. Indian Journal of Dermatology
33. Indian Journal of Dermatology Venereology & Leprology
34. International Journal of Cosmetic Science
35. International Journal of Dermatology
36. International Journal of Lower Extremity Wounds
37. International Wound Journal
38. Italian Journal of Dermatology and Venereology
39. JAMA Dermatology
40. Journal der Deutschen Dermatologischen Gesellschaft
41. Journal of Burn Care & Research
42. Journal of Cosmetic and Laser Therapy
43. Journal of Cosmetic Dermatology
44. Journal of Cosmetic Science
45. Journal of Cutaneous Medicine and Surgery
46. Journal of Cutaneous Pathology
47. Journal of Dermatological Science
48. Journal of Dermatological Treatment
49. Journal of Dermatology
50. Journal of Drugs in Dermatology
51. Journal of Investigative Dermatology
52. Journal of the American Academy of Dermatology
53. Journal of the European Academy of Dermatology and Venereology
54. Journal of Tissue Viability
55. Journal of Wound Care
56. Lasers in Surgery and Medicine
57. Leprosy Review
58. Melanoma Research
59. Mycoses
60. Pediatric Dermatology
61. Photodermatology Photoimmunology & Photomedicine
62. Pigment Cell & Melanoma Research
63. Postepy Dermatologii i Alergologii
64. Skin Pharmacology and Physiology
65. Skin Research and Technology
66. Veterinary Dermatology
67. Wound Management & Prevention
68. Wound Repair and Regeneration
69. Wounds-A Compendium of Clinical Research and Practice

<a id="scie-developmental-biology"></a>

### Developmental Biology

期刊数：38

1. Annual Review of Cell and Developmental Biology
2. Birth Defects Research
3. Cells & Development
4. Cells Tissues Organs
5. Development
6. Development Growth & Differentiation
7. Developmental Biology
8. Developmental Biology Advances
9. Developmental Cell
10. Developmental Dynamics
11. Developmental Neurobiology
12. Developmental Neuroscience
13. Developmental Psychobiology
14. Differentiation
15. Discover Developmental Biology
16. Discover Neuroscience
17. Evolution & Development
18. Frontiers in Cell and Developmental Biology
19. Gene Expression Patterns
20. Genes & Development
21. Genesis
22. In Vitro Cellular & Developmental Biology-Animal
23. In Vitro Cellular & Developmental Biology-Plant
24. International Journal of Developmental Biology
25. International Journal of Developmental Neuroscience
26. Journal of Experimental Zoology Part B-Molecular and Developmental Evolution
27. Molecular Human Reproduction
28. Molecular Reproduction and Development
29. Organogenesis
30. Placenta
31. Reproduction
32. Reproduction Fertility and Development
33. Romanian Journal of Morphology and Embryology
34. Russian Journal of Developmental Biology
35. Seminars in Cell & Developmental Biology
36. Sexual Development
37. Zebrafish
38. Zygote

<a id="scie-ecology"></a>

### Ecology

期刊数：171

1. Acta Amazonica
2. Acta Oecologica-International Journal of Ecology
3. African Journal of Ecology
4. African Journal of Range & Forage Science
5. African Journal of Wildlife Research
6. Agriculture Ecosystems & Environment
7. American Naturalist
8. Animal Biotelemetry
9. Animal Conservation
10. Annales Zoologici Fennici
11. Annual Review of Ecology Evolution and Systematics
12. AoB Plants
13. Applied Ecology and Environmental Research
14. Applied Vegetation Science
15. Aquatic Ecology
16. Aquatic Invasions
17. Aquatic Microbial Ecology
18. Arctic Science
19. Austral Ecology
20. Basic and Applied Ecology
21. Behavioral Ecology
22. Behavioral Ecology and Sociobiology
23. Biochemical Systematics and Ecology
24. Biodiversity and Conservation
25. Biogeosciences
26. Biological Conservation
27. Biological Invasions
28. Biology Letters
29. Biotropica
30. BMC Ecology and Evolution
31. Bulletin of the American Museum of Natural History
32. Bulletin of the Peabody Museum of Natural History
33. Chemistry and Ecology
34. Community Ecology
35. Compost Science & Utilization
36. Conservation Biology
37. Conservation Physiology
38. Contemporary Problems of Ecology
39. Current Opinion in Insect Science
40. Diversity and Distributions
41. Diversity-Basel
42. Eco Mont-Journal on Protected Mountain Areas Research
43. Ecography
44. Ecohydrology
45. Ecohydrology & Hydrobiology
46. Ecological Applications
47. Ecological Complexity
48. Ecological Economics
49. Ecological Engineering
50. Ecological Informatics
51. Ecological Management & Restoration
52. Ecological Modelling
53. Ecological Monographs
54. Ecological Processes
55. Ecological Research
56. Ecological Restoration
57. Ecology
58. Ecology and Evolution
59. Ecology and Society
60. Ecology Letters
61. Ecoscience
62. Ecosphere
63. Ecosystem Health and Sustainability
64. Ecosystem Services
65. Ecosystems
66. Ecotoxicology
67. Environmental Biology of Fishes
68. European Journal of Soil Biology
69. European Journal of Wildlife Research
70. Evolution
71. Evolutionary Ecology
72. Fire Ecology
73. Fire-Switzerland
74. Flora
75. Food Webs
76. Freshwater Biology
77. Freshwater Science
78. Frontiers in Ecology and Evolution
79. Frontiers in Ecology and the Environment
80. Frontiers in Forests and Global Change
81. Functional Ecology
82. Fungal Ecology
83. Global Change Biology
84. Global Ecology and Biogeography
85. Global Ecology and Conservation
86. Heredity
87. Human-Wildlife Interactions
88. Interciencia
89. International Journal for Parasitology-Parasites and Wildlife
90. International Journal of Sustainable Development and World Ecology
91. International Journal of Wildland Fire
92. ISME Journal
93. Israel Journal of Ecology & Evolution
94. Journal for Nature Conservation
95. Journal of Animal Ecology
96. Journal of Applied Ecology
97. Journal of Arid Environments
98. Journal of Biogeography
99. Journal of Biological Dynamics
100. Journal of Chemical Ecology
101. Journal of Ecology
102. Journal of Evolutionary Biology
103. Journal of Experimental Marine Biology and Ecology
104. Journal of Fish and Wildlife Management
105. Journal of Freshwater Ecology
106. Journal of Natural History
107. Journal of Plant Ecology
108. Journal of Soil and Water Conservation
109. Journal of Tropical Ecology
110. Journal of Vegetation Science
111. Journal of Wildlife Management
112. Landscape and Ecological Engineering
113. Landscape and Urban Planning
114. Landscape Ecology
115. Mammal Review
116. Marine Biology Research
117. Marine Ecology Progress Series
118. Methods in Ecology and Evolution
119. Microbial Ecology
120. Molecular Ecology
121. Molecular Ecology Resources
122. Movement Ecology
123. Natural Areas Journal
124. Natural History
125. Nature Ecology & Evolution
126. NeoBiota
127. New Zealand Journal of Ecology
128. Northeastern Naturalist
129. Northwest Science
130. Oecologia
131. Oikos
132. Oryx
133. Paleobiology
134. Pedobiologia
135. People and Nature
136. Perspectives in Plant Ecology Evolution and Systematics
137. Phytocoenologia
138. Plant Ecology
139. Plant Species Biology
140. Plants People Planet
141. Polar Biology
142. Polar Record
143. Polar Research
144. Polar Science
145. Polish Journal of Ecology
146. Polish Polar Research
147. Population Ecology
148. Proceedings of the Academy of Natural Sciences of Philadelphia
149. Proceedings of the Linnean Society of New South Wales
150. Proceedings of the Royal Society B-Biological Sciences
151. Rangeland Ecology & Management
152. Rangeland Journal
153. Regional Studies in Marine Science
154. Remote Sensing in Ecology and Conservation
155. Restoration Ecology
156. Revista Chilena de Historia Natural
157. Russian Journal of Ecology
158. Southeastern Naturalist
159. Southwestern Naturalist
160. Theoretical Ecology
161. Theoretical Population Biology
162. Trends in Ecology & Evolution
163. Tropical Ecology
164. Urban Ecosystems
165. Vie et Milieu-Life and Environment
166. Web Ecology
167. Western North American Naturalist
168. Wetlands
169. Wildlife Biology
170. Wildlife Monographs
171. Wildlife Research

<a id="scie-education-scientific-disciplines"></a>

### Education, Scientific Disciplines

期刊数：44

1. Academic Medicine
2. ACM Transactions on Computing Education
3. Advances in Health Sciences Education
4. Advances in Physiology Education
5. American Biology Teacher
6. American Journal of Pharmaceutical Education
7. American Journal of Physics
8. Anatomical Sciences Education
9. Biochemistry and Molecular Biology Education
10. BMC Medical Education
11. CBE-Life Sciences Education
12. Chemistry Education Research and Practice
13. Computer Applications in Engineering Education
14. Education for Chemical Engineers
15. Engineering Studies
16. European Journal of Dental Education
17. European Journal of Physics
18. Hematology-American Society of Hematology Education Program
19. IEEE Transactions on Education
20. Indian Journal of Pharmaceutical Education and Research
21. International Journal of Engineering Education
22. International Journal of STEM Education
23. International Journal of Technology and Design Education
24. JMIR Medical Education
25. Journal of Biological Education
26. Journal of Cancer Education
27. Journal of Chemical Education
28. Journal of Civil Engineering Education
29. Journal of Continuing Education in the Health Professions
30. Journal of Engineering Education
31. Journal of Materials Education
32. Journal of Nutrition Education and Behavior
33. Journal of School Health
34. Journal of Science Education and Technology
35. Journal of Surgical Education
36. Journal of Veterinary Medical Education
37. Medical Education
38. Medical Teacher
39. Nurse Education Today
40. Perspectives on Medical Education
41. Physical Review Physics Education Research
42. Physics Teacher
43. Studies in Science Education
44. Teaching and Learning in Medicine

<a id="scie-electrochemistry"></a>

### Electrochemistry

期刊数：31

1. ACS Energy Letters
2. Batteries & Supercaps
3. Batteries-Basel
4. Bioelectrochemistry
5. Biosensors & Bioelectronics
6. ChemElectroChem
7. Chemosensors
8. Corrosion Reviews
9. Current Opinion in Electrochemistry
10. Electroanalysis
11. Electrocatalysis
12. Electrochemical Energy Reviews
13. Electrochemistry
14. Electrochemistry Communications
15. Electrochimica Acta
16. eScience
17. Fuel Cells
18. International Journal of Electrochemical Science
19. International Journal of Hydrogen Energy
20. Ionics
21. Journal of Applied Electrochemistry
22. Journal of Electroanalytical Chemistry
23. Journal of Electrochemical Energy Conversion and Storage
24. Journal of Electrochemical Science and Technology
25. Journal of Power Sources
26. Journal of Solid State Electrochemistry
27. Journal of the Electrochemical Society
28. Russian Journal of Electrochemistry
29. Sensors and Actuators B-Chemical
30. Sensors and Actuators Reports
31. Transactions of the Institute of Metal Finishing

<a id="scie-emergency-medicine"></a>

### Emergency Medicine

期刊数：31

1. Academic Emergency Medicine
2. African Journal of Emergency Medicine
3. American Journal of Emergency Medicine
4. Annals of Emergency Medicine
5. Australasian Emergency Care
6. BMC Emergency Medicine
7. Burns & Trauma
8. Canadian Journal of Emergency Medicine
9. Emergencias
10. Emergency Medicine Australasia
11. Emergency Medicine Clinics of North America
12. Emergency Medicine International
13. Emergency Medicine Journal
14. European Journal of Emergency Medicine
15. European Journal of Trauma and Emergency Surgery
16. Hong Kong Journal of Emergency Medicine
17. Injury-International Journal of the Care of the Injured
18. Journal of Emergency Medicine
19. Journal of Emergency Nursing
20. Notarzt
21. Notfall & Rettungsmedizin
22. Pediatric Emergency Care
23. Prehospital and Disaster Medicine
24. Prehospital Emergency Care
25. Resuscitation
26. Scandinavian Journal of Trauma Resuscitation & Emergency Medicine
27. Ulusal Travma ve Acil Cerrahi Dergisi-Turkish Journal of Trauma & Emergency Surgery
28. Unfallchirurgie
29. Western Journal of Emergency Medicine
30. World Journal of Emergency Medicine
31. World Journal of Emergency Surgery

<a id="scie-endocrinology-metabolism"></a>

### Endocrinology & Metabolism

期刊数：142

1. Acta Diabetologica
2. Acta Endocrinologica-Bucharest
3. Adipocyte
4. Aging Male
5. American Journal of Physiology-Endocrinology and Metabolism
6. Annales d Endocrinologie
7. Annals of Nutrition and Metabolism
8. Antioxidants & Redox Signaling
9. Archives of Endocrinology Metabolism
10. Archives of Osteoporosis
11. Archives of Physiology and Biochemistry
12. Best Practice & Research Clinical Endocrinology & Metabolism
13. BioFactors
14. Biological Trace Element Research
15. Biology of Sex Differences
16. BMC Endocrine Disorders
17. BMJ Open Diabetes Research & Care
18. Bone
19. Calcified Tissue International
20. Canadian Journal of Diabetes
21. Cardiovascular Diabetology
22. Cell Metabolism
23. Clinical Endocrinology
24. Comparative Biochemistry and Physiology C-Toxicology & Pharmacology
25. Correspondances en Metabolismes Hormones Diabetes et Nutrition
26. Current Diabetes Reports
27. Current Obesity Reports
28. Current Opinion in Clinical Nutrition and Metabolic Care
29. Current Opinion in Endocrinology Diabetes and Obesity
30. Current Opinion in Lipidology
31. Current Osteoporosis Reports
32. Diabetes
33. Diabetes & Metabolism
34. Diabetes & Metabolism Journal
35. Diabetes & Vascular Disease Research
36. Diabetes Care
37. Diabetes Metabolic Syndrome and Obesity
38. Diabetes Obesity & Metabolism
39. Diabetes Research and Clinical Practice
40. Diabetes Stoffwechsel und Herz
41. Diabetes Technology & Therapeutics
42. Diabetes Therapy
43. Diabetes-Metabolism Research and Reviews
44. Diabetic Medicine
45. Diabetologia
46. Diabetologie
47. Diabetologie und Stoffwechsel
48. Diabetology & Metabolic Syndrome
49. Discover Oncology
50. Domestic Animal Endocrinology
51. Endocrine
52. Endocrine Connections
53. Endocrine Journal
54. Endocrine Metabolic & Immune Disorders-Drug Targets
55. Endocrine Pathology
56. Endocrine Practice
57. Endocrine Research
58. Endocrine Reviews
59. Endocrine-Related Cancer
60. Endocrinologia Diabetes y Nutricion
61. Endocrinology
62. Endocrinology and Metabolism
63. Endocrinology and Metabolism Clinics of North America
64. Endokrynologia Polska
65. European Journal of Endocrinology
66. European Thyroid Journal
67. Experimental and Clinical Endocrinology & Diabetes
68. Free Radical Biology and Medicine
69. Frontiers in Endocrinology
70. Frontiers in Neuroendocrinology
71. General and Comparative Endocrinology
72. Growth Factors
73. Growth Hormone & IGF Research
74. Gynecological Endocrinology
75. Hormone and Metabolic Research
76. Hormone Research in Paediatrics
77. Hormones and Behavior
78. Hormones-International Journal of Endocrinology and Metabolism
79. International Journal of Diabetes in Developing Countries
80. International Journal of Endocrinology
81. International Journal of Obesity
82. Islets
83. Journal of Bone and Mineral Metabolism
84. Journal of Bone and Mineral Research
85. Journal of Cerebral Blood Flow and Metabolism
86. Journal of Clinical Densitometry
87. Journal of Clinical Endocrinology & Metabolism
88. Journal of Clinical Research in Pediatric Endocrinology
89. Journal of Diabetes
90. Journal of Diabetes and Its Complications
91. Journal of Diabetes Investigation
92. Journal of Diabetes Research
93. Journal of Endocrinological Investigation
94. Journal of Endocrinology
95. Journal of Inherited Metabolic Disease
96. Journal of Mammary Gland Biology and Neoplasia
97. Journal of Molecular Endocrinology
98. Journal of Neuroendocrinology
99. Journal of Pediatric Endocrinology & Metabolism
100. Journal of Pineal Research
101. Journal of Steroid Biochemistry and Molecular Biology
102. Journal of Trace Elements in Medicine and Biology
103. Lancet Diabetes & Endocrinology
104. Magnesium Research
105. Metabolic Brain Disease
106. Metabolism-Clinical and Experimental
107. Metabolomics
108. Minerva Endocrinology
109. Molecular and Cellular Endocrinology
110. Molecular Genetics and Metabolism
111. Molecular Metabolism
112. Nature Metabolism
113. Nature Reviews Endocrinology
114. Neuroendocrinology
115. Neuroendocrinology Letters
116. NeuroImmunoModulation
117. Neuropeptides
118. Nutrition & Diabetes
119. Nutrition Clinique et Metabolisme
120. Nutrition Metabolism and Cardiovascular Diseases
121. Obesity
122. Obesity Facts
123. Obesity Research & Clinical Practice
124. Obesity Reviews
125. Osteoporosis International
126. Pediatric Diabetes
127. Peptides
128. Pituitary
129. Primary Care Diabetes
130. Prostaglandins Leukotrienes and Essential Fatty Acids
131. Prostate
132. Psychoneuroendocrinology
133. Reproductive Biology and Endocrinology
134. Reviews in Endocrine & Metabolic Disorders
135. Science of Diabetes Self-Management and Care
136. Steroids
137. Stress-the International Journal on the Biology of Stress
138. Therapeutic Advances in Endocrinology and Metabolism
139. Thyroid
140. Trace Elements and Electrolytes
141. Trends in Endocrinology and Metabolism
142. World Journal of Diabetes

<a id="scie-energy-fuels"></a>

### Energy & Fuels

期刊数：119

1. ACS Applied Energy Materials
2. ACS Energy Letters
3. Advanced Energy Materials
4. Applied Energy
5. Applied Thermal Engineering
6. Batteries-Basel
7. BioEnergy Research
8. Biofuels Bioproducts & Biorefining-Biofpr
9. Biofuels-UK
10. Biomass & Bioenergy
11. Biomass Conversion and Biorefinery
12. Bioresource Technology
13. Biotechnology for Biofuels and Bioproducts
14. Carbon and Hydrogen
15. Carbon Energy
16. Cell Reports Physical Science
17. Chemical Engineering and Processing-Process Intensification
18. Chemistry and Technology of Fuels and Oils
19. Combustion and Flame
20. Combustion Explosion and Shock Waves
21. Combustion Science and Technology
22. Combustion Theory and Modelling
23. CSEE Journal of Power and Energy Systems
24. CT&F-Ciencia Tecnologia y Futuro
25. Energies
26. Energy
27. Energy & Environmental Science
28. Energy & Fuels
29. Energy and Buildings
30. Energy Conversion and Management
31. Energy Efficiency
32. Energy Exploration & Exploitation
33. Energy for Sustainable Development
34. Energy Journal
35. Energy Policy
36. Energy Reports
37. Energy Science & Engineering
38. Energy Sources Part A-Recovery Utilization and Environmental Effects
39. Energy Sources Part B-Economics Planning and Policy
40. Energy Strategy Reviews
41. Energy Sustainability and Society
42. Energy Technology
43. Engineering Energy
44. eTransportation
45. Frontiers in Energy Research
46. Fuel
47. Fuel Cells
48. Fuel Processing Technology
49. Gas Science and Engineering
50. Geoenergy Science and Engineering
51. Geomechanics and Geophysics for Geo-Energy and Geo-Resources
52. Geomechanics for Energy and the Environment
53. Geothermal Energy
54. Geothermics
55. Global Change Biology Bioenergy
56. Green Energy & Environment
57. Greenhouse Gases-Science and Technology
58. IEEE Journal of Photovoltaics
59. IEEE Transactions on Energy Conversion
60. IEEE Transactions on Sustainable Energy
61. IET Renewable Power Generation
62. International Journal of Coal Geology
63. International Journal of Coal Preparation and Utilization
64. International Journal of Coal Science & Technology
65. International Journal of Energy Research
66. International Journal of Exergy
67. International Journal of Green Energy
68. International Journal of Greenhouse Gas Control
69. International Journal of Hydrogen Energy
70. International Journal of Low-Carbon Technologies
71. International Journal of Oil Gas and Coal Technology
72. International Journal of Photoenergy
73. International Journal of Ventilation
74. Joule
75. Journal of Analytical and Applied Pyrolysis
76. Journal of Electrochemical Energy Conversion and Storage
77. Journal of Energy Chemistry
78. Journal of Energy Engineering
79. Journal of Energy in Southern Africa
80. Journal of Energy Resources Technology Part A-Sustainable and Renewable Energy
81. Journal of Energy Resources Technology Part B-Subsurface Energy and Carbon Capture
82. Journal of Energy Storage
83. Journal of Materials Chemistry A
84. Journal of Petroleum Exploration and Production Technology
85. Journal of Physics-Energy
86. Journal of Pipeline Science and Engineering
87. Journal of Power Sources
88. Journal of Renewable and Sustainable Energy
89. Journal of Solar Energy Engineering-Transactions of the ASME
90. Journal of the Energy Institute
91. Journal of the Japan Petroleum Institute
92. Materials Today Energy
93. Nature Energy
94. Oil Shale
95. Petroleum Chemistry
96. Petroleum Exploration and Development
97. Petroleum Science
98. Petroleum Science and Technology
99. Proceedings of the Combustion Institute
100. Proceedings of the Institution of Civil Engineers-Energy
101. Progress in Energy and Combustion Science
102. Progress in Photovoltaics
103. Protection and Control of Modern Power Systems
104. Renewable & Sustainable Energy Reviews
105. Renewable Energy
106. Science and Technology for Energy Transition
107. Solar Energy
108. Solar Energy Materials and Solar Cells
109. Solar RRL
110. Solid Fuel Chemistry
111. Sustainable Cities and Society
112. Sustainable Energy & Fuels
113. Sustainable Energy Grids & Networks
114. Sustainable Energy Technologies and Assessments
115. Sustainable Materials and Technologies
116. Thermal Science and Engineering Progress
117. Utilities Policy
118. Wiley Interdisciplinary Reviews-Energy and Environment
119. Wind Energy

<a id="scie-engineering-aerospace"></a>

### Engineering, Aerospace

期刊数：36

1. Acta Astronautica
2. Advances in Space Research
3. Aeronautical Journal
4. Aerospace
5. Aerospace America
6. Aerospace Science and Technology
7. AIAA Journal
8. Aircraft Engineering and Aerospace Technology
9. Chinese Journal of Aeronautics
10. Cosmic Research
11. IEEE Aerospace and Electronic Systems Magazine
12. IEEE Transactions on Aerospace and Electronic Systems
13. International Journal of Aeroacoustics
14. International Journal of Aeronautical and Space Sciences
15. International Journal of Aerospace Engineering
16. International Journal of Micro Air Vehicles
17. International Journal of Satellite Communications and Networking
18. International Journal of Turbo & Jet-Engines
19. Journal of Aerospace Engineering
20. Journal of Aerospace Information Systems
21. Journal of Aircraft
22. Journal of Astronomical Telescopes Instruments and Systems
23. Journal of Guidance Control and Dynamics
24. Journal of Propulsion and Power
25. Journal of Spacecraft and Rockets
26. Journal of the American Helicopter Society
27. Journal of the Astronautical Sciences
28. Microgravity Science and Technology
29. Navigation-Journal of the Institute of Navigation
30. Proceedings of the Institution of Mechanical Engineers Part G-Journal of Aerospace Engineering
31. Progress in Aerospace Sciences
32. Propulsion and Power Research
33. Satellite Navigation
34. Space-Science & Technology
35. Thermophysics and Aeromechanics
36. Transactions of the Japan Society for Aeronautical and Space Sciences

<a id="scie-engineering-biomedical"></a>

### Engineering, Biomedical

期刊数：99

1. Acta Biomaterialia
2. Acta of Bioengineering and Biomechanics
3. Advanced Healthcare Materials
4. Annals of Biomedical Engineering
5. Annual Review of Biomedical Engineering
6. APL Bioengineering
7. Applied Bionics and Biomechanics
8. Artificial Cells Nanomedicine and Biotechnology
9. Artificial Intelligence in Medicine
10. Artificial Organs
11. ASAIO Journal
12. Bio-Design and Manufacturing
13. Bio-Medical Materials and Engineering
14. Bioactive Materials
15. Biocybernetics and Biomedical Engineering
16. Bioengineering & Translational Medicine
17. Bioengineering-Basel
18. Biofabrication
19. Bioinspired Biomimetic and Nanobiomaterials
20. Biomaterials
21. Biomaterials Research
22. Biomechanics and Modeling in Mechanobiology
23. Biomedical Engineering Letters
24. BioMedical Engineering OnLine
25. Biomedical Engineering-Biomedizinische Technik
26. Biomedical Materials
27. Biomedical Microdevices
28. Biomedical Signal Processing and Control
29. Biorheology
30. Cardiovascular Engineering and Technology
31. Cell and Tissue Banking
32. Cellular and Molecular Bioengineering
33. Clinical Biomechanics
34. Clinical Oral Implants Research
35. Computer Methods and Programs in Biomedicine
36. Computer Methods in Biomechanics and Biomedical Engineering
37. Computerized Medical Imaging and Graphics
38. Current Opinion in Biomedical Engineering
39. Cyborg and Bionic Systems
40. European Cells & Materials
41. Expert Review of Medical Devices
42. Frontiers in Bioengineering and Biotechnology
43. IEEE Journal of Translational Engineering in Health and Medicine
44. IEEE Pulse
45. IEEE Reviews in Biomedical Engineering
46. IEEE Transactions on Biomedical Circuits and Systems
47. IEEE Transactions on Biomedical Engineering
48. IEEE Transactions on Medical Imaging
49. IEEE Transactions on Neural Systems and Rehabilitation Engineering
50. International Journal for Numerical Methods in Biomedical Engineering
51. International Journal of Artificial Organs
52. International Journal of Bioprinting
53. International Journal of Computer Assisted Radiology and Surgery
54. Irbm
55. Isokinetics and Exercise Science
56. Journal of Applied Biomaterials & Functional Materials
57. Journal of Applied Biomechanics
58. Journal of Artificial Organs
59. Journal of Biomaterials Applications
60. Journal of Biomaterials Science-Polymer Edition
61. Journal of Biomechanical Engineering-Transactions of the ASME
62. Journal of Biomechanics
63. Journal of Biomedical Materials Research Part A
64. Journal of Biomedical Materials Research Part B-Applied Biomaterials
65. Journal of Functional Biomaterials
66. Journal of Hard Tissue Biology
67. Journal of Materials Science-Materials in Medicine
68. Journal of Mechanics in Medicine and Biology
69. Journal of Medical and Biological Engineering
70. Journal of Medical Devices-Transactions of the ASME
71. Journal of Neural Engineering
72. Journal of NeuroEngineering and Rehabilitation
73. Journal of the Mechanical Behavior of Biomedical Materials
74. Journal of Tissue Engineering and Regenerative Medicine
75. Lasers in Medical Science
76. Materials Today Bio
77. Medical & Biological Engineering & Computing
78. Medical Engineering & Physics
79. Medical Image Analysis
80. Nature Biomedical Engineering
81. Nature Reviews Bioengineering
82. Npj Regenerative Medicine
83. Organogenesis
84. Pace-Pacing and Clinical Electrophysiology
85. Photoacoustics
86. Physical and Engineering Sciences in Medicine
87. Physics in Medicine and Biology
88. Physiological Measurement
89. Proceedings of the Institution of Mechanical Engineers Part H-Journal of Engineering in Medicine
90. Progress in Biomaterials
91. Regenerative Medicine
92. Regenerative Therapy
93. Sports Biomechanics
94. Technology and Health Care
95. Tissue Engineering and Regenerative Medicine
96. Tissue Engineering Part A
97. Tissue Engineering Part B-Reviews
98. Tissue Engineering Part C-Methods
99. Ultrasonic Imaging

<a id="scie-engineering-chemical"></a>

### Engineering, Chemical

期刊数：142

1. AATCC Review
2. ACS Sustainable Chemistry & Engineering
3. Adsorption Science & Technology
4. Adsorption-Journal of the International Adsorption Society
5. Advanced Powder Technology
6. Advances in Polymer Technology
7. Aerosol Science and Technology
8. AIChE Journal
9. Annual Review of Chemical and Biomolecular Engineering
10. Applied Catalysis B-Environment and Energy
11. Applied Energy
12. Asia-Pacific Journal of Chemical Engineering
13. Atomization and Sprays
14. Biochemical Engineering Journal
15. Biomass Conversion and Biorefinery
16. Bioprocess and Biosystems Engineering
17. Brazilian Journal of Chemical Engineering
18. C&en Global Enterprise
19. Canadian Journal of Chemical Engineering
20. Catalysis Today
21. Central European Journal of Energetic Materials
22. ChemBioEng Reviews
23. Chemical and Biochemical Engineering Quarterly
24. Chemical and Process Engineering-New Frontiers
25. Chemical Engineering & Technology
26. Chemical Engineering and Processing-Process Intensification
27. Chemical Engineering Communications
28. Chemical Engineering Journal
29. Chemical Engineering Progress
30. Chemical Engineering Research & Design
31. Chemical Engineering Science
32. Chemical Industry & Chemical Engineering Quarterly
33. Chemie Ingenieur Technik
34. Chemistry and Technology of Fuels and Oils
35. Chinese Journal of Catalysis
36. Chinese Journal of Chemical Engineering
37. Coloration Technology
38. Combustion and Flame
39. Combustion Explosion and Shock Waves
40. Combustion Science and Technology
41. Combustion Theory and Modelling
42. Computers & Chemical Engineering
43. Current Opinion in Chemical Engineering
44. Desalination
45. Desalination and Water Treatment
46. Drying Technology
47. Dyes and Pigments
48. Education for Chemical Engineers
49. Energy & Environmental Science
50. Energy & Fuels
51. Energy Sources Part A-Recovery Utilization and Environmental Effects
52. Engineering Chemical Engineering
53. Environmental Progress & Sustainable Energy
54. Filtration + Separation
55. Fluid Phase Equilibria
56. Food and Bioproducts Processing
57. Fuel
58. Fuel Processing Technology
59. Gas Science and Engineering
60. Green Energy & Environment
61. Green Processing and Synthesis
62. Green Sciences
63. Hemijska Industrija
64. Indian Journal of Chemical Technology
65. Industrial & Engineering Chemistry Research
66. International Journal of Adhesion and Adhesives
67. International Journal of Chemical Engineering
68. International Journal of Chemical Reactor Engineering
69. International Journal of Greenhouse Gas Control
70. International Journal of Oil Gas and Coal Technology
71. International Polymer Processing
72. Iranian Journal of Chemistry & Chemical Engineering-International English Edition
73. Journal of Adhesion
74. Journal of Adhesion Science and Technology
75. Journal of Aerosol Science
76. Journal of Analytical and Applied Pyrolysis
77. Journal of Catalysis
78. Journal of Chemical and Engineering Data
79. Journal of Chemical Engineering of Japan
80. Journal of Chemical Technology and Biotechnology
81. Journal of CO2 Utilization
82. Journal of Energetic Materials
83. Journal of Energy Chemistry
84. Journal of Environmental Chemical Engineering
85. Journal of Food Engineering
86. Journal of Food Process Engineering
87. Journal of Industrial and Engineering Chemistry
88. Journal of Loss Prevention in the Process Industries
89. Journal of Membrane Science
90. Journal of Microencapsulation
91. Journal of Microwave Power and Electromagnetic Energy
92. Journal of Process Control
93. Journal of Supercritical Fluids
94. Journal of Surfactants and Detergents
95. Journal of the Taiwan Institute of Chemical Engineers
96. Journal of Water Process Engineering
97. Kagaku Kogaku Ronbunshu
98. Kgk-Kautschuk Gummi Kunststoffe
99. Kona Powder and Particle Journal
100. Korean Journal of Chemical Engineering
101. Latin American Applied Research
102. Lubrication Science
103. Macedonian Journal of Chemistry and Chemical Engineering
104. Macromolecular Reaction Engineering
105. Membrane and Water Treatment
106. Membranes
107. Minerals Engineering
108. Npj Clean Water
109. Particulate Science and Technology
110. Particuology
111. Periodica Polytechnica-Chemical Engineering
112. Petroleum Chemistry
113. Petroleum Science and Technology
114. Pigment & Resin Technology
115. Plasma Chemistry and Plasma Processing
116. Polymer Engineering and Science
117. Powder Technology
118. Proceedings of the Combustion Institute
119. Process Biochemistry
120. Process Safety and Environmental Protection
121. Process Safety Progress
122. Processes
123. Progress in Energy and Combustion Science
124. Propellants Explosives Pyrotechnics
125. Przemysl Chemiczny
126. Reaction Chemistry & Engineering
127. Reactive & Functional Polymers
128. Reviews in Chemical Engineering
129. Revista Mexicana de Ingenieria Quimica
130. Science and Technology for Energy Transition
131. Science and Technology of Energetic Materials
132. Separation and Purification Reviews
133. Separation and Purification Technology
134. Separation Science and Technology
135. Solid Fuel Chemistry
136. Solvent Extraction Research and Development-Japan
137. Surface Coatings International
138. Tenside Surfactants Detergents
139. Theoretical Foundations of Chemical Engineering
140. Transport in Porous Media
141. Tribology Letters
142. Turkish Journal of Chemistry

<a id="scie-engineering-civil"></a>

### Engineering, Civil

期刊数：139

1. ACI Structural Journal
2. Advanced Steel Construction
3. Advances in Civil Engineering
4. Advances in Concrete Construction
5. Advances in Structural Engineering
6. Aqua-Water Infrastructure Ecosystems and Society
7. Architectural Engineering and Design Management
8. Archives of Civil and Mechanical Engineering
9. ASCE-ASME Journal of Risk and Uncertainty in Engineering Systems Part A-Civil Engineering
10. Automation in Construction
11. Baltic Journal of Road and Bridge Engineering
12. Bauingenieur
13. Bautechnik
14. Beton- und Stahlbetonbau
15. Building and Environment
16. Buildings
17. Canadian Journal of Civil Engineering
18. Case Studies in Construction Materials
19. China Ocean Engineering
20. Civil Engineering
21. Civil Engineering and Environmental Systems
22. Coastal Engineering
23. Coastal Engineering Journal
24. Cold Regions Science and Technology
25. Computer-Aided Civil and Infrastructure Engineering
26. Computers & Structures
27. Computers and Concrete
28. Construction and Building Materials
29. Developments in the Built Environment
30. Earthquake Engineering & Structural Dynamics
31. Earthquake Engineering and Engineering Vibration
32. Earthquake Spectra
33. Earthquakes and Structures
34. Energy and Buildings
35. Engineering Construction and Architectural Management
36. Engineering Journal-American Institute of Steel Construction
37. Engineering Structure and Civil Engineering
38. Engineering Structures
39. European Journal of Environmental and Civil Engineering
40. Fire Safety Journal
41. Gefahrstoffe Reinhaltung der Luft
42. Geomechanics and Engineering
43. Gradevinar
44. IEEE Journal of Oceanic Engineering
45. IEEE Transactions on Intelligent Transportation Systems
46. Informes de la Construccion
47. Ingegneria Sismica
48. International Journal of Architectural Heritage
49. International Journal of Civil Engineering
50. International Journal of Concrete Structures and Materials
51. International Journal of Offshore and Polar Engineering
52. International Journal of Pavement Engineering
53. International Journal of Steel Structures
54. International Journal of Structural Stability and Dynamics
55. Ite Journal-Institute of Transportation Engineers
56. Journal Awwa
57. Journal of Advanced Concrete Technology
58. Journal of Advanced Transportation
59. Journal of Aerospace Engineering
60. Journal of Bridge Engineering
61. Journal of Building Engineering
62. Journal of Civil Engineering and Management
63. Journal of Civil Structural Health Monitoring
64. Journal of Cold Regions Engineering
65. Journal of Composites for Construction
66. Journal of Computing in Civil Engineering
67. Journal of Construction Engineering and Management
68. Journal of Constructional Steel Research
69. Journal of Earthquake and Tsunami
70. Journal of Earthquake Engineering
71. Journal of Energy Engineering
72. Journal of Environmental Engineering
73. Journal of Hydraulic Engineering
74. Journal of Hydraulic Research
75. Journal of Hydro-Environment Research
76. Journal of Hydroinformatics
77. Journal of Hydrologic Engineering
78. Journal of Hydrology
79. Journal of Infrastructure Systems
80. Journal of Irrigation and Drainage Engineering
81. Journal of Management in Engineering
82. Journal of Marine Science and Technology
83. Journal of Materials in Civil Engineering
84. Journal of Performance of Constructed Facilities
85. Journal of Pipeline Systems Engineering and Practice
86. Journal of Ship Research
87. Journal of Structural Engineering
88. Journal of Surveying Engineering
89. Journal of the South African Institution of Civil Engineering
90. Journal of Transportation Engineering Part A-Systems
91. Journal of Transportation Engineering Part B-Pavements
92. Journal of Urban Planning and Development
93. Journal of Water Resources Planning and Management
94. Journal of Waterway Port Coastal and Ocean Engineering
95. Journal of Wind Engineering and Industrial Aerodynamics
96. KSCE Journal of Civil Engineering
97. Latin American Journal of Solids and Structures
98. Marine Structures
99. Maritime Engineering
100. Materials and Structures
101. Natural Hazards Review
102. Naval Engineers Journal
103. Ocean Engineering
104. Periodica Polytechnica-Civil Engineering
105. Proceedings of the Institution of Civil Engineers-Civil Engineering
106. Proceedings of the Institution of Civil Engineers-Engineering Sustainability
107. Proceedings of the Institution of Civil Engineers-Municipal Engineer
108. Proceedings of the Institution of Civil Engineers-Structures and Buildings
109. Proceedings of the Institution of Civil Engineers-Transport
110. Proceedings of the Institution of Civil Engineers-Water Management
111. Proceedings of the Institution of Mechanical Engineers Part F-Journal of Rail and Rapid Transit
112. Revista de la Construccion
113. Road Materials and Pavement Design
114. Smart Structures and Systems
115. Stahlbau
116. Steel and Composite Structures
117. Stochastic Environmental Research and Risk Assessment
118. Structural Concrete
119. Structural Control & Health Monitoring
120. Structural Design of Tall and Special Buildings
121. Structural Engineering and Mechanics
122. Structural Engineering International
123. Structural Safety
124. Structure and Infrastructure Engineering
125. Structures
126. Survey Review
127. Tecnologia y Ciencias del Agua
128. Thin-Walled Structures
129. Transportation
130. Transportation Geotechnics
131. Transportation Research Part B-Methodological
132. Transportation Research Part E-Logistics and Transportation Review
133. Transportation Research Record
134. Tunnelling and Underground Space Technology
135. Turkish Journal of Civil Engineering
136. Underground Space
137. Water International
138. Water Resources Management
139. Wind and Structures

<a id="scie-engineering-electrical-electronic"></a>

### Engineering, Electrical & Electronic

期刊数：268

1. ACM Journal on Emerging Technologies in Computing Systems
2. ACS Applied Electronic Materials
3. Advances in Electrical and Computer Engineering
4. AEU-International Journal of Electronics and Communications
5. Analog Integrated Circuits and Signal Processing
6. Applied Artificial Intelligence
7. Applied Computational Electromagnetics Society Journal
8. Automatica
9. Automatika
10. Chinese Journal of Electronics
11. Circuit World
12. Circuits Systems and Signal Processing
13. COMPEL-the International Journal for Computation and Mathematics in Electrical and Electronic Engineering
14. Computer Communications
15. Computer Networks
16. Computer Vision and Image Understanding
17. Computers & Electrical Engineering
18. Control Engineering Practice
19. CSEE Journal of Power and Energy Systems
20. Digital Signal Processing
21. Displays
22. Electric Power Components and Systems
23. Electric Power Systems Research
24. Electrical Engineering
25. Electrical Engineering in Japan
26. Electromagnetics
27. Electronics
28. Electronics and Communications in Japan
29. Electronics Letters
30. Elektronika IR Elektrotechnika
31. Engineering Applications of Artificial Intelligence
32. Engineering Information Technology & Electronic Engineering
33. eTransportation
34. ETRI Journal
35. Expert Systems with Applications
36. Flexible and Printed Electronics
37. Frequenz
38. High Voltage
39. IEEE Access
40. IEEE Aerospace and Electronic Systems Magazine
41. IEEE Antennas and Propagation Magazine
42. IEEE Antennas and Wireless Propagation Letters
43. IEEE Canadian Journal of Electrical and Computer Engineering
44. IEEE Circuits and Systems Magazine
45. IEEE Communications Magazine
46. IEEE Consumer Electronics Magazine
47. IEEE Design & Test
48. IEEE Electrical Insulation Magazine
49. IEEE Electron Device Letters
50. IEEE Geoscience and Remote Sensing Letters
51. IEEE Industrial Electronics Magazine
52. IEEE Industry Applications Magazine
53. IEEE Instrumentation & Measurement Magazine
54. IEEE Intelligent Systems
55. IEEE Intelligent Transportation Systems Magazine
56. IEEE Internet of Things Journal
57. IEEE Journal of Emerging and Selected Topics in Power Electronics
58. IEEE Journal of Oceanic Engineering
59. IEEE Journal of Quantum Electronics
60. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing
61. IEEE Journal of Selected Topics in Quantum Electronics
62. IEEE Journal of Selected Topics in Signal Processing
63. IEEE Journal of Solid-State Circuits
64. IEEE Journal of the Electron Devices Society
65. IEEE Journal on Emerging and Selected Topics in Circuits and Systems
66. IEEE Journal on Selected Areas in Communications
67. IEEE Latin America Transactions
68. IEEE Magnetics Letters
69. IEEE Microwave and Wireless Technology Letters
70. IEEE Microwave Magazine
71. IEEE Network
72. IEEE Pervasive Computing
73. IEEE Photonics Journal
74. IEEE Photonics Technology Letters
75. IEEE Power & Energy Magazine
76. IEEE Sensors Journal
77. IEEE Signal Processing Letters
78. IEEE Signal Processing Magazine
79. IEEE Spectrum
80. IEEE Systems Journal
81. IEEE Technology and Society Magazine
82. IEEE Transactions on Aerospace and Electronic Systems
83. IEEE Transactions on Antennas and Propagation
84. IEEE Transactions on Applied Superconductivity
85. IEEE Transactions on Audio Speech and Language Processing
86. IEEE Transactions on Automatic Control
87. IEEE Transactions on Biomedical Circuits and Systems
88. IEEE Transactions on Broadcasting
89. IEEE Transactions on Circuits and Systems for Video Technology
90. IEEE Transactions on Circuits and Systems I-Regular Papers
91. IEEE Transactions on Circuits and Systems II-Express Briefs
92. IEEE Transactions on Communications
93. IEEE Transactions on Components Packaging and Manufacturing Technology
94. IEEE Transactions on Computational Imaging
95. IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems
96. IEEE Transactions on Computers
97. IEEE Transactions on Consumer Electronics
98. IEEE Transactions on Control Systems Technology
99. IEEE Transactions on Device and Materials Reliability
100. IEEE Transactions on Dielectrics and Electrical Insulation
101. IEEE Transactions on Education
102. IEEE Transactions on Electromagnetic Compatibility
103. IEEE Transactions on Electron Devices
104. IEEE Transactions on Energy Conversion
105. IEEE Transactions on Fuzzy Systems
106. IEEE Transactions on Geoscience and Remote Sensing
107. IEEE Transactions on Image Processing
108. IEEE Transactions on Industrial Electronics
109. IEEE Transactions on Industry Applications
110. IEEE Transactions on Information Forensics and Security
111. IEEE Transactions on Information Theory
112. IEEE Transactions on Instrumentation and Measurement
113. IEEE Transactions on Intelligent Transportation Systems
114. IEEE Transactions on Intelligent Vehicles
115. IEEE Transactions on Knowledge and Data Engineering
116. IEEE Transactions on Magnetics
117. IEEE Transactions on Medical Imaging
118. IEEE Transactions on Microwave Theory and Techniques
119. IEEE Transactions on Nanotechnology
120. IEEE Transactions on Networking
121. IEEE Transactions on Neural Networks and Learning Systems
122. IEEE Transactions on Nuclear Science
123. IEEE Transactions on Parallel and Distributed Systems
124. IEEE Transactions on Pattern Analysis and Machine Intelligence
125. IEEE Transactions on Power Delivery
126. IEEE Transactions on Power Electronics
127. IEEE Transactions on Power Systems
128. IEEE Transactions on Reliability
129. IEEE Transactions on Semiconductor Manufacturing
130. IEEE Transactions on Signal and Information Processing over Networks
131. IEEE Transactions on Signal Processing
132. IEEE Transactions on Smart Grid
133. IEEE Transactions on Software Engineering
134. IEEE Transactions on Sustainable Energy
135. IEEE Transactions on Terahertz Science and Technology
136. IEEE Transactions on Transportation Electrification
137. IEEE Transactions on Ultrasonics Ferroelectrics and Frequency Control
138. IEEE Transactions on Vehicular Technology
139. IEEE Transactions on Very Large Scale Integration (VLSI) Systems
140. IEEE Transactions on Wireless Communications
141. IEEE Vehicular Technology Magazine
142. IEEE Wireless Communications
143. IEEE Wireless Communications Letters
144. IEEE-ASME Transactions on Mechatronics
145. IEEJ Transactions on Electrical and Electronic Engineering
146. IEICE Electronics Express
147. IEICE Transactions on Communications
148. IEICE Transactions on Electronics
149. IEICE Transactions on Fundamentals of Electronics Communications and Computer Sciences
150. IET Circuits Devices & Systems
151. IET Communications
152. IET Computer Vision
153. IET Control Theory and Applications
154. IET Electric Power Applications
155. IET Electrical Systems in Transportation
156. IET Generation Transmission & Distribution
157. IET Image Processing
158. IET Intelligent Transport Systems
159. IET Microwaves Antennas & Propagation
160. IET Optoelectronics
161. IET Power Electronics
162. IET Radar Sonar and Navigation
163. IET Renewable Power Generation
164. IET Science Measurement & Technology
165. IET Signal Processing
166. IETE Journal of Research
167. IETE Technical Review
168. Image and Vision Computing
169. Informacije MIDEM-Journal of Microelectronics Electronic Components and Materials
170. Integrated Ferroelectrics
171. Integration-the VLSI Journal
172. International Arab Journal of Information Technology
173. International Journal of Adaptive Control and Signal Processing
174. International Journal of Antennas and Propagation
175. International Journal of Applied Electromagnetics and Mechanics
176. International Journal of Circuit Theory and Applications
177. International Journal of Communication Systems
178. International Journal of Electrical Power & Energy Systems
179. International Journal of Electronics
180. International Journal of Imaging Systems and Technology
181. International Journal of Microwave and Wireless Technologies
182. International Journal of Numerical Modelling-Electronic Networks Devices and Fields
183. International Journal of Optomechatronics
184. International Journal of RF and Microwave Computer-Aided Engineering
185. International Journal of Robust and Nonlinear Control
186. International Journal of Software Engineering and Knowledge Engineering
187. International Transactions on Electrical Energy Systems
188. Internet of Things
189. Iranian Journal of Science and Technology-Transactions of Electrical Engineering
190. Journal of Circuits Systems and Computers
191. Journal of Communications Technology and Electronics
192. Journal of Computational Electronics
193. Journal of Cryptology
194. Journal of Electrical Engineering & Technology
195. Journal of Electrical Engineering-Elektrotechnicky Casopis
196. Journal of Electromagnetic Engineering and Science
197. Journal of Electromagnetic Waves and Applications
198. Journal of Electronic Imaging
199. Journal of Electronic Materials
200. Journal of Electronic Packaging
201. Journal of Electronic Testing-Theory and Applications
202. Journal of Electrostatics
203. Journal of Infrared Millimeter and Terahertz Waves
204. Journal of Lightwave Technology
205. Journal of Materials Science-Materials in Electronics
206. Journal of Micro-Nanopatterning Materials and Metrology-Jm3
207. Journal of Microelectromechanical Systems
208. Journal of Micromechanics and Microengineering
209. Journal of Microwave Power and Electromagnetic Energy
210. Journal of Modern Power Systems and Clean Energy
211. Journal of Nanoelectronics and Optoelectronics
212. Journal of Power Electronics
213. Journal of Real-Time Image Processing
214. Journal of Semiconductor Technology and Science
215. Journal of Sensors
216. Journal of Signal Processing Systems for Signal Image and Video Technology
217. Journal of Supercomputing
218. Journal of Systems Engineering and Electronics
219. Journal of the Franklin Institute
220. Journal of the Society for Information Display
221. Journal of Vacuum Science & Technology B
222. Journal on Advances in Signal Processing
223. Journal on Audio Speech and Music Processing
224. Journal on Wireless Communications and Networking
225. Light & Engineering
226. Machine Vision and Applications
227. Machines
228. Materials Science in Semiconductor Processing
229. Mathematics of Control Signals and Systems
230. Mechatronics
231. Microelectronic Engineering
232. Microelectronics International
233. Microelectronics Journal
234. Microelectronics Reliability
235. Microprocessors and Microsystems
236. Microsystem Technologies-Micro-and Nanosystems-Information Storage and Processing Systems
237. Microwave and Optical Technology Letters
238. Microwave Journal
239. Multidimensional Systems and Signal Processing
240. Nano Communication Networks
241. Nature Electronics
242. Network-Computation in Neural Systems
243. Npj Flexible Electronics
244. Optical and Quantum Electronics
245. Optical Fiber Technology
246. Opto-Electronics Review
247. Pattern Recognition
248. Physical Communication
249. Proceedings of the IEEE
250. Progress in Electromagnetics Research-Pier
251. Progress in Quantum Electronics
252. Protection and Control of Modern Power Systems
253. Radioengineering
254. Radiophysics and Quantum Electronics
255. Revue Roumaine des Sciences Techniques-Serie Electrotechnique et Energetique
256. Science China-Information Sciences
257. Semiconductor Science and Technology
258. Sensors
259. Sensors and Actuators A-Physical
260. Signal Image and Video Processing
261. Signal Processing
262. Signal Processing-Image Communication
263. Soldering & Surface Mount Technology
264. Solid-State Electronics
265. Sustainable Energy Grids & Networks
266. Tsinghua Science and Technology
267. Turkish Journal of Electrical Engineering and Computer Sciences
268. Wireless Networks

<a id="scie-engineering-environmental"></a>

### Engineering, Environmental

期刊数：54

1. Ambio
2. Applied Catalysis B-Environment and Energy
3. Building and Environment
4. Bulletin of Engineering Geology and the Environment
5. Chemical Engineering Journal
6. Clean Technologies and Environmental Policy
7. Cold Regions Science and Technology
8. Critical Reviews in Environmental Science and Technology
9. Ecological Engineering
10. Engineering Environment
11. Environment Protection Engineering
12. Environmental & Engineering Geoscience
13. Environmental Chemistry Letters
14. Environmental Engineering Research
15. Environmental Engineering Science
16. Environmental Geochemistry and Health
17. Environmental Modelling & Software
18. Environmental Progress & Sustainable Energy
19. Environmental Science & Technology
20. Environmental Science & Technology Letters
21. Environmental Science-Water Research & Technology
22. Environmental Technology & Innovation
23. Gefahrstoffe Reinhaltung der Luft
24. Greenhouse Gases-Science and Technology
25. Indoor Air
26. Indoor and Built Environment
27. International Journal of Greenhouse Gas Control
28. International Journal of Life Cycle Assessment
29. Journal of Chemical Technology and Biotechnology
30. Journal of Cleaner Production
31. Journal of Cold Regions Engineering
32. Journal of Environmental Chemical Engineering
33. Journal of Environmental Engineering
34. Journal of Environmental Health Science and Engineering
35. Journal of Environmental Science and Health Part A-Toxic/Hazardous Substances & Environmental Engineering
36. Journal of Hazardous Materials
37. Journal of Industrial Ecology
38. Journal of Polymers and the Environment
39. Journal of Terramechanics
40. Journal of the Air & Waste Management Association
41. Journal of the American Water Resources Association
42. Journal of Water Process Engineering
43. Ozone-Science & Engineering
44. Process Safety and Environmental Protection
45. Resources Conservation and Recycling
46. Stochastic Environmental Research and Risk Assessment
47. Sustainable Environment Research
48. Waste Management
49. Waste Management & Research
50. Water Environment Research
51. Water Research
52. Water Research X
53. Water Reuse
54. Water Science and Technology

<a id="scie-engineering-geological"></a>

### Engineering, Geological

期刊数：41

1. Acta Geotechnica
2. Acta Geotechnica Slovenica
3. Bulletin of Earthquake Engineering
4. Bulletin of Engineering Geology and the Environment
5. Canadian Geotechnical Journal
6. Computers and Geotechnics
7. Earthquake Engineering & Structural Dynamics
8. Earthquake Engineering and Engineering Vibration
9. Earthquake Spectra
10. Earthquakes and Structures
11. Engineering Geology
12. Environmental & Engineering Geoscience
13. Environmental Geotechnics
14. European Journal of Environmental and Civil Engineering
15. Geomechanics and Engineering
16. Geomechanics and Geophysics for Geo-Energy and Geo-Resources
17. Geomechanics for Energy and the Environment
18. Georisk-Assessment and Management of Risk for Engineered Systems and Geohazards
19. Geosynthetics International
20. Geotechnical Testing Journal
21. Geotechnique
22. Geotechnique Letters
23. Geotextiles and Geomembranes
24. Ingegneria Sismica
25. International Journal for Numerical and Analytical Methods in Geomechanics
26. International Journal of Geomechanics
27. International Journal of Physical Modelling in Geotechnics
28. International Journal of Rock Mechanics and Mining Sciences
29. Journal of Earthquake Engineering
30. Journal of Environmental and Engineering Geophysics
31. Journal of Geotechnical and Geoenvironmental Engineering
32. Journal of Rock Mechanics and Geotechnical Engineering
33. Landslides
34. Marine Georesources & Geotechnology
35. Proceedings of the Institution of Civil Engineers-Geotechnical Engineering
36. Quarterly Journal of Engineering Geology and Hydrogeology
37. Rock Mechanics and Rock Engineering
38. Soil Dynamics and Earthquake Engineering
39. Soil Mechanics and Foundation Engineering
40. Soils and Foundations
41. Transportation Geotechnics

<a id="scie-engineering-industrial"></a>

### Engineering, Industrial

期刊数：50

1. Applied Ergonomics
2. CIRP Annals-Manufacturing Technology
3. Cognition Technology & Work
4. Computers & Industrial Engineering
5. Computers & Operations Research
6. Engineering Construction and Architectural Management
7. Engineering Economist
8. Engineering Management Journal
9. Ergonomics
10. European Journal of Industrial Engineering
11. Flexible Services and Manufacturing Journal
12. Human Factors
13. IEEE Industry Applications Magazine
14. IEEE Transactions on Engineering Management
15. IEEE Transactions on Industrial Informatics
16. IISE Transactions
17. Industrial Management & Data Systems
18. Industrial Robot-the International Journal of Robotics Research and Application
19. International Journal of Industrial Engineering Computations
20. International Journal of Industrial Engineering-Theory Applications and Practice
21. International Journal of Industrial Ergonomics
22. International Journal of Lean Six Sigma
23. International Journal of Production Economics
24. International Journal of Production Research
25. International Journal of Simulation Modelling
26. International Journal of Systems Science-Operations & Logistics
27. Issues in Science and Technology
28. Journal of Construction Engineering and Management
29. Journal of Engineering and Technology Management
30. Journal of Industrial Information Integration
31. Journal of Management in Engineering
32. Journal of Manufacturing Systems
33. Journal of Manufacturing Technology Management
34. Journal of Materials Processing Technology
35. Journal of Product Innovation Management
36. Journal of Quality Technology
37. Probability in the Engineering and Informational Sciences
38. Proceedings of the Institution of Mechanical Engineers Part O-Journal of Risk and Reliability
39. Production Planning & Control
40. Quality and Reliability Engineering International
41. Quality Engineering
42. Quality Technology and Quantitative Management
43. Reliability Engineering & System Safety
44. Research in Engineering Design
45. Research-Technology Management
46. Safety Science
47. South African Journal of Industrial Engineering
48. Systems Engineering
49. Technovation
50. Travail Humain

<a id="scie-engineering-manufacturing"></a>

### Engineering, Manufacturing

期刊数：50

1. 3D Printing and Additive Manufacturing
2. Additive Manufacturing
3. Advances in Manufacturing
4. Advances in Production Engineering & Management
5. AI Edam-Artificial Intelligence for Engineering Design Analysis and Manufacturing
6. CIRP Annals-Manufacturing Technology
7. CIRP Journal of Manufacturing Science and Technology
8. Composites Part A-Applied Science and Manufacturing
9. Design Studies
10. Flexible Services and Manufacturing Journal
11. Human Factors and Ergonomics in Manufacturing & Service Industries
12. IEEE Transactions on Components Packaging and Manufacturing Technology
13. IEEE Transactions on Semiconductor Manufacturing
14. IEEE-ASME Transactions on Mechatronics
15. Integrating Materials and Manufacturing Innovation
16. International Journal of Advanced Manufacturing Technology
17. International Journal of Computer Integrated Manufacturing
18. International Journal of Crashworthiness
19. International Journal of Design
20. International Journal of Extreme Manufacturing
21. International Journal of Industrial Engineering-Theory Applications and Practice
22. International Journal of Machine Tools & Manufacture
23. International Journal of Material Forming
24. International Journal of Precision Engineering and Manufacturing
25. International Journal of Precision Engineering and Manufacturing-Green Technology
26. International Journal of Production Economics
27. International Journal of Production Research
28. International Journal of Simulation Modelling
29. Journal of Advanced Mechanical Design Systems and Manufacturing
30. Journal of Computing and Information Science in Engineering
31. Journal of Intelligent Manufacturing
32. Journal of Manufacturing Processes
33. Journal of Manufacturing Science and Engineering-Transactions of the ASME
34. Journal of Manufacturing Systems
35. Journal of Manufacturing Technology Management
36. Journal of Materials Processing Technology
37. Journal of Scheduling
38. Machining Science and Technology
39. Manufacturing Engineering
40. Materials and Manufacturing Processes
41. Packaging Technology and Science
42. Precision Engineering-Journal of the International Societies for Precision Engineering and Nanotechnology
43. Proceedings of the Institution of Mechanical Engineers Part B-Journal of Engineering Manufacture
44. Production and Operations Management
45. Production Planning & Control
46. Research in Engineering Design
47. Robotic Intelligence and Automation
48. Robotics and Computer-Integrated Manufacturing
49. Soldering & Surface Mount Technology
50. Virtual and Physical Prototyping

<a id="scie-engineering-marine"></a>

### Engineering, Marine

期刊数：16

1. Brodogradnja
2. International Journal of Maritime Engineering
3. International Journal of Naval Architecture and Ocean Engineering
4. Journal of Marine Engineering and Technology
5. Journal of Marine Science and Engineering
6. Journal of Marine Science and Technology
7. Journal of Navigation
8. Journal of Ocean Engineering and Science
9. Journal of Ship Production and Design
10. Journal of Ship Research
11. Marine Structures
12. Naval Engineers Journal
13. Ocean Engineering
14. Polish Maritime Research
15. Proceedings of the Institution of Mechanical Engineers Part M-Journal of Engineering for the Maritime Environment
16. Ships and Offshore Structures

<a id="scie-engineering-mechanical"></a>

### Engineering, Mechanical

期刊数：136

1. Acta Mechanica Sinica
2. Actuators
3. Advances in Mechanical Engineering
4. Aerosol Science and Technology
5. Applied Thermal Engineering
6. Archives of Civil and Mechanical Engineering
7. Ashrae Journal
8. ASME Journal of Heat and Mass Transfer
9. Atomization and Sprays
10. China Ocean Engineering
11. Chinese Journal of Mechanical Engineering
12. Combustion and Flame
13. Drying Technology
14. Engineering Applications of Computational Fluid Mechanics
15. Engineering Failure Analysis
16. Engineering Mechanical Engineering
17. Engineering Research
18. Engineering with Computers
19. Experimental Heat Transfer
20. Experimental Techniques
21. Experimental Thermal and Fluid Science
22. Experiments in Fluids
23. Facta Universitatis-Series Mechanical Engineering
24. Fatigue & Fracture of Engineering Materials & Structures
25. Flow Measurement and Instrumentation
26. Friction
27. Heat Transfer Engineering
28. IEEE-ASME Transactions on Mechatronics
29. Industrial Lubrication and Tribology
30. International Journal of Acoustics and Vibration
31. International Journal of Automotive Technology
32. International Journal of Crashworthiness
33. International Journal of Engine Research
34. International Journal of Fatigue
35. International Journal of Heat and Fluid Flow
36. International Journal of Heat and Mass Transfer
37. International Journal of Heavy Vehicle Systems
38. International Journal of Impact Engineering
39. International Journal of Machine Tools & Manufacture
40. International Journal of Mechanical Sciences
41. International Journal of Mechanics and Materials in Design
42. International Journal of Offshore and Polar Engineering
43. International Journal of Optomechatronics
44. International Journal of Plasticity
45. International Journal of Precision Engineering and Manufacturing
46. International Journal of Precision Engineering and Manufacturing-Green Technology
47. International Journal of Pressure Vessels and Piping
48. International Journal of Refrigeration
49. International Journal of Spray and Combustion Dynamics
50. International Journal of Structural Stability and Dynamics
51. International Journal of Surface Science and Engineering
52. International Journal of Thermal Sciences
53. International Journal of Vehicle Design
54. Iranian Journal of Science and Technology-Transactions of Mechanical Engineering
55. Isi Bilimi ve Teknigi Dergisi-Journal of Thermal Science and Technology
56. Journal of Advanced Mechanical Design Systems and Manufacturing
57. Journal of Aerosol Science
58. Journal of Computational and Nonlinear Dynamics
59. Journal of Electronic Packaging
60. Journal of Engineering for Gas Turbines and Power-Transactions of the ASME
61. Journal of Engineering Materials and Technology-Transactions of the ASME
62. Journal of Engineering Mechanics
63. Journal of Engineering Thermophysics
64. Journal of Enhanced Heat Transfer
65. Journal of Fluids and Structures
66. Journal of Fluids Engineering-Transactions of the ASME
67. Journal of Friction and Wear
68. Journal of Hydraulic Engineering
69. Journal of Manufacturing Science and Engineering-Transactions of the ASME
70. Journal of Mechanical Design
71. Journal of Mechanical Science and Technology
72. Journal of Mechanisms and Robotics-Transactions of the ASME
73. Journal of Offshore Mechanics and Arctic Engineering-Transactions of the ASME
74. Journal of Pipeline Science and Engineering
75. Journal of Porous Media
76. Journal of Pressure Vessel Technology-Transactions of the ASME
77. Journal of Sandwich Structures & Materials
78. Journal of Solar Energy Engineering-Transactions of the ASME
79. Journal of Sound and Vibration
80. Journal of Strain Analysis for Engineering Design
81. Journal of the Brazilian Society of Mechanical Sciences and Engineering
82. Journal of the Chinese Society of Mechanical Engineers
83. Journal of Thermal Science
84. Journal of Thermal Science and Engineering Applications
85. Journal of Thermophysics and Heat Transfer
86. Journal of Tribology-Transactions of the ASME
87. Journal of Turbomachinery-Transactions of the ASME
88. Journal of Vibration and Acoustics-Transactions of the ASME
89. Journal of Vibration and Control
90. Journal of Vibration Engineering & Technologies
91. Latin American Journal of Solids and Structures
92. Lubricants
93. Lubrication Science
94. Machines
95. Machining Science and Technology
96. Mechanical Sciences
97. Mechanical Systems and Signal Processing
98. Mechanics & Industry
99. Mechanism and Machine Theory
100. Mechatronics
101. Nanoscale and Microscale Thermophysical Engineering
102. Nonlinear Dynamics
103. Probabilistic Engineering Mechanics
104. Proceedings of the Combustion Institute
105. Proceedings of the Institution of Mechanical Engineers Part A-Journal of Power and Energy
106. Proceedings of the Institution of Mechanical Engineers Part B-Journal of Engineering Manufacture
107. Proceedings of the Institution of Mechanical Engineers Part C-Journal of Mechanical Engineering Science
108. Proceedings of the Institution of Mechanical Engineers Part D-Journal of Automobile Engineering
109. Proceedings of the Institution of Mechanical Engineers Part E-Journal of Process Mechanical Engineering
110. Proceedings of the Institution of Mechanical Engineers Part F-Journal of Rail and Rapid Transit
111. Proceedings of the Institution of Mechanical Engineers Part G-Journal of Aerospace Engineering
112. Proceedings of the Institution of Mechanical Engineers Part J-Journal of Engineering Tribology
113. Proceedings of the Institution of Mechanical Engineers Part K-Journal of Multi-Body Dynamics
114. Proceedings of the Institution of Mechanical Engineers Part P-Journal of Sports Engineering and Technology
115. Progress in Energy and Combustion Science
116. Propulsion and Power Research
117. Rapid Prototyping Journal
118. Science and Technology for the Built Environment
119. Shock and Vibration
120. Smart Structures and Systems
121. Strojniski Vestnik-Journal of Mechanical Engineering
122. Structural Engineering and Mechanics
123. Structure and Infrastructure Engineering
124. Surface Topography-Metrology and Properties
125. Theoretical and Applied Fracture Mechanics
126. Thermal Science and Engineering Progress
127. Thermophysics and Aeromechanics
128. Thin-Walled Structures
129. Transactions of FAMENA
130. Transactions of the Canadian Society for Mechanical Engineering
131. Tribology International
132. Tribology Letters
133. Tribology Transactions
134. Vehicle System Dynamics
135. Wear
136. Wind Energy

<a id="scie-engineering-multidisciplinary"></a>

### Engineering, Multidisciplinary

期刊数：90

1. Acta Polytechnica Hungarica
2. Advanced Engineering Informatics
3. Advances in Engineering Software
4. AI Edam-Artificial Intelligence for Engineering Design Analysis and Manufacturing
5. Ain Shams Engineering Journal
6. Alexandria Engineering Journal
7. Applied Mathematical Modelling
8. Applied Mathematics in Science and Engineering
9. Applied Sciences-Basel
10. Archives of Computational Methods in Engineering
11. Atomization and Sprays
12. Bioinspiration & Biomimetics
13. Biomimetics
14. Bulletin of the Polish Academy of Sciences-Technical Sciences
15. Cmes-Computer Modeling in Engineering & Sciences
16. Combustion and Flame
17. Combustion Explosion and Shock Waves
18. Combustion Science and Technology
19. Composites Part B-Engineering
20. Computer Applications in Engineering Education
21. Computer Methods in Applied Mechanics and Engineering
22. Defence Technology
23. Design Studies
24. Dyna
25. Eksploatacja i Niezawodnosc-Maintenance and Reliability
26. Engineering
27. Engineering Analysis with Boundary Elements
28. Engineering Applications of Artificial Intelligence
29. Engineering Applications of Computational Fluid Mechanics
30. Engineering Computations
31. Engineering Optimization
32. Engineering Research
33. Engineering Science and Technology-an International Journal-Jestech
34. Engineering Studies
35. Fire Technology
36. IEEE Transactions on Industry Applications
37. IEEE Transactions on Network Science and Engineering
38. Indian Journal of Engineering and Materials Sciences
39. Ingenieria e Investigacion
40. Instruments and Experimental Techniques
41. Integrated Computer-Aided Engineering
42. International Journal for Multiscale Computational Engineering
43. International Journal for Numerical Methods in Engineering
44. International Journal for Uncertainty Quantification
45. International Journal of Computational Methods
46. International Journal of Critical Infrastructure Protection
47. International Journal of Design
48. International Journal of Engineering Education
49. International Journal of Engineering Science
50. International Journal of Pressure Vessels and Piping
51. International Journal of Technology and Design Education
52. International Journal of Technology Management
53. ISA Transactions
54. Issues in Science and Technology
55. Journal of Bionic Engineering
56. Journal of Civil Engineering Education
57. Journal of Computational Design and Engineering
58. Journal of Elasticity
59. Journal of Engineering Design
60. Journal of Engineering Education
61. Journal of Engineering Mathematics
62. Journal of Engineering Research
63. Journal of Engineering Technology
64. Journal of Fire Sciences
65. Journal of Industrial and Management Optimization
66. Journal of Marine Science and Technology-Taiwan
67. Journal of Nonlinear Complex and Data Science
68. Journal of Scientific & Industrial Research
69. Journal of the Audio Engineering Society
70. Journal of the Chinese Institute of Engineers
71. Journal of the Faculty of Engineering and Architecture of Gazi University
72. Journal of the Franklin Institute
73. Journal of Zhejiang University-Science A
74. Measurement
75. Measurement Science and Technology
76. Noise Control Engineering Journal
77. Optimization and Engineering
78. Precision Engineering-Journal of the International Societies for Precision Engineering and Nanotechnology
79. Proceedings of the Institution of Mechanical Engineers Part O-Journal of Risk and Reliability
80. Quality and Reliability Engineering International
81. Research in Engineering Design
82. Revista Internacional de Metodos Numericos para Calculo y Diseno en Ingenieria
83. Sadhana-Academy Proceedings in Engineering Sciences
84. Sampe Journal
85. Science and Engineering Ethics
86. Science China-Technological Sciences
87. Scientia Iranica
88. Structural and Multidisciplinary Optimization
89. Structural Health Monitoring-an International Journal
90. Tehnicki Vjesnik-Technical Gazette

<a id="scie-engineering-ocean"></a>

### Engineering, Ocean

期刊数：15

1. Applied Ocean Research
2. China Ocean Engineering
3. Coastal Engineering
4. Coastal Engineering Journal
5. IEEE Journal of Oceanic Engineering
6. International Journal of Offshore and Polar Engineering
7. Journal of Atmospheric and Oceanic Technology
8. Journal of Marine Science and Engineering
9. Journal of Ocean Engineering and Science
10. Journal of Offshore Mechanics and Arctic Engineering-Transactions of the ASME
11. Journal of Waterway Port Coastal and Ocean Engineering
12. Marine Georesources & Geotechnology
13. Marine Technology Society Journal
14. Maritime Engineering
15. Ocean Engineering

<a id="scie-engineering-petroleum"></a>

### Engineering, Petroleum

期刊数：17

1. Chemistry and Technology of Fuels and Oils
2. CT&F-Ciencia Tecnologia y Futuro
3. Geoenergy Science and Engineering
4. International Journal of Oil Gas and Coal Technology
5. Journal of Petroleum Exploration and Production Technology
6. Journal of Pipeline Science and Engineering
7. Journal of the Japan Petroleum Institute
8. Oil Shale
9. Petroleum Chemistry
10. Petroleum Exploration and Development
11. Petroleum Science
12. Petroleum Science and Technology
13. Petrophysics
14. Science and Technology for Energy Transition
15. SPE Drilling & Completion
16. SPE Journal
17. SPE Production & Operations

<a id="scie-entomology"></a>

### Entomology

期刊数：100

1. Acarologia
2. Acta Entomologica Musei Nationalis Pragae
3. African Entomology
4. African Invertebrates
5. Agricultural and Forest Entomology
6. Annales de la Societe Entomologique de France
7. Annales Zoologici
8. Annals of the Entomological Society of America
9. Annual Review of Entomology
10. Apidologie
11. Applied Entomology and Zoology
12. Aquatic Insects
13. Archives of Insect Biochemistry and Physiology
14. Arthropod Structure & Development
15. Arthropod Systematics & Phylogeny
16. Arthropod-Plant Interactions
17. Arthropoda Selecta
18. Asian Myrmecology
19. Austral Entomology
20. BioControl
21. Biocontrol Science and Technology
22. Biological Control
23. Bulletin of Entomological Research
24. Bulletin of Insectology
25. Canadian Entomologist
26. Coleopterists Bulletin
27. Current Opinion in Insect Science
28. Deutsche Entomologische Zeitschrift
29. Ecological Entomology
30. Egyptian Journal of Biological Pest Control
31. Entomologia Experimentalis et Applicata
32. Entomologia Generalis
33. Entomologica Americana
34. Entomological News
35. Entomological Research
36. Entomological Science
37. Environmental Entomology
38. European Journal of Entomology
39. European Journal of Taxonomy
40. Experimental and Applied Acarology
41. Florida Entomologist
42. Insect Biochemistry and Molecular Biology
43. Insect Conservation and Diversity
44. Insect Molecular Biology
45. Insect Science
46. Insect Systematics & Evolution
47. Insect Systematics and Diversity
48. Insectes Sociaux
49. Insects
50. International Journal of Acarology
51. International Journal of Odonatology
52. International Journal of Pest Management
53. International Journal of Tropical Insect Science
54. Japanese Journal of Applied Entomology and Zoology
55. Journal of Apicultural Research
56. Journal of Apicultural Science
57. Journal of Applied Entomology
58. Journal of Arachnology
59. Journal of Asia-Pacific Entomology
60. Journal of Economic Entomology
61. Journal of Entomological Science
62. Journal of Hymenoptera Research
63. Journal of Insect Behavior
64. Journal of Insect Conservation
65. Journal of Insect Physiology
66. Journal of Insect Science
67. Journal of Insects as Food and Feed
68. Journal of Integrated Pest Management
69. Journal of Medical Entomology
70. Journal of Pest Science
71. Journal of Pesticide Science
72. Journal of Stored Products Research
73. Journal of the American Mosquito Control Association
74. Journal of the Entomological Research Society
75. Journal of the Kansas Entomological Society
76. Journal of the Lepidopterists Society
77. Journal of Vector Ecology
78. Medical and Veterinary Entomology
79. Myrmecological News
80. Neotropical Entomology
81. New Zealand Entomologist
82. Nota Lepidopterologica
83. Odonatologica
84. Oriental Insects
85. Pan-Pacific Entomologist
86. Pest Management Science
87. Pesticide Biochemistry and Physiology
88. Physiological Entomology
89. Phytoparasitica
90. Proceedings of the Entomological Society of Washington
91. Revista Brasileira de Entomologia
92. Revista Colombiana de Entomologia
93. Revista de la Sociedad Entomologica Argentina
94. SHILAP-Revista de Lepidopterologia
95. Sociobiology
96. Southwestern Entomologist
97. Systematic and Applied Acarology
98. Systematic Entomology
99. Transactions of the American Entomological Society
100. Turkiye Entomoloji Dergisi-Turkish Journal of Entomology

<a id="scie-environmental-sciences"></a>

### Environmental Sciences

期刊数：273

1. Advances in Climate Change Research
2. Aerobiologia
3. Aerosol and Air Quality Research
4. Aerosol Science and Technology
5. African Journal of Range & Forage Science
6. Agricultural & Environmental Letters
7. Agriculture Ecosystems & Environment
8. Air Quality Atmosphere and Health
9. Ambio
10. Annali di Botanica
11. Annals of Agricultural and Environmental Medicine
12. Annual Review of Environment and Resources
13. Antarctic Science
14. Anthropocene
15. Anthropocene Review
16. Applied Catalysis A-General
17. Applied Ecology and Environmental Research
18. Aquatic Conservation-Marine and Freshwater Ecosystems
19. Aquatic Ecosystem Health & Management
20. Aquatic Sciences
21. Archives of Environmental & Occupational Health
22. Archives of Environmental Contamination and Toxicology
23. Archives of Environmental Protection
24. Arctic
25. Arctic Antarctic and Alpine Research
26. Arctic Science
27. Arid Land Research and Management
28. Atmosphere
29. Atmospheric Chemistry and Physics
30. Atmospheric Environment
31. Atmospheric Pollution Research
32. Biochar
33. Biodiversity and Conservation
34. BioEnergy Research
35. Biogeochemistry
36. Biological Conservation
37. Biology and Environment-Proceedings of the Royal Irish Academy
38. Biomedical and Environmental Sciences
39. Bioremediation Journal
40. Biotechnologie Agronomie Societe et Environnement
41. Boreal Environment Research
42. Bulletin of Environmental Contamination and Toxicology
43. Carbon Balance and Management
44. Carbon Management
45. Carpathian Journal of Earth and Environmental Sciences
46. Chemistry and Ecology
47. Chinese Geographical Science
48. Clean Technologies and Environmental Policy
49. Clean-Soil Air Water
50. Climate Research
51. Climate Risk Management
52. Climate Services
53. Climatic Change
54. Coastal Management
55. Communications Earth & Environment
56. Conservation Biology
57. Conservation Physiology
58. Critical Reviews in Environmental Science and Technology
59. Current Opinion in Environmental Sustainability
60. Current Pollution Reports
61. Earths Future
62. EcoHealth
63. Ecohydrology
64. Ecological Applications
65. Ecological Chemistry and Engineering S-Chemia i Inzynieria Ekologiczna S
66. Ecological Economics
67. Ecological Engineering
68. Ecological Indicators
69. Ecological Processes
70. Ecosystem Health and Sustainability
71. Ecosystem Services
72. Ecotoxicology
73. Ecotoxicology and Environmental Safety
74. Egyptian Journal of Remote Sensing and Space Sciences
75. Elementa-Science of the Anthropocene
76. Energy & Environmental Science
77. Energy Policy
78. Engineering Environment
79. Environment
80. Environment Development and Sustainability
81. Environment International
82. Environmental and Ecological Statistics
83. Environmental and Experimental Botany
84. Environmental and Molecular Mutagenesis
85. Environmental Chemistry
86. Environmental Chemistry Letters
87. Environmental Conservation
88. Environmental Development
89. Environmental Earth Sciences
90. Environmental Engineering and Management Journal
91. Environmental Engineering Research
92. Environmental Engineering Science
93. Environmental Evidence
94. Environmental Fluid Mechanics
95. Environmental Forensics
96. Environmental Geochemistry and Health
97. Environmental Health
98. Environmental Health Perspectives
99. Environmental Innovation and Societal Transitions
100. Environmental Management
101. Environmental Microbiology Reports
102. Environmental Modeling & Assessment
103. Environmental Modelling & Software
104. Environmental Monitoring and Assessment
105. Environmental Pollutants and Bioavailability
106. Environmental Pollution
107. Environmental Progress & Sustainable Energy
108. Environmental Research
109. Environmental Research Communications
110. Environmental Research Letters
111. Environmental Reviews
112. Environmental Science & Policy
113. Environmental Science & Technology
114. Environmental Science & Technology Letters
115. Environmental Science and Ecotechnology
116. Environmental Science-Nano
117. Environmental Science-Processes & Impacts
118. Environmental Science-Water Research & Technology
119. Environmental Sciences Europe
120. Environmental Technology
121. Environmental Technology & Innovation
122. Environmental Toxicology
123. Environmental Toxicology and Chemistry
124. Environmental Toxicology and Pharmacology
125. Environmetrics
126. Estuaries and Coasts
127. Food and Environmental Virology
128. Frontiers in Ecology and the Environment
129. Frontiers in Environmental Science
130. Gaia-Ecological Perspectives for Science and Society
131. Gefahrstoffe Reinhaltung der Luft
132. Geobiology
133. Geocarto International
134. GeoHealth
135. Geomicrobiology Journal
136. Global Biogeochemical Cycles
137. Global Change Biology
138. Global Change Biology Bioenergy
139. Global Environmental Change-Human and Policy Dimensions
140. Global Nest Journal
141. Greenhouse Gases-Science and Technology
142. Grundwasser
143. Health Physics
144. Human and Ecological Risk Assessment
145. Human Dimensions of Wildlife
146. Industrial Health
147. Integrated Environmental Assessment and Management
148. International Biodeterioration & Biodegradation
149. International Journal of Biometeorology
150. International Journal of Environment and Pollution
151. International Journal of Environmental Analytical Chemistry
152. International Journal of Environmental Health Research
153. International Journal of Environmental Research
154. International Journal of Environmental Science and Technology
155. International Journal of Global Warming
156. International Journal of Life Cycle Assessment
157. International Journal of Mining Reclamation and Environment
158. International Journal of Phytoremediation
159. International Journal of Sediment Research
160. International Soil and Water Conservation Research
161. Isotopes in Environmental and Health Studies
162. Italian Journal of Agrometeorology-Rivista Italiana di Agrometeorologia
163. Journal of Aerosol Science
164. Journal of Agricultural & Environmental Ethics
165. Journal of Applied Remote Sensing
166. Journal of Arid Environments
167. Journal of Arid Land
168. Journal of Atmospheric Chemistry
169. Journal of Cleaner Production
170. Journal of Coastal Conservation
171. Journal of Contaminant Hydrology
172. Journal of Elementology
173. Journal of Environmental Engineering
174. Journal of Environmental Engineering and Landscape Management
175. Journal of Environmental Health
176. Journal of Environmental Health Science and Engineering
177. Journal of Environmental Informatics
178. Journal of Environmental Management
179. Journal of Environmental Quality
180. Journal of Environmental Radioactivity
181. Journal of Environmental Science and Health Part A-Toxic/Hazardous Substances & Environmental Engineering
182. Journal of Environmental Science and Health Part B-Pesticides Food Contaminants and Agricultural Wastes
183. Journal of Environmental Science and Health Part C-Toxicology and Carcinogenesis
184. Journal of Environmental Science and Management
185. Journal of Environmental Sciences
186. Journal of Exposure Science and Environmental Epidemiology
187. Journal of Flood Risk Management
188. Journal of Geophysical Research-Biogeosciences
189. Journal of Great Lakes Research
190. Journal of Hazardous Materials
191. Journal of Health Population and Nutrition
192. Journal of Hydro-Environment Research
193. Journal of Hydroinformatics
194. Journal of Hydrologic Engineering
195. Journal of Industrial Ecology
196. Journal of Integrative Environmental Sciences
197. Journal of Material Cycles and Waste Management
198. Journal of Mountain Science
199. Journal of Occupational and Environmental Hygiene
200. Journal of Paleolimnology
201. Journal of Radiological Protection
202. Journal of Soil Science and Plant Nutrition
203. Journal of Soils and Sediments
204. Journal of the Air & Waste Management Association
205. Journal of the Indian Society of Remote Sensing
206. Journal of Toxicology and Environmental Health-Part A-Current Issues
207. Journal of Toxicology and Environmental Health-Part B-Critical Reviews
208. Journal of Water and Health
209. Lancet Planetary Health
210. Land Degradation & Development
211. Marine Environmental Research
212. Marine Pollution Bulletin
213. Microbial Risk Analysis
214. Mires and Peat
215. Mitigation and Adaptation Strategies for Global Change
216. Mountain Research and Development
217. NanoImpact
218. Natural Resource Modeling
219. Natural Resources Forum
220. Nature Climate Change
221. Nature Reviews Earth & Environment
222. Nature Sustainability
223. Nature Water
224. Npj Clean Water
225. One Earth
226. Ozone-Science & Engineering
227. Physical Geography
228. Polar Record
229. Polish Journal of Environmental Studies
230. Radiation and Environmental Biophysics
231. Radiation Protection Dosimetry
232. Radioprotection
233. Rangeland Ecology & Management
234. Regional Environmental Change
235. Remote Sensing
236. Remote Sensing of Environment
237. Resources Conservation and Recycling
238. Reviews in Environmental Science and Bio-Technology
239. Reviews of Environmental Contamination and Toxicology
240. Reviews on Environmental Health
241. Revista Internacional de Contaminacion Ambiental
242. River Research and Applications
243. Rocznik Ochrona Srodowiska
244. SAR and QSAR in Environmental Research
245. Soil & Sediment Contamination
246. Soil Science and Plant Nutrition
247. Stochastic Environmental Research and Risk Assessment
248. Sustainability
249. Sustainability Science
250. Sustainable Chemistry and Pharmacy
251. Sustainable Environment Research
252. Toxicological and Environmental Chemistry
253. Toxics
254. Trends in Environmental Analytical Chemistry
255. Urban Climate
256. Utilities Policy
257. Vadose Zone Journal
258. Waste and Biomass Valorization
259. Waste Management
260. Waste Management & Research
261. Water
262. Water Air and Soil Pollution
263. Water and Environment Journal
264. Water Environment Research
265. Water Research
266. Water Research X
267. Water Resources and Economics
268. Water Resources Research
269. Water Science and Technology
270. Web Ecology
271. Wetlands
272. Wetlands Ecology and Management
273. Wiley Interdisciplinary Reviews-Water

<a id="scie-evolutionary-biology"></a>

### Evolutionary Biology

期刊数：51

1. American Journal of Biological Anthropology
2. American Naturalist
3. Annual Review of Ecology Evolution and Systematics
4. Anthropological Science
5. Australian Systematic Botany
6. Biochemical Systematics and Ecology
7. Biological Journal of the Linnean Society
8. Biology Letters
9. BMC Ecology and Evolution
10. Cladistics
11. Developmental Biology Advances
12. Discover Developmental Biology
13. Ecology and Evolution
14. Evolution
15. Evolution & Development
16. Evolution Letters
17. Evolution Medicine and Public Health
18. Evolutionary Applications
19. Evolutionary Bioinformatics
20. Evolutionary Biology
21. Evolutionary Ecology
22. Genome Biology and Evolution
23. Heredity
24. Insect Systematics & Evolution
25. Integrative Organismal Biology
26. Invertebrate Systematics
27. Israel Journal of Ecology & Evolution
28. Journal of Evolutionary Biochemistry and Physiology
29. Journal of Evolutionary Biology
30. Journal of Experimental Zoology Part B-Molecular and Developmental Evolution
31. Journal of Heredity
32. Journal of Human Evolution
33. Journal of Molecular Evolution
34. Journal of Systematic Palaeontology
35. Journal of Zoological Systematics and Evolutionary Research
36. Molecular Biology and Evolution
37. Molecular Ecology
38. Molecular Ecology Resources
39. Molecular Phylogenetics and Evolution
40. Nature Ecology & Evolution
41. Organisms Diversity & Evolution
42. Paleobiology
43. Plant Systematics and Evolution
44. Proceedings of the Royal Society B-Biological Sciences
45. Systematic Biology
46. Systematic Botany
47. Systematic Entomology
48. Taxon
49. Theoretical Population Biology
50. Trends in Ecology & Evolution
51. Zoologica Scripta

<a id="scie-fisheries"></a>

### Fisheries

期刊数：54

1. Acta Ichthyologica et Piscatoria
2. Aquacultural Engineering
3. Aquaculture
4. Aquaculture Economics & Management
5. Aquaculture Environment Interactions
6. Aquaculture International
7. Aquaculture Nutrition
8. Aquaculture Reports
9. Aquaculture Research
10. Aquatic Living Resources
11. Boletim do Instituto de Pesca
12. Bulletin of the European Association of Fish Pathologists
13. California Fish and Wildlife Journal
14. Canadian Journal of Fisheries and Aquatic Sciences
15. Developmental and Comparative Immunology
16. Diseases of Aquatic Organisms
17. Ecology of Freshwater Fish
18. Fish & Shellfish Immunology
19. Fish and Fisheries
20. Fish Pathology
21. Fish Physiology and Biochemistry
22. Fisheries
23. Fisheries Management and Ecology
24. Fisheries Oceanography
25. Fisheries Research
26. Fisheries Science
27. Fishery Bulletin
28. Fishes
29. ICES Journal of Marine Science
30. Ichthyological Research
31. Indian Journal of Fisheries
32. Iranian Journal of Fisheries Sciences
33. Israeli Journal of Aquaculture-Bamidgeh
34. Journal of Applied Ichthyology
35. Journal of Aquatic Animal Health
36. Journal of Fish Biology
37. Journal of Fish Diseases
38. Journal of Ichthyology
39. Journal of Shellfish Research
40. Journal of the World Aquaculture Society
41. Knowledge and Management of Aquatic Ecosystems
42. Latin American Journal of Aquatic Research
43. Marine and Coastal Fisheries
44. Marine and Freshwater Research
45. Marine Resource Economics
46. New Zealand Journal of Marine and Freshwater Research
47. Nippon Suisan Gakkaishi
48. North American Journal of Aquaculture
49. North American Journal of Fisheries Management
50. Reviews in Aquaculture
51. Reviews in Fish Biology and Fisheries
52. Reviews in Fisheries Science & Aquaculture
53. Transactions of the American Fisheries Society
54. Turkish Journal of Fisheries and Aquatic Sciences

<a id="scie-food-science-technology"></a>

### Food Science & Technology

期刊数：137

1. Acta Alimentaria
2. Agribusiness
3. Agricultural and Food Science
4. American Journal of Enology and Viticulture
5. Analytical Methods
6. Annual Review of Food Science and Technology
7. Antioxidants
8. Applied Biological Chemistry
9. Australian Journal of Grape and Wine Research
10. Bioscience Biotechnology and Biochemistry
11. Biotechnology Progress
12. British Food Journal
13. Cereal Chemistry
14. Chemical Senses
15. Ciencia e Tecnica Vitivinicola
16. Comprehensive Reviews in Food Science and Food Safety
17. Critical Reviews in Food Science and Nutrition
18. Current Opinion in Food Science
19. Current Research in Food Science
20. CyTA-Journal of Food
21. Czech Journal of Food Sciences
22. Efsa Journal
23. Emirates Journal of Food and Agriculture
24. European Food Research and Technology
25. European Journal of Lipid Science and Technology
26. Flavour and Fragrance Journal
27. Fleischwirtschaft
28. Food & Function
29. Food & Nutrition Research
30. Food Additives & Contaminants Part B-Surveillance
31. Food Additives and Contaminants Part A-Chemistry Analysis Control Exposure & Risk Assessment
32. Food Analytical Methods
33. Food and Agricultural Immunology
34. Food and Bioprocess Technology
35. Food and Bioproducts Processing
36. Food and Chemical Toxicology
37. Food and Drug Law Journal
38. Food and Energy Security
39. Food and Environmental Virology
40. Food and Nutrition Bulletin
41. Food Biophysics
42. Food Bioscience
43. Food Biotechnology
44. Food Chemistry
45. Food Chemistry-X
46. Food Control
47. Food Engineering Reviews
48. Food Hydrocolloids
49. Food Microbiology
50. Food Packaging and Shelf Life
51. Food Policy
52. Food Quality and Preference
53. Food Quality and Safety
54. Food Research International
55. Food Reviews International
56. Food Science & Nutrition
57. Food Science and Biotechnology
58. Food Science and Human Wellness
59. Food Science and Technology International
60. Food Science and Technology Research
61. Food Science of Animal Resources
62. Food Security
63. Food Structure-Netherlands
64. Food Technology and Biotechnology
65. Foodborne Pathogens and Disease
66. Foods
67. Frontiers in Sustainable Food Systems
68. Global Food Security-Agriculture Policy Economics and Environment
69. Grasas y Aceites
70. Innovative Food Science & Emerging Technologies
71. International Dairy Journal
72. International Food Research Journal
73. International Journal of Dairy Technology
74. International Journal of Food Engineering
75. International Journal of Food Microbiology
76. International Journal of Food Properties
77. International Journal of Food Science and Technology
78. International Journal of Food Sciences and Nutrition
79. International Journal of Gastronomy and Food Science
80. Irish Journal of Agricultural and Food Research
81. Journal of Agricultural and Food Chemistry
82. Journal of AOAC International
83. Journal of Aquatic Food Product Technology
84. Journal of Bioscience and Bioengineering
85. Journal of Cereal Science
86. Journal of Consumer Protection and Food Safety
87. Journal of Dairy Research
88. Journal of Dairy Science
89. Journal of Essential Oil Research
90. Journal of Food and Drug Analysis
91. Journal of Food and Nutrition Research
92. Journal of Food Biochemistry
93. Journal of Food Composition and Analysis
94. Journal of Food Engineering
95. Journal of Food Measurement and Characterization
96. Journal of Food Process Engineering
97. Journal of Food Processing and Preservation
98. Journal of Food Protection
99. Journal of Food Quality
100. Journal of Food Safety
101. Journal of Food Safety and Food Quality-Archiv für Lebensmittelhygiene
102. Journal of Food Science
103. Journal of Food Science and Technology-Mysore
104. Journal of Functional Foods
105. Journal of Insects as Food and Feed
106. Journal of Medicinal Food
107. Journal of Oil Palm Research
108. Journal of Oleo Science
109. Journal of Sensory Studies
110. Journal of Texture Studies
111. Journal of the American Oil Chemists Society
112. Journal of the American Society of Brewing Chemists
113. Journal of the Institute of Brewing
114. Journal of the Japanese Society for Food Science and Technology-Nippon Shokuhin Kagaku Kogaku Kaishi
115. Journal of the Science of Food and Agriculture
116. Journal of Wine Economics
117. Listy Cukrovarnicke a Reparske
118. Lwt-Food Science and Technology
119. Meat Science
120. Microbial Risk Analysis
121. Mitteilungen Klosterneuburg: Journal of Viticulture Oenology Pomology and Fruit Processing
122. Molecular Nutrition & Food Research
123. Natural Product Communications
124. Nature Food
125. Npj Science of Food
126. Oeno One
127. Packaging Technology and Science
128. Plant Foods for Human Nutrition
129. Polish Journal of Food and Nutrition Sciences
130. Postharvest Biology and Technology
131. Quality Assurance and Safety of Crops & Foods
132. Rivista Italiana delle Sostanze Grasse
133. South African Journal of Enology and Viticulture
134. Starch-Starke
135. Sugar Industry International
136. Trends in Food Science & Technology
137. World Mycotoxin Journal

<a id="scie-forestry"></a>

### Forestry

期刊数：69

1. Agricultural and Forest Meteorology
2. Agroforestry Systems
3. Annals of Forest Research
4. Annals of Forest Science
5. Applied Vegetation Science
6. Australian Forestry
7. Austrian Journal of Forest Science
8. Baltic Forestry
9. Bois et Forets des Tropiques
10. Bosque
11. Canadian Journal of Forest Research
12. Cerne
13. Ciencia Florestal
14. Croatian Journal of Forest Engineering
15. Current Forestry Reports
16. Dendrobiology
17. Dendrochronologia
18. European Journal of Forest Research
19. European Journal of Wood and Wood Products
20. Fire Ecology
21. Fire-Switzerland
22. Forest Ecology and Management
23. Forest Ecosystems
24. Forest Pathology
25. Forest Policy and Economics
26. Forest Products Journal
27. Forest Science
28. Forest Systems
29. Forestry
30. Forestry Chronicle
31. Forests
32. Frontiers in Forests and Global Change
33. Holzforschung
34. IAWA Journal
35. iForest-Biogeosciences and Forestry
36. International Forestry Review
37. International Journal of Forest Engineering
38. International Journal of Wildland Fire
39. Journal of Forest Economics
40. Journal of Forest Research
41. Journal of Forestry
42. Journal of Forestry Research
43. Journal of Plant Ecology
44. Journal of Sustainable Forestry
45. Journal of Tropical Forest Science
46. Journal of Vegetation Science
47. Journal of Wood Science
48. Madera y Bosques
49. Natural Areas Journal
50. New Forests
51. New Zealand Journal of Forestry Science
52. Plant Ecology
53. Revista Arvore
54. Revista Chapingo Serie Ciencias Forestales y del Ambiente
55. Scandinavian Journal of Forest Research
56. Scientia Forestalis
57. Silva Fennica
58. Silvae Genetica
59. Small-Scale Forestry
60. Southern Forests
61. Sumarski List
62. Sylwan
63. Tree Genetics & Genomes
64. Tree Physiology
65. Tree-Ring Research
66. Trees-Structure and Function
67. Urban Forestry & Urban Greening
68. Wood and Fiber Science
69. Wood Science and Technology

<a id="scie-gastroenterology-hepatology"></a>

### Gastroenterology & Hepatology

期刊数：93

1. Acta Gastro-Enterologica Belgica
2. Alimentary Pharmacology & Therapeutics
3. American Journal of Gastroenterology
4. American Journal of Physiology-Gastrointestinal and Liver Physiology
5. Annals of Gastroenterological Surgery
6. Annals of Hepatology
7. Arab Journal of Gastroenterology
8. Best Practice & Research Clinical Gastroenterology
9. BMC Gastroenterology
10. Canadian Journal of Gastroenterology and Hepatology
11. Cellular and Molecular Gastroenterology and Hepatology
12. Clinical and Molecular Hepatology
13. Clinical and Translational Gastroenterology
14. Clinical Gastroenterology and Hepatology
15. Clinics and Research in Hepatology and Gastroenterology
16. Clinics in Colon and Rectal Surgery
17. Clinics in Liver Disease
18. Colorectal Disease
19. Current Opinion in Gastroenterology
20. Digestion
21. Digestive and Liver Disease
22. Digestive Diseases
23. Digestive Diseases and Sciences
24. Digestive Endoscopy
25. Digestive Surgery
26. Diseases of the Colon & Rectum
27. Diseases of the Esophagus
28. Endoscopic Ultrasound
29. Endoscopy
30. Esophagus
31. European Journal of Gastroenterology & Hepatology
32. Expert Review of Gastroenterology & Hepatology
33. Gastric Cancer
34. Gastroenterologia y Hepatologia
35. Gastroenterology
36. Gastroenterology Clinics of North America
37. Gastroenterology Nursing
38. Gastroenterology Report
39. Gastroenterology Research and Practice
40. Gastrointestinal Endoscopy
41. Gut
42. Gut and Liver
43. Gut Microbes
44. Gut Pathogens
45. Helicobacter
46. Hepatitis Monthly
47. Hepatobiliary & Pancreatic Diseases International
48. HepatoBiliary Surgery and Nutrition
49. Hepatology
50. Hepatology Communications
51. Hepatology International
52. Hepatology Research
53. Hpb
54. Inflammatory Bowel Diseases
55. International Journal of Colorectal Disease
56. JHEP Reports
57. Journal of Clinical and Translational Hepatology
58. Journal of Clinical Gastroenterology
59. Journal of Crohns & Colitis
60. Journal of Digestive Diseases
61. Journal of Gastric Cancer
62. Journal of Gastroenterology
63. Journal of Gastroenterology and Hepatology
64. Journal of Gastrointestinal and Liver Diseases
65. Journal of Gastrointestinal Oncology
66. Journal of Gastrointestinal Surgery
67. Journal of Hepato-Biliary-Pancreatic Sciences
68. Journal of Hepatology
69. Journal of Neurogastroenterology and Motility
70. Journal of Pediatric Gastroenterology and Nutrition
71. Journal of Viral Hepatitis
72. Lancet Gastroenterology & Hepatology
73. Liver Cancer
74. Liver International
75. Liver Transplantation
76. Minerva Gastroenterology
77. Nature Reviews Gastroenterology & Hepatology
78. Neurogastroenterology and Motility
79. Pancreas
80. Pancreatology
81. Revista Espanola de Enfermedades Digestivas
82. Saudi Journal of Gastroenterology
83. Scandinavian Journal of Gastroenterology
84. Seminars in Liver Disease
85. Techniques in Coloproctology
86. Therapeutic Advances in Gastroenterology
87. Turkish Journal of Gastroenterology
88. United European Gastroenterology Journal
89. Visceral Medicine
90. World Journal of Gastroenterology
91. World Journal of Gastrointestinal Oncology
92. World Journal of Gastrointestinal Surgery
93. Zeitschrift für Gastroenterologie

<a id="scie-genetics-heredity"></a>

### Genetics & Heredity

期刊数：169

1. American Journal of Human Genetics
2. American Journal of Medical Genetics Part A
3. American Journal of Medical Genetics Part B-Neuropsychiatric Genetics
4. American Journal of Medical Genetics Part C-Seminars in Medical Genetics
5. Animal Genetics
6. Annals of Human Genetics
7. Annual Review of Genetics
8. Annual Review of Genomics and Human Genetics
9. Balkan Journal of Medical Genetics
10. Behavior Genetics
11. Biochemical Genetics
12. Biology of Sex Differences
13. Biotechnology and Genetic Engineering Reviews
14. BMC Ecology and Evolution
15. BMC Genomic Data
16. BMC Genomics
17. BMC Medical Genomics
18. Briefings in Functional Genomics
19. Cancer Gene Therapy
20. Cancer Genetics
21. Cancer Genomics & Proteomics
22. Cellular Reprogramming
23. Chromosome Research-Biology of the Nucleus
24. Circulation-Genomic and Precision Medicine
25. Clinical Dysmorphology
26. Clinical Epigenetics
27. Clinical Genetics
28. Comparative Biochemistry and Physiology D-Genomics & Proteomics
29. Comparative Cytogenetics
30. Conservation Genetics
31. Conservation Genetics Resources
32. CRISPR Journal
33. Critical Reviews in Eukaryotic Gene Expression
34. Current Gene Therapy
35. Current Genomics
36. Current Opinion in Genetics & Development
37. Cytogenetic and Genome Research
38. Cytologia
39. Cytology and Genetics
40. Discover Genetics and Evolution
41. DNA and Cell Biology
42. DNA Repair
43. DNA Research
44. Environmental and Molecular Mutagenesis
45. Environmental Microbiome
46. Epigenetics
47. Epigenetics & Chromatin
48. Epigenomics
49. European Journal of Human Genetics
50. European Journal of Medical Genetics
51. Evolution
52. Evolution & Development
53. Evolutionary Ecology
54. Familial Cancer
55. Forensic Science International-Genetics
56. Frontiers in Genetics
57. Functional & Integrative Genomics
58. Fungal Genetics and Biology
59. G3-Genes Genomes Genetics
60. Gene
61. Gene Expression Patterns
62. Gene Therapy
63. Genes
64. Genes & Development
65. Genes & Diseases
66. Genes & Genetic Systems
67. Genes & Genomics
68. Genes and Environment
69. Genes and Immunity
70. Genes and Nutrition
71. Genes Chromosomes & Cancer
72. Genes to Cells
73. Genesis
74. Genetic Epidemiology
75. Genetic Testing and Molecular Biomarkers
76. Genetica
77. Genetics
78. Genetics and Molecular Biology
79. Genetics in Medicine
80. Genetics Research
81. Genetics Selection Evolution
82. Genome
83. Genome Biology
84. Genome Biology and Evolution
85. Genome Medicine
86. Genome Research
87. Genomics
88. Genomics Proteomics & Bioinformatics
89. Hereditas
90. Heredity
91. Horticulture Research
92. Human Biology
93. Human Gene Therapy
94. Human Genetics
95. Human Genomics
96. Human Heredity
97. Human Molecular Genetics
98. Human Mutation
99. Immunogenetics
100. International Journal of Genomics
101. International Journal of Human Genetics
102. International Journal of Immunogenetics
103. Journal of Applied Genetics
104. Journal of Assisted Reproduction and Genetics
105. Journal of Evolutionary Biology
106. Journal of Gene Medicine
107. Journal of Genetic Counseling
108. Journal of Genetics
109. Journal of Genetics and Genomics
110. Journal of Heredity
111. Journal of Human Genetics
112. Journal of Inherited Metabolic Disease
113. Journal of Medical Genetics
114. Journal of Molecular Evolution
115. Journal of Molecular Medicine-Jmm
116. Journal of Neurogenetics
117. Lifestyle Genomics
118. Mammalian Genome
119. Marine Genomics
120. Medizinische Genetik
121. Microbial Genomics
122. Mitochondrial DNA Part A
123. Mitochondrial DNA Part B-Resources
124. Mitochondrion
125. Mobile DNA
126. Molecular Autism
127. Molecular Biology and Evolution
128. Molecular Breeding
129. Molecular Cytogenetics
130. Molecular Diagnosis & Therapy
131. Molecular Genetics & Genomic Medicine
132. Molecular Genetics and Genomics
133. Molecular Genetics and Metabolism
134. Molecular Genetics and Metabolism Reports
135. Molecular Phylogenetics and Evolution
136. Molecular Syndromology
137. Molecular Therapy
138. Mutagenesis
139. Mutation Research-Fundamental and Molecular Mechanisms of Mutagenesis
140. Mutation Research-Genetic Toxicology and Environmental Mutagenesis
141. Mutation Research-Reviews in Mutation Research
142. Nature Genetics
143. Nature Reviews Genetics
144. Neurogenetics
145. Neurology-Genetics
146. New Genetics and Society
147. Npj Genomic Medicine
148. Omics-A Journal of Integrative Biology
149. Oncogene
150. Ophthalmic Genetics
151. Orphanet Journal of Rare Diseases
152. Pharmacogenetics and Genomics
153. Pharmacogenomics Journal
154. Physiological Genomics
155. Plant Genome
156. Plasmid
157. PLOS Genetics
158. Prenatal Diagnosis
159. Psychiatric Genetics
160. Public Health Genomics
161. Russian Journal of Genetics
162. Silvae Genetica
163. Theoretical and Applied Genetics
164. Theoretical Population Biology
165. Tree Genetics & Genomes
166. Trends in Ecology & Evolution
167. Trends in Genetics
168. Twin Research and Human Genetics
169. Virus Genes

<a id="scie-geochemistry-geophysics"></a>

### Geochemistry & Geophysics

期刊数：87

1. ACS Earth and Space Chemistry
2. Acta Geodaetica et Geophysica
3. Acta Geodynamica et Geomaterialia
4. Acta Geophysica
5. American Mineralogist
6. Annals of Geophysics
7. Annual Review of Marine Science
8. Applied Geochemistry
9. Applied Geophysics
10. Aquatic Geochemistry
11. Astronomy & Geophysics
12. Atmospheric Science Letters
13. Biogeochemical Advances
14. Bulletin of Geophysics and Oceanography
15. Bulletin of the Seismological Society of America
16. Chemical Geology
17. Chinese Journal of Geophysics-Chinese Edition
18. Contributions to Mineralogy and Petrology
19. Dynamics of Atmospheres and Oceans
20. Earth and Planetary Science Letters
21. Economic Geology
22. Elements
23. Exploration Geophysics
24. Geochemical Journal
25. Geochemical Perspectives
26. Geochemical Perspectives Letters
27. Geochemistry
28. Geochemistry Geophysics Geosystems
29. Geochemistry International
30. Geochemistry-Exploration Environment Analysis
31. Geochimica et Cosmochimica Acta
32. Geofisica Internacional
33. Geofizika
34. Geofluids
35. Geomagnetism and Aeronomy
36. Geophysical and Astrophysical Fluid Dynamics
37. Geophysical Journal International
38. Geophysical Prospecting
39. Geophysics
40. Geostandards and Geoanalytical Research
41. Geotectonics
42. IEEE Geoscience and Remote Sensing Letters
43. IEEE Geoscience and Remote Sensing Magazine
44. IEEE Transactions on Geoscience and Remote Sensing
45. Interpretation-a Journal of Subsurface Characterization
46. Izvestiya-Physics of the Solid Earth
47. Journal of Atmospheric and Solar-Terrestrial Physics
48. Journal of Earthquake and Tsunami
49. Journal of Environmental and Engineering Geophysics
50. Journal of Geochemical Exploration
51. Journal of Geodesy
52. Journal of Geodynamics
53. Journal of Geophysical Research-Planets
54. Journal of Geophysical Research-Solid Earth
55. Journal of Geophysics and Engineering
56. Journal of Geosciences
57. Journal of Petrology
58. Journal of Seismic Exploration
59. Journal of Seismology
60. Journal of Space Weather and Space Climate
61. Journal of Volcanology and Seismology
62. Lithology and Mineral Resources
63. Lithos
64. Lithosphere
65. Marine Geodesy
66. Marine Geophysical Research
67. Meteoritics & Planetary Science
68. Mineralium Deposita
69. Mineralogy and Petrology
70. Minerals
71. Near Surface Geophysics
72. Organic Geochemistry
73. Periodico di Mineralogia
74. Petrology
75. Petrophysics
76. Physics of the Earth and Planetary Interiors
77. Pure and Applied Geophysics
78. Radio Science
79. Radiocarbon
80. Reviews of Geophysics
81. Seismological Research Letters
82. Solid Earth
83. Space Weather-the International Journal of Research and Applications
84. Studia Geophysica et Geodaetica
85. Surveys in Geophysics
86. Tectonics
87. Tectonophysics

<a id="scie-geography-physical"></a>

### Geography, Physical

期刊数：50

1. Acta Geographica Slovenica-Geografski Zbornik
2. Aeolian Research
3. Annals of Glaciology
4. Antarctic Science
5. Anthropocene
6. Arctic
7. Arctic Antarctic and Alpine Research
8. Boreas
9. Cryosphere
10. Dendrochronologia
11. Earth Surface Dynamics
12. Earth Surface Processes and Landforms
13. Erde
14. Erdkunde
15. Geografia Fisica e Dinamica Quaternaria
16. Geografiska Annaler Series A-Physical Geography
17. GeoInformatica
18. Geomorphologie-Relief Processus Environnement
19. Geomorphology
20. GIScience & Remote Sensing
21. Global and Planetary Change
22. Global Ecology and Biogeography
23. Holocene
24. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing
25. International Journal of Applied Earth Observation and Geoinformation
26. International Journal of Digital Earth
27. International Journal of Geographical Information Science
28. ISPRS International Journal of Geo-Information
29. ISPRS Journal of Photogrammetry and Remote Sensing
30. Journal of Biogeography
31. Journal of Geographical Sciences
32. Journal of Glaciology
33. Journal of Maps
34. Journal of Quaternary Science
35. Journal of Spatial Science
36. Landscape and Urban Planning
37. Landscape Ecology
38. Mountain Research and Development
39. Palaeogeography Palaeoclimatology Palaeoecology
40. Permafrost and Periglacial Processes
41. Photogrammetric Engineering and Remote Sensing
42. Photogrammetric Record
43. Physical Geography
44. Progress in Physical Geography-Earth and Environment
45. Quaternary Geochronology
46. Quaternary International
47. Quaternary Research
48. Quaternary Science Reviews
49. Revista de Geografia Norte Grande
50. Zeitschrift für Geomorphologie

<a id="scie-geology"></a>

### Geology

期刊数：49

1. Acta Geologica Polonica
2. Acta Petrologica Sinica
3. Andean Geology
4. Annales Societatis Geologorum Poloniae
5. Atlantic Geology
6. Baltica
7. Boletin de la Sociedad Geologica Mexicana
8. Bulletin of the Geological Society of Finland
9. Carbonates and Evaporites
10. Carnets Geol.
11. Cretaceous Research
12. Depositional Record
13. Estudios Geologicos-Madrid
14. Facies
15. Geofluids
16. Geografiska Annaler Series A-Physical Geography
17. Geologia Croatica
18. Geologica Acta
19. Geologica Belgica
20. Geologica Carpathica
21. Geological Quarterly
22. Geology
23. Geology of Ore Deposits
24. GEUS Bulletin
25. Gff
26. Himalayan Geology
27. International Geology Review
28. Journal of Geology
29. Journal of Iberian Geology
30. Journal of Metamorphic Geology
31. Journal of Sedimentary Research
32. Lithology and Mineral Resources
33. Lithosphere
34. New Zealand Journal of Geology and Geophysics
35. Newsletters on Stratigraphy
36. Ofioliti
37. Ore Geology Reviews
38. Palaios
39. Permafrost and Periglacial Processes
40. Proceedings of the Geologists Association
41. Proceedings of the Yorkshire Geological Society
42. Resource Geology
43. Rivista Italiana di Paleontologia e Stratigrafia
44. Scottish Journal of Geology
45. Sedimentary Geology
46. Sedimentology
47. South African Journal of Geology
48. Stratigraphy
49. Stratigraphy and Geological Correlation

<a id="scie-geosciences-multidisciplinary"></a>

### Geosciences, Multidisciplinary

期刊数：199

1. AAPG Bulletin
2. Acta Carsologica
3. Acta Geologica Sinica-English Edition
4. Acta Montanistica Slovaca
5. Advances in Space Research
6. AGU Advances
7. All Earth
8. American Journal of Science
9. Annales Geophysicae
10. Annals of Glaciology
11. Annual Review of Earth and Planetary Sciences
12. Antarctic Science
13. Anthropocene
14. Anthropocene Review
15. Archaeological and Anthropological Sciences
16. Archaeological Prospection
17. Archaeometry
18. ArchéoSciences-Revue d Archeometrie
19. Astrobiology
20. Australian Journal of Earth Sciences
21. Austrian Journal of Earth Sciences
22. Basin Research
23. Biogeochemistry
24. Biogeosciences
25. Boreas
26. Brazilian Journal of Geology
27. BSGF-Earth Sciences Bulletin
28. Bulletin of Earthquake Engineering
29. Bulletin of Engineering Geology and the Environment
30. Bulletin of Geosciences
31. Bulletin of the Geological Society of Denmark
32. Bulletin of Volcanology
33. Canadian Geotechnical Journal
34. Canadian Journal of Earth Sciences
35. Catena
36. Clay Minerals
37. Clays and Clay Minerals
38. Climate of the Past
39. Cold Regions Science and Technology
40. Communications Earth & Environment
41. Comptes Rendus Geoscience
42. Computational Geosciences
43. Computers & Geosciences
44. Computers and Geotechnics
45. Cryosphere
46. Discover Space
47. Doklady Earth Sciences
48. Earth and Environmental Science Transactions of the Royal Society of Edinburgh
49. Earth and Space Science
50. Earth Interactions
51. Earth Planets and Space
52. Earth Science Informatics
53. Earth Sciences History
54. Earth Sciences Research Journal
55. Earth Surface Dynamics
56. Earth Surface Processes and Landforms
57. Earth System Dynamics
58. Earth System Science Data
59. Earth-Science Reviews
60. Earths Future
61. Engineering Geology
62. Environmental & Engineering Geoscience
63. Environmental Archaeology
64. Environmental Earth Sciences
65. Episodes
66. Erde
67. Estonian Journal of Earth Sciences
68. Frontiers in Earth Science
69. Frontiers of Earth Science
70. Geo-Marine Letters
71. Geoarchaeology-an International Journal
72. Geobiology
73. Geocarto International
74. Geochronometria
75. Geofizika
76. Geoheritage
77. Geological Journal
78. Geological Magazine
79. Geological Society of America Bulletin
80. Geomatics Natural Hazards & Risk
81. Geomechanics and Geophysics for Geo-Energy and Geo-Resources
82. Geomechanics for Energy and the Environment
83. Geomicrobiology Journal
84. Geomorphologie-Relief Processus Environnement
85. Geomorphology
86. Geophysical Research Letters
87. Georisk-Assessment and Management of Risk for Engineered Systems and Geohazards
88. Geoscience Canada
89. Geoscience Data Journal
90. Geoscience Frontiers
91. Geoscience Letters
92. Geosciences Journal
93. Geoscientific Instrumentation Methods and Data Systems
94. Geoscientific Model Development
95. Geosphere
96. Geosynthetics International
97. Geotechnical Testing Journal
98. Geotextiles and Geomembranes
99. Geothermal Energy
100. Geothermics
101. Global and Planetary Change
102. Global Biogeochemical Cycles
103. Gondwana Research
104. Groundwater
105. History of Geo- and Space Sciences
106. Holocene
107. Hydrogeology Journal
108. Hydrology and Earth System Sciences
109. International Journal of Astrobiology
110. International Journal of Coal Geology
111. International Journal of Disaster Risk Reduction
112. International Journal of Disaster Risk Science
113. International Journal of Earth Sciences
114. International Journal of Speleology
115. Island Arc
116. ISPRS Journal of Photogrammetry and Remote Sensing
117. Italian Journal of Geosciences
118. Jokull
119. Journal of African Earth Sciences
120. Journal of Applied Geophysics
121. Journal of Archaeological Science
122. Journal of Asian Earth Sciences
123. Journal of Cave and Karst Studies
124. Journal of Cold Regions Engineering
125. Journal of Contaminant Hydrology
126. Journal of Cultural Heritage
127. Journal of Earth Science
128. Journal of Earth System Science
129. Journal of Earthquake Engineering
130. Journal of Geophysical Research-Biogeosciences
131. Journal of Geophysical Research-Earth Surface
132. Journal of Geotechnical and Geoenvironmental Engineering
133. Journal of Glaciology
134. Journal of Hydrology
135. Journal of Marine Systems
136. Journal of Palaeogeography-English
137. Journal of Paleolimnology
138. Journal of Petroleum Exploration and Production Technology
139. Journal of Petroleum Geology
140. Journal of Quaternary Science
141. Journal of South American Earth Sciences
142. Journal of Structural Geology
143. Journal of the American Water Resources Association
144. Journal of the Geological Society
145. Journal of the Geological Society of India
146. Journal of Volcanology and Geothermal Research
147. Landscape Ecology
148. Landslides
149. Marine Geology
150. Marine Geoscience and Energy Resources
151. Mathematical Geosciences
152. Natural Hazards
153. Natural Hazards and Earth System Sciences
154. Natural Hazards Review
155. Natural Resources Research
156. Nature Geoscience
157. Nature Reviews Earth & Environment
158. Netherlands Journal of Geosciences
159. New Zealand Journal of Geology and Geophysics
160. Nonlinear Processes in Geophysics
161. Norwegian Journal of Geology
162. Open Geosciences
163. Palaeogeography Palaeoclimatology Palaeoecology
164. Paleoceanography and Paleoclimatology
165. Petroleum Exploration and Development
166. Petroleum Geoscience
167. Photogrammetric Engineering and Remote Sensing
168. Photogrammetric Record
169. Physical Geography
170. Physics and Chemistry of the Earth
171. Polar Research
172. Polar Science
173. Polish Polar Research
174. Precambrian Research
175. Proceedings of the Institution of Civil Engineers-Geotechnical Engineering
176. Progress in Earth and Planetary Science
177. Progress in Physical Geography-Earth and Environment
178. Quarterly Journal of Engineering Geology and Hydrogeology
179. Quaternaire
180. Quaternary Geochronology
181. Quaternary International
182. Quaternary Research
183. Quaternary Science Reviews
184. Remote Sensing
185. Revista Mexicana de Ciencias Geologicas
186. Rock Mechanics and Rock Engineering
187. Russian Geology and Geophysics
188. Russian Journal of Pacific Geology
189. Science China-Earth Sciences
190. Soil Dynamics and Earthquake Engineering
191. Soils and Foundations
192. Spatial Statistics
193. Survey Review
194. Swiss Journal of Geosciences
195. Terra Nova
196. Terrestrial Atmospheric and Oceanic Sciences
197. Turkish Journal of Earth Sciences
198. Zeitschrift der Deutschen Gesellschaft für Geowissenschaften
199. Zeitschrift für Geomorphologie

<a id="scie-geriatrics-gerontology"></a>

### Geriatrics & Gerontology

期刊数：56

1. Age and Ageing
2. Ageing Research Reviews
3. Aging & Mental Health
4. Aging and Disease
5. Aging Cell
6. Aging Clinical and Experimental Research
7. American Journal of Alzheimers Disease and Other Dementias
8. American Journal of Geriatric Psychiatry
9. Archives of Gerontology and Geriatrics
10. Australasian Journal on Ageing
11. Biogerontology
12. BMC Geriatrics
13. Clinical Gerontologist
14. Clinical Interventions in Aging
15. Clinics in Geriatric Medicine
16. Dementia and Geriatric Cognitive Disorders
17. Drugs & Aging
18. European Geriatric Medicine
19. European Review of Aging and Physical Activity
20. Experimental Aging Research
21. Experimental Gerontology
22. Frontiers in Aging Neuroscience
23. Geriatric Nursing
24. Geriatric Orthopaedic Surgery & Rehabilitation
25. Geriatrics & Gerontology International
26. Gerodontology
27. Gerontology
28. GeroScience
29. Immunity & Ageing
30. Innovation in Aging
31. International Journal of Geriatric Psychiatry
32. International Journal of Gerontology
33. International Journal of Older People Nursing
34. International Psychogeriatrics
35. JMIR Aging
36. Journal of Aging and Physical Activity
37. Journal of Cachexia Sarcopenia and Muscle
38. Journal of Geriatric Cardiology
39. Journal of Geriatric Oncology
40. Journal of Geriatric Physical Therapy
41. Journal of Geriatric Psychiatry and Neurology
42. Journal of Gerontological Nursing
43. Journal of Nutrition Health & Aging
44. Journal of the American Geriatrics Society
45. Journal of the American Medical Directors Association
46. Journals of Gerontology Series A-Biological Sciences and Medical Sciences
47. Journals of Gerontology Series B-Psychological Sciences and Social Sciences
48. Lancet Healthy Longevity
49. Maturitas
50. Mechanisms of Ageing and Development
51. Nature Aging
52. Neurobiology of Aging
53. Psychogeriatrics
54. Rejuvenation Research
55. Turkish Journal of Geriatrics-Turk Geriatri Dergisi
56. Zeitschrift für Gerontologie und Geriatrie

<a id="scie-green-sustainable-science-technology"></a>

### Green & Sustainable Science & Technology

期刊数：47

1. ACS Sustainable Chemistry & Engineering
2. Advanced Sustainable Systems
3. Agroecology and Sustainable Food Systems
4. Agronomy for Sustainable Development
5. ChemSusChem
6. Clean Technologies and Environmental Policy
7. Clean-Soil Air Water
8. Current Opinion in Environmental Sustainability
9. Current Opinion in Green and Sustainable Chemistry
10. EcoMat
11. Energy Efficiency
12. Energy for Sustainable Development
13. Energy Sustainability and Society
14. Environment Development and Sustainability
15. Environmental Progress & Sustainable Energy
16. Environmental Science and Ecotechnology
17. Green Chemistry
18. Green Chemistry Letters and Reviews
19. Green Energy & Environment
20. Green Materials
21. Green Processing and Synthesis
22. IEEE Transactions on Sustainable Energy
23. IET Renewable Power Generation
24. International Journal of Agricultural Sustainability
25. International Journal of Green Energy
26. International Journal of Greenhouse Gas Control
27. International Journal of Precision Engineering and Manufacturing-Green Technology
28. International Journal of Sustainable Development and World Ecology
29. Journal of Cleaner Production
30. Journal of Industrial Ecology
31. Journal of Renewable and Sustainable Energy
32. Journal of Sustainable Cement-Based Materials
33. Journal of Sustainable Metallurgy
34. Materials Today Sustainability
35. One Earth
36. Proceedings of the Institution of Civil Engineers-Engineering Sustainability
37. Renewable & Sustainable Energy Reviews
38. Renewable Energy
39. SusMat
40. Sustainability
41. Sustainability Science
42. Sustainable Chemistry and Pharmacy
43. Sustainable Cities and Society
44. Sustainable Energy Technologies and Assessments
45. Sustainable Environment Research
46. Sustainable Materials and Technologies
47. Sustainable Production and Consumption

<a id="scie-health-care-sciences-services"></a>

### Health Care Sciences & Services

期刊数：107

1. Academic Medicine
2. Advances in Health Sciences Education
3. American Health and Drug Benefits
4. American Journal of Hospice & Palliative Medicine
5. American Journal of Managed Care
6. American Journal of Medical Quality
7. Applied Health Economics and Health Policy
8. Australian Health Review
9. Australian Journal of Primary Health
10. BMC Health Services Research
11. BMC Medical Research Methodology
12. BMC Palliative Care
13. BMJ Quality & Safety
14. BMJ Supportive & Palliative Care
15. Bulletin of the History of Medicine
16. Cambridge Quarterly of Healthcare Ethics
17. Chronic Illness
18. Current Opinion in Supportive and Palliative Care
19. Digital Health
20. Disability and Health Journal
21. Eastern Mediterranean Health Journal
22. European Journal of Cancer Care
23. Evaluation & the Health Professions
24. Expert Review of Pharmacoeconomics & Outcomes Research
25. Families Systems & Health
26. Gaceta Sanitaria
27. Geospatial Health
28. Hastings Center Report
29. Health Affairs
30. Health and Quality of Life Outcomes
31. Health Economics
32. Health Expectations
33. Health Informatics Journal
34. Health Policy
35. Health Policy and Planning
36. Health Services Research
37. Health Technology Assessment
38. Healthcare
39. Implementation Science
40. Informatics for Health & Social Care
41. Inquiry-the Journal of Health Care Organization Provision and Financing
42. International Journal for Quality in Health Care
43. International Journal of Health Policy and Management
44. International Journal of Integrated Care
45. International Journal of Medical Informatics
46. International Journal of Social Determinants of Health and Health Services
47. International Journal of Technology Assessment in Health Care
48. Internet Interventions-the Application of Information Technology in Mental and Behavioural Health
49. JAMA Health Forum
50. JBI Evidence Implementation
51. JMIR Mhealth and Uhealth
52. JMIR Serious Games
53. Journal for Healthcare Quality
54. Journal of Behavioral Health Services & Research
55. Journal of Clinical Epidemiology
56. Journal of Comparative Effectiveness Research
57. Journal of Continuing Education in the Health Professions
58. Journal of Evaluation in Clinical Practice
59. Journal of General Internal Medicine
60. Journal of Health Economics
61. Journal of Health Politics Policy and Law
62. Journal of Interprofessional Care
63. Journal of Managed Care & Specialty Pharmacy
64. Journal of Manipulative and Physiological Therapeutics
65. Journal of Medical Economics
66. Journal of Medical Internet Research
67. Journal of Medical Systems
68. Journal of Multidisciplinary Healthcare
69. Journal of Pain and Symptom Management
70. Journal of Palliative Care
71. Journal of Palliative Medicine
72. Journal of Patient Safety
73. Journal of Public Health Policy
74. Journal of Rural Health
75. Journal of School Health
76. Journal of Telemedicine and Telecare
77. Journal of the American Association of Nurse Practitioners
78. Journal of the American Medical Informatics Association
79. Journal of the History of Medicine and Allied Sciences
80. Lancet Regional Health-Europe
81. Lancet Regional Health-Western Pacific
82. Medical Care
83. Medical Care Research and Review
84. Medical Decision Making
85. Medical Education
86. Medical History
87. Medical Teacher
88. Methods of Information in Medicine
89. Milbank Quarterly
90. Npj Digital Medicine
91. Palliative Medicine
92. Patient-Patient Centered Outcomes Research
93. Perspectives on Medical Education
94. PharmacoEconomics
95. Population Health Management
96. Quality Management in Health Care
97. Quality of Life Research
98. Risk Management and Healthcare Policy
99. Scandinavian Journal of Primary Health Care
100. Simulation in Healthcare-Journal of the Society for Simulation in Healthcare
101. Statistical Methods in Medical Research
102. Supportive Care in Cancer
103. Teaching and Learning in Medicine
104. Technology and Health Care
105. Telemedicine and e-Health
106. Therapeutics and Clinical Risk Management
107. Value in Health

<a id="scie-hematology"></a>

### Hematology

期刊数：78

1. Acta Haematologica
2. American Journal of Hematology
3. Annals of Hematology
4. Arteriosclerosis Thrombosis and Vascular Biology
5. Best Practice & Research Clinical Haematology
6. Biorheology
7. Blood
8. Blood Advances
9. Blood Cancer Journal
10. Blood Cells Molecules and Diseases
11. Blood Coagulation & Fibrinolysis
12. Blood Purification
13. Blood Reviews
14. Blood Transfusion
15. Bone Marrow Transplantation
16. British Journal of Haematology
17. Circulation Research
18. Clinical and Applied Thrombosis-Hemostasis
19. Clinical Hemorheology and Microcirculation
20. Clinical Lymphoma Myeloma & Leukemia
21. Critical Reviews in Oncology Hematology
22. Current Hematologic Malignancy Reports
23. Current Opinion in Hematology
24. Cytotherapy
25. European Journal of Haematology
26. Experimental Hematology
27. Experimental Hematology & Oncology
28. Expert Review of Hematology
29. Gematologiya i Transfuziologiya
30. Haematologica
31. Haemophilia
32. Hamostaseologie
33. HemaSphere
34. Hematological Oncology
35. Hematology
36. Hematology-American Society of Hematology Education Program
37. Hematology-Oncology Clinics of North America
38. Hemoglobin
39. Indian Journal of Hematology and Blood Transfusion
40. International Journal of Hematology
41. International Journal of Laboratory Hematology
42. Journal of Cerebral Blood Flow and Metabolism
43. Journal of Clinical Apheresis
44. Journal of Hematology & Oncology
45. Journal of Hematopathology
46. Journal of Leukocyte Biology
47. Journal of Pediatric Hematology Oncology
48. Journal of Thrombosis and Haemostasis
49. Journal of Thrombosis and Thrombolysis
50. Lancet Haematology
51. Leukemia
52. Leukemia & Lymphoma
53. Leukemia Research
54. Mediterranean Journal of Hematology and Infectious Diseases
55. Microcirculation
56. Pediatric Blood & Cancer
57. Pediatric Hematology and Oncology
58. Platelets
59. Research and Practice in Thrombosis and Haemostasis
60. Seminars in Hematology
61. Seminars in Thrombosis and Hemostasis
62. Shock
63. STEM Cells
64. STEM Cells and Development
65. Therapeutic Advances in Hematology
66. Therapeutic Apheresis and Dialysis
67. Thrombosis and Haemostasis
68. Thrombosis Journal
69. Thrombosis Research
70. Transfusion
71. Transfusion and Apheresis Science
72. Transfusion Clinique et Biologique
73. Transfusion Medicine
74. Transfusion Medicine and Hemotherapy
75. Transfusion Medicine Reviews
76. Transplantation and Cellular Therapy
77. Turkish Journal of Hematology
78. Vox Sanguinis

<a id="scie-history-philosophy-of-science"></a>

### History & Philosophy of Science

期刊数：60

1. Agricultural History
2. Agriculture and Human Values
3. Ambix
4. Annals of Science
5. Archive for History of Exact Sciences
6. Archives of Natural History
7. Berichte zur Wissenschaftsgeschichte
8. Biology & Philosophy
9. Biosemiotics
10. Bollettino di Storia delle Scienze Matematiche
11. British Journal for the Philosophy of Science
12. Bulletin of the History of Medicine
13. Centaurus
14. Cryptologia
15. Dynamis
16. Early Science and Medicine
17. Earth Sciences History
18. Endeavour
19. Engineering Studies
20. European Journal for Philosophy of Science
21. European Physical Journal H
22. Foundations of Chemistry
23. Foundations of Science
24. Herald of the Russian Academy of Sciences
25. Historia Mathematica
26. Historical Records of Australian Science
27. Historical Studies in the Natural Sciences
28. History and Philosophy of Logic
29. History and Philosophy of the Life Sciences
30. History of Geo- and Space Sciences
31. History of Science
32. History of the Human Sciences
33. IEEE Annals of the History of Computing
34. Isis
35. Journal for the History of Astronomy
36. Journal of Agricultural & Environmental Ethics
37. Journal of the History of Biology
38. Journal of the History of Medicine and Allied Sciences
39. Journal of the History of the Neurosciences
40. Medical History
41. Nexus Network Journal
42. Notes and Records-the Royal Society Journal of the History of Science
43. Nuncius-Journal of the History of Science
44. Osiris
45. Perspectives in Biology and Medicine
46. Philosophia Mathematica
47. Philosophy Ethics and Humanities in Medicine
48. Philosophy of Science
49. Physics in Perspective
50. Research Integrity and Peer Review
51. Revue d Histoire des Mathematiques
52. Science & Education
53. Science and Engineering Ethics
54. Science in Context
55. Social History of Medicine
56. Social Studies of Science
57. Studies in History and Philosophy of Science
58. Synthese
59. Technology and Culture
60. Theology and Science

<a id="scie-horticulture"></a>

### Horticulture

期刊数：37

1. Acta Scientiarum Polonorum-Hortorum Cultus
2. American Journal of Enology and Viticulture
3. Applied Fruit Science
4. Australian Journal of Grape and Wine Research
5. Biological Agriculture & Horticulture
6. Euphytica
7. European Journal of Horticultural Science
8. European Journal of Plant Pathology
9. Folia Horticulturae
10. Horticultura Brasileira
11. Horticulturae
12. Horticultural Plant Journal
13. Horticultural Science
14. Horticultural Science & Technology
15. Horticulture Environment and Biotechnology
16. Horticulture Journal
17. Horticulture Research
18. HortScience
19. HortTechnology
20. International Journal of Fruit Science
21. Journal of Horticultural Science & Biotechnology
22. Journal of the American Pomological Society
23. Journal of the American Society for Horticultural Science
24. Journal of the Professional Association for Cactus Development
25. Mitteilungen Klosterneuburg: Journal of Viticulture Oenology Pomology and Fruit Processing
26. Molecular Breeding
27. Molecular Horticulture
28. New Zealand Journal of Crop and Horticultural Science
29. Oeno One
30. Postharvest Biology and Technology
31. Propagation of Ornamental Plants
32. Revista Brasileira de Fruticultura
33. Scientia Horticulturae
34. Seed Science and Technology
35. Theoretical and Applied Genetics
36. Tree Genetics & Genomes
37. Vitis

<a id="scie-imaging-science-photographic-technology"></a>

### Imaging Science & Photographic Technology

期刊数：27

1. Color Research and Application
2. Geocarto International
3. IEEE Geoscience and Remote Sensing Letters
4. IEEE Geoscience and Remote Sensing Magazine
5. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing
6. IEEE Transactions on Computational Imaging
7. IEEE Transactions on Geoscience and Remote Sensing
8. IEEE Transactions on Medical Imaging
9. IET Image Processing
10. Imaging Science Journal
11. International Journal of Imaging Systems and Technology
12. International Journal of Remote Sensing
13. ISPRS Journal of Photogrammetry and Remote Sensing
14. Journal of Applied Remote Sensing
15. Journal of Electronic Imaging
16. Journal of Imaging Science and Technology
17. Journal of Real-Time Image Processing
18. Journal of Visualization
19. PFG-Journal of Photogrammetry Remote Sensing and Geoinformation Science
20. Photogrammetric Engineering and Remote Sensing
21. Photogrammetric Record
22. Remote Sensing
23. Remote Sensing Letters
24. Remote Sensing of Environment
25. SIAM Journal on Imaging Sciences
26. Signal Image and Video Processing
27. Virtual Reality

<a id="scie-immunology"></a>

### Immunology

期刊数：157

1. Acta Microbiologica et Immunologica Hungarica
2. AIDS
3. AIDS Research and Human Retroviruses
4. AIDS Reviews
5. Allergology International
6. Allergy
7. Allergy Asthma & Immunology Research
8. Allergy Asthma and Clinical Immunology
9. American Journal of Reproductive Immunology
10. Annals of Allergy Asthma & Immunology
11. Annual Review of Immunology
12. Apmis
13. Archivum Immunologiae et Therapiae Experimentalis
14. Asian Pacific Journal of Allergy and Immunology
15. Autoimmunity
16. Autoimmunity Reviews
17. BioDrugs
18. BMC Immunology
19. Bone Marrow Transplantation
20. Brain Behavior and Immunity
21. Cancer Immunology Immunotherapy
22. Cancer Immunology Research
23. Cellular & Molecular Immunology
24. Cellular Immunology
25. Central European Journal of Immunology
26. Clinical & Translational Immunology
27. Clinical and Experimental Allergy
28. Clinical and Experimental Immunology
29. Clinical Immunology
30. Clinical Infectious Diseases
31. Clinical Reviews in Allergy & Immunology
32. Comparative Immunology Microbiology and Infectious Diseases
33. Critical Reviews in Immunology
34. Current Allergy and Asthma Reports
35. Current HIV Research
36. Current Opinion in Allergy and Clinical Immunology
37. Current Opinion in HIV and AIDS
38. Current Opinion in Immunology
39. Cytokine
40. Developmental and Comparative Immunology
41. Emerging Infectious Diseases
42. Emerging Microbes & Infections
43. Endocrine Metabolic & Immune Disorders-Drug Targets
44. European Cytokine Network
45. European Journal of Immunology
46. European Journal of Inflammation
47. Exercise Immunology Review
48. Expert Review of Clinical Immunology
49. Expert Review of Vaccines
50. Fish & Shellfish Immunology
51. Food and Agricultural Immunology
52. Frontiers in Cellular and Infection Microbiology
53. Frontiers in Immunology
54. Genes and Immunity
55. HLA
56. Human Immunology
57. Human Vaccines & Immunotherapeutics
58. Immune Network
59. Immunity
60. Immunity & Ageing
61. Immunity Inflammation and Disease
62. Immunobiology
63. Immunogenetics
64. Immunologic Research
65. Immunological Investigations
66. Immunological Reviews
67. Immunology
68. Immunology and Allergy Clinics of North America
69. Immunology and Cell Biology
70. Immunology Letters
71. Immunopharmacology and Immunotoxicology
72. Immunotherapy
73. Indian Journal of Medical Microbiology
74. Indian Journal of Medical Research
75. Infection and Immunity
76. Infectious Agents and Cancer
77. Infectious Disease Clinics of North America
78. Inflammation
79. Inflammation and Regeneration
80. Inflammation Research
81. Inflammopharmacology
82. Innate Immunity
83. International Archives of Allergy and Immunology
84. International Immunology
85. International Immunopharmacology
86. International Journal of Immunogenetics
87. International Journal of Immunopathology and Pharmacology
88. International Journal of STD & AIDS
89. International Reviews of Immunology
90. Iranian Journal of Allergy Asthma and Immunology
91. Iranian Journal of Immunology
92. Isj-Invertebrate Survival Journal
93. JAIDS-Journal of Acquired Immune Deficiency Syndromes
94. Journal for ImmunoTherapy of Cancer
95. Journal of Allergy and Clinical Immunology
96. Journal of Allergy and Clinical Immunology-in Practice
97. Journal of Antibiotics
98. Journal of Asthma and Allergy
99. Journal of Autoimmunity
100. Journal of Clinical Immunology
101. Journal of Experimental Medicine
102. Journal of Immunological Methods
103. Journal of Immunology
104. Journal of Immunology Research
105. Journal of Immunotherapy
106. Journal of Infectious Diseases
107. Journal of Inflammation Research
108. Journal of Inflammation-London
109. Journal of Innate Immunity
110. Journal of Interferon and Cytokine Research
111. Journal of Investigational Allergology and Clinical Immunology
112. Journal of Leukocyte Biology
113. Journal of Microbiology Immunology and Infection
114. Journal of Neuroimmunology
115. Journal of Neuroinflammation
116. Journal of Reproductive Immunology
117. Journal of the International AIDS Society
118. Journal of Virus Eradication
119. Lancet HIV
120. Lymphology
121. Mediators of Inflammation
122. Medical Microbiology and Immunology
123. Microbes and Infection
124. Microbial Pathogenesis
125. Microbiology and Immunology
126. Molecular Immunology
127. Mucosal Immunology
128. Nature Immunology
129. Nature Reviews Immunology
130. NeuroImmunoModulation
131. Npj Vaccines
132. OncoImmunology
133. Open Forum Infectious Diseases
134. Parasite Immunology
135. Pediatric Allergy and Immunology
136. Pediatric Allergy Immunology and Pulmonology
137. Pediatric Infectious Disease Journal
138. Scandinavian Journal of Immunology
139. Science Immunology
140. Seminars in Immunology
141. Seminars in Immunopathology
142. Transfusion Clinique et Biologique
143. Transfusion Medicine and Hemotherapy
144. Transplant Immunology
145. Transplant Infectious Disease
146. Transplantation
147. Transplantation and Cellular Therapy
148. Transplantation Proceedings
149. Transplantation Reviews
150. Trends in Immunology
151. Tuberculosis
152. Vaccine
153. Vaccines
154. Veterinary Immunology and Immunopathology
155. Viral Immunology
156. Virulence
157. World Allergy Organization Journal

<a id="scie-infectious-diseases"></a>

### Infectious Diseases

期刊数：94

1. ACS Infectious Diseases
2. AIDS
3. AIDS Patient Care and STDs
4. AIDS Research and Human Retroviruses
5. AIDS Research and Therapy
6. AIDS Reviews
7. American Journal of Infection Control
8. Antibiotics-Basel
9. Antimicrobial Resistance and Infection Control
10. Antiviral Therapy
11. BMC Infectious Diseases
12. Brazilian Journal of Infectious Diseases
13. Canadian Journal of Infectious Diseases & Medical Microbiology
14. Clinical Infectious Diseases
15. Clinical Microbiology and Infection
16. Current HIV Research
17. Current HIV/AIDS Reports
18. Current Infectious Disease Reports
19. Current Opinion in HIV and AIDS
20. Current Opinion in Infectious Diseases
21. Diagnostic Microbiology and Infectious Disease
22. Emerging Infectious Diseases
23. Emerging Microbes & Infections
24. Enfermedades Infecciosas y Microbiologia Clinica
25. Epidemics
26. Epidemiology & Infection
27. European Journal of Clinical Microbiology & Infectious Diseases
28. Eurosurveillance
29. Expert Review of Anti-Infective Therapy
30. HIV Medicine
31. HIV Research & Clinical Practice
32. Infection
33. Infection and Drug Resistance
34. Infection and Immunity
35. Infection Control & Hospital Epidemiology
36. Infection Genetics and Evolution
37. Infectious Disease Clinics of North America
38. Infectious Diseases
39. Infectious Diseases and Therapy
40. Infectious Diseases Now
41. Infectious Diseases of Poverty
42. Influenza and Other Respiratory Viruses
43. International Journal of Antimicrobial Agents
44. International Journal of Hygiene and Environmental Health
45. International Journal of Infectious Diseases
46. International Journal of STD & AIDS
47. International Journal of Tuberculosis and Lung Disease
48. JAIDS-Journal of Acquired Immune Deficiency Syndromes
49. Japanese Journal of Infectious Diseases
50. Journal of Antimicrobial Chemotherapy
51. Journal of Chemotherapy
52. Journal of Global Antimicrobial Resistance
53. Journal of Hospital Infection
54. Journal of Infection
55. Journal of Infection and Chemotherapy
56. Journal of Infection and Public Health
57. Journal of Infection in Developing Countries
58. Journal of Infectious Diseases
59. Journal of Microbiology Immunology and Infection
60. Journal of Pediatric Infectious Diseases
61. Journal of the International AIDS Society
62. Journal of the Pediatric Infectious Diseases Society
63. Journal of Travel Medicine
64. Journal of Vector Borne Diseases
65. Journal of Viral Hepatitis
66. Journal of Virus Eradication
67. Lancet HIV
68. Lancet Infectious Diseases
69. Lancet Microbe
70. Leprosy Review
71. Malaria Journal
72. Medical Mycology
73. Mediterranean Journal of Hematology and Infectious Diseases
74. Microbes and Infection
75. Microbial Drug Resistance
76. One Health
77. Open Forum Infectious Diseases
78. Pediatric Infectious Disease Journal
79. Revista Chilena de Infectologia
80. Revista do Instituto de Medicina Tropical de Sao Paulo
81. Sexual Health
82. Sexually Transmitted Diseases
83. Sexually Transmitted Infections
84. Southeast Asian Journal of Tropical Medicine and Public Health
85. Southern African Journal of HIV Medicine
86. Surgical Infections
87. Ticks and Tick-Borne Diseases
88. Transboundary and Emerging Diseases
89. Transplant Infectious Disease
90. Travel Medicine and Infectious Disease
91. Tropical Medicine and Infectious Disease
92. Vector-Borne and Zoonotic Diseases
93. Virulence
94. Zoonoses and Public Health

<a id="scie-instruments-instrumentation"></a>

### Instruments & Instrumentation

期刊数：62

1. Accreditation and Quality Assurance
2. Actuators
3. Applied Spectroscopy
4. Applied Spectroscopy Reviews
5. Automation and Remote Control
6. Biosensors-Basel
7. Chemometrics and Intelligent Laboratory Systems
8. Chemosensors
9. Displays
10. Flow Measurement and Instrumentation
11. IEEE Instrumentation & Measurement Magazine
12. IEEE Sensors Journal
13. IEEE Transactions on Industrial Electronics
14. IEEE Transactions on Instrumentation and Measurement
15. IET Control Theory and Applications
16. Infrared Physics & Technology
17. Insight
18. Instrumentation Science & Technology
19. Instruments and Experimental Techniques
20. ISA Transactions
21. Journal of Astronomical Telescopes Instruments and Systems
22. Journal of Chemometrics
23. Journal of Dynamic Systems Measurement and Control-Transactions of the ASME
24. Journal of Guidance Control and Dynamics
25. Journal of Instrumentation
26. Journal of Microelectromechanical Systems
27. Journal of Micromechanics and Microengineering
28. Journal of Sensors
29. Journal of Synchrotron Radiation
30. Journal of X-Ray Science and Technology
31. Lab on a Chip
32. Mapan-Journal of Metrology Society of India
33. Measurement
34. Measurement & Control
35. Measurement Science and Technology
36. Measurement Science Review
37. Metrologia
38. Metrology and Measurement Systems
39. Microfluidics and Nanofluidics
40. Micromachines
41. Microsystems & Nanoengineering
42. Nuclear Instruments & Methods in Physics Research Section A-Accelerators Spectrometers Detectors and Associated Equipment
43. Nuclear Instruments & Methods in Physics Research Section B-Beam Interactions with Materials and Atoms
44. Photoacoustics
45. Photonic Sensors
46. Precision Engineering-Journal of the International Societies for Precision Engineering and Nanotechnology
47. Quantitative InfraRed Thermography Journal
48. Review of Scientific Instruments
49. Romanian Journal of Information Science and Technology
50. Sensor Review
51. Sensors
52. Sensors and Actuators A-Physical
53. Sensors and Actuators B-Chemical
54. Sensors and Actuators Reports
55. Sensors and Materials
56. Smart Materials and Structures
57. Smart Structures and Systems
58. Structural Control & Health Monitoring
59. Structural Health Monitoring-an International Journal
60. Surface Topography-Metrology and Properties
61. Tm-Technisches Messen
62. Transactions of the Institute of Measurement and Control

<a id="scie-integrative-complementary-medicine"></a>

### Integrative & Complementary Medicine

期刊数：28

1. Acupuncture & Electro-Therapeutics Research
2. Acupuncture in Medicine
3. American Journal of Chinese Medicine
4. BMC Complementary Medicine and Therapies
5. Boletin Latinoamericano y del Caribe de Plantas Medicinales y Aromaticas
6. Chinese Journal of Integrative Medicine
7. Chinese Journal of Natural Medicines
8. Chinese Medicine
9. Complementary Medicine Research
10. Complementary Therapies in Clinical Practice
11. Complementary Therapies in Medicine
12. European Journal of Integrative Medicine
13. Explore-the Journal of Science and Healing
14. Fitoterapia
15. Holistic Nursing Practice
16. Homeopathy
17. Integrative Cancer Therapies
18. Integrative Medicine Research
19. Journal of Ethnopharmacology
20. Journal of Ginseng Research
21. Journal of Herbal Medicine
22. Journal of Integrative and Complementary Medicine
23. Journal of Integrative Medicine-Jim
24. Journal of Manipulative and Physiological Therapeutics
25. Journal of Traditional and Complementary Medicine
26. Journal of Traditional Chinese Medicine
27. Phytomedicine
28. Planta Medica

<a id="scie-limnology"></a>

### Limnology

期刊数：21

1. Aquatic Ecology
2. Aquatic Sciences
3. Fundamental and Applied Limnology
4. Inland Waters
5. International Journal of Limnology
6. Journal of Freshwater Ecology
7. Journal of Great Lakes Research
8. Journal of Limnology
9. Journal of Oceanology and Limnology
10. Journal of Paleolimnology
11. Lake and Reservoir Management
12. Limnetica
13. Limnologica
14. Limnology
15. Limnology and Oceanography
16. Limnology and Oceanography Letters
17. Limnology and Oceanography-Methods
18. Marine and Freshwater Research
19. Water and Environment Journal
20. Water Environment Research
21. Water Resources Research

<a id="scie-logic"></a>

### Logic

期刊数：21

1. ACM Transactions on Computational Logic
2. Algebra and Logic
3. Annals of Pure and Applied Logic
4. Archive for Mathematical Logic
5. Bulletin of Symbolic Logic
6. History and Philosophy of Logic
7. Journal of Logic and Computation
8. Journal of Logic Language and Information
9. Journal of Logical and Algebraic Methods in Programming
10. Journal of Mathematical Logic
11. Journal of Multiple-Valued Logic and Soft Computing
12. Journal of Symbolic Logic
13. Logic Journal of the IGPL
14. Logica Universalis
15. Logical Methods in Computer Science
16. Mathematical Logic Quarterly
17. Notre Dame Journal of Formal Logic
18. Reports on Mathematical Logic
19. Review of Symbolic Logic
20. Studia Logica
21. Theory and Practice of Logic Programming

<a id="scie-marine-freshwater-biology"></a>

### Marine & Freshwater Biology

期刊数：109

1. Acta Adriatica
2. African Journal of Aquatic Science
3. African Journal of Marine Science
4. Algae
5. American Malacological Bulletin
6. Animal Biotelemetry
7. Annual Review of Marine Science
8. Aquaculture
9. Aquaculture Environment Interactions
10. Aquatic Biology
11. Aquatic Botany
12. Aquatic Conservation-Marine and Freshwater Ecosystems
13. Aquatic Ecology
14. Aquatic Ecosystem Health & Management
15. Aquatic Invasions
16. Aquatic Living Resources
17. Aquatic Mammals
18. Aquatic Microbial Ecology
19. Aquatic Sciences
20. Aquatic Toxicology
21. Archiv für Molluskenkunde
22. Biofouling
23. Biological Bulletin
24. Botanica Marina
25. Bulletin of Marine Science
26. Bulletin of the European Association of Fish Pathologists
27. Cahiers de Biologie Marine
28. Canadian Journal of Fisheries and Aquatic Sciences
29. Ciencias Marinas
30. Clean-Soil Air Water
31. Coral Reefs
32. Crustaceana
33. Cryptogamie Algologie
34. Diatom Research
35. Ecology of Freshwater Fish
36. Environmental Biology of Fishes
37. Estuaries and Coasts
38. Estuarine Coastal and Shelf Science
39. European Journal of Phycology
40. Fish & Shellfish Immunology
41. Fishes
42. Freshwater Biology
43. Freshwater Science
44. Frontiers in Marine Science
45. Fundamental and Applied Limnology
46. Harmful Algae
47. Hidrobiologica
48. Hydrobiologia
49. ICES Journal of Marine Science
50. Ichthyological Exploration of Freshwaters
51. Ichthyological Research
52. Inland Water Biology
53. Inland Waters
54. International Review of Hydrobiology
55. Invertebrate Biology
56. Journal of Applied Ichthyology
57. Journal of Applied Phycology
58. Journal of Aquatic Plant Management
59. Journal of Coastal Conservation
60. Journal of Conchology
61. Journal of Crustacean Biology
62. Journal of Experimental Marine Biology and Ecology
63. Journal of Fish Biology
64. Journal of Fish Diseases
65. Journal of Great Lakes Research
66. Journal of Marine Systems
67. Journal of Molluscan Studies
68. Journal of Phycology
69. Journal of Plankton Research
70. Journal of Sea Research
71. Journal of Shellfish Research
72. Journal of the Marine Biological Association of the United Kingdom
73. Knowledge and Management of Aquatic Ecosystems
74. Lake and Reservoir Management
75. Latin American Journal of Aquatic Research
76. Limnetica
77. Marine and Coastal Fisheries
78. Marine and Freshwater Behaviour and Physiology
79. Marine and Freshwater Research
80. Marine Biodiversity
81. Marine Biology
82. Marine Biology Research
83. Marine Biotechnology
84. Marine Ecology Progress Series
85. Marine Ecology-an Evolutionary Perspective
86. Marine Environmental Research
87. Marine Life Science & Technology
88. Marine Mammal Science
89. Marine Pollution Bulletin
90. Mediterranean Marine Science
91. Microbial Ecology
92. Nauplius
93. Nautilus
94. New Zealand Journal of Marine and Freshwater Research
95. Ocean and Coastal Research
96. Ocean Science Journal
97. Pacific Science
98. Phycologia
99. Phycological Research
100. Plankton & Benthos Research
101. Regional Studies in Marine Science
102. Reviews in Fish Biology and Fisheries
103. Revista de Biologia Marina y Oceanografia
104. Russian Journal of Marine Biology
105. Scientia Marina
106. Thalassas
107. Turkish Journal of Fisheries and Aquatic Sciences
108. Undersea and Hyperbaric Medicine
109. Vie et Milieu-Life and Environment

<a id="scie-materials-science-biomaterials"></a>

### Materials Science, Biomaterials

期刊数：44

1. ACS Biomaterials Science & Engineering
2. Acta Biomaterialia
3. Advanced Biology
4. Advanced Healthcare Materials
5. Artificial Cells Nanomedicine and Biotechnology
6. Bio-Medical Materials and Engineering
7. Bioactive Materials
8. Biofabrication
9. Bioinspiration & Biomimetics
10. Bioinspired Biomimetic and Nanobiomaterials
11. Biointerphases
12. Biomaterials
13. Biomaterials Advances
14. Biomaterials Research
15. Biomaterials Science
16. Biomedical Materials
17. Biomimetics
18. Cellular Polymers
19. Colloids and Surfaces B-Biointerfaces
20. Dental Materials
21. Dental Materials Journal
22. European Cells & Materials
23. International Journal of Bioprinting
24. International Journal of Polymeric Materials and Polymeric Biomaterials
25. Journal of Applied Biomaterials & Functional Materials
26. Journal of Bioactive and Compatible Polymers
27. Journal of Biomaterials Applications
28. Journal of Biomaterials Science-Polymer Edition
29. Journal of Biomedical Materials Research Part A
30. Journal of Biomedical Materials Research Part B-Applied Biomaterials
31. Journal of Bionic Engineering
32. Journal of Functional Biomaterials
33. Journal of Materials Chemistry B
34. Journal of Materials Science-Materials in Medicine
35. Journal of Oral Science
36. Journal of the Mechanical Behavior of Biomedical Materials
37. Macromolecular Bioscience
38. Materials Today Bio
39. Nature Reviews Bioengineering
40. Progress in Biomaterials
41. Regenerative Biomaterials
42. Tissue Engineering Part A
43. Tissue Engineering Part B-Reviews
44. Tissue Engineering Part C-Methods

<a id="scie-materials-science-ceramics"></a>

### Materials Science, Ceramics

期刊数：29

1. Advances in Applied Ceramics
2. American Ceramic Society Bulletin
3. Boletin de la Sociedad Espanola de Ceramica y Vidrio
4. Ceramics International
5. Ceramics-Silikaty
6. Glass and Ceramics
7. Glass Physics and Chemistry
8. Glass Technology-European Journal of Glass Science and Technology Part A
9. International Journal of Applied Ceramic Technology
10. International Journal of Applied Glass Science
11. Journal of Advanced Ceramics
12. Journal of Asian Ceramic Societies
13. Journal of Ceramic Processing Research
14. Journal of Ceramic Science and Technology
15. Journal of Electroceramics
16. Journal of Inorganic Materials
17. Journal of Non-Crystalline Solids
18. Journal of Sol-Gel Science and Technology
19. Journal of the American Ceramic Society
20. Journal of the Australian Ceramic Society
21. Journal of the Ceramic Society of Japan
22. Journal of the European Ceramic Society
23. Journal of the Korean Ceramic Society
24. Physics and Chemistry of Glasses-European Journal of Glass Science and Technology Part B
25. Powder Metallurgy and Metal Ceramics
26. Processing and Application of Ceramics
27. Refractories and Industrial Ceramics
28. Science of Sintering
29. Transactions of the Indian Ceramic Society

<a id="scie-materials-science-characterization-testing"></a>

### Materials Science, Characterization, Testing

期刊数：31

1. Advanced Steel Construction
2. Archives of Mechanics
3. Beton- und Stahlbetonbau
4. Computers and Concrete
5. Engineering Failure Analysis
6. Experimental Mechanics
7. Experimental Techniques
8. High Temperatures-High Pressures
9. Insight
10. International Journal of Pavement Engineering
11. Journal of Nondestructive Evaluation
12. Journal of Sandwich Structures & Materials
13. Journal of Strain Analysis for Engineering Design
14. Journal of Testing and Evaluation
15. Materials Characterization
16. Materials Evaluation
17. Materials Testing
18. Mechanics of Time-Dependent Materials
19. Nanoscale and Microscale Thermophysical Engineering
20. NDT & E International
21. Nondestructive Testing and Evaluation
22. Physical Mesomechanics
23. Polymer Testing
24. Polymers & Polymer Composites
25. Powder Diffraction
26. Progress in Crystal Growth and Characterization of Materials
27. Quantitative InfraRed Thermography Journal
28. Research in Nondestructive Evaluation
29. Russian Journal of Nondestructive Testing
30. Strain
31. Strength of Materials

<a id="scie-materials-science-coatings-films"></a>

### Materials Science, Coatings & Films

期刊数：21

1. Applied Surface Science
2. Coatings
3. Coatingstech
4. Colloid and Interface Science Communications
5. Corrosion Reviews
6. Diamond and Related Materials
7. International Journal of Surface Science and Engineering
8. Journal of Coatings Technology and Research
9. Journal of Plastic Film & Sheeting
10. Journal of the Electrochemical Society
11. Journal of Thermal Spray Technology
12. Journal of Vacuum Science & Technology A
13. Pigment & Resin Technology
14. Progress in Organic Coatings
15. Surface & Coatings Technology
16. Surface Coatings International
17. Surface Engineering
18. Surface Innovations
19. Surfaces and Interfaces
20. Thin Solid Films
21. Transactions of the Institute of Metal Finishing

<a id="scie-materials-science-composites"></a>

### Materials Science, Composites

期刊数：26

1. Advanced Composite Materials
2. Advanced Composites and Hybrid Materials
3. Applied Composite Materials
4. Beton- und Stahlbetonbau
5. Cement & Concrete Composites
6. Cement Wapno Beton
7. Composite Interfaces
8. Composite Structures
9. Composites and Advanced Materials
10. Composites Communications
11. Composites Part A-Applied Science and Manufacturing
12. Composites Part B-Engineering
13. Composites Science and Technology
14. Journal of Composite Materials
15. Journal of Composites for Construction
16. Journal of Reinforced Plastics and Composites
17. Journal of Sandwich Structures & Materials
18. Journal of Thermoplastic Composite Materials
19. Mechanics of Composite Materials
20. Nanocomposites
21. Plastics Rubber and Composites
22. Polymer Composites
23. Polymers & Polymer Composites
24. Progress in Rubber Plastics and Recycling Technology
25. Science and Engineering of Composite Materials
26. Steel and Composite Structures

<a id="scie-materials-science-multidisciplinary"></a>

### Materials Science, Multidisciplinary

期刊数：341

1. 2D Materials
2. 3D Printing and Additive Manufacturing
3. ACI Materials Journal
4. ACI Structural Journal
5. ACS Applied Electronic Materials
6. ACS Applied Energy Materials
7. ACS Applied Materials & Interfaces
8. ACS Applied Nano Materials
9. ACS Applied Polymer Materials
10. ACS Energy Letters
11. ACS Materials Letters
12. ACS Nano
13. ACS Photonics
14. Acta Materialia
15. Acta Mechanica Solida Sinica
16. Additive Manufacturing
17. Advanced Electronic Materials
18. Advanced Energy Materials
19. Advanced Engineering Materials
20. Advanced Fiber Materials
21. Advanced Functional Materials
22. Advanced Materials
23. Advanced Materials & Processes
24. Advanced Materials Interfaces
25. Advanced Materials Technologies
26. Advanced Optical Materials
27. Advanced Science
28. Advanced Sustainable Systems
29. Advances in Cement Research
30. Advances in Concrete Construction
31. Advances in Manufacturing
32. Advances in Nano Research
33. Advances in Production Engineering & Management
34. AIP Advances
35. Annual Review of Materials Research
36. APL Materials
37. Applied Clay Science
38. Applied Materials Today
39. Applied Physics A-Materials Science & Processing
40. Applied Sciences-Basel
41. Archives of Civil and Mechanical Engineering
42. Atomization and Sprays
43. Batteries & Supercaps
44. Batteries-Basel
45. Beilstein Journal of Nanotechnology
46. Bulletin of Materials Science
47. Calphad-Computer Coupling of Phase Diagrams and Thermochemistry
48. Carbon
49. Carbon Energy
50. Carbon Letters
51. Case Studies in Construction Materials
52. Cell Reports Physical Science
53. Cement and Concrete Research
54. Chalcogenide Letters
55. Chemistry of Materials
56. ChemNanoMat
57. Circuit World
58. Cmc-Computers Materials & Continua
59. Coatings
60. Combustion Explosion and Shock Waves
61. Computational Materials Science
62. Construction and Building Materials
63. Corrosion
64. Corrosion Engineering Science and Technology
65. Corrosion Science
66. Critical Reviews in Solid State and Materials Sciences
67. Crystal Growth & Design
68. Crystals
69. Current Applied Physics
70. Current Nanoscience
71. Current Opinion in Electrochemistry
72. Current Opinion in Solid State & Materials Science
73. Diamond and Related Materials
74. Digest Journal of Nanomaterials and Biostructures
75. Discover Metals
76. Discover Nano
77. EcoMat
78. ECS Journal of Solid State Science and Technology
79. Electronic Materials Letters
80. Emerging Materials Research
81. Energy & Environmental Materials
82. Energy Storage Materials
83. eScience
84. European Physical Journal E
85. Experimental Mechanics
86. Extreme Mechanics Letters
87. Fatigue & Fracture of Engineering Materials & Structures
88. Ferroelectrics
89. Fibre Chemistry
90. Fire and Materials
91. Fire Safety Journal
92. Fire Technology
93. FlatChem
94. Flexible and Printed Electronics
95. Frontiers in Materials
96. Frontiers of Materials Science
97. Fullerenes Nanotubes and Carbon Nanostructures
98. Functional Materials Letters
99. Geosynthetics International
100. Granular Matter
101. Green Materials
102. High Temperature Materials and Processes
103. IEEE Journal of Photovoltaics
104. IEEE Transactions on Components Packaging and Manufacturing Technology
105. IEEE Transactions on Nanotechnology
106. Image Analysis & Stereology
107. Indian Journal of Engineering and Materials Sciences
108. InfoMat
109. Informacije MIDEM-Journal of Microelectronics Electronic Components and Materials
110. Inorganic Materials
111. Integrating Materials and Manufacturing Innovation
112. Intermetallics
113. International Journal for Numerical and Analytical Methods in Geomechanics
114. International Journal of Adhesion and Adhesives
115. International Journal of Concrete Structures and Materials
116. International Journal of Damage Mechanics
117. International Journal of Extreme Manufacturing
118. International Journal of Fatigue
119. International Journal of Fracture
120. International Journal of Material Forming
121. International Journal of Materials & Product Technology
122. International Journal of Mechanics and Materials in Design
123. International Journal of Minerals Metallurgy and Materials
124. International Journal of Nanotechnology
125. International Journal of Plasticity
126. International Journal of Refractory Metals & Hard Materials
127. International Journal of Smart and Nano Materials
128. International Journal of Surface Science and Engineering
129. International Materials Reviews
130. IUCrJ
131. JOM
132. Joule
133. Journal of Adhesion
134. Journal of Adhesion Science and Technology
135. Journal of Advanced Concrete Technology
136. Journal of Alloys and Compounds
137. Journal of Crystal Growth
138. Journal of Cultural Heritage
139. Journal of Elasticity
140. Journal of Elastomers and Plastics
141. Journal of Electronic Materials
142. Journal of Energetic Materials
143. Journal of Engineering Materials and Technology-Transactions of the ASME
144. Journal of Experimental Nanoscience
145. Journal of Fire Sciences
146. Journal of Friction and Wear
147. Journal of Information Display
148. Journal of Intelligent Material Systems and Structures
149. Journal of Laser Applications
150. Journal of Laser Micro Nanoengineering
151. Journal of Magnesium and Alloys
152. Journal of Magnetics
153. Journal of Magnetism and Magnetic Materials
154. Journal of Materials Chemistry A
155. Journal of Materials Chemistry C
156. Journal of Materials Education
157. Journal of Materials Engineering and Performance
158. Journal of Materials in Civil Engineering
159. Journal of Materials Processing Technology
160. Journal of Materials Research
161. Journal of Materials Research and Technology-Jmr&T
162. Journal of Materials Science
163. Journal of Materials Science & Technology
164. Journal of Materials Science-Materials in Electronics
165. Journal of Materiomics
166. Journal of Mechanics of Materials and Structures
167. Journal of Micro-Nanopatterning Materials and Metrology-Jm3
168. Journal of Microwave Power and Electromagnetic Energy
169. Journal of Nano Research
170. Journal of Nanoparticle Research
171. Journal of Nanostructure in Chemistry
172. Journal of Non-Crystalline Solids
173. Journal of Nuclear Materials
174. Journal of Optoelectronics and Advanced Materials
175. Journal of Ovonic Research
176. Journal of Phase Equilibria and Diffusion
177. Journal of Photonics for Energy
178. Journal of Physical Chemistry C
179. Journal of Physical Chemistry Letters
180. Journal of Physics-Energy
181. Journal of Physics-Materials
182. Journal of Porous Materials
183. Journal of Power Sources
184. Journal of Science-Advanced Materials and Devices
185. Journal of Superhard Materials
186. Journal of Sustainable Cement-Based Materials
187. Journal of the Mechanics and Physics of Solids
188. Journal of the Society for Information Display
189. Journal of Wuhan University of Technology-Materials Science Edition
190. Kona Powder and Particle Journal
191. Korean Journal of Metals and Materials
192. Kovove Materialy-Metallic Materials
193. Langmuir
194. Lasers in Engineering
195. Liquid Crystals
196. Liquid Crystals Reviews
197. Machining Science and Technology
198. Macromolecular Materials and Engineering
199. Magazine of Concrete Research
200. Magnetochemistry
201. Materia-Rio de Janeiro
202. Materiale Plastice
203. Materiales de Construccion
204. Materiali in Tehnologije
205. Materials
206. Materials & Design
207. Materials and Corrosion-Werkstoffe und Korrosion
208. Materials and Manufacturing Processes
209. Materials and Structures
210. Materials at High Temperatures
211. Materials Characterization
212. Materials Chemistry and Physics
213. Materials Chemistry Frontiers
214. Materials Horizons
215. Materials Letters
216. Materials Research Bulletin
217. Materials Research Express
218. Materials Research Letters
219. Materials Research-Ibero-American Journal of Materials
220. Materials Science
221. Materials Science & Engineering R-Reports
222. Materials Science and Engineering A-Structural Materials Properties Microstructure and Processing
223. Materials Science and Engineering B-Advanced Functional Solid-State Materials
224. Materials Science and Technology
225. Materials Science in Semiconductor Processing
226. Materials Science-Medziagotyra
227. Materials Science-Poland
228. Materials Technology
229. Materials Today
230. Materials Today Advances
231. Materials Today Chemistry
232. Materials Today Communications
233. Materials Today Energy
234. Materials Today Nano
235. Materials Today Physics
236. Materials Today Sustainability
237. Materials Transactions
238. Materialwissenschaft und Werkstofftechnik
239. Mathematics and Mechanics of Solids
240. Matter
241. Mechanics of Materials
242. Membranes
243. Metallurgical and Materials Transactions A-Physical Metallurgy and Materials Science
244. Metallurgical and Materials Transactions B-Process Metallurgy and Materials Processing Science
245. Metals
246. Metals and Materials International
247. Micro & Nano Letters
248. Microelectronics International
249. Microporous and Mesoporous Materials
250. Microscopy and Microanalysis
251. Microsystem Technologies-Micro-and Nanosystems-Information Storage and Processing Systems
252. Modelling and Simulation in Materials Science and Engineering
253. Molecular Crystals and Liquid Crystals
254. Molecular Systems Design & Engineering
255. MRS Bulletin
256. MRS Communications
257. Multidiscipline Modeling in Materials and Structures
258. Nano
259. Nano Convergence
260. Nano Energy
261. Nano Futures
262. Nano Letters
263. Nano Research
264. Nano Today
265. Nano-Micro Letters
266. Nanomaterials
267. Nanomaterials and Nanotechnology
268. Nanophotonics
269. Nanoscale
270. Nanoscale Advances
271. Nanoscale Horizons
272. Nanotechnology
273. Nanotechnology Reviews
274. Nature Energy
275. Nature Materials
276. Nature Nanotechnology
277. Nature Reviews Materials
278. New Carbon Materials
279. NPG Asia Materials
280. Npj 2D Materials and Applications
281. Npj Computational Materials
282. Npj Flexible Electronics
283. Npj Heritage Science
284. Npj Materials Degradation
285. Npj Quantum Materials
286. Optical Materials
287. Optical Materials Express
288. Optoelectronics and Advanced Materials-Rapid Communications
289. Organic Electronics
290. Particle & Particle Systems Characterization
291. Particuology
292. Philosophical Magazine
293. Philosophical Magazine Letters
294. Photonics and Nanostructures-Fundamentals and Applications
295. Physica Status Solidi a-Applications and Materials Science
296. Physica Status Solidi-Rapid Research Letters
297. Physical Review B
298. Physical Review Materials
299. Physics and Chemistry of Minerals
300. Plasmonics
301. Proceedings of the Institution of Mechanical Engineers Part L-Journal of Materials-Design and Applications
302. Progress in Materials Science
303. Progress in Natural Science-Materials International
304. Progress in Photovoltaics
305. Rapid Prototyping Journal
306. Rare Metal Materials and Engineering
307. Rare Metals
308. Recent Patents on Nanotechnology
309. Reviews on Advanced Materials Science
310. Revista Romana de Materiale-Romanian Journal of Materials
311. Road Materials and Pavement Design
312. Sampe Journal
313. Science and Technology of Advanced Materials
314. Science and Technology of Energetic Materials
315. Science and Technology of Welding and Joining
316. Science China-Materials
317. Science China-Technological Sciences
318. Scripta Materialia
319. Semiconductor Science and Technology
320. Sensors and Materials
321. Silicon
322. Small
323. Small Methods
324. Small Structures
325. Smart Materials and Structures
326. Soft Materials
327. Soft Matter
328. Solar Energy Materials and Solar Cells
329. Solar RRL
330. Soldering & Surface Mount Technology
331. Surface Topography-Metrology and Properties
332. SusMat
333. Sustainable Energy & Fuels
334. Sustainable Materials and Technologies
335. Synthetic Metals
336. Thin Solid Films
337. Transactions of FAMENA
338. Vacuum
339. Virtual and Physical Prototyping
340. Wear
341. ZKG International

<a id="scie-materials-science-paper-wood"></a>

### Materials Science, Paper & Wood

期刊数：21

1. BioResources
2. Cellulose
3. Cellulose Chemistry and Technology
4. Drewno
5. Drvna Industrija
6. European Journal of Wood and Wood Products
7. Forest Products Journal
8. Holzforschung
9. Journal of Bioresources and Bioproducts
10. Journal of Wood Chemistry and Technology
11. Journal of Wood Science
12. Maderas-Ciencia y Tecnologia
13. Mokuzai Gakkaishi
14. Nordic Pulp & Paper Research Journal
15. Pulp & Paper-Canada
16. TAPPI Journal
17. Wochenblatt für Papierfabrikation
18. Wood and Fiber Science
19. Wood Material Science & Engineering
20. Wood Research
21. Wood Science and Technology

<a id="scie-materials-science-textiles"></a>

### Materials Science, Textiles

期刊数：26

1. AATCC Journal of Research
2. AATCC Review
3. Advanced Fiber Materials
4. Autex Research Journal
5. Cellulose
6. Coloration Technology
7. Dyes and Pigments
8. Fashion and Textiles
9. Fibers and Polymers
10. Fibre Chemistry
11. Fibres & Textiles in Eastern Europe
12. Indian Journal of Fibre & Textile Research
13. Industria Textila
14. International Journal of Clothing Science and Technology
15. Journal of Engineered Fibers and Fabrics
16. Journal of Fiber Science and Technology
17. Journal of Industrial Textiles
18. Journal of Natural Fibers
19. Journal of the American Leather Chemists Association
20. Journal of the Society of Leather Technologists and Chemists
21. Journal of the Textile Institute
22. Journal of Vinyl & Additive Technology
23. Sen-i Gakkaishi
24. Tekstil ve Konfeksiyon
25. Textile Research Journal
26. Wood and Fiber Science

<a id="scie-mathematical-computational-biology"></a>

### Mathematical & Computational Biology

期刊数：53

1. Acta Biotheoretica
2. Algorithms for Molecular Biology
3. Annual Review of Biomedical Data  Science
4. BioData Mining
5. Bioinformatics
6. Biometrical Journal
7. Biometrics
8. Biometrika
9. Biostatistics
10. Biosystems
11. BMC Bioinformatics
12. Briefings in Bioinformatics
13. Bulletin of Mathematical Biology
14. Current Bioinformatics
15. Database-the Journal of Biological Databases and Curation
16. Evolutionary Bioinformatics
17. Frontiers in Computational Neuroscience
18. Frontiers in Neuroinformatics
19. Genetic Epidemiology
20. IEEE Journal of Biomedical and Health Informatics
21. IET Systems Biology
22. Interdisciplinary Sciences-Computational Life Sciences
23. International Journal for Numerical Methods in Biomedical Engineering
24. International Journal of Biomathematics
25. International Journal of Biostatistics
26. International Journal of Data Mining and Bioinformatics
27. Journal of Agricultural Biological and Environmental Statistics
28. Journal of Bioinformatics and Computational Biology
29. Journal of Biological Dynamics
30. Journal of Biological Systems
31. Journal of Biomedical Semantics
32. Journal of Computational Biology
33. Journal of Computational Neuroscience
34. Journal of Mathematical Biology
35. Journal of Molecular Graphics & Modelling
36. Journal of Theoretical Biology
37. Mathematical Biosciences
38. Mathematical Medicine and Biology-A Journal of the IMA
39. Mathematical Modelling of Natural Phenomena
40. Medical & Biological Engineering & Computing
41. Molecular Informatics
42. Npj Systems Biology and Applications
43. PLOS Computational Biology
44. Research Synthesis Methods
45. SAR and QSAR in Environmental Research
46. Statistical Applications in Genetics and Molecular Biology
47. Statistical Methods in Medical Research
48. Statistics and Its Interface
49. Statistics in Biopharmaceutical Research
50. Statistics in Medicine
51. Theoretical Population Biology
52. Theory in Biosciences
53. Wiley Interdisciplinary Reviews-Computational Molecular Science

<a id="scie-mathematics"></a>

### Mathematics

期刊数：334

1. Abhandlungen aus dem Mathematischen Seminar der Universitat Hamburg
2. Acta Arithmetica
3. Acta Mathematica
4. Acta Mathematica Hungarica
5. Acta Mathematica Scientia
6. Acta Mathematica Sinica-English Series
7. Acta Numerica
8. Advanced Nonlinear Studies
9. Advances in Calculus of Variations
10. Advances in Continuous and Discrete Models
11. Advances in Differential Equations
12. Advances in Geometry
13. Advances in Mathematics
14. Advances in Nonlinear Analysis
15. Aequationes Mathematicae
16. AIMS Mathematics
17. AKCE International Journal of Graphs and Combinatorics
18. Algebra & Number Theory
19. Algebra and Logic
20. Algebra Colloquium
21. Algebra Universalis
22. Algebraic and Geometric Topology
23. Algebraic Geometry
24. Algebras and Representation Theory
25. American Journal of Mathematics
26. American Mathematical Monthly
27. Analele Stiintifice Ale Universitatii Ovidius Constanta-Seria Matematica
28. Analysis & PDE
29. Analysis and Applications
30. Analysis and Geometry in Metric Spaces
31. Analysis and Mathematical Physics
32. Analysis Mathematica
33. Annales de l Institut Fourier
34. Annales Fennici Mathematici
35. Annales Polonici Mathematici
36. Annales Scientifiques de l Ecole Normale Superieure
37. Annali della Scuola Normale Superiore di Pisa-Classe di Scienze
38. Annali di Matematica Pura Ed Applicata
39. Annals of Functional Analysis
40. Annals of Global Analysis and Geometry
41. Annals of Mathematics
42. Annals of PDE
43. Annals of Pure and Applied Logic
44. Applicable Analysis and Discrete Mathematics
45. Applied Categorical Structures
46. Archiv der Mathematik
47. Archive for Mathematical Logic
48. Arkiv för Matematik
49. Ars Mathematica Contemporanea
50. Asian Journal of Mathematics
51. Asterisque
52. Banach Journal of Mathematical Analysis
53. Boundary Value Problems
54. Bulletin de la Societe Mathematique de France
55. Bulletin des Sciences Mathematiques
56. Bulletin Mathematique de la Societe des Sciences Mathematiques de Roumanie
57. Bulletin of Mathematical Sciences
58. Bulletin of Symbolic Logic
59. Bulletin of the American Mathematical Society
60. Bulletin of the Australian Mathematical Society
61. Bulletin of the Belgian Mathematical Society-Simon Stevin
62. Bulletin of the Brazilian Mathematical Society
63. Bulletin of the Iranian Mathematical Society
64. Bulletin of the Korean Mathematical Society
65. Bulletin of the London Mathematical Society
66. Bulletin of the Malaysian Mathematical Sciences Society
67. Calcolo
68. Calculus of Variations and Partial Differential Equations
69. Cambridge Journal of Mathematics
70. Canadian Journal of Mathematics-Journal Canadien de Mathematiques
71. Canadian Mathematical Bulletin-Bulletin Canadien de Mathematiques
72. Carpathian Journal of Mathematics
73. Chinese Annals of Mathematics Series B
74. Collectanea Mathematica
75. Colloquium Mathematicum
76. Combinatorica
77. Combinatorics Probability and Computing
78. Commentarii Mathematici Helvetici
79. Communications in Algebra
80. Communications in Analysis and Geometry
81. Communications in Contemporary Mathematics
82. Communications in Mathematics and Statistics
83. Communications in Number Theory and Physics
84. Communications in Partial Differential Equations
85. Communications on Pure and Applied Analysis
86. Communications on Pure and Applied Mathematics
87. Complex Analysis and Operator Theory
88. Complex Variables and Elliptic Equations
89. Compositio Mathematica
90. Comptes Rendus Mathematique
91. Computational Complexity
92. Computational Geometry-Theory and Applications
93. Computational Methods and Function Theory
94. Constructive Approximation
95. Contributions to Discrete Mathematics
96. Czechoslovak Mathematical Journal
97. Demonstratio Mathematica
98. Differential and Integral Equations
99. Differential Equations
100. Differential Geometry and Its Applications
101. Discrete & Computational Geometry
102. Discrete Analysis
103. Discrete and Continuous Dynamical Systems
104. Discrete Mathematics
105. Discrete Mathematics and Theoretical Computer Science
106. Discussiones Mathematicae Graph Theory
107. Dissertationes Mathematicae
108. Documenta Mathematica
109. Doklady Mathematics
110. Duke Mathematical Journal
111. Electronic Journal of Combinatorics
112. Electronic Journal of Differential Equations
113. Electronic Journal of Linear Algebra
114. Electronic Journal of Qualitative Theory of Differential Equations
115. Electronic Research Archive
116. Ergodic Theory and Dynamical Systems
117. European Journal of Combinatorics
118. Evolution Equations and Control Theory
119. Experimental Mathematics
120. Expositiones Mathematicae
121. Filomat
122. Finite Fields and Their Applications
123. Fixed Point Theory
124. Forum Mathematicum
125. Forum of Mathematics Pi
126. Forum of Mathematics Sigma
127. Foundations of Computational Mathematics
128. Fractional Calculus and Applied Analysis
129. Frontiers of Mathematics
130. Functional Analysis and Its Applications
131. Fundamenta Mathematicae
132. Funkcialaj Ekvacioj-Serio Internacia
133. Geometriae Dedicata
134. Geometric and Functional Analysis
135. Geometry & Topology
136. Georgian Mathematical Journal
137. Glasgow Mathematical Journal
138. Glasnik Matematicki
139. Graphs and Combinatorics
140. Groups Geometry and Dynamics
141. Hacettepe Journal of Mathematics and Statistics
142. Hiroshima Mathematical Journal
143. Historia Mathematica
144. Hokkaido Mathematical Journal
145. Homology Homotopy and Applications
146. Houston Journal of Mathematics
147. Indagationes Mathematicae-New Series
148. Indian Journal of Pure & Applied Mathematics
149. Indiana University Mathematics Journal
150. Integral Equations and Operator Theory
151. Integral Transforms and Special Functions
152. Interfaces and Free Boundaries
153. International Journal of Algebra and Computation
154. International Journal of Mathematics
155. International Journal of Number Theory
156. International Journal of Numerical Analysis and Modeling
157. International Mathematics Research Notices
158. Inventiones Mathematicae
159. Iranian Journal of Fuzzy Systems
160. Israel Journal of Mathematics
161. Izvestiya Mathematics
162. Japanese Journal of Mathematics
163. Journal d Analyse Mathematique
164. Journal de l Ecole Polytechnique-Mathematiques
165. Journal de Mathematiques Pures et Appliquees
166. Journal de Theorie des Nombres de Bordeaux
167. Journal für die Reine und Angewandte Mathematik
168. Journal of Algebra
169. Journal of Algebra and Its Applications
170. Journal of Algebraic Combinatorics
171. Journal of Algebraic Geometry
172. Journal of Applied Mathematics and Computing
173. Journal of Approximation Theory
174. Journal of Combinatorial Algebra
175. Journal of Combinatorial Designs
176. Journal of Combinatorial Theory Series A
177. Journal of Combinatorial Theory Series B
178. Journal of Commutative Algebra
179. Journal of Complexity
180. Journal of Computational Mathematics
181. Journal of Contemporary Mathematical Analysis-Armenian Academy of Sciences
182. Journal of Convex Analysis
183. Journal of Difference Equations and Applications
184. Journal of Differential Equations
185. Journal of Differential Geometry
186. Journal of Dynamics and Differential Equations
187. Journal of Evolution Equations
188. Journal of Fixed Point Theory and Applications
189. Journal of Fractal Geometry
190. Journal of Function Spaces
191. Journal of Functional Analysis
192. Journal of Geometric Analysis
193. Journal of Geometry and Physics
194. Journal of Graph Theory
195. Journal of Group Theory
196. Journal of Homotopy and Related Structures
197. Journal of Inequalities and Applications
198. Journal of Integral Equations and Applications
199. Journal of Inverse and Ill-Posed Problems
200. Journal of Knot Theory and Its Ramifications
201. Journal of Lie Theory
202. Journal of Mathematical Analysis and Applications
203. Journal of Mathematical Inequalities
204. Journal of Mathematical Logic
205. Journal of Mathematical Physics Analysis Geometry
206. Journal of Mathematics
207. Journal of Modern Dynamics
208. Journal of Noncommutative Geometry
209. Journal of Nonlinear and Convex Analysis
210. Journal of Nonlinear and Variational Analysis
211. Journal of Number Theory
212. Journal of Numerical Mathematics
213. Journal of Operator Theory
214. Journal of Pseudo-Differential Operators and Applications
215. Journal of Pure and Applied Algebra
216. Journal of Spectral Theory
217. Journal of Symbolic Logic
218. Journal of Symplectic Geometry
219. Journal of the American Mathematical Society
220. Journal of the Australian Mathematical Society
221. Journal of the European Mathematical Society
222. Journal of the Institute of Mathematics of Jussieu
223. Journal of the Korean Mathematical Society
224. Journal of the London Mathematical Society-Second Series
225. Journal of the Mathematical Society of Japan
226. Journal of the Ramanujan Mathematical Society
227. Journal of Topology
228. Journal of Topology and Analysis
229. Kinetic and Related Models
230. Kodai Mathematical Journal
231. Kyoto Journal of Mathematics
232. Kyushu Journal of Mathematics
233. Law Probability & Risk
234. Linear & Multilinear Algebra
235. Linear Algebra and Its Applications
236. Lithuanian Mathematical Journal
237. Logic Journal of the IGPL
238. Manuscripta Mathematica
239. Mathematica Scandinavica
240. Mathematica Slovaca
241. Mathematical Communications
242. Mathematical Control and Related Fields
243. Mathematical Inequalities & Applications
244. Mathematical Intelligencer
245. Mathematical Logic Quarterly
246. Mathematical Modelling and Analysis
247. Mathematical Notes
248. Mathematical Proceedings of the Cambridge Philosophical Society
249. Mathematical Reports
250. Mathematical Research Letters
251. Mathematical Sciences
252. Mathematics
253. Mathematika
254. Mathematische Annalen
255. Mathematische Nachrichten
256. Mathematische Zeitschrift
257. Mediterranean Journal of Mathematics
258. Memoirs of the American Mathematical Society
259. Michigan Mathematical Journal
260. Milan Journal of Mathematics
261. Miskolc Mathematical Notes
262. Monatshefte für Mathematik
263. Moscow Mathematical Journal
264. Nagoya Mathematical Journal
265. New York Journal of Mathematics
266. Nonlinear Analysis-Theory Methods & Applications
267. Notre Dame Journal of Formal Logic
268. Numerical Linear Algebra with Applications
269. Numerical Mathematics-Theory Methods and Applications
270. Open Mathematics
271. Operators and Matrices
272. Order-a Journal on the Theory of Ordered Sets and Its Applications
273. Osaka Journal of Mathematics
274. Pacific Journal of Mathematics
275. Periodica Mathematica Hungarica
276. Portugaliae Mathematica
277. Positivity
278. Potential Analysis
279. Proceedings of the American Mathematical Society
280. Proceedings of the Edinburgh Mathematical Society
281. Proceedings of the Indian Academy of Sciences-Mathematical Sciences
282. Proceedings of the Japan Academy Series A-Mathematical Sciences
283. Proceedings of the London Mathematical Society
284. Proceedings of the Royal Society of Edinburgh Section A-Mathematics
285. Proceedings of the Steklov Institute of Mathematics
286. Publicacions Matematiques
287. Publicationes Mathematicae Debrecen
288. Publications Mathematiques de l Ihes
289. Publications of the Research Institute for Mathematical Sciences
290. Pure and Applied Mathematics Quarterly
291. Quaestiones Mathematicae
292. Qualitative Theory of Dynamical Systems
293. Quantum Topology
294. Quarterly Journal of Mathematics
295. Ramanujan Journal
296. Random Structures & Algorithms
297. Rendiconti del Seminario Matematico della Universita di Padova
298. Rendiconti Lincei-Matematica e Applicazioni
299. Reports on Mathematical Logic
300. Representation Theory
301. Research in the Mathematical Sciences
302. Results in Mathematics
303. Review of Symbolic Logic
304. Revista de la Real Academia de Ciencias Exactas Fisicas y Naturales Serie A-Matematicas
305. Revista de la Union Matematica Argentina
306. Revista Matematica Complutense
307. Revista Matematica Iberoamericana
308. Ricerche di Matematica
309. Rocky Mountain Journal of Mathematics
310. Russian Mathematical Surveys
311. Sbornik Mathematics
312. Science China-Mathematics
313. Selecta Mathematica-New Series
314. Semigroup Forum
315. SIAM Journal on Discrete Mathematics
316. Siberian Mathematical Journal
317. St Petersburg Mathematical Journal
318. Studia Logica
319. Studia Mathematica
320. Studia Scientiarum Mathematicarum Hungarica
321. Symmetry Integrability and Geometry-Methods and Applications
322. Taiwanese Journal of Mathematics
323. Theory and Applications of Categories
324. Theory of Computing Systems
325. Tohoku Mathematical Journal
326. Tokyo Journal of Mathematics
327. Topological Methods in Nonlinear Analysis
328. Topology and Its Applications
329. Transactions of the American Mathematical Society
330. Transformation Groups
331. Turkish Journal of Mathematics
332. TWMS Journal of Pure and Applied Mathematics
333. Ukrainian Mathematical Journal
334. Zeitschrift für Analysis und Ihre Anwendungen

<a id="scie-mathematics-applied"></a>

### Mathematics, Applied

期刊数：267

1. ACM Transactions on Algorithms
2. ACM Transactions on Mathematical Software
3. ACM Transactions on Modeling and Computer Simulation
4. Acta Applicandae Mathematicae
5. Acta Mathematica Sinica-English Series
6. Acta Mathematicae Applicatae Sinica-English Series
7. Advanced Nonlinear Studies
8. Advances in Applied Clifford Algebras
9. Advances in Applied Mathematics
10. Advances in Applied Mathematics and Mechanics
11. Advances in Calculus of Variations
12. Advances in Computational Mathematics
13. Advances in Continuous and Discrete Models
14. Advances in Differential Equations
15. Advances in Mathematics of Communications
16. Advances in Nonlinear Analysis
17. Aequationes Mathematicae
18. AIMS Mathematics
19. AKCE International Journal of Graphs and Combinatorics
20. Algebra Colloquium
21. Algorithmica
22. Analele Stiintifice Ale Universitatii Ovidius Constanta-Seria Matematica
23. Analysis & PDE
24. Analysis and Applications
25. Analysis and Mathematical Physics
26. Annales de l Institut Henri Poincare-Analyse Non Lineaire
27. Annali di Matematica Pura Ed Applicata
28. Annals of Combinatorics
29. Annals of Functional Analysis
30. Annals of Mathematics and Artificial Intelligence
31. Annals of Pure and Applied Logic
32. ANZIAM Journal
33. Applicable Algebra in Engineering Communication and Computing
34. Applicable Analysis
35. Applicable Analysis and Discrete Mathematics
36. Applications of Mathematics
37. Applied and Computational Harmonic Analysis
38. Applied and Computational Mathematics
39. Applied Mathematics and Computation
40. Applied Mathematics and Mechanics-English Edition
41. Applied Mathematics and Optimization
42. Applied Mathematics Letters
43. Applied Mathematics-A Journal of Chinese Universities Series B
44. Applied Numerical Mathematics
45. Archive for Rational Mechanics and Analysis
46. Archives of Control Sciences
47. Ars Mathematica Contemporanea
48. Asian Journal of Mathematics
49. Asymptotic Analysis
50. Axioms
51. Banach Journal of Mathematical Analysis
52. BIT Numerical Mathematics
53. Boundary Value Problems
54. Bulletin des Sciences Mathematiques
55. Calcolo
56. Calculus of Variations and Partial Differential Equations
57. Carpathian Journal of Mathematics
58. Chaos
59. Collectanea Mathematica
60. Communications in Analysis and Mechanics
61. Communications in Applied Mathematics and Computational Science
62. Communications in Contemporary Mathematics
63. Communications in Mathematical Sciences
64. Communications in Nonlinear Science and Numerical Simulation
65. Communications in Number Theory and Physics
66. Communications in Partial Differential Equations
67. Communications on Pure and Applied Analysis
68. Communications on Pure and Applied Mathematics
69. COMPEL-the International Journal for Computation and Mathematics in Electrical and Electronic Engineering
70. Complex Analysis and Operator Theory
71. Computational & Applied Mathematics
72. Computational Geometry-Theory and Applications
73. Computational Mathematics and Mathematical Physics
74. Computational Methods and Function Theory
75. Computational Methods in Applied Mathematics
76. Computational Optimization and Applications
77. Computer Aided Geometric Design
78. Computers & Mathematics with Applications
79. Cryptography and Communications-Discrete-Structures Boolean Functions and Sequences
80. Cryptologia
81. Designs Codes and Cryptography
82. Differential and Integral Equations
83. Differential Geometry and Its Applications
84. Discrete and Continuous Dynamical Systems
85. Discrete and Continuous Dynamical Systems-Series B
86. Discrete and Continuous Dynamical Systems-Series S
87. Discrete Applied Mathematics
88. Discrete Event Dynamic Systems-Theory and Applications
89. Discrete Mathematics and Theoretical Computer Science
90. Discrete Optimization
91. Dynamical Systems-an International Journal
92. Dynamics of Partial Differential Equations
93. East Asian Journal on Applied Mathematics
94. Electronic Journal of Combinatorics
95. Electronic Journal of Differential Equations
96. Electronic Journal of Qualitative Theory of Differential Equations
97. Electronic Transactions on Numerical Analysis
98. Ergodic Theory and Dynamical Systems
99. ESAIM-Control Optimisation and Calculus of Variations
100. ESAIM-Mathematical Modelling and Numerical Analysis
101. European Journal of Applied Mathematics
102. Evolution Equations and Control Theory
103. Filomat
104. Finite Elements in Analysis and Design
105. Finite Fields and Their Applications
106. Fixed Point Theory
107. Forum Mathematicum
108. Forum of Mathematics Pi
109. Forum of Mathematics Sigma
110. Foundations of Computational Mathematics
111. Fractional Calculus and Applied Analysis
112. Functional Analysis and Its Applications
113. Fundamenta Informaticae
114. Funkcialaj Ekvacioj-Serio Internacia
115. Fuzzy Sets and Systems
116. Glasnik Matematicki
117. Homology Homotopy and Applications
118. IEEE Transactions on Information Theory
119. IMA Journal of Applied Mathematics
120. IMA Journal of Mathematical Control and Information
121. IMA Journal of Numerical Analysis
122. Image Analysis & Stereology
123. Infinite Dimensional Analysis Quantum Probability and Related Topics
124. Informatica
125. Information and Computation
126. Information and Inference-A Journal of the IMA
127. Integral Transforms and Special Functions
128. Interfaces and Free Boundaries
129. International Journal of Applied Mathematics and Computer Science
130. International Journal of Computer Mathematics
131. International Journal of Numerical Analysis and Modeling
132. International Journal of Robust and Nonlinear Control
133. Inverse Problems
134. Inverse Problems and Imaging
135. Iranian Journal of Fuzzy Systems
136. Japan Journal of Industrial and Applied Mathematics
137. Journal de Mathematiques Pures et Appliquees
138. Journal of Algebra and Its Applications
139. Journal of Applied Analysis and Computation
140. Journal of Applied Mathematics and Computing
141. Journal of Combinatorial Optimization
142. Journal of Complexity
143. Journal of Computational and Applied Mathematics
144. Journal of Computational and Theoretical Transport
145. Journal of Computational Mathematics
146. Journal of Cryptology
147. Journal of Difference Equations and Applications
148. Journal of Dynamical and Control Systems
149. Journal of Dynamics and Differential Equations
150. Journal of Evolution Equations
151. Journal of Fixed Point Theory and Applications
152. Journal of Fourier Analysis and Applications
153. Journal of Function Spaces
154. Journal of Global Optimization
155. Journal of Hyperbolic Differential Equations
156. Journal of Inequalities and Applications
157. Journal of Integral Equations and Applications
158. Journal of Inverse and Ill-Posed Problems
159. Journal of Mathematical Analysis and Applications
160. Journal of Mathematical Fluid Mechanics
161. Journal of Mathematical Imaging and Vision
162. Journal of Mathematical Inequalities
163. Journal of Modern Dynamics
164. Journal of Noncommutative Geometry
165. Journal of Nonlinear and Convex Analysis
166. Journal of Nonlinear and Variational Analysis
167. Journal of Nonlinear Complex and Data Science
168. Journal of Nonlinear Mathematical Physics
169. Journal of Nonlinear Science
170. Journal of Numerical Mathematics
171. Journal of Optimization Theory and Applications
172. Journal of Pseudo-Differential Operators and Applications
173. Journal of Pure and Applied Algebra
174. Journal of Scientific Computing
175. Journal of Spectral Theory
176. Journal of Symbolic Computation
177. Journal of the European Mathematical Society
178. Journal of the Korean Mathematical Society
179. Kinetic and Related Models
180. Linear Algebra and Its Applications
181. Logic Journal of the IGPL
182. Mathematical and Computer Modelling of Dynamical Systems
183. Mathematical Communications
184. Mathematical Control and Related Fields
185. Mathematical Methods in the Applied Sciences
186. Mathematical Methods of Operations Research
187. Mathematical Modelling of Natural Phenomena
188. Mathematical Models & Methods in Applied Sciences
189. Mathematical Physics Analysis and Geometry
190. Mathematical Programming
191. Mathematical Programming Computation
192. Mathematical Sciences
193. Mathematics and Computers in Simulation
194. Mathematics of Computation
195. Mathematics of Operations Research
196. Mathematika
197. Mediterranean Journal of Mathematics
198. Milan Journal of Mathematics
199. Moscow Mathematical Journal
200. NoDEA-Nonlinear Differential Equations and Applications
201. Nonlinear Analysis-Hybrid Systems
202. Nonlinear Analysis-Modelling and Control
203. Nonlinear Analysis-Real World Applications
204. Nonlinear Analysis-Theory Methods & Applications
205. Nonlinearity
206. Numerical Algorithms
207. Numerical Functional Analysis and Optimization
208. Numerical Linear Algebra with Applications
209. Numerical Mathematics-Theory Methods and Applications
210. Numerical Methods for Partial Differential Equations
211. Numerische Mathematik
212. Optimal Control Applications & Methods
213. Optimization
214. Optimization Letters
215. Optimization Methods & Software
216. Pacific Journal of Optimization
217. Periodica Mathematica Hungarica
218. Physica D-Nonlinear Phenomena
219. Portugaliae Mathematica
220. Problems of Information Transmission
221. Proceedings of the American Mathematical Society
222. Proceedings of the Royal Society of Edinburgh Section A-Mathematics
223. Proceedings of the Steklov Institute of Mathematics
224. Pure and Applied Mathematics Quarterly
225. Qualitative Theory of Dynamical Systems
226. Quarterly Journal of Mechanics and Applied Mathematics
227. Quarterly of Applied Mathematics
228. RAIRO-Theoretical Informatics and Applications
229. Random Structures & Algorithms
230. Regular & Chaotic Dynamics
231. Rendiconti del Seminario Matematico della Universita di Padova
232. Rendiconti Lincei-Matematica e Applicazioni
233. Results in Mathematics
234. Review of Symbolic Logic
235. Revista de la Union Matematica Argentina
236. Revista Matematica Complutense
237. Ricerche di Matematica
238. Russian Journal of Numerical Analysis and Mathematical Modelling
239. Science China-Mathematics
240. Selecta Mathematica-New Series
241. Set-Valued and Variational Analysis
242. SIAM Journal on Applied Algebra and Geometry
243. SIAM Journal on Applied Dynamical Systems
244. SIAM Journal on Applied Mathematics
245. SIAM Journal on Computing
246. SIAM Journal on Control and Optimization
247. SIAM Journal on Discrete Mathematics
248. SIAM Journal on Imaging Sciences
249. SIAM Journal on Mathematical Analysis
250. SIAM Journal on Mathematics of Data Science
251. SIAM Journal on Matrix Analysis and Applications
252. SIAM Journal on Numerical Analysis
253. SIAM Journal on Optimization
254. SIAM Journal on Scientific Computing
255. SIAM Review
256. Stochastic Analysis and Applications
257. Stochastics and Partial Differential Equations-Analysis and Computations
258. Stochastics-an International Journal of Probability and Stochastic Processes
259. Studies in Applied Mathematics
260. Theory and Applications of Categories
261. Topology and Its Applications
262. TWMS Journal of Pure and Applied Mathematics
263. Ukrainian Mathematical Journal
264. University Politehnica of Bucharest Scientific Bulletin-Series A-Applied Mathematics and Physics
265. ZAMM-Zeitschrift für Angewandte Mathematik und Mechanik
266. Zeitschrift für Analysis und Ihre Anwendungen
267. Zeitschrift für Angewandte Mathematik und Physik

<a id="scie-mathematics-interdisciplinary-applications"></a>

### Mathematics, Interdisciplinary Applications

期刊数：106

1. Advances in Complex Systems
2. Annual Review of Statistics and Its Application
3. Applied Mathematical Modelling
4. Applied Mathematics in Science and Engineering
5. Applied Stochastic Models in Business and Industry
6. Archive for History of Exact Sciences
7. Archives of Computational Methods in Engineering
8. ASTIN Bulletin-the Journal of the International Actuarial Association
9. Bayesian Analysis
10. Bollettino di Storia delle Scienze Matematiche
11. British Journal of Mathematical & Statistical Psychology
12. Celestial Mechanics & Dynamical Astronomy
13. Chaos Solitons & Fractals
14. Chemometrics and Intelligent Laboratory Systems
15. Cmes-Computer Modeling in Engineering & Sciences
16. Combustion Theory and Modelling
17. Communications in Nonlinear Science and Numerical Simulation
18. Complexity
19. Computational and Mathematical Organization Theory
20. Computational Economics
21. Computational Mechanics
22. Computational Particle Mechanics
23. Computer Methods in Applied Mechanics and Engineering
24. Discrete Dynamics in Nature and Society
25. Dynamic Games and Applications
26. Econometric Reviews
27. Econometric Theory
28. Econometrica
29. Econometrics Journal
30. Economic Computation and Economic Cybernetics Studies and Research
31. Educational and Psychological Measurement
32. Engineering Analysis with Boundary Elements
33. Engineering Computations
34. Environmental and Ecological Statistics
35. Environmetrics
36. EPJ Data Science
37. Extremes
38. Finance and Stochastics
39. Fluctuation and Noise Letters
40. Fractal and Fractional
41. Fractals-Complex Geometry Patterns and Scaling in Nature and Society
42. Fractional Calculus and Applied Analysis
43. Grey Systems-Theory and Application
44. Historia Mathematica
45. IEEE Transactions on Computational Biology and Bioinformatics
46. IEEE Transactions on Network Science and Engineering
47. IMA Journal of Management Mathematics
48. Insurance Mathematics & Economics
49. International Journal for Multiscale Computational Engineering
50. International Journal for Numerical Methods in Biomedical Engineering
51. International Journal for Numerical Methods in Engineering
52. International Journal for Numerical Methods in Fluids
53. International Journal for Uncertainty Quantification
54. International Journal of Bifurcation and Chaos
55. International Journal of Computational Methods
56. International Journal of Game Theory
57. International Journal of Numerical Methods for Heat & Fluid Flow
58. International Journal of Numerical Modelling-Electronic Networks Devices and Fields
59. International Journal of Quantum Chemistry
60. International Journal of Wavelets Multiresolution and Information Processing
61. Journal of Causal Inference
62. Journal of Cellular Automata
63. Journal of Chemometrics
64. Journal of Classification
65. Journal of Complex Networks
66. Journal of Econometrics
67. Journal of Engineering Mathematics
68. Journal of Grey System
69. Journal of Industrial and Management Optimization
70. Journal of Mathematical Chemistry
71. Journal of Mathematical Economics
72. Journal of Mathematical Psychology
73. Journal of Mathematical Sociology
74. Journal of Mathematics and Music
75. Journal of Systems Science & Complexity
76. Journal of the Franklin Institute
77. Journal of Theoretical and Computational Acoustics
78. Journal of Time Series Analysis
79. Lifetime Data Analysis
80. Match-Communications in Mathematical and in Computer Chemistry
81. Mathematical Finance
82. Mathematical Geosciences
83. Mathematical Modelling of Natural Phenomena
84. Mathematical Population Studies
85. Mathematical Social Sciences
86. Mathematics and Financial Economics
87. Mathematics and Mechanics of Solids
88. Mathematics in Engineering
89. Mathematics of Control Signals and Systems
90. Multiscale Modeling & Simulation
91. Multivariate Behavioral Research
92. Natural Resource Modeling
93. Networks and Heterogeneous Media
94. Nonlinear Analysis-Modelling and Control
95. Nonlinear Processes in Geophysics
96. Optimization and Engineering
97. Psychometrika
98. Quantitative Finance
99. Revista Internacional de Metodos Numericos para Calculo y Diseno en Ingenieria
100. Risk Analysis
101. Scandinavian Actuarial Journal
102. SIAM Journal on Financial Mathematics
103. SIAM-ASA Journal on Uncertainty Quantification
104. Spatial Statistics
105. Statistics and Its Interface
106. Structural Equation Modeling-A Multidisciplinary Journal

<a id="scie-mechanics"></a>

### Mechanics

期刊数：137

1. Acta Mechanica
2. Acta Mechanica Sinica
3. Acta Mechanica Solida Sinica
4. Advances in Applied Mathematics and Mechanics
5. Annual Review of Fluid Mechanics
6. Applied Mathematical Modelling
7. Applied Mathematics and Mechanics-English Edition
8. Applied Mechanics Reviews
9. Applied Rheology
10. Applied Thermal Engineering
11. Archive for Rational Mechanics and Analysis
12. Archive of Applied Mechanics
13. Archives of Mechanics
14. Communications in Nonlinear Science and Numerical Simulation
15. Composite Structures
16. Comptes Rendus Mecanique
17. Computational Mechanics
18. Computational Particle Mechanics
19. Computer Methods in Applied Mechanics and Engineering
20. Computers & Fluids
21. Continuum Mechanics and Thermodynamics
22. Doklady Physics
23. Energy Conversion and Management
24. Engineering Applications of Computational Fluid Mechanics
25. Engineering Computations
26. Engineering Fracture Mechanics
27. Environmental Fluid Mechanics
28. European Journal of Mechanics A-Solids
29. European Journal of Mechanics B-Fluids
30. Experimental Mechanics
31. Experimental Techniques
32. Experiments in Fluids
33. Extreme Mechanics Letters
34. Finite Elements in Analysis and Design
35. Flow Turbulence and Combustion
36. Fluid Dynamics
37. Fluid Dynamics Research
38. Geophysical and Astrophysical Fluid Dynamics
39. Granular Matter
40. Heat and Mass Transfer
41. Heat Transfer Engineering
42. High Temperatures-High Pressures
43. Image Analysis & Stereology
44. International Communications in Heat and Mass Transfer
45. International Journal for Numerical and Analytical Methods in Geomechanics
46. International Journal for Numerical Methods in Fluids
47. International Journal of Acoustics and Vibration
48. International Journal of Aeroacoustics
49. International Journal of Applied Electromagnetics and Mechanics
50. International Journal of Applied Mechanics
51. International Journal of Computational Fluid Dynamics
52. International Journal of Damage Mechanics
53. International Journal of Fracture
54. International Journal of Heat and Fluid Flow
55. International Journal of Heat and Mass Transfer
56. International Journal of Impact Engineering
57. International Journal of Mechanical Sciences
58. International Journal of Mechanics and Materials in Design
59. International Journal of Multiphase Flow
60. International Journal of Non-Linear Mechanics
61. International Journal of Numerical Methods for Heat & Fluid Flow
62. International Journal of Plasticity
63. International Journal of Solids and Structures
64. International Journal of Structural Stability and Dynamics
65. International Journal of Thermophysics
66. Journal of Adhesion
67. Journal of Adhesion Science and Technology
68. Journal of Applied Fluid Mechanics
69. Journal of Applied Mechanics and Technical Physics
70. Journal of Applied Mechanics-Transactions of the ASME
71. Journal of Composites for Construction
72. Journal of Computational and Nonlinear Dynamics
73. Journal of Elasticity
74. Journal of Engineering Thermophysics
75. Journal of Fluid Mechanics
76. Journal of Fluids and Structures
77. Journal of Hydrodynamics
78. Journal of Mathematical Fluid Mechanics
79. Journal of Mechanics
80. Journal of Mechanics of Materials and Structures
81. Journal of Non-Equilibrium Thermodynamics
82. Journal of Non-Newtonian Fluid Mechanics
83. Journal of Nonlinear Complex and Data Science
84. Journal of Nonlinear Science
85. Journal of Porous Media
86. Journal of Rheology
87. Journal of Sound and Vibration
88. Journal of Statistical Mechanics-Theory and Experiment
89. Journal of Strain Analysis for Engineering Design
90. Journal of the Mechanics and Physics of Solids
91. Journal of Theoretical and Applied Mechanics
92. Journal of Thermal Stresses
93. Journal of Turbulence
94. Journal of Vibration and Acoustics-Transactions of the ASME
95. Journal of Vibration and Control
96. Journal of Vibration Engineering & Technologies
97. Journal of Wind Engineering and Industrial Aerodynamics
98. Korea-Australia Rheology Journal
99. Latin American Journal of Solids and Structures
100. Magnetohydrodynamics
101. Mathematics and Mechanics of Solids
102. Meccanica
103. Mechanics & Industry
104. Mechanics Based Design of Structures and Machines
105. Mechanics of Composite Materials
106. Mechanics of Materials
107. Mechanics of Solids
108. Mechanics of Time-Dependent Materials
109. Mechanics Research Communications
110. Mechanika
111. Microgravity Science and Technology
112. Multibody System Dynamics
113. Multidiscipline Modeling in Materials and Structures
114. Nihon Reoroji Gakkaishi
115. Nonlinear Analysis-Modelling and Control
116. Nonlinear Dynamics
117. Numerical Heat Transfer Part A-Applications
118. Numerical Heat Transfer Part B-Fundamentals
119. Physical Mesomechanics
120. Physics of Fluids
121. Probabilistic Engineering Mechanics
122. Proceedings of the Institution of Mechanical Engineers Part K-Journal of Multi-Body Dynamics
123. Progress in Computational Fluid Dynamics
124. Quarterly Journal of Mechanics and Applied Mathematics
125. Regular & Chaotic Dynamics
126. Rheologica Acta
127. Shock and Vibration
128. Shock Waves
129. Structural and Multidisciplinary Optimization
130. Theoretical and Applied Fracture Mechanics
131. Theoretical and Computational Fluid Dynamics
132. Thermal Science and Engineering Progress
133. Thermophysics and Aeromechanics
134. Thin-Walled Structures
135. Wave Motion
136. Wind and Structures
137. ZAMM-Zeitschrift für Angewandte Mathematik und Mechanik

<a id="scie-medical-ethics"></a>

### Medical Ethics

期刊数：16

1. Accountability in Research-Ethics Integrity and Policy
2. Acta Bioethica
3. American Journal of Bioethics
4. Bioethics
5. BMC Medical Ethics
6. Developing World Bioethics
7. Ethik in der Medizin
8. Hastings Center Report
9. Journal of Bioethical Inquiry
10. Journal of Empirical Research on Human Research Ethics
11. Journal of Law and the Biosciences
12. Journal of Law Medicine & Ethics
13. Journal of Medical Ethics
14. Neuroethics
15. Philosophy Ethics and Humanities in Medicine
16. Public Health Ethics

<a id="scie-medical-informatics"></a>

### Medical Informatics

期刊数：32

1. Applied Clinical Informatics
2. Artificial Intelligence in Medicine
3. Biomedical Engineering-Biomedizinische Technik
4. BMC Medical Informatics and Decision Making
5. CIN-Computers Informatics Nursing
6. Computer Methods and Programs in Biomedicine
7. Digital Health
8. Health Informatics Journal
9. Health Information Management Journal
10. Health Information Science and Systems
11. IEEE Journal of Biomedical and Health Informatics
12. Informatics for Health & Social Care
13. International Journal of Medical Informatics
14. International Journal of Technology Assessment in Health Care
15. Internet Interventions-the Application of Information Technology in Mental and Behavioural Health
16. JMIR Aging
17. JMIR Medical Informatics
18. JMIR Mhealth and Uhealth
19. JMIR Serious Games
20. Journal of Biomedical Informatics
21. Journal of Evaluation in Clinical Practice
22. Journal of Medical Internet Research
23. Journal of Medical Systems
24. Journal of the American Medical Informatics Association
25. Lancet Digital Health
26. Medical & Biological Engineering & Computing
27. Medical Decision Making
28. Methods of Information in Medicine
29. Npj Digital Medicine
30. Statistical Methods in Medical Research
31. Statistics in Medicine
32. Therapeutic Innovation & Regulatory Science

<a id="scie-medical-laboratory-technology"></a>

### Medical Laboratory Technology

期刊数：29

1. Acta Bioquimica Clinica Latinoamericana
2. Annales de Biologie Clinique
3. Annals of Clinical and Laboratory Science
4. Annals of Clinical Biochemistry
5. Annals of Laboratory Medicine
6. Applied Immunohistochemistry & Molecular Morphology
7. Archives of Pathology & Laboratory Medicine
8. Biochemia Medica
9. Biopreservation and Biobanking
10. British Journal of Biomedical Science
11. Clinica Chimica Acta
12. Clinical Biochemistry
13. Clinical Chemistry
14. Clinical Chemistry and Laboratory Medicine
15. Clinical Laboratory
16. Clinics in Laboratory Medicine
17. Critical Reviews in Clinical Laboratory Sciences
18. Cytometry Part B-Clinical Cytometry
19. Diagnostic Cytopathology
20. Journal of Clinical Laboratory Analysis
21. Journal of Cytology
22. Journal of Laboratory Medicine
23. Journal of Mass Spectrometry and Advances in the Clinical Lab
24. Laboratory Medicine
25. Pharmaceutical Biology
26. Scandinavian Journal of Clinical & Laboratory Investigation
27. Seminars in Diagnostic Pathology
28. Therapeutic Drug Monitoring
29. Translational Research

<a id="scie-medicine-general-internal"></a>

### Medicine, General & Internal

期刊数：162

1. Acta Clinica Belgica
2. Acta Clinica Croatica
3. Acta Medica Portuguesa
4. African Health Sciences
5. American Family Physician
6. American Journal of Chinese Medicine
7. American Journal of Managed Care
8. American Journal of Medicine
9. American Journal of Preventive Medicine
10. American Journal of the Medical Sciences
11. Amyloid-Journal of Protein Folding Disorders
12. Annals Academy of Medicine Singapore
13. Annals of Family Medicine
14. Annals of Internal Medicine
15. Annals of Medicine
16. Annals of Saudi Medicine
17. Archives of Iranian Medicine
18. Archives of Medical Science
19. Atencion Primaria
20. Australian Journal of General Practice
21. Balkan Medical Journal
22. BMC Medicine
23. BMC Primary Care
24. BMJ Evidence-Based Medicine
25. BMJ Military Health
26. BMJ Open
27. BMJ-British Medical Journal
28. Bratislava Medical Journal
29. British Journal of General Practice
30. British Journal of Hospital Medicine
31. British Medical Bulletin
32. Bulletin de l Academie Nationale de Medecine
33. Canadian Family Physician
34. Canadian Medical Association Journal
35. Chinese Medical Journal
36. Chronic Illness
37. Cleveland Clinic Journal of Medicine
38. Clinical Medicine
39. Clinics
40. Cochrane Database of Systematic Reviews
41. Colombia Medica
42. Croatian Medical Journal
43. Current Medical Research and Opinion
44. Danish Medical Journal
45. Deutsche Medizinische Wochenschrift
46. Deutsches Arzteblatt International
47. Diagnostics
48. Dm Disease-a-Month
49. EClinicalMedicine
50. European Journal of Clinical Investigation
51. European Journal of General Practice
52. European Journal of Internal Medicine
53. Family Medicine
54. Family Practice
55. Frontiers in Medicine
56. Gaceta Medica de Mexico
57. Hippokratia
58. Hong Kong Medical Journal
59. Indian Journal of Medical Research
60. Innere Medizin
61. Internal and Emergency Medicine
62. Internal Medicine
63. Internal Medicine Journal
64. International Journal of Clinical Practice
65. International Journal of General Medicine
66. International Journal of Medical Sciences
67. International Journal of Osteopathic Medicine
68. Iranian Red Crescent Medical Journal
69. Irish Journal of Medical Science
70. Israel Medical Association Journal
71. Jaapa-Journal of the American Academy of Physician Assistants
72. JAMA Internal Medicine
73. JAMA Network Open
74. JAMA-Journal of the American Medical Association
75. JBI Evidence Implementation
76. Jcpsp-Journal of the College of Physicians and Surgeons Pakistan
77. Journal of Cachexia Sarcopenia and Muscle
78. Journal of Clinical Medicine
79. Journal of Evaluation in Clinical Practice
80. Journal of Evidence Based Medicine
81. Journal of General Internal Medicine
82. Journal of Hospital Medicine
83. Journal of Internal Medicine
84. Journal of Investigative Medicine
85. Journal of Korean Medical Science
86. Journal of Medical Economics
87. Journal of Nippon Medical School
88. Journal of Pain and Symptom Management
89. Journal of Postgraduate Medicine
90. Journal of Research in Medical Sciences
91. Journal of the American Board of Family Medicine
92. Journal of the Chinese Medical Association
93. Journal of the Formosan Medical Association
94. Journal of the National Medical Association
95. Journal of the Pakistan Medical Association
96. Journal of the Royal Society of Medicine
97. Journal of Translational Internal Medicine
98. Journal of Travel Medicine
99. Journal of Urban Health-Bulletin of the New York Academy of Medicine
100. Journal of Womens Health
101. Korean Journal of Internal Medicine
102. Kuwait Medical Journal
103. Laeknabladid
104. Lancet
105. Lancet Digital Health
106. Libyan Journal of Medicine
107. Mayo Clinic Proceedings
108. Medical Clinics of North America
109. Medical Journal of Australia
110. Medical Principles and Practice
111. Medical Problems of Performing Artists
112. Medicina Clinica
113. Medicina Dello Sport
114. Medicina-Buenos Aires
115. Medicina-Lithuania
116. Medicine
117. Medizinische Klinik-Intensivmedizin und Notfallmedizin
118. Military Medical Research
119. Military Medicine
120. National Medical Journal of India
121. Nature Reviews Disease Primers
122. New England Journal of Medicine
123. Nigerian Journal of Clinical Practice
124. Open Medicine
125. Orvosi Hetilap
126. Pain Medicine
127. Pakistan Journal of Medical Sciences
128. Palliative Medicine
129. Patient Preference and Adherence
130. PLOS Medicine
131. Polish Archives of Internal Medicine-Polskie Archiwum Medycyny Wewnetrznej
132. Postgraduate Medical Journal
133. Postgraduate Medicine
134. Presse Medicale
135. Preventive Medicine
136. Primary Care
137. QJM-an International Journal of Medicine
138. Revista Clinica Espanola
139. Revista da Associacao Medica Brasileira
140. Revista de Investigacion Clinica-Clinical and Translational Investigation
141. Revista Medica de Chile
142. Revue de Medecine Interne
143. Samj South African Medical Journal
144. Sao Paulo Medical Journal
145. Saudi Medical Journal
146. Scandinavian Journal of Primary Health Care
147. Scottish Medical Journal
148. Sexual Medicine
149. Singapore Medical Journal
150. Southern Medical Journal
151. Srpski Arhiv za Celokupno Lekarstvo
152. Swiss Medical Weekly
153. Systematic Reviews
154. Terapevticheskii Arkhiv
155. Tohoku Journal of Experimental Medicine
156. Translational Research
157. Turkish Journal of Medical Sciences
158. Upsala Journal of Medical Sciences
159. Vojnosanitetski Pregled
160. West Indian Medical Journal
161. Wiener Klinische Wochenschrift
162. Yonsei Medical Journal

<a id="scie-medicine-legal"></a>

### Medicine, Legal

期刊数：17

1. American Journal of Forensic Medicine and Pathology
2. Australian Journal of Forensic Sciences
3. Forensic Science International
4. Forensic Science International-Genetics
5. Forensic Science Medicine and Pathology
6. International Journal of Legal Medicine
7. Journal of Forensic and Legal Medicine
8. Journal of Forensic Sciences
9. Journal of Health Politics Policy and Law
10. Journal of Law and the Biosciences
11. Journal of Law Medicine & Ethics
12. Legal Medicine
13. Medical Law Review
14. Medicine Science and the Law
15. Rechtsmedizin
16. Regulatory Toxicology and Pharmacology
17. Science & Justice

<a id="scie-medicine-research-experimental"></a>

### Medicine, Research & Experimental

期刊数：134

1. Acta Medica Okayama
2. Advances in Clinical and Experimental Medicine
3. Advances in Medical Sciences
4. Advances in Therapy
5. Aerospace Medicine and Human Performance
6. Altex-Alternatives to Animal Experimentation
7. American Journal of Translational Research
8. Amyloid-Journal of Protein Folding Disorders
9. Annales de Biologie Clinique
10. Annual Review of Medicine
11. Archives of Medical Research
12. Archives of Pathology & Laboratory Medicine
13. Asian Biomedicine
14. ATLA-Alternatives to Laboratory Animals
15. Biomarker Research
16. Biomarkers in Medicine
17. Biomedical Journal
18. Biomedical Papers-Olomouc
19. Biomedical Research-Tokyo
20. Biomedicine & Pharmacotherapy
21. Biomedicines
22. Biomolecules and Biomedicine
23. Brazilian Journal of Medical and Biological Research
24. Bulletin of Experimental Biology and Medicine
25. Cancer Biology & Medicine
26. Cancer Biotherapy and Radiopharmaceuticals
27. Cancer Gene Therapy
28. Cell Reports Medicine
29. Cell Transplantation
30. Clinical and Experimental Medicine
31. Clinical and Investigative Medicine
32. Clinical and Translational Medicine
33. Clinical Science
34. Clinical Trials
35. Cold Spring Harbor Perspectives in Medicine
36. Contemporary Clinical Trials
37. Cts-Clinical and Translational Science
38. Current Medical Research and Opinion
39. Current Medical Science
40. Current Molecular Medicine
41. Current Research in Translational Medicine
42. Cytotherapy
43. Discovery Medicine
44. Disease Models & Mechanisms
45. Drug Delivery and Translational Research
46. EBioMedicine
47. EMBO Molecular Medicine
48. EPMA Journal
49. European Journal of Clinical Investigation
50. European Journal of Medical Research
51. Experimental and Molecular Medicine
52. Experimental and Therapeutic Medicine
53. Experimental Biology and Medicine
54. Experimental Hematology
55. Experimental Neurobiology
56. Expert Opinion on Biological Therapy
57. Expert Reviews in Molecular Medicine
58. Gene Therapy
59. Human Gene Therapy
60. In Vivo
61. Indian Journal of Medical Research
62. Inflammation and Regeneration
63. Innate Immunity
64. International Journal of Molecular Medicine
65. Investigacion Clinica
66. Iranian Journal of Basic Medical Sciences
67. JCI Insight
68. Journal of Applied Biomedicine
69. Journal of Biomedical Science
70. Journal of Bone and Mineral Metabolism
71. Journal of Cardiovascular Translational Research
72. Journal of Cellular and Molecular Medicine
73. Journal of Clinical Investigation
74. Journal of Diabetes Research
75. Journal of Experimental Medicine
76. Journal of Gene Medicine
77. Journal of Immunotherapy
78. Journal of Inherited Metabolic Disease
79. Journal of International Medical Research
80. Journal of Investigative Medicine
81. Journal of Molecular Medicine-Jmm
82. Journal of the Pakistan Medical Association
83. Journal of Translational Medicine
84. Journal of Zhejiang University-Science B
85. Kaohsiung Journal of Medical Sciences
86. Laboratory Investigation
87. Laryngoscope
88. Life Sciences
89. Lymphatic Research and Biology
90. M S-Medecine Sciences
91. mAbs
92. Medical Hypotheses
93. Medical Science Monitor
94. MedScience
95. Melanoma Research
96. Metabolic Syndrome and Related Disorders
97. Molecular Aspects of Medicine
98. Molecular Genetics and Metabolism
99. Molecular Medicine
100. Molecular Medicine Reports
101. Molecular Pharmaceutics
102. Molecular Therapy
103. Molecular Therapy Methods & Clinical Development
104. Molecular Therapy Nucleic Acids
105. Molecular Therapy Oncology
106. Nagoya Journal of Medical Science
107. Nanomedicine-Nanotechnology Biology and Medicine
108. Nature Medicine
109. Neuromodulation
110. Npj Vaccines
111. Nucleic Acid Therapeutics
112. Orphanet Journal of Rare Diseases
113. Perspectives in Biology and Medicine
114. Postepy Higieny i Medycyny Doswiadczalnej
115. PPAR Research
116. Revista Romana de Medicina de Laborator
117. Science Translational Medicine
118. Statistics in Medicine
119. STEM Cell Research & Therapy
120. STEM Cell Reviews and Reports
121. STEM Cells and Development
122. Theranostics
123. Tohoku Journal of Experimental Medicine
124. Translational Research
125. Trends in Molecular Medicine
126. Trials
127. Undersea and Hyperbaric Medicine
128. Vaccine
129. Vaccines
130. Wiley Interdisciplinary Reviews-Nanomedicine and Nanobiotechnology
131. WIREs Mechanisms of Disease
132. Wound Repair and Regeneration
133. Xenotransplantation
134. Yonago Acta Medica

<a id="scie-metallurgy-metallurgical-engineering"></a>

### Metallurgy & Metallurgical Engineering

期刊数：80

1. Acta Materialia
2. Acta Metallurgica Sinica
3. Anti-Corrosion Methods and Materials
4. Archives of Metallurgy and Materials
5. Calphad-Computer Coupling of Phase Diagrams and Thermochemistry
6. Canadian Metallurgical Quarterly
7. China Foundry
8. Corrosion
9. Corrosion Engineering Science and Technology
10. Corrosion Reviews
11. Corrosion Science
12. High Temperature Corrosion of Materials
13. Hydrometallurgy
14. Intermetallics
15. International Journal of Cast Metals Research
16. International Journal of Material Forming
17. International Journal of Materials Research
18. International Journal of Metalcasting
19. International Journal of Minerals Metallurgy and Materials
20. International Journal of Powder Metallurgy
21. International Journal of Refractory Metals & Hard Materials
22. Ironmaking & Steelmaking
23. ISIJ International
24. JOM
25. Journal of Alloys and Compounds
26. Journal of Central South University
27. Journal of Iron and Steel Research International
28. Journal of Magnesium and Alloys
29. Journal of Materials Research and Technology-Jmr&T
30. Journal of Materials Science & Technology
31. Journal of Mining and Metallurgy Section B-Metallurgy
32. Journal of Phase Equilibria and Diffusion
33. Journal of Sustainable Metallurgy
34. Journal of the Japan Institute of Metals and Materials
35. Journal of the Southern African Institute of Mining and Metallurgy
36. Korean Journal of Metals and Materials
37. Kovove Materialy-Metallic Materials
38. Materiali in Tehnologije
39. Materials
40. Materials and Corrosion-Werkstoffe und Korrosion
41. Materials at High Temperatures
42. Materials Characterization
43. Materials Research Letters
44. Materials Science and Engineering A-Structural Materials Properties Microstructure and Processing
45. Materials Science and Technology
46. Materials Transactions
47. Metal Science and Heat Treatment
48. Metallurgia Italiana
49. Metallurgical and Materials Transactions A-Physical Metallurgy and Materials Science
50. Metallurgical and Materials Transactions B-Process Metallurgy and Materials Processing Science
51. Metallurgical Research & Technology
52. Metallurgist
53. Metals
54. Metals Advances
55. Metals and Materials International
56. Mineral Processing and Extractive Metallurgy Review
57. Mining Metallurgy & Exploration
58. Philosophical Magazine
59. Philosophical Magazine Letters
60. Physics of Metals and Metallography
61. Powder Metallurgy
62. Powder Metallurgy and Metal Ceramics
63. Praktische Metallographie-Practical Metallography
64. Protection of Metals and Physical Chemistry of Surfaces
65. Rare Metal Materials and Engineering
66. Rare Metals
67. Revista de Metalurgia
68. Russian Journal of Non-Ferrous Metals
69. Science and Technology of Welding and Joining
70. Science of Sintering
71. Scripta Materialia
72. Soldagem & Inspecao
73. Soldering & Surface Mount Technology
74. Steel Research International
75. Tetsu to Hagane-Journal of the Iron and Steel Institute of Japan
76. Transactions of Nonferrous Metals Society of China
77. Transactions of the Indian Institute of Metals
78. Transactions of the Institute of Metal Finishing
79. Welding in the World
80. Welding Journal

<a id="scie-meteorology-atmospheric-sciences"></a>

### Meteorology & Atmospheric Sciences

期刊数：95

1. Advances in Atmospheric Sciences
2. Advances in Climate Change Research
3. Advances in Meteorology
4. Advances in Space Research
5. Aerosol Science and Technology
6. Agricultural and Forest Meteorology
7. Annales Geophysicae
8. Asia-Pacific Journal of Atmospheric Sciences
9. Atmosfera
10. Atmosphere
11. Atmosphere-Ocean
12. Atmospheric Chemistry and Physics
13. Atmospheric Environment
14. Atmospheric Measurement Techniques
15. Atmospheric Research
16. Atmospheric Science Letters
17. Boundary-Layer Meteorology
18. Bulletin of the American Meteorological Society
19. Climate Dynamics
20. Climate of the Past
21. Climate Research
22. Climate Risk Management
23. Climate Services
24. Climatic Change
25. Communications Earth & Environment
26. Current Climate Change Reports
27. Dynamics of Atmospheres and Oceans
28. Earth System Science Data
29. Earths Future
30. Elementa-Science of the Anthropocene
31. Environmental Fluid Mechanics
32. Environmental Research Letters
33. Geofizika
34. Geomatics Natural Hazards & Risk
35. Geoscience Data Journal
36. Geoscience Letters
37. Geoscientific Instrumentation Methods and Data Systems
38. Global Biogeochemical Cycles
39. Idojaras
40. International Journal of Biometeorology
41. International Journal of Climatology
42. International Journal of Disaster Risk Reduction
43. International Journal of Disaster Risk Science
44. Italian Journal of Agrometeorology-Rivista Italiana di Agrometeorologia
45. Izvestiya Atmospheric and Oceanic Physics
46. Journal of Advances in Modeling Earth Systems
47. Journal of Aerosol Science
48. Journal of Agricultural Meteorology
49. Journal of Applied Meteorology and Climatology
50. Journal of Atmospheric and Oceanic Technology
51. Journal of Atmospheric and Solar-Terrestrial Physics
52. Journal of Atmospheric Chemistry
53. Journal of Climate
54. Journal of Geophysical Research-Atmospheres
55. Journal of Hydrometeorology
56. Journal of Meteorological Research
57. Journal of Operational Oceanography
58. Journal of Southern Hemisphere Earth Systems Science
59. Journal of Space Weather and Space Climate
60. Journal of the Air & Waste Management Association
61. Journal of the Atmospheric Sciences
62. Journal of the Meteorological Society of Japan
63. Journal of Tropical Meteorology
64. Mausam
65. Meteorological Applications
66. Meteorologische Zeitschrift
67. Meteorology and Atmospheric Physics
68. Monthly Weather Review
69. Natural Hazards
70. Natural Hazards and Earth System Sciences
71. Natural Hazards Review
72. Nature Climate Change
73. Nature Reviews Earth & Environment
74. Nonlinear Processes in Geophysics
75. Npj Climate and Atmospheric Science
76. Ocean Modelling
77. Ocean Science
78. Physical Geography
79. Physics and Chemistry of the Earth
80. Quarterly Journal of the Royal Meteorological Society
81. Radio Science
82. Russian Meteorology and Hydrology
83. Sola
84. Space Weather-the International Journal of Research and Applications
85. Tellus Series A-Dynamic Meteorology and Oceanography
86. Tellus Series B-Chemical and Physical Meteorology
87. Terrestrial Atmospheric and Oceanic Sciences
88. Theoretical and Applied Climatology
89. Urban Climate
90. Water Air and Soil Pollution
91. Weather
92. Weather and Climate Extremes
93. Weather and Forecasting
94. Weather Climate and Society
95. Wiley Interdisciplinary Reviews-Climate Change

<a id="scie-microbiology"></a>

### Microbiology

期刊数：134

1. Acta Microbiologica et Immunologica Hungarica
2. Acta Protozoologica
3. Advancements of Microbiology
4. Anaerobe
5. Annals of Clinical Microbiology and Antimicrobials
6. Annals of Microbiology
7. Annual Review of Microbiology
8. Antimicrobial Agents and Chemotherapy
9. Antimicrobial Resistance and Infection Control
10. Antonie van Leeuwenhoek International Journal of General and Molecular Microbiology
11. Apmis
12. Applied and Environmental Microbiology
13. Applied Biochemistry and Microbiology
14. Aquatic Microbial Ecology
15. Archives of Microbiology
16. Beneficial Microbes
17. Bioscience of Microbiota Food and Health
18. BMC Microbiology
19. Brazilian Journal of Microbiology
20. Canadian Journal of Infectious Diseases & Medical Microbiology
21. Canadian Journal of Microbiology
22. Cell Host & Microbe
23. Cellular Microbiology
24. Clinical Infectious Diseases
25. Clinical Microbiology and Infection
26. Clinical Microbiology Reviews
27. Comparative Immunology Microbiology and Infectious Diseases
28. Critical Reviews in Microbiology
29. Current Microbiology
30. Current Opinion in Microbiology
31. Diagnostic Microbiology and Infectious Disease
32. Emerging Microbes & Infections
33. Enfermedades Infecciosas y Microbiologia Clinica
34. Environmental Microbiology
35. Environmental Microbiology Reports
36. Environmental Microbiome
37. Epidemiologie Mikrobiologie Imunologie
38. European Journal of Clinical Microbiology & Infectious Diseases
39. European Journal of Protistology
40. Expert Review of Anti-Infective Therapy
41. Extremophiles
42. FEMS Microbiology Ecology
43. FEMS Microbiology Letters
44. FEMS Microbiology Reviews
45. FEMS Yeast Research
46. Folia Microbiologica
47. Food and Environmental Virology
48. Food Microbiology
49. Frontiers in Cellular and Infection Microbiology
50. Frontiers in Microbiology
51. Future Microbiology
52. Gut Microbes
53. Gut Pathogens
54. Helicobacter
55. iMeta
56. Indian Journal of Microbiology
57. Innate Immunity
58. International Journal of Antimicrobial Agents
59. International Journal of Food Microbiology
60. International Journal of Medical Microbiology
61. International Journal of Systematic and Evolutionary Microbiology
62. International Microbiology
63. ISME Journal
64. Journal of Antibiotics
65. Journal of Antimicrobial Chemotherapy
66. Journal of Applied Microbiology
67. Journal of Bacteriology
68. Journal of Basic Microbiology
69. Journal of Clinical Microbiology
70. Journal of Eukaryotic Microbiology
71. Journal of Fungi
72. Journal of General and Applied Microbiology
73. Journal of Infectious Diseases
74. Journal of Medical Microbiology
75. Journal of Microbiological Methods
76. Journal of Microbiology
77. Journal of Microbiology and Biotechnology
78. Journal of Microbiology Immunology and Infection
79. Journal of Oral Microbiology
80. Journal of Water and Health
81. Jundishapur Journal of Microbiology
82. Lancet Microbe
83. Letters in Applied Microbiology
84. mBio
85. Medical Microbiology and Immunology
86. Microbes and Environments
87. Microbes and Infection
88. Microbial Biotechnology
89. Microbial Cell
90. Microbial Drug Resistance
91. Microbial Ecology
92. Microbial Genomics
93. Microbial Pathogenesis
94. Microbial Physiology
95. Microbial Risk Analysis
96. Microbiological Research
97. Microbiology
98. Microbiology and Immunology
99. Microbiology and Molecular Biology Reviews
100. Microbiology Spectrum
101. Microbiology-Sgm
102. MicrobiologyOpen
103. Microbiome
104. Microorganisms
105. Mikrobiyoloji Bulteni
106. Molecular Genetics Microbiology and Virology
107. Molecular Microbiology
108. Molecular Oral Microbiology
109. mSphere
110. mSystems
111. Nature Microbiology
112. Nature Reviews Microbiology
113. New Microbiologica
114. Npj Biofilms and Microbiomes
115. Open Forum Infectious Diseases
116. Pathogens
117. Phytobiomes Journal
118. Plasmid
119. PLOS Pathogens
120. Polish Journal of Microbiology
121. Probiotics and Antimicrobial Proteins
122. Protist
123. Research in Microbiology
124. Revista Argentina de Microbiologia
125. Revista Espanola de Quimioterapia
126. Rhizosphere
127. Symbiosis
128. Systematic and Applied Microbiology
129. Ticks and Tick-Borne Diseases
130. Trends in Microbiology
131. Tuberculosis
132. Veterinary Microbiology
133. Virulence
134. Yeast

<a id="scie-microscopy"></a>

### Microscopy

期刊数：8

1. Histochemistry and Cell Biology
2. Journal of Microscopy
3. Micron
4. Microscopy
5. Microscopy and Microanalysis
6. Microscopy Research and Technique
7. Ultramicroscopy
8. Ultrastructural Pathology

<a id="scie-mineralogy"></a>

### Mineralogy

期刊数：29

1. American Mineralogist
2. Applied Clay Science
3. Canadian Journal of Mineralogy and Petrology
4. Clay Minerals
5. Clays and Clay Minerals
6. Contributions to Mineralogy and Petrology
7. Economic Geology
8. Elements
9. European Journal of Mineralogy
10. Gems & Gemology
11. Geology of Ore Deposits
12. Gospodarka Surowcami Mineralnymi-Mineral Resources Management
13. JOM
14. Journal of Gemmology
15. Journal of Geosciences
16. Journal of Mineralogical and Petrological Sciences
17. Lithology and Mineral Resources
18. Lithos
19. Mineralium Deposita
20. Mineralogical Magazine
21. Mineralogy and Petrology
22. Minerals
23. Minerals Engineering
24. Neues Jahrbuch für Mineralogie-Abhandlungen
25. Ore Geology Reviews
26. Periodico di Mineralogia
27. Petrology
28. Physics and Chemistry of Minerals
29. Resource Geology

<a id="scie-mining-mineral-processing"></a>

### Mining & Mineral Processing

期刊数：21

1. Acta Geodynamica et Geomaterialia
2. Acta Montanistica Slovaca
3. Archives of Mining Sciences
4. Gospodarka Surowcami Mineralnymi-Mineral Resources Management
5. International Journal of Coal Preparation and Utilization
6. International Journal of Coal Science & Technology
7. International Journal of Minerals Metallurgy and Materials
8. International Journal of Mining Reclamation and Environment
9. International Journal of Mining Science and Technology
10. International Journal of Rock Mechanics and Mining Sciences
11. JOM
12. Journal of Applied Geophysics
13. Journal of Mining Science
14. Journal of the Southern African Institute of Mining and Metallurgy
15. Marine Georesources & Geotechnology
16. Mineral Processing and Extractive Metallurgy Review
17. Minerals
18. Minerals Engineering
19. Mining Metallurgy & Exploration
20. Ore Geology Reviews
21. Physicochemical Problems of Mineral Processing

<a id="scie-multidisciplinary-sciences"></a>

### Multidisciplinary Sciences

期刊数：76

1. Acta Scientiarum-Technology
2. Advanced Theory and Simulations
3. Advances in Complex Systems
4. All Life
5. American Scientist
6. Anais da Academia Brasileira de Ciencias
7. Annals of the New York Academy of Sciences
8. Arabian Journal for Science and Engineering
9. Chiang Mai Journal of Science
10. Complexity
11. Comptes Rendus de l Academie Bulgare des Sciences
12. Current Science
13. Defence Science Journal
14. Discrete Dynamics in Nature and Society
15. Endeavour
16. Facets
17. Fractals-Complex Geometry Patterns and Scaling in Nature and Society
18. GigaScience
19. Global Challenges
20. Heliyon
21. Herald of the Russian Academy of Sciences
22. Interdisciplinary Science Reviews
23. International Journal of Bifurcation and Chaos
24. Iranian Journal of Science
25. iScience
26. Issues in Science and Technology
27. Journal of Advanced Research
28. Journal of King Saud University Science
29. Journal of Radiation Research and Applied Sciences
30. Journal of Taibah University for Science
31. Journal of the Indian Institute of Science
32. Journal of the National Science Foundation of Sri Lanka
33. Journal of the Royal Society Interface
34. Journal of the Royal Society of New Zealand
35. Jove-Journal of Visualized Experiments
36. Kuwait Journal of Science
37. Machine Learning-Science and Technology
38. Maejo International Journal of Science and Technology
39. MIT Technology Review
40. National Academy Science Letters-India
41. National Science Review
42. Nature
43. Nature Communications
44. Nature Computational Science
45. Nature Human Behaviour
46. Nature Reviews Methods Primers
47. New Scientist
48. Npj Microgravity
49. PeerJ
50. Philosophical Transactions of the Royal Society A-Mathematical Physical and Engineering Sciences
51. PLOS One
52. Proceedings of the Estonian Academy of Sciences
53. Proceedings of the Japan Academy Series B-Physical and Biological Sciences
54. Proceedings of the National Academy of Sciences India Section A-Physical Sciences
55. Proceedings of the National Academy of Sciences of the United States of America
56. Proceedings of the Romanian Academy Series A-Mathematics Physics Technical Sciences Information Science
57. Proceedings of the Royal Society A-Mathematical Physical and Engineering Sciences
58. Rendiconti Lincei-Scienze Fisiche e Naturali
59. Research
60. Research Synthesis Methods
61. Royal Society Open Science
62. Sains Malaysiana
63. Science
64. Science Advances
65. Science and Engineering Ethics
66. Science Bulletin
67. Science of Nature
68. Science Progress
69. ScienceAsia
70. Scientific American
71. Scientific Data
72. Scientific Reports
73. Scientist
74. South African Journal of Science
75. Symmetry-Basel
76. Transactions of the Royal Society of South Australia

<a id="scie-mycology"></a>

### Mycology

期刊数：29

1. Cryptogamie Mycologie
2. FEMS Yeast Research
3. Fungal Biology
4. Fungal Biology Reviews
5. Fungal Diversity
6. Fungal Ecology
7. Fungal Genetics and Biology
8. IMA Fungus
9. International Journal of Medicinal Mushrooms
10. Journal de Mycologie Medicale
11. Journal of Fungi
12. Lichenologist
13. Medical Mycology
14. Mycobiology
15. MycoKeys
16. Mycologia
17. Mycological Progress
18. Mycopathologia
19. Mycorrhiza
20. Mycoscience
21. Mycoses
22. Mycosphere
23. Mycotoxin Research
24. Persoonia
25. Revista Iberoamericana de Micologia
26. Studies in Mycology
27. Sydowia
28. World Mycotoxin Journal
29. Yeast

<a id="scie-nanoscience-nanotechnology"></a>

### Nanoscience & Nanotechnology

期刊数：107

1. 2D Materials
2. ACM Journal on Emerging Technologies in Computing Systems
3. ACS Applied Materials & Interfaces
4. ACS Applied Nano Materials
5. ACS Energy Letters
6. ACS Nano
7. ACS Photonics
8. ACS Sensors
9. Advanced Composites and Hybrid Materials
10. Advanced Electronic Materials
11. Advanced Functional Materials
12. Advanced Healthcare Materials
13. Advanced Materials
14. Advanced Science
15. Advances in Nano Research
16. AIP Advances
17. APL Materials
18. Beilstein Journal of Nanotechnology
19. BioChip Journal
20. Biomedical Microdevices
21. Biomicrofluidics
22. Biosensors & Bioelectronics
23. Biosensors-Basel
24. Cancer Nanotechnology
25. Carbon Energy
26. ChemNanoMat
27. Colloid and Interface Science Communications
28. Current Nanoscience
29. Digest Journal of Nanomaterials and Biostructures
30. Discover Nano
31. Energy Storage Materials
32. Environmental Science-Nano
33. Fullerenes Nanotubes and Carbon Nanostructures
34. IEEE Transactions on NanoBioscience
35. IEEE Transactions on Nanotechnology
36. IET Nanobiotechnology
37. Inorganic and Nano-Metal Chemistry
38. International Journal of Nanomedicine
39. International Journal of Nanotechnology
40. Journal of Experimental Nanoscience
41. Journal of Laser Micro Nanoengineering
42. Journal of Micro-Nanopatterning Materials and Metrology-Jm3
43. Journal of Microelectromechanical Systems
44. Journal of Micromechanics and Microengineering
45. Journal of Nano Research
46. Journal of Nanobiotechnology
47. Journal of Nanoelectronics and Optoelectronics
48. Journal of Nanoparticle Research
49. Journal of Nanophotonics
50. Journal of Nanostructure in Chemistry
51. Journal of Physical Chemistry C
52. Journal of Physical Chemistry Letters
53. Journal of Physics-Materials
54. Journal of Science-Advanced Materials and Devices
55. Journal of Vacuum Science & Technology B
56. Lab on a Chip
57. Materials Science and Engineering A-Structural Materials Properties Microstructure and Processing
58. Materials Today Nano
59. Micro & Nano Letters
60. Microelectronic Engineering
61. Microelectronics Journal
62. Microelectronics Reliability
63. Microfluidics and Nanofluidics
64. Micromachines
65. Microporous and Mesoporous Materials
66. Microsystem Technologies-Micro-and Nanosystems-Information Storage and Processing Systems
67. Microsystems & Nanoengineering
68. Molecular Systems Design & Engineering
69. Nano
70. Nano Communication Networks
71. Nano Convergence
72. Nano Energy
73. Nano Futures
74. Nano Letters
75. Nano Research
76. Nano Today
77. Nano-Micro Letters
78. Nanocomposites
79. NanoImpact
80. Nanomaterials
81. Nanomaterials and Nanotechnology
82. Nanomedicine
83. Nanomedicine-Nanotechnology Biology and Medicine
84. Nanophotonics
85. Nanoscale
86. Nanoscale Advances
87. Nanoscale and Microscale Thermophysical Engineering
88. Nanoscale Horizons
89. Nanotechnology
90. Nanotechnology Reviews
91. Nanotoxicology
92. Nature Nanotechnology
93. Nature Reviews Materials
94. Npj 2D Materials and Applications
95. Particle & Particle Systems Characterization
96. Photonics and Nanostructures-Fundamentals and Applications
97. Physica E-Low-Dimensional Systems & Nanostructures
98. Plasmonics
99. Precision Engineering-Journal of the International Societies for Precision Engineering and Nanotechnology
100. Recent Patents on Nanotechnology
101. Reviews on Advanced Materials Science
102. Scripta Materialia
103. Sensors and Actuators Reports
104. Small
105. Small Methods
106. Small Structures
107. Wiley Interdisciplinary Reviews-Nanomedicine and Nanobiotechnology

<a id="scie-neuroimaging"></a>

### Neuroimaging

期刊数：14

1. American Journal of Neuroradiology
2. Brain Imaging and Behavior
3. Clinical EEG and Neuroscience
4. Human Brain Mapping
5. Journal of Neuroimaging
6. Journal of NeuroInterventional Surgery
7. Journal of Neuroradiology
8. Klinische Neurophysiologie
9. NeuroImage
10. NeuroImage-Clinical
11. Neuroimaging Clinics of North America
12. Neuroradiology
13. Psychiatry Research-Neuroimaging
14. Stereotactic and Functional Neurosurgery

<a id="scie-neurosciences"></a>

### Neurosciences

期刊数：271

1. ACS Chemical Neuroscience
2. Acta Neurobiologiae Experimentalis
3. Acta Neurologica Belgica
4. Acta Neuropathologica
5. Acta Neuropathologica Communications
6. Acta Neuropsychiatrica
7. Actas Espanolas de Psiquiatria
8. Acupuncture & Electro-Therapeutics Research
9. Alzheimers Research & Therapy
10. Annals of Clinical and Translational Neurology
11. Annals of Neurology
12. Annual Review of Neuroscience
13. Annual Review of Vision Science
14. Arquivos de Neuro-Psiquiatria
15. Asn Neuro
16. Audiology and Neurotology
17. Autonomic Neuroscience-Basic & Clinical
18. Behavioral and Brain Functions
19. Behavioral and Brain Sciences
20. Behavioral Neuroscience
21. Behavioural Brain Research
22. Behavioural Pharmacology
23. Biological Cybernetics
24. Biological Psychiatry
25. Biological Psychiatry-Cognitive Neuroscience and Neuroimaging
26. Bipolar Disorders
27. BMC Neuroscience
28. Brain
29. Brain and Behavior
30. Brain and Cognition
31. Brain and Language
32. Brain Behavior and Evolution
33. Brain Behavior and Immunity
34. Brain Connectivity
35. Brain Impairment
36. Brain Injury
37. Brain Mechanisms
38. Brain Pathology
39. Brain Research
40. Brain Research Bulletin
41. Brain Sciences
42. Brain Stimulation
43. Brain Structure & Function
44. Brain Topography
45. Cellular and Molecular Neurobiology
46. Cephalalgia
47. Cerebellum
48. Cerebral Cortex
49. Ceska a Slovenska Neurologie a Neurochirurgie
50. Chemical Senses
51. Clinical Autonomic Research
52. Clinical EEG and Neuroscience
53. Clinical Neurophysiology
54. Clinical Psychopharmacology and Neuroscience
55. CNS & Neurological Disorders-Drug Targets
56. CNS Neuroscience & Therapeutics
57. Cognitive Affective & Behavioral Neuroscience
58. Cognitive Computation
59. Cognitive Neurodynamics
60. Cognitive Neuroscience
61. Cognitive Systems Research
62. Cortex
63. Current Alzheimer Research
64. Current Neurology and Neuroscience Reports
65. Current Neuropharmacology
66. Current Neurovascular Research
67. Current Opinion in Behavioral Sciences
68. Current Opinion in Neurobiology
69. Current Opinion in Neurology
70. Developmental Cognitive Neuroscience
71. Developmental Neurobiology
72. Developmental Neuroscience
73. Dialogues in Clinical Neuroscience
74. Discover Neuroscience
75. Encephale-Revue de Psychiatrie Clinique Biologique et Therapeutique
76. eNeuro
77. Epilepsia Open
78. European Journal of Neurology
79. European Journal of Neuroscience
80. European Journal of Pain
81. European Neurology
82. European Neuropsychopharmacology
83. Experimental Brain Research
84. Experimental Neurobiology
85. Experimental Neurology
86. Fluids and Barriers of the CNS
87. Folia Neuropathologica
88. Frontiers in Aging Neuroscience
89. Frontiers in Behavioral Neuroscience
90. Frontiers in Cellular Neuroscience
91. Frontiers in Computational Neuroscience
92. Frontiers in Human Neuroscience
93. Frontiers in Integrative Neuroscience
94. Frontiers in Molecular Neuroscience
95. Frontiers in Neural Circuits
96. Frontiers in Neuroanatomy
97. Frontiers in Neuroendocrinology
98. Frontiers in Neuroinformatics
99. Frontiers in Neurology
100. Frontiers in Neurorobotics
101. Frontiers in Neuroscience
102. Frontiers in Synaptic Neuroscience
103. Frontiers in Systems Neuroscience
104. Gait & Posture
105. Genes Brain and Behavior
106. Glia
107. Hearing Research
108. Hippocampus
109. Human Brain Mapping
110. Human Movement Science
111. Ideggyogyaszati Szemle-Clinical Neuroscience
112. IEEE Transactions on Cognitive and Developmental Systems
113. International Journal of Developmental Neuroscience
114. International Journal of Neuropsychopharmacology
115. International Journal of Neuroscience
116. International Journal of Psychophysiology
117. Jaro-Journal of the Association for Research in Otolaryngology
118. Journal of Alzheimers Disease
119. Journal of Cerebral Blood Flow and Metabolism
120. Journal of Clinical Neurophysiology
121. Journal of Clinical Neuroscience
122. Journal of Cognitive Neuroscience
123. Journal of Comparative Neurology
124. Journal of Comparative Physiology A-Neuroethology Sensory Neural and Behavioral Physiology
125. Journal of Computational Neuroscience
126. Journal of Electromyography and Kinesiology
127. Journal of Headache and Pain
128. Journal of Integrative Neuroscience
129. Journal of Molecular Neuroscience
130. Journal of Motor Behavior
131. Journal of Musculoskeletal & Neuronal Interactions
132. Journal of Neural Engineering
133. Journal of Neural Transmission
134. Journal of Neurochemistry
135. Journal of Neurodevelopmental Disorders
136. Journal of Neuroendocrinology
137. Journal of NeuroEngineering and Rehabilitation
138. Journal of Neurogenetics
139. Journal of Neuroimmune Pharmacology
140. Journal of Neuroimmunology
141. Journal of Neuroinflammation
142. Journal of Neurolinguistics
143. Journal of Neuromuscular Diseases
144. Journal of Neuropathology and Experimental Neurology
145. Journal of Neurophysiology
146. Journal of Neuropsychiatry and Clinical Neurosciences
147. Journal of Neuroscience
148. Journal of Neuroscience Methods
149. Journal of Neuroscience Research
150. Journal of Neurotrauma
151. Journal of NeuroVirology
152. Journal of Pain
153. Journal of Parkinsons Disease
154. Journal of Physiology-London
155. Journal of Pineal Research
156. Journal of Psychiatry & Neuroscience
157. Journal of Psychopharmacology
158. Journal of Psychophysiology
159. Journal of Sleep Research
160. Journal of Stroke & Cerebrovascular Diseases
161. Journal of the History of the Neurosciences
162. Journal of the International Neuropsychological Society
163. Journal of the Neurological Sciences
164. Journal of the Peripheral Nervous System
165. Journal of Vestibular Research-Equilibrium & Orientation
166. Learning & Memory
167. Metabolic Brain Disease
168. Molecular and Cellular Neuroscience
169. Molecular Autism
170. Molecular Brain
171. Molecular Neurobiology
172. Molecular Neurodegeneration
173. Molecular Pain
174. Molecular Psychiatry
175. Motor Control
176. Multiple Sclerosis Journal
177. Muscle & Nerve
178. Nature Aging
179. Nature and Science of Sleep
180. Nature Human Behaviour
181. Nature Neuroscience
182. Nature Reviews Neuroscience
183. Network Neuroscience
184. Network-Computation in Neural Systems
185. Neural Computation
186. Neural Networks
187. Neural Plasticity
188. Neural Regeneration Research
189. Neurobiology of Aging
190. Neurobiology of Disease
191. Neurobiology of Learning and Memory
192. Neurobiology of Stress
193. Neurochemical Journal
194. Neurochemical Research
195. Neurochemistry International
196. Neurocirugia
197. Neurodegenerative Diseases
198. Neuroendocrinology
199. Neuroendocrinology Letters
200. Neurogastroenterology and Motility
201. NeuroImage
202. Neuroimaging Clinics of North America
203. NeuroImmunoModulation
204. Neuroinformatics
205. Neurologic Clinics
206. Neurological Research
207. Neurological Sciences
208. Neurological Sciences and Neurophysiology
209. Neurology India
210. Neurology-Neuroimmunology & Neuroinflammation
211. Neuromodulation
212. NeuroMolecular Medicine
213. Neuromuscular Disorders
214. Neuron
215. Neuropathology
216. Neuropathology and Applied Neurobiology
217. Neuropeptides
218. Neuropharmacology
219. Neurophotonics
220. Neurophysiologie Clinique-Clinical Neurophysiology
221. Neurophysiology
222. Neuropsychobiology
223. Neuropsychologia
224. Neuropsychological Rehabilitation
225. Neuropsychology
226. Neuropsychology Review
227. Neuropsychopharmacology
228. Neuroreport
229. Neuroscience
230. Neuroscience and Biobehavioral Reviews
231. Neuroscience Bulletin
232. Neuroscience Letters
233. Neuroscience Research
234. Neuroscientist
235. Neurotherapeutics
236. Neurotoxicity Research
237. NeuroToxicology
238. Neurotoxicology and Teratology
239. Npj Parkinsons Disease
240. Npj Science of Learning
241. Nutritional Neuroscience
242. Pain
243. Pharmacology Biochemistry and Behavior
244. Progress in Neuro-Psychopharmacology & Biological Psychiatry
245. Progress in Neurobiology
246. Psychiatric Genetics
247. Psychiatry and Clinical Neurosciences
248. Psychoneuroendocrinology
249. Psychopharmacology
250. Psychophysiology
251. Purinergic Signalling
252. Restorative Neurology and Neuroscience
253. Reviews in the Neurosciences
254. Seizure-European Journal of Epilepsy
255. Sleep
256. Sleep and Biological Rhythms
257. Sleep Medicine Reviews
258. Social Cognitive and Affective Neuroscience
259. Social Neuroscience
260. Somatosensory and Motor Research
261. Stereotactic and Functional Neurosurgery
262. Stress-the International Journal on the Biology of Stress
263. Synapse-Structure Function Connectivity
264. Translational Neurodegeneration
265. Translational Neuroscience
266. Translational Stroke Research
267. Trends in Cognitive Sciences
268. Trends in Neurosciences
269. Vision Research
270. Visual Neuroscience
271. Zhurnal Vysshei Nervnoi Deyatelnosti Imeni i P Pavlova

<a id="scie-nuclear-science-technology"></a>

### Nuclear Science & Technology

期刊数：34

1. Annals of Nuclear Energy
2. Applied Radiation and Isotopes
3. Atomic Energy
4. Atw-International Journal for Nuclear Power
5. Fusion Engineering and Design
6. Fusion Science and Technology
7. Health Physics
8. IEEE Transactions on Nuclear Science
9. International Journal of Energy Research
10. International Journal of Radiation Biology
11. Journal of Fusion Energy
12. Journal of Nuclear Materials
13. Journal of Nuclear Science and Technology
14. Journal of Radioanalytical and Nuclear Chemistry
15. Journal of Radiological Protection
16. Kerntechnik
17. Nuclear Engineering and Design
18. Nuclear Engineering and Technology
19. Nuclear Engineering International
20. Nuclear Instruments & Methods in Physics Research Section A-Accelerators Spectrometers Detectors and Associated Equipment
21. Nuclear Instruments & Methods in Physics Research Section B-Beam Interactions with Materials and Atoms
22. Nuclear Materials and Energy
23. Nuclear Science and Engineering
24. Nuclear Science and Techniques
25. Nuclear Technology
26. Nuclear Technology & Radiation Protection
27. Progress in Nuclear Energy
28. Radiation Effects and Defects in Solids
29. Radiation Measurements
30. Radiation Physics and Chemistry
31. Radiation Protection Dosimetry
32. Radiochimica Acta
33. Radioprotection
34. Science and Technology of Nuclear Installations

<a id="scie-nursing"></a>

### Nursing

期刊数：125

1. Acta Paulista de Enfermagem
2. Advances in Neonatal Care
3. Advances in Nursing Science
4. Advances in Skin & Wound Care
5. American Journal of Critical Care
6. American Journal of Nursing
7. AORN Journal
8. Applied Nursing Research
9. Archives of Psychiatric Nursing
10. Asia-Pacific Journal of Oncology Nursing
11. Asian Nursing Research
12. Assistenza Infermieristica e Ricerca
13. Australasian Emergency Care
14. Australian Critical Care
15. Australian Journal of Advanced Nursing
16. Australian Journal of Rural Health
17. Bariatric Surgical Practice and Patient Care
18. Biological Research for Nursing
19. Birth-Issues in Perinatal Care
20. BMC Nursing
21. Cancer Nursing
22. CIN-Computers Informatics Nursing
23. Clinical Journal of Oncology Nursing
24. Clinical Nurse Specialist
25. Clinical Nursing Research
26. Clinical Simulation in Nursing
27. Collegian
28. Contemporary Nurse
29. Critical Care Nurse
30. Critical Care Nursing Clinics of North America
31. European Journal of Cancer Care
32. European Journal of Cardiovascular Nursing
33. European Journal of Oncology Nursing
34. Gastroenterology Nursing
35. Geriatric Nursing
36. Heart & Lung
37. Holistic Nursing Practice
38. Intensive and Critical Care Nursing
39. International Emergency Nursing
40. International Journal of Mental Health Nursing
41. International Journal of Nursing Knowledge
42. International Journal of Nursing Practice
43. International Journal of Nursing Studies
44. International Journal of Older People Nursing
45. International Nursing Review
46. Issues in Mental Health Nursing
47. JANAC-Journal of the Association of Nurses in AIDS Care
48. Japan Journal of Nursing Science
49. Jnp- the Journal for Nurse Practitioners
50. Jognn-Journal of Obstetric Gynecologic and Neonatal Nursing
51. Journal for Specialists in Pediatric Nursing
52. Journal of Addictions Nursing
53. Journal of Advanced Nursing
54. Journal of Cardiovascular Nursing
55. Journal of Child Health Care
56. Journal of Clinical Nursing
57. Journal of Community Health Nursing
58. Journal of Continuing Education in Nursing
59. Journal of Emergency Nursing
60. Journal of Family Nursing
61. Journal of Forensic Nursing
62. Journal of Gerontological Nursing
63. Journal of Hospice & Palliative Nursing
64. Journal of Human Lactation
65. Journal of Korean Academy of Nursing
66. Journal of Midwifery & Womens Health
67. Journal of Neuroscience Nursing
68. Journal of Nursing Administration
69. Journal of Nursing Care Quality
70. Journal of Nursing Education
71. Journal of Nursing Management
72. Journal of Nursing Regulation
73. Journal of Nursing Research
74. Journal of Nursing Scholarship
75. Journal of Pediatric Health Care
76. Journal of Pediatric Hematology-Oncology Nursing
77. Journal of Pediatric Nursing-Nursing Care of Children & Families
78. Journal of PeriAnesthesia Nursing
79. Journal of Perinatal & Neonatal Nursing
80. Journal of Professional Nursing
81. Journal of Psychiatric and Mental Health Nursing
82. Journal of Psychosocial Nursing and Mental Health Services
83. Journal of Renal Care
84. Journal of School Nursing
85. Journal of the American Association of Nurse Practitioners
86. Journal of the American Psychiatric Nurses Association
87. Journal of Tissue Viability
88. Journal of Transcultural Nursing
89. Journal of Trauma Nursing
90. Journal of Wound Ostomy and Continence Nursing
91. MCN-the American Journal of Maternal-Child Nursing
92. Midwifery
93. Nephrology Nursing Journal
94. Nurse Education in Practice
95. Nurse Education Today
96. Nurse Educator
97. Nursing & Health Sciences
98. Nursing Clinics of North America
99. Nursing Economics
100. Nursing Ethics
101. Nursing in Critical Care
102. Nursing Inquiry
103. Nursing Open
104. Nursing Outlook
105. Nursing Philosophy
106. Nursing Research
107. Nursing Science Quarterly
108. Oncology Nursing Forum
109. Orthopaedic Nursing
110. Pain Management Nursing
111. Perspectives in Psychiatric Care
112. Pflege
113. Public Health Nursing
114. Rehabilitation Nursing
115. Research and Theory for Nursing Practice
116. Research in Gerontological Nursing
117. Research in Nursing & Health
118. Revista da Escola de Enfermagem da USP
119. Revista Latino-Americana de Enfermagem
120. Seminars in Oncology Nursing
121. Western Journal of Nursing Research
122. Women and Birth
123. Workplace Health & Safety
124. Worldviews on Evidence-Based Nursing
125. Wound Management & Prevention

<a id="scie-nutrition-dietetics"></a>

### Nutrition & Dietetics

期刊数：87

1. Acta Alimentaria
2. Advances in Nutrition
3. American Journal of Clinical Nutrition
4. Annals of Nutrition and Metabolism
5. Annual Review of Nutrition
6. Appetite
7. Applied Physiology Nutrition and Metabolism
8. Archivos Latinoamericanos de Nutricion
9. Asia Pacific Journal of Clinical Nutrition
10. Beneficial Microbes
11. Bioscience of Microbiota Food and Health
12. British Journal of Nutrition
13. Canadian Journal of Dietetic Practice and Research
14. Clinical Nutrition
15. Correspondances en Metabolismes Hormones Diabetes et Nutrition
16. Critical Reviews in Food Science and Nutrition
17. Current Nutrition Reports
18. Current Obesity Reports
19. Current Opinion in Clinical Nutrition and Metabolic Care
20. Ecology of Food and Nutrition
21. Endocrinologia Diabetes y Nutricion
22. Ernahrungs Umschau
23. European Journal of Clinical Nutrition
24. European Journal of Lipid Science and Technology
25. European Journal of Nutrition
26. Food & Nutrition Research
27. Food and Drug Law Journal
28. Food and Nutrition Bulletin
29. Food Chemistry
30. Food Policy
31. Food Reviews International
32. Food Science and Human Wellness
33. Frontiers in Nutrition
34. Genes and Nutrition
35. HepatoBiliary Surgery and Nutrition
36. International Journal for Vitamin and Nutrition Research
37. International Journal of Behavioral Nutrition and Physical Activity
38. International Journal of Eating Disorders
39. International Journal of Food Sciences and Nutrition
40. International Journal of Obesity
41. International Journal of Sport Nutrition and Exercise Metabolism
42. Journal of Clinical Biochemistry and Nutrition
43. Journal of Eating Disorders
44. Journal of Functional Foods
45. Journal of Human Nutrition and Dietetics
46. Journal of Medicinal Food
47. Journal of Nutrition
48. Journal of Nutrition Education and Behavior
49. Journal of Nutrition Health & Aging
50. Journal of Nutritional Biochemistry
51. Journal of Nutritional Science and Vitaminology
52. Journal of Parenteral and Enteral Nutrition
53. Journal of Pediatric Gastroenterology and Nutrition
54. Journal of Renal Nutrition
55. Journal of the Academy of Nutrition and Dietetics
56. Journal of the American Nutrition Association
57. Journal of the International Society of Sports Nutrition
58. Lifestyle Genomics
59. Lipids
60. Lipids in Health and Disease
61. Maternal and Child Nutrition
62. Nutricion Hospitalaria
63. Nutrients
64. Nutrition
65. Nutrition & Diabetes
66. Nutrition & Dietetics
67. Nutrition & Metabolism
68. Nutrition and Cancer-an International Journal
69. Nutrition Bulletin
70. Nutrition Clinique et Metabolisme
71. Nutrition in Clinical Practice
72. Nutrition Journal
73. Nutrition Metabolism and Cardiovascular Diseases
74. Nutrition Research
75. Nutrition Research and Practice
76. Nutrition Research Reviews
77. Nutrition Reviews
78. Nutritional Neuroscience
79. Obesity
80. Obesity Facts
81. Obesity Research & Clinical Practice
82. Plant Foods for Human Nutrition
83. Proceedings of the Nutrition Society
84. Progress in Lipid Research
85. Public Health Nutrition
86. Revista de Nutricao-Brazilian Journal of Nutrition
87. Topics in Clinical Nutrition

<a id="scie-obstetrics-gynecology"></a>

### Obstetrics & Gynecology

期刊数：84

1. Acta Obstetricia et Gynecologica Scandinavica
2. American Journal of Obstetrics & Gynecology MFM
3. American Journal of Obstetrics and Gynecology
4. American Journal of Perinatology
5. Archives of Gynecology and Obstetrics
6. Australian & New Zealand Journal of Obstetrics & Gynaecology
7. Best Practice & Research Clinical Obstetrics & Gynaecology
8. Birth-Issues in Perinatal Care
9. BJOG-an International Journal of Obstetrics and Gynaecology
10. BMC Pregnancy and Childbirth
11. BMC Womens Health
12. BMJ Sexual & Reproductive Health
13. Breast
14. Breast Cancer
15. Breast Care
16. Breast Journal
17. Breastfeeding Medicine
18. Climacteric
19. Clinical and Experimental Obstetrics & Gynecology
20. Clinical Obstetrics and Gynecology
21. Clinics in Perinatology
22. Contraception
23. Current Opinion in Obstetrics & Gynecology
24. Early Human Development
25. European Journal of Contraception and Reproductive Health Care
26. European Journal of Obstetrics & Gynecology and Reproductive Biology
27. Fertility and Sterility
28. Fetal Diagnosis and Therapy
29. Geburtshilfe und Frauenheilkunde
30. Ginekologia Polska
31. Gynecologic and Obstetric Investigation
32. Gynecologic Oncology
33. Gynecological Endocrinology
34. Gynecologie Obstetrique Fertilite & Senologie
35. Human Fertility
36. Human Reproduction
37. Human Reproduction Open
38. Human Reproduction Update
39. Hypertension in Pregnancy
40. International Breastfeeding Journal
41. International Journal of Gynecological Cancer
42. International Journal of Gynecological Pathology
43. International Journal of Gynecology & Obstetrics
44. International Journal of Obstetric Anesthesia
45. International Journal of Womens Health
46. International Urogynecology Journal
47. Jognn-Journal of Obstetric Gynecologic and Neonatal Nursing
48. Journal of Assisted Reproduction and Genetics
49. Journal of Gynecologic Oncology
50. Journal of Gynecology Obstetrics and Human Reproduction
51. Journal of Human Lactation
52. Journal of Lower Genital Tract Disease
53. Journal of Maternal-Fetal & Neonatal Medicine
54. Journal of Minimally Invasive Gynecology
55. Journal of Obstetrics and Gynaecology
56. Journal of Obstetrics and Gynaecology Research
57. Journal of Pediatric and Adolescent Gynecology
58. Journal of Perinatal & Neonatal Nursing
59. Journal of Perinatal Medicine
60. Journal of Perinatology
61. Journal of Psychosomatic Obstetrics & Gynecology
62. Journal of Reproductive Immunology
63. Journal of Womens Health
64. Maturitas
65. Menopause-the Journal of the Menopause Society
66. Molecular Human Reproduction
67. Obstetrical & Gynecological Survey
68. Obstetrics and Gynecology
69. Obstetrics and Gynecology Clinics of North America
70. Paediatric and Perinatal Epidemiology
71. Placenta
72. Pregnancy Hypertension-an International Journal of Womens Cardiovascular Health
73. Prenatal Diagnosis
74. Reproductive BioMedicine Online
75. Reproductive Medicine and Biology
76. Reproductive Sciences
77. Seminars in Perinatology
78. Seminars in Reproductive Medicine
79. Taiwanese Journal of Obstetrics & Gynecology
80. Twin Research and Human Genetics
81. Ultrasound in Obstetrics & Gynecology
82. Urogynecology
83. Women and Birth
84. Zeitschrift für Geburtshilfe und Neonatologie

<a id="scie-oceanography"></a>

### Oceanography

期刊数：63

1. Acta Adriatica
2. Acta Oceanologica Sinica
3. Annual Review of Marine Science
4. Applied Ocean Research
5. Atmosphere-Ocean
6. Bulletin of Marine Science
7. Continental Shelf Research
8. Deep-Sea Research Part I-Oceanographic Research Papers
9. Deep-Sea Research Part II-Topical Studies in Oceanography
10. Dynamics of Atmospheres and Oceans
11. Environmental Fluid Mechanics
12. Estuarine Coastal and Shelf Science
13. Fisheries Oceanography
14. Frontiers in Marine Science
15. Geo-Marine Letters
16. ICES Journal of Marine Science
17. IEEE Journal of Oceanic Engineering
18. Indian Journal of Geo-Marine Sciences
19. Izvestiya Atmospheric and Oceanic Physics
20. Journal of Geophysical Research-Oceans
21. Journal of Marine Science and Engineering
22. Journal of Marine Systems
23. Journal of Navigation
24. Journal of Ocean University of China
25. Journal of Oceanography
26. Journal of Oceanology and Limnology
27. Journal of Operational Oceanography
28. Journal of Physical Oceanography
29. Journal of Plankton Research
30. Journal of Sea Research
31. Journal of Southern Hemisphere Earth Systems Science
32. Limnology and Oceanography
33. Limnology and Oceanography Letters
34. Limnology and Oceanography-Methods
35. Marine and Freshwater Research
36. Marine Chemistry
37. Marine Ecology Progress Series
38. Marine Geodesy
39. Marine Geology
40. Marine Geophysical Research
41. Marine Georesources & Geotechnology
42. Marine Technology Society Journal
43. Naval Engineers Journal
44. New Zealand Journal of Marine and Freshwater Research
45. Ocean & Coastal Management
46. Ocean and Coastal Research
47. Ocean Dynamics
48. Ocean Engineering
49. Ocean Modelling
50. Ocean Science
51. Ocean Science Journal
52. Oceanography
53. Oceanologia
54. Oceanological and Hydrobiological Studies
55. Oceanology
56. Paleoceanography and Paleoclimatology
57. Plankton & Benthos Research
58. Polar Research
59. Progress in Oceanography
60. Revista de Biologia Marina y Oceanografia
61. Tellus Series A-Dynamic Meteorology and Oceanography
62. Terrestrial Atmospheric and Oceanic Sciences
63. Thalassas

<a id="scie-oncology"></a>

### Oncology

期刊数：240

1. Acta Oncologica
2. American Journal of Cancer Research
3. American Journal of Clinical Oncology-Cancer Clinical Trials
4. American Journal of Translational Research
5. Analytical Cellular Pathology
6. Annals of Oncology
7. Annals of Surgical Oncology
8. Annual Review of Cancer Biology
9. Anti-Cancer Agents in Medicinal Chemistry
10. Anti-Cancer Drugs
11. Anticancer Research
12. Asia-Pacific Journal of Clinical Oncology
13. Biochimica et Biophysica Acta-Reviews on Cancer
14. BioDrugs
15. Biomarker Research
16. Bladder Cancer
17. Blood Cancer Journal
18. BMC Cancer
19. Bone Marrow Transplantation
20. Brachytherapy
21. Brain Tumor Pathology
22. Breast
23. Breast Cancer
24. Breast Cancer Research
25. Breast Cancer Research and Treatment
26. Breast Cancer-Targets and Therapy
27. Breast Care
28. Breast Journal
29. British Journal of Cancer
30. Bulletin du Cancer
31. CA-A Cancer Journal for Clinicians
32. Cancer
33. Cancer & Metabolism
34. Cancer and Metastasis Reviews
35. Cancer Biology & Medicine
36. Cancer Biology & Therapy
37. Cancer Biomarkers
38. Cancer Biotherapy and Radiopharmaceuticals
39. Cancer Causes & Control
40. Cancer Cell
41. Cancer Cell International
42. Cancer Chemotherapy and Pharmacology
43. Cancer Communications
44. Cancer Control
45. Cancer Cytopathology
46. Cancer Discovery
47. Cancer Epidemiology
48. Cancer Epidemiology Biomarkers & Prevention
49. Cancer Gene Therapy
50. Cancer Genetics
51. Cancer Genomics & Proteomics
52. Cancer Imaging
53. Cancer Immunology Immunotherapy
54. Cancer Immunology Research
55. Cancer Investigation
56. Cancer Journal
57. Cancer Letters
58. Cancer Management and Research
59. Cancer Medicine
60. Cancer Nanotechnology
61. Cancer Nursing
62. Cancer Prevention Research
63. Cancer Radiotherapie
64. Cancer Research
65. Cancer Research and Treatment
66. Cancer Science
67. Cancer Treatment Reviews
68. Cancers
69. Carcinogenesis
70. Cellular Oncology
71. Chemotherapy
72. Chinese Journal of Cancer Research
73. Clinical & Experimental Metastasis
74. Clinical & Translational Oncology
75. Clinical and Translational Medicine
76. Clinical and Translational Radiation Oncology
77. Clinical Breast Cancer
78. Clinical Cancer Research
79. Clinical Colorectal Cancer
80. Clinical Epigenetics
81. Clinical Genitourinary Cancer
82. Clinical Journal of Oncology Nursing
83. Clinical Lung Cancer
84. Clinical Lymphoma Myeloma & Leukemia
85. Clinical Medicine Insights-Oncology
86. Clinical Oncology
87. Critical Reviews in Oncology Hematology
88. Current Cancer Drug Targets
89. Current Hematologic Malignancy Reports
90. Current Oncology
91. Current Oncology Reports
92. Current Opinion in Oncology
93. Current Problems in Cancer
94. Current Treatment Options in Oncology
95. Discover Oncology
96. Ejso
97. Endocrine-Related Cancer
98. ESMO Open
99. European Journal of Cancer
100. European Journal of Cancer Care
101. European Journal of Cancer Prevention
102. European Journal of Oncology Nursing
103. European Urology Oncology
104. Experimental Cell Research
105. Experimental Hematology & Oncology
106. Expert Review of Anticancer Therapy
107. Familial Cancer
108. Folia Biologica
109. Frontiers in Oncology
110. Future Oncology
111. Gastric Cancer
112. Genes Chromosomes & Cancer
113. Gynecologic Oncology
114. Hematological Oncology
115. Hematology-Oncology Clinics of North America
116. Hereditary Cancer in Clinical Practice
117. Indian Journal of Cancer
118. Infectious Agents and Cancer
119. Integrative Cancer Therapies
120. International Journal of Biological Markers
121. International Journal of Cancer
122. International Journal of Clinical Oncology
123. International Journal of Gynecological Cancer
124. International Journal of Hyperthermia
125. International Journal of Oncology
126. International Journal of Radiation Oncology Biology Physics
127. Investigational New Drugs
128. JACC: CardioOncology
129. JAMA Oncology
130. Japanese Journal of Clinical Oncology
131. JCO Oncology Practice
132. JCO Precision Oncology
133. JNCI-Journal of the National Cancer Institute
134. Journal for ImmunoTherapy of Cancer
135. Journal of Adolescent and Young Adult Oncology
136. Journal of Bone Oncology
137. Journal of Breast Cancer
138. Journal of Cancer
139. Journal of Cancer Education
140. Journal of Cancer Research and Clinical Oncology
141. Journal of Cancer Research and Therapeutics
142. Journal of Cancer Survivorship
143. Journal of Chemotherapy
144. Journal of Clinical Oncology
145. Journal of Contemporary Brachytherapy
146. Journal of Environmental Science and Health Part C-Toxicology and Carcinogenesis
147. Journal of Experimental & Clinical Cancer Research
148. Journal of Gastric Cancer
149. Journal of Gastrointestinal Oncology
150. Journal of Geriatric Oncology
151. Journal of Gynecologic Oncology
152. Journal of Hematology & Oncology
153. Journal of Hepatocellular Carcinoma
154. Journal of Immunotherapy
155. Journal of Mammary Gland Biology and Neoplasia
156. Journal of Neuro-Oncology
157. Journal of Oncology Pharmacy Practice
158. Journal of Pathology
159. Journal of Pediatric Hematology Oncology
160. Journal of Pediatric Hematology-Oncology Nursing
161. Journal of Radiation Research
162. Journal of Surgical Oncology
163. Journal of the National Comprehensive Cancer Network
164. Journal of Thoracic Oncology
165. Lancet Oncology
166. Leukemia
167. Leukemia & Lymphoma
168. Leukemia Research
169. Liver Cancer
170. Lung Cancer
171. Medical Dosimetry
172. Medical Oncology
173. MedScience
174. Melanoma Research
175. Molecular Cancer
176. Molecular Cancer Research
177. Molecular Cancer Therapeutics
178. Molecular Carcinogenesis
179. Molecular Medicine Reports
180. Molecular Oncology
181. Molecular Therapy Oncology
182. Nature Cancer
183. Nature Reviews Cancer
184. Nature Reviews Clinical Oncology
185. Neoplasia
186. Neoplasma
187. Neuro-Oncology
188. Npj Breast Cancer
189. Npj Precision Oncology
190. Nutrition and Cancer-an International Journal
191. Oncogene
192. Oncogenesis
193. OncoImmunology
194. Oncologie
195. Oncologist
196. Oncology
197. Oncology Letters
198. Oncology Nursing Forum
199. Oncology Reports
200. Oncology Research
201. Oncology Research and Treatment
202. Oncology-New York
203. OncoTargets and Therapy
204. Onkologie
205. Oral Oncology
206. Pathology & Oncology Research
207. Pediatric Blood & Cancer
208. Pediatric Hematology and Oncology
209. Photodiagnosis and Photodynamic Therapy
210. Pigment Cell & Melanoma Research
211. Practical Radiation Oncology
212. Prostate Cancer and Prostatic Diseases
213. Psycho-Oncologie
214. Psycho-Oncology
215. Radiation Oncology
216. Radiology and Oncology
217. Radiotherapy and Oncology
218. Recent Patents on Anti-Cancer Drug Discovery
219. Seminars in Cancer Biology
220. Seminars in Oncology
221. Seminars in Oncology Nursing
222. Seminars in Radiation Oncology
223. STEM Cells
224. Strahlentherapie und Onkologie
225. Supportive Care in Cancer
226. Surgical Oncology Clinics of North America
227. Surgical Oncology-Oxford
228. Targeted Oncology
229. Technology in Cancer Research & Treatment
230. Therapeutic Advances in Medical Oncology
231. Thoracic Cancer
232. Translational Cancer Research
233. Translational Lung Cancer Research
234. Translational Oncology
235. Trends in Cancer
236. Tumori Journal
237. Uhod-Uluslararasi Hematoloji-Onkoloji Dergisi
238. Urologic Oncology-Seminars and Original Investigations
239. World Journal of Gastrointestinal Oncology
240. World Journal of Surgical Oncology

<a id="scie-operations-research-management-science"></a>

### Operations Research & Management Science

期刊数：86

1. 4OR-a Quarterly Journal of Operations Research
2. Annals of Operations Research
3. Applied Stochastic Models in Business and Industry
4. Asia-Pacific Journal of Operational Research
5. Central European Journal of Operations Research
6. Computational Optimization and Applications
7. Computers & Operations Research
8. Decision Support Systems
9. Discrete Event Dynamic Systems-Theory and Applications
10. Discrete Optimization
11. Engineering Economist
12. Engineering Optimization
13. European Journal of Industrial Engineering
14. European Journal of Operational Research
15. Expert Systems with Applications
16. Flexible Services and Manufacturing Journal
17. Fuzzy Optimization and Decision Making
18. IEEE Systems Journal
19. IISE Transactions
20. IMA Journal of Management Mathematics
21. INFOR
22. INFORMS Journal on Applied Analytics
23. INFORMS Journal on Computing
24. International Journal of Computer Integrated Manufacturing
25. International Journal of Industrial Engineering Computations
26. International Journal of Information Technology & Decision Making
27. International Journal of Production Economics
28. International Journal of Production Research
29. International Journal of Systems Science
30. International Journal of Systems Science-Operations & Logistics
31. International Journal of Technology Management
32. International Transactions in Operational Research
33. Journal of Global Optimization
34. Journal of Industrial and Management Optimization
35. Journal of Manufacturing Systems
36. Journal of Operations Management
37. Journal of Optimization Theory and Applications
38. Journal of Quality Technology
39. Journal of Scheduling
40. Journal of Simulation
41. Journal of Systems Engineering and Electronics
42. Journal of Systems Science and Systems Engineering
43. Journal of the Operational Research Society
44. M&Som-Manufacturing & Service Operations Management
45. Management Science
46. Mathematical Methods of Operations Research
47. Mathematical Programming
48. Mathematical Programming Computation
49. Mathematics of Operations Research
50. Memetic Computing
51. Military Operations Research
52. Naval Research Logistics
53. Networks
54. Networks & Spatial Economics
55. Omega-International Journal of Management Science
56. Operational Research
57. Operations Research
58. Operations Research Letters
59. Operations Research Perspectives
60. Optimal Control Applications & Methods
61. Optimization
62. Optimization and Engineering
63. Optimization Letters
64. Optimization Methods & Software
65. OR Spectrum
66. Pacific Journal of Optimization
67. Probability in the Engineering and Informational Sciences
68. Proceedings of the Institution of Mechanical Engineers Part O-Journal of Risk and Reliability
69. Production and Operations Management
70. Production Planning & Control
71. Quality and Reliability Engineering International
72. Quality Technology and Quantitative Management
73. Queueing Systems
74. RAIRO-Operations Research
75. Reliability Engineering & System Safety
76. Safety Science
77. Socio-Economic Planning Sciences
78. Sort-Statistics and Operations Research Transactions
79. Studies in Informatics and Control
80. Systems & Control Letters
81. Systems Engineering
82. Technovation
83. Top
84. Transportation Research Part B-Methodological
85. Transportation Research Part E-Logistics and Transportation Review
86. Transportation Science

<a id="scie-ophthalmology"></a>

### Ophthalmology

期刊数：62

1. Acta Ophthalmologica
2. American Journal of Ophthalmology
3. Annual Review of Vision Science
4. Arquivos Brasileiros de Oftalmologia
5. Asia-Pacific Journal of Ophthalmology
6. BMC Ophthalmology
7. British Journal of Ophthalmology
8. Canadian Journal of Ophthalmology-Journal Canadien d Ophtalmologie
9. Clinical and Experimental Ophthalmology
10. Clinical and Experimental Optometry
11. Contact Lens & Anterior Eye
12. Cornea
13. Current Eye Research
14. Current Opinion in Ophthalmology
15. Cutaneous and Ocular Toxicology
16. Documenta Ophthalmologica
17. European Journal of Ophthalmology
18. Experimental Eye Research
19. Eye
20. Eye & Contact Lens-Science and Clinical Practice
21. Eye and Vision
22. Graefes Archive for Clinical and Experimental Ophthalmology
23. Indian Journal of Ophthalmology
24. International Journal of Ophthalmology
25. International Ophthalmology
26. Investigative Ophthalmology & Visual Science
27. JAMA Ophthalmology
28. Japanese Journal of Ophthalmology
29. Journal Francais d Ophtalmologie
30. Journal of Aapos
31. Journal of Cataract and Refractive Surgery
32. Journal of Eye Movement Research
33. Journal of Glaucoma
34. Journal of Neuro-Ophthalmology
35. Journal of Ocular Pharmacology and Therapeutics
36. Journal of Ophthalmology
37. Journal of Pediatric Ophthalmology & Strabismus
38. Journal of Refractive Surgery
39. Journal of Vision
40. Klinische Monatsblatter für Augenheilkunde
41. Molecular Vision
42. Ocular Immunology and Inflammation
43. Ocular Surface
44. Ophthalmic and Physiological Optics
45. Ophthalmic Epidemiology
46. Ophthalmic Genetics
47. Ophthalmic Plastic and Reconstructive Surgery
48. Ophthalmic Research
49. Ophthalmic Surgery Lasers & Imaging Retina
50. Ophthalmologica
51. Ophthalmologie
52. Ophthalmology
53. Ophthalmology and Therapy
54. Optometry and Vision Science
55. Perception
56. Progress in Retinal and Eye Research
57. Retina-the Journal of Retinal and Vitreous Diseases
58. Seminars in Ophthalmology
59. Survey of Ophthalmology
60. Translational Vision Science & Technology
61. Vision Research
62. Visual Neuroscience

<a id="scie-optics"></a>

### Optics

期刊数：100

1. ACS Photonics
2. Advanced Optical Materials
3. Advanced Photonics
4. Advanced Quantum Technologies
5. Advances in Optics and Photonics
6. APL Photonics
7. Applied Optics
8. Applied Physics B-Lasers and Optics
9. Biomedical Optics Express
10. Chinese Optics Letters
11. Color Research and Application
12. Current Optics and Photonics
13. Displays
14. eLight
15. EPJ Quantum Technology
16. European Physical Journal D
17. Fiber and Integrated Optics
18. High Power Laser Science and Engineering
19. IEEE Journal of Quantum Electronics
20. IEEE Journal of Selected Topics in Quantum Electronics
21. IEEE Photonics Journal
22. IEEE Photonics Technology Letters
23. IEEE Transactions on Terahertz Science and Technology
24. IET Optoelectronics
25. Image and Vision Computing
26. Infrared Physics & Technology
27. International Journal of Imaging Systems and Technology
28. International Journal of Optics
29. International Journal of Optomechatronics
30. International Journal of Photoenergy
31. Journal of Astronomical Telescopes Instruments and Systems
32. Journal of Biomedical Optics
33. Journal of Biophotonics
34. Journal of Electronic Imaging
35. Journal of Infrared and Millimeter Waves
36. Journal of Infrared Millimeter and Terahertz Waves
37. Journal of Innovative Optical Health Sciences
38. Journal of Laser Applications
39. Journal of Laser Micro Nanoengineering
40. Journal of Lightwave Technology
41. Journal of Luminescence
42. Journal of Micro-Nanopatterning Materials and Metrology-Jm3
43. Journal of Modern Optics
44. Journal of Nanophotonics
45. Journal of Nonlinear Optical Physics & Materials
46. Journal of Optical Communications and Networking
47. Journal of Optical Technology
48. Journal of Optics
49. Journal of Optoelectronics and Advanced Materials
50. Journal of Photonics for Energy
51. Journal of Physics B-Atomic Molecular and Optical Physics
52. Journal of Quantitative Spectroscopy & Radiative Transfer
53. Journal of Russian Laser Research
54. Journal of Synchrotron Radiation
55. Journal of the European Optical Society-Rapid Publications
56. Journal of the Optical Society of America A-Optics Image Science and Vision
57. Journal of the Optical Society of America B-Optical Physics
58. Journal of the Society for Information Display
59. Journal of X-Ray Science and Technology
60. Laser & Photonics Reviews
61. Laser Focus World
62. Laser Physics
63. Laser Physics Letters
64. Lasers in Engineering
65. Leukos
66. Light & Engineering
67. Light-Science & Applications
68. Lighting Research & Technology
69. Microelectronic Engineering
70. Microwave and Optical Technology Letters
71. Nanophotonics
72. Nature Photonics
73. Neurophotonics
74. Optica
75. Optica Applicata
76. Optical and Quantum Electronics
77. Optical Engineering
78. Optical Fiber Technology
79. Optical Materials
80. Optical Materials Express
81. Optical Review
82. Optical Switching and Networking
83. Optics and Laser Technology
84. Optics and Lasers in Engineering
85. Optics and Spectroscopy
86. Optics Communications
87. Optics Express
88. Optics Letters
89. Opto-Electronic Advances
90. Opto-Electronics Review
91. Optoelectronics and Advanced Materials-Rapid Communications
92. Photonic Network Communications
93. Photonic Sensors
94. Photonics
95. Photonics and Nanostructures-Fundamentals and Applications
96. Photonics Research
97. PhotoniX
98. Physical Review A
99. Progress in Quantum Electronics
100. Ukrainian Journal of Physical Optics

<a id="scie-ornithology"></a>

### Ornithology

期刊数：27

1. Acta Ornithologica
2. Ardea
3. Ardeola-International Journal of Ornithology
4. Avian Biology Research
5. Avian Conservation and Ecology
6. Avian Research
7. Bird Conservation International
8. Bird Study
9. Emu-Austral Ornithology
10. Ibis
11. Journal of Avian Biology
12. Journal of Field Ornithology
13. Journal of Ornithology
14. Journal of Raptor Research
15. Malimbus
16. Marine Ornithology
17. Notornis
18. Ornis Fennica
19. Ornithological Applications
20. Ornithological Science
21. Ornithology
22. Ornithology Research
23. Ornitologia Neotropical
24. Ostrich
25. Waterbirds
26. Wildfowl
27. Wilson Journal of Ornithology

<a id="scie-orthopedics"></a>

### Orthopedics

期刊数：86

1. Acta Chirurgiae Orthopaedicae et Traumatologiae Cechoslovaca
2. Acta Orthopaedica
3. Acta Orthopaedica Belgica
4. Acta Orthopaedica et Traumatologica Turcica
5. Acta Ortopedica Brasileira
6. American Journal of Sports Medicine
7. Archives of Orthopaedic and Trauma Surgery
8. Archives of Osteoporosis
9. Arthroscopy-the Journal of Arthroscopic and Related Surgery
10. BMC Musculoskeletal Disorders
11. Bone & Joint Journal
12. Bone & Joint Research
13. Brazilian Journal of Physical Therapy
14. Cartilage
15. Clinical Biomechanics
16. Clinical Journal of Sport Medicine
17. Clinical Orthopaedics and Related Research
18. Clinical Spine Surgery
19. Clinics in Orthopedic Surgery
20. Clinics in Podiatric Medicine and Surgery
21. Connective Tissue Research
22. Current Reviews in Musculoskeletal Medicine
23. EFORT Open Reviews
24. European Cells & Materials
25. European Spine Journal
26. Foot & Ankle International
27. Foot and Ankle Clinics
28. Foot and Ankle Surgery
29. Gait & Posture
30. Geriatric Orthopaedic Surgery & Rehabilitation
31. Global Spine Journal
32. Hand Clinics
33. Hand Surgery & Rehabilitation
34. Hip International
35. HSS Journal
36. Indian Journal of Orthopaedics
37. Injury-International Journal of the Care of the Injured
38. International Orthopaedics
39. Isokinetics and Exercise Science
40. Joint Diseases and Related Surgery
41. JOR Spine
42. Journal of Arthroplasty
43. Journal of Back and Musculoskeletal Rehabilitation
44. Journal of Bone and Joint Surgery-American Volume
45. Journal of Childrens Orthopaedics
46. Journal of Foot & Ankle Surgery
47. Journal of Foot and Ankle Research
48. Journal of Hand Surgery-American Volume
49. Journal of Hand Surgery-European Volume
50. Journal of Hand Therapy
51. Journal of Hip Preservation Surgery
52. Journal of Knee Surgery
53. Journal of Orthopaedic & Sports Physical Therapy
54. Journal of Orthopaedic Research
55. Journal of Orthopaedic Science
56. Journal of Orthopaedic Surgery
57. Journal of Orthopaedic Surgery and Research
58. Journal of Orthopaedic Translation
59. Journal of Orthopaedic Trauma
60. Journal of Orthopaedics and Traumatology
61. Journal of Pediatric Orthopaedics
62. Journal of Pediatric Orthopaedics-Part B
63. Journal of Physiotherapy
64. Journal of Plastic Surgery and Hand Surgery
65. Journal of Shoulder and Elbow Surgery
66. Journal of the American Academy of Orthopaedic Surgeons
67. Journal of the American Podiatric Medical Association
68. Knee
69. Knee Surgery Sports Traumatology Arthroscopy
70. Operative Orthopadie und Traumatologie
71. Orthopadie
72. Orthopaedic Journal of Sports Medicine
73. Orthopaedic Nursing
74. Orthopaedic Surgery
75. Orthopaedics & Traumatology-Surgery & Research
76. Orthopedic Clinics of North America
77. Orthopedics
78. Osteoarthritis and Cartilage
79. Physical Therapy
80. Physician and Sportsmedicine
81. Prosthetics and Orthotics International
82. Skeletal Radiology
83. Spine
84. Spine Journal
85. Sportverletzung-Sportschaden
86. Zeitschrift für Orthopadie und Unfallchirurgie

<a id="scie-otorhinolaryngology"></a>

### Otorhinolaryngology

期刊数：43

1. Acta Oto-Laryngologica
2. Acta Otorhinolaryngologica Italica
3. American Journal of Audiology
4. American Journal of Otolaryngology
5. American Journal of Rhinology & Allergy
6. Annals of Otology Rhinology and Laryngology
7. Audiology and Neurotology
8. Auris Nasus Larynx
9. B-Ent
10. Brazilian Journal of Otorhinolaryngology
11. Clinical and Experimental Otorhinolaryngology
12. Clinical Otolaryngology
13. Current Opinion in Otolaryngology & Head and Neck Surgery
14. Dysphagia
15. Ear and Hearing
16. Ent-Ear Nose & Throat Journal
17. European Annals of Otorhinolaryngology-Head and Neck Diseases
18. European Archives of Oto-Rhino-Laryngology
19. Folia Phoniatrica et Logopaedica
20. Head and Neck-Journal for the Sciences and Specialties of the Head and Neck
21. Hearing Research
22. Hno
23. International Forum of Allergy & Rhinology
24. International Journal of Audiology
25. International Journal of Pediatric Otorhinolaryngology
26. JAMA Otolaryngology-Head & Neck Surgery
27. Jaro-Journal of the Association for Research in Otolaryngology
28. Journal of International Advanced Otology
29. Journal of Laryngology and Otology
30. Journal of Otolaryngology-Head & Neck Surgery
31. Journal of the American Academy of Audiology
32. Journal of Vestibular Research-Equilibrium & Orientation
33. Journal of Voice
34. Laryngo-Rhino-Otologie
35. Laryngoscope
36. Laryngoscope Investigative Otolaryngology
37. Logopedics Phoniatrics Vocology
38. Orl-Journal for Oto-Rhino-Laryngology Head and Neck Surgery
39. Otolaryngologic Clinics of North America
40. Otolaryngology-Head and Neck Surgery
41. Otology & Neurotology
42. Rhinology
43. Trends in Hearing

<a id="scie-paleontology"></a>

### Paleontology

期刊数：54

1. Acta Palaeontologica Polonica
2. African Invertebrates
3. Alcheringa
4. Ameghiniana
5. Annales de Paleontologie
6. Annals of Carnegie Museum
7. Bollettino della Societa Paleontologica Italiana
8. Bulletin of Geosciences
9. Carnets Geol.
10. Comptes Rendus Palevol
11. Cretaceous Research
12. Earth and Environmental Science Transactions of the Royal Society of Edinburgh
13. Facies
14. Fossil Record
15. Geobios
16. Geodiversitas
17. Gff
18. Historical Biology
19. Ichnos-an International Journal for Plant and Animal Traces
20. International Journal of Paleopathology
21. Journal of Foraminiferal Research
22. Journal of Micropalaeontology
23. Journal of Palaeogeography-English
24. Journal of Paleontology
25. Journal of Systematic Palaeontology
26. Journal of the Palaeontological Society of India
27. Journal of Vertebrate Paleontology
28. Lethaia
29. Marine Micropaleontology
30. Micropaleontology
31. Neues Jahrbuch für Geologie und Palaontologie-Abhandlungen
32. Palaeobiodiversity and Palaeoenvironments
33. Palaeogeography Palaeoclimatology Palaeoecology
34. Palaeontographica Abteilung A-Palaozoologie-Stratigraphie
35. Palaeontographica Abteilung B-Palaeophytologie Palaeobotany-Palaeophytology
36. Palaeontologia Electronica
37. Palaeontology
38. Palaeoworld
39. Palaios
40. Paleobiology
41. Paleoceanography and Paleoclimatology
42. Paleontological Journal
43. Paleontological Research
44. Palynology
45. PalZ
46. Papers in Palaeontology
47. Proceedings of the Geologists Association
48. Review of Palaeobotany and Palynology
49. Revista Brasileira de Paleontologia
50. Rivista Italiana di Paleontologia e Stratigrafia
51. Stratigraphy
52. Stratigraphy and Geological Correlation
53. Swiss Journal of Palaeontology
54. Vegetation History and Archaeobotany

<a id="scie-parasitology"></a>

### Parasitology

期刊数：38

1. Acta Parasitologica
2. Acta Tropica
3. Cell Host & Microbe
4. Comparative Parasitology
5. Experimental Parasitology
6. Folia Parasitologica
7. Helminthologia
8. Infectious Diseases of Poverty
9. International Journal for Parasitology
10. International Journal for Parasitology-Drugs and Drug Resistance
11. International Journal for Parasitology-Parasites and Wildlife
12. Iranian Journal of Parasitology
13. Journal of Arthropod-Borne Diseases
14. Journal of Helminthology
15. Journal of Parasitology
16. Journal of Vector Borne Diseases
17. Malaria Journal
18. Memorias do Instituto Oswaldo Cruz
19. Molecular and Biochemical Parasitology
20. Parasite
21. Parasite Immunology
22. Parasites & Vectors
23. Parasites Hosts and Diseases
24. Parasitology
25. Parasitology International
26. Parasitology Research
27. Pathogens and Global Health
28. PLOS Neglected Tropical Diseases
29. PLOS Pathogens
30. Revista Brasileira de Parasitologia Veterinaria
31. Revista da Sociedade Brasileira de Medicina Tropical
32. Revista do Instituto de Medicina Tropical de Sao Paulo
33. Systematic Parasitology
34. Ticks and Tick-Borne Diseases
35. Trends in Parasitology
36. Tropical Biomedicine
37. Tropical Medicine and Infectious Disease
38. Veterinary Parasitology

<a id="scie-pathology"></a>

### Pathology

期刊数：75

1. Acta Cytologica
2. Acta Neuropathologica
3. Advances in Anatomic Pathology
4. Alzheimer Disease & Associated Disorders
5. American Journal of Clinical Pathology
6. American Journal of Forensic Medicine and Pathology
7. American Journal of Pathology
8. American Journal of Surgical Pathology
9. Analytical Cellular Pathology
10. Annales de Pathologie
11. Annals of Diagnostic Pathology
12. Annual Review of Pathology-Mechanisms of Disease
13. Apmis
14. Applied Immunohistochemistry & Molecular Morphology
15. Archives of Pathology & Laboratory Medicine
16. Brain Pathology
17. Brain Tumor Pathology
18. Cancer Cytopathology
19. Cardiovascular Pathology
20. Cellular Oncology
21. Clinical Neuropathology
22. CytoJournal
23. Cytometry Part B-Clinical Cytometry
24. Cytopathology
25. Diagnostic Cytopathology
26. Diagnostic Pathology
27. Disease Models & Mechanisms
28. Endocrine Pathology
29. Experimental and Molecular Pathology
30. Expert Review of Molecular Diagnostics
31. Fetal and Pediatric Pathology
32. Folia Neuropathologica
33. Forensic Science Medicine and Pathology
34. Histology and Histopathology
35. Histopathology
36. HLA
37. Human Pathology
38. Indian Journal of Pathology and Microbiology
39. International Journal of Gynecological Pathology
40. International Journal of Immunopathology and Pharmacology
41. International Journal of Paleopathology
42. International Journal of Surgical Pathology
43. Journal of Clinical Pathology
44. Journal of Comparative Pathology
45. Journal of Cutaneous Pathology
46. Journal of Hematopathology
47. Journal of Molecular Diagnostics
48. Journal of Neuropathology and Experimental Neurology
49. Journal of Oral Pathology & Medicine
50. Journal of Pathology
51. Journal of Pathology Clinical Research
52. Journal of Toxicologic Pathology
53. Laboratory Investigation
54. Leprosy Review
55. Malaysian Journal of Pathology
56. Medecine Nucleaire-Imagerie Fonctionnelle et Metabolique
57. Medical Molecular Morphology
58. Modern Pathology
59. Neuropathology
60. Neuropathology and Applied Neurobiology
61. Pathobiology
62. Pathologie
63. Pathology
64. Pathology & Oncology Research
65. Pathology International
66. Pathology Research and Practice
67. Pediatric and Developmental Pathology
68. Polish Journal of Pathology
69. Science & Justice
70. Seminars in Diagnostic Pathology
71. Seminars in Immunopathology
72. Toxicologic Pathology
73. Ultrastructural Pathology
74. Veterinary Pathology
75. Virchows Archiv

<a id="scie-pediatrics"></a>

### Pediatrics

期刊数：129

1. Academic Pediatrics
2. Acta Paediatrica
3. American Journal of Perinatology
4. Anales de Pediatria
5. Archives de Pediatrie
6. Archives of Disease in Childhood
7. Archives of Disease in Childhood-Education and Practice Edition
8. Archives of Disease in Childhood-Fetal and Neonatal Edition
9. Archivos Argentinos de Pediatria
10. Birth-Issues in Perinatal Care
11. BMC Pediatrics
12. BMJ Paediatrics Open
13. Brain & Development
14. Breastfeeding Medicine
15. Cardiology in the Young
16. Child and Adolescent Mental Health
17. Child and Adolescent Psychiatry and Mental Health
18. Child Care Health and Development
19. Childhood Obesity
20. Children-Basel
21. Childs Nervous System
22. Clinical Pediatrics
23. Clinics in Perinatology
24. Congenital Anomalies
25. Current Opinion in Pediatrics
26. Current Problems in Pediatric and Adolescent Health Care
27. Developmental Medicine and Child Neurology
28. Developmental Neurorehabilitation
29. Early Human Development
30. European Child & Adolescent Psychiatry
31. European Journal of Paediatric Dentistry
32. European Journal of Paediatric Neurology
33. European Journal of Pediatric Surgery
34. European Journal of Pediatrics
35. Fetal and Pediatric Pathology
36. Frontiers in Pediatrics
37. Hong Kong Journal of Paediatrics
38. Hormone Research in Paediatrics
39. Indian Journal of Pediatrics
40. Indian Pediatrics
41. Innovative Journal of Pediatrics
42. International Breastfeeding Journal
43. International Journal of Paediatric Dentistry
44. International Journal of Pediatric Otorhinolaryngology
45. Italian Journal of Pediatrics
46. JAMA Pediatrics
47. Jornal de Pediatria
48. Journal for Specialists in Pediatric Nursing
49. Journal of Aapos
50. Journal of Adolescent Health
51. Journal of Child and Adolescent Psychopharmacology
52. Journal of Child Health Care
53. Journal of Child Neurology
54. Journal of Childrens Orthopaedics
55. Journal of Clinical Pediatric Dentistry
56. Journal of Clinical Research in Pediatric Endocrinology
57. Journal of Developmental and Behavioral Pediatrics
58. Journal of Human Lactation
59. Journal of Neurosurgery-Pediatrics
60. Journal of Paediatrics and Child Health
61. Journal of Pediatric and Adolescent Gynecology
62. Journal of Pediatric Endocrinology & Metabolism
63. Journal of Pediatric Gastroenterology and Nutrition
64. Journal of Pediatric Health Care
65. Journal of Pediatric Hematology Oncology
66. Journal of Pediatric Infectious Diseases
67. Journal of Pediatric Nursing-Nursing Care of Children & Families
68. Journal of Pediatric Ophthalmology & Strabismus
69. Journal of Pediatric Orthopaedics
70. Journal of Pediatric Orthopaedics-Part B
71. Journal of Pediatric Surgery
72. Journal of Pediatric Urology
73. Journal of Pediatrics
74. Journal of Perinatal & Neonatal Nursing
75. Journal of Perinatal Medicine
76. Journal of Perinatology
77. Journal of the American Academy of Child and Adolescent Psychiatry
78. Journal of the Pediatric Infectious Diseases Society
79. Journal of Tropical Pediatrics
80. Klinische Padiatrie
81. Lancet Child & Adolescent Health
82. Maternal and Child Nutrition
83. Monatsschrift Kinderheilkunde
84. Neonatology
85. Neuropediatrics
86. Paediatric and Perinatal Epidemiology
87. Paediatric Respiratory Reviews
88. Paediatrics & Child Health
89. Paediatrics and International Child Health
90. Pediatric Allergy and Immunology
91. Pediatric Allergy Immunology and Pulmonology
92. Pediatric and Developmental Pathology
93. Pediatric Anesthesia
94. Pediatric Annals
95. Pediatric Blood & Cancer
96. Pediatric Cardiology
97. Pediatric Clinics of North America
98. Pediatric Critical Care Medicine
99. Pediatric Dentistry
100. Pediatric Dermatology
101. Pediatric Diabetes
102. Pediatric Drugs
103. Pediatric Emergency Care
104. Pediatric Exercise Science
105. Pediatric Hematology and Oncology
106. Pediatric Infectious Disease Journal
107. Pediatric Nephrology
108. Pediatric Neurology
109. Pediatric Neurosurgery
110. Pediatric Obesity
111. Pediatric Physical Therapy
112. Pediatric Pulmonology
113. Pediatric Radiology
114. Pediatric Research
115. Pediatric Rheumatology
116. Pediatric Surgery International
117. Pediatric Transplantation
118. Pediatrics
119. Pediatrics and Neonatology
120. Pediatrics International
121. Physical & Occupational Therapy in Pediatrics
122. Seminars in Fetal & Neonatal Medicine
123. Seminars in Pediatric Neurology
124. Seminars in Pediatric Surgery
125. Seminars in Perinatology
126. Translational Pediatrics
127. Turkish Journal of Pediatrics
128. World Journal of Pediatrics
129. Zeitschrift für Geburtshilfe und Neonatologie

<a id="scie-peripheral-vascular-diseases"></a>

### Peripheral Vascular Diseases

期刊数：67

1. American Journal of Hypertension
2. American Journal of Physiology-Heart and Circulatory Physiology
3. Angiogenesis
4. Angiology
5. Annals of Vascular Surgery
6. Arteriosclerosis Thrombosis and Vascular Biology
7. Artery Research
8. Atherosclerosis
9. Atherosclerosis Plus
10. Blood Pressure
11. Blood Pressure Monitoring
12. Cerebrovascular Diseases
13. Circulation
14. Circulation Research
15. Clinical and Applied Thrombosis-Hemostasis
16. Clinical and Experimental Hypertension
17. Clinical Hemorheology and Microcirculation
18. Current Atherosclerosis Reports
19. Current Hypertension Reports
20. Current Opinion in Lipidology
21. Current Opinion in Nephrology and Hypertension
22. Current Vascular Pharmacology
23. Diabetes & Vascular Disease Research
24. European Journal of Vascular and Endovascular Surgery
25. European Stroke Journal
26. Heart and Vessels
27. Hypertension
28. Hypertension in Pregnancy
29. Hypertension Research
30. International Angiology
31. International Journal of Hypertension
32. International Journal of Stroke
33. Journal of Atherosclerosis and Thrombosis
34. Journal of Cardiothoracic and Vascular Anesthesia
35. Journal of Cardiovascular Surgery
36. Journal of Clinical Hypertension
37. Journal of Endovascular Therapy
38. Journal of Human Hypertension
39. Journal of Hypertension
40. Journal of Stroke
41. Journal of Stroke & Cerebrovascular Diseases
42. Journal of the Renin-Angiotensin-Aldosterone System
43. Journal of Thrombosis and Haemostasis
44. Journal of Thrombosis and Thrombolysis
45. Journal of Vascular Access
46. Journal of Vascular and Interventional Radiology
47. Journal of Vascular Research
48. Journal of Vascular Surgery
49. Journal of Vascular Surgery-Venous and Lymphatic Disorders
50. Kidney & Blood Pressure Research
51. Microcirculation
52. Microvascular Research
53. Perfusion-UK
54. Phlebology
55. Pregnancy Hypertension-an International Journal of Womens Cardiovascular Health
56. Research and Practice in Thrombosis and Haemostasis
57. Seminars in Thrombosis and Hemostasis
58. Seminars in Vascular Surgery
59. Shock
60. Stroke
61. Thrombosis and Haemostasis
62. Thrombosis Journal
63. Thrombosis Research
64. Vasa-European Journal of Vascular Medicine
65. Vascular
66. Vascular and Endovascular Surgery
67. Vascular Medicine

<a id="scie-pharmacology-pharmacy"></a>

### Pharmacology & Pharmacy

期刊数：270

1. AAPS Journal
2. AAPS PharmSciTech
3. Acta Pharmaceutica
4. Acta Pharmaceutica Sinica B
5. Acta Pharmacologica Sinica
6. Acta Poloniae Pharmaceutica
7. Advanced Drug Delivery Reviews
8. Advanced Therapeutics
9. Advances in Therapy
10. Alcohol
11. Alimentary Pharmacology & Therapeutics
12. American Journal of Cardiovascular Drugs
13. American Journal of Health-System Pharmacy
14. American Journal of Pharmaceutical Education
15. American Journal of Therapeutics
16. Annals of Pharmacotherapy
17. Annual Review of Pharmacology and Toxicology
18. Anti-Cancer Drugs
19. Antibiotics-Basel
20. Antimicrobial Agents and Chemotherapy
21. Antiviral Research
22. Antiviral Therapy
23. Archiv der Pharmazie
24. Archives of Pharmacal Research
25. Asian Journal of Pharmaceutical Sciences
26. Assay and Drug Development Technologies
27. Bangladesh Journal of Pharmacology
28. Basic & Clinical Pharmacology & Toxicology
29. Behavioural Pharmacology
30. Biochemical Pharmacology
31. BioDrugs
32. Bioimpacts
33. Biological & Pharmaceutical Bulletin
34. Biologicals
35. Biomedical Chromatography
36. Biomedicine & Pharmacotherapy
37. Biomedicines
38. Biomolecules & Therapeutics
39. Biopharm International
40. Biopharmaceutics & Drug Disposition
41. BMC Pharmacology & Toxicology
42. Boletin Latinoamericano y del Caribe de Plantas Medicinales y Aromaticas
43. Brazilian Journal of Pharmaceutical Sciences
44. British Journal of Clinical Pharmacology
45. British Journal of Pharmacology
46. Canadian Journal of Physiology and Pharmacology
47. Cancer Biotherapy and Radiopharmaceuticals
48. Cancer Chemotherapy and Pharmacology
49. Cannabis and Cannabinoid Research
50. Cardiovascular Drugs and Therapy
51. Cardiovascular Therapeutics
52. Chemical & Pharmaceutical Bulletin
53. Chemico-Biological Interactions
54. ChemMedChem
55. Chemotherapy
56. Chinese Journal of Natural Medicines
57. Chinese Medicine
58. Chirality
59. Clinical and Experimental Hypertension
60. Clinical and Experimental Pharmacology and Physiology
61. Clinical Drug Investigation
62. Clinical Neuropharmacology
63. Clinical Pharmacokinetics
64. Clinical Pharmacology & Therapeutics
65. Clinical Pharmacology in Drug Development
66. Clinical Psychopharmacology and Neuroscience
67. Clinical Therapeutics
68. CNS & Neurological Disorders-Drug Targets
69. CNS Drugs
70. CNS Neuroscience & Therapeutics
71. Combinatorial Chemistry & High Throughput Screening
72. Contemporary Clinical Trials
73. CPT-Pharmacometrics & Systems Pharmacology
74. Critical Reviews in Therapeutic Drug Carrier Systems
75. Current Drug Delivery
76. Current Drug Metabolism
77. Current Drug Targets
78. Current Medicinal Chemistry
79. Current Molecular Pharmacology
80. Current Neuropharmacology
81. Current Opinion in Pharmacology
82. Current Pharmaceutical Analysis
83. Current Pharmaceutical Biotechnology
84. Current Pharmaceutical Design
85. Current Radiopharmaceuticals
86. Current Vascular Pharmacology
87. DARU-Journal of Pharmaceutical Sciences
88. Dissolution Technologies
89. Dose-Response
90. Drug and Chemical Toxicology
91. Drug Delivery
92. Drug Delivery and Translational Research
93. Drug Design Development and Therapy
94. Drug Development and Industrial Pharmacy
95. Drug Development Research
96. Drug Discovery Today
97. Drug Metabolism and Disposition
98. Drug Metabolism and Pharmacokinetics
99. Drug Metabolism Reviews
100. Drug Resistance Updates
101. Drug Safety
102. Drug Testing and Analysis
103. Drugs
104. Drugs & Aging
105. Drugs in R&D
106. Endocrine Metabolic & Immune Disorders-Drug Targets
107. Environmental Toxicology and Pharmacology
108. European Heart Journal-Cardiovascular Pharmacotherapy
109. European Journal of Clinical Pharmacology
110. European Journal of Drug Metabolism and Pharmacokinetics
111. European Journal of Hospital Pharmacy
112. European Journal of Pharmaceutical Sciences
113. European Journal of Pharmaceutics and Biopharmaceutics
114. European Journal of Pharmacology
115. European Neuropsychopharmacology
116. Experimental and Clinical Psychopharmacology
117. Expert Opinion on Drug Delivery
118. Expert Opinion on Drug Discovery
119. Expert Opinion on Drug Metabolism & Toxicology
120. Expert Opinion on Drug Safety
121. Expert Opinion on Emerging Drugs
122. Expert Opinion on Investigational Drugs
123. Expert Opinion on Pharmacotherapy
124. Expert Opinion on Therapeutic Patents
125. Expert Opinion on Therapeutic Targets
126. Expert Review of Anti-Infective Therapy
127. Expert Review of Clinical Pharmacology
128. Expert Review of Neurotherapeutics
129. Expert Review of Pharmacoeconomics & Outcomes Research
130. Farmacia
131. Fitoterapia
132. Food and Drug Law Journal
133. Frontiers in Pharmacology
134. Fundamental & Clinical Pharmacology
135. HIV Research & Clinical Practice
136. Human Psychopharmacology-Clinical and Experimental
137. Immunopharmacology and Immunotoxicology
138. Indian Journal of Pharmaceutical Education and Research
139. Indian Journal of Pharmacology
140. Infection and Drug Resistance
141. International Clinical Psychopharmacology
142. International Immunopharmacology
143. International Journal for Parasitology-Drugs and Drug Resistance
144. International Journal of Antimicrobial Agents
145. International Journal of Clinical Pharmacology and Therapeutics
146. International Journal of Clinical Pharmacy
147. International Journal of Immunopathology and Pharmacology
148. International Journal of Medicinal Mushrooms
149. International Journal of Nanomedicine
150. International Journal of Neuropsychopharmacology
151. International Journal of Pharmaceutics
152. International Journal of Pharmaceutics-X
153. International Journal of Pharmacology
154. International Journal of Toxicology
155. Investigational New Drugs
156. Iranian Journal of Basic Medical Sciences
157. Iranian Journal of Pharmaceutical Research
158. Journal of Antibiotics
159. Journal of Antimicrobial Chemotherapy
160. Journal of Applied Biomedicine
161. Journal of Asian Natural Products Research
162. Journal of Biopharmaceutical Statistics
163. Journal of Cardiovascular Pharmacology
164. Journal of Cardiovascular Pharmacology and Therapeutics
165. Journal of Chemotherapy
166. Journal of Child and Adolescent Psychopharmacology
167. Journal of Clinical Lipidology
168. Journal of Clinical Pharmacology
169. Journal of Clinical Pharmacy and Therapeutics
170. Journal of Clinical Psychopharmacology
171. Journal of Controlled Release
172. Journal of Drug Delivery Science and Technology
173. Journal of Drug Targeting
174. Journal of Ethnobiology and Ethnomedicine
175. Journal of Ethnopharmacology
176. Journal of Food and Drug Analysis
177. Journal of Global Antimicrobial Resistance
178. Journal of Infection and Chemotherapy
179. Journal of International Medical Research
180. Journal of Liposome Research
181. Journal of Managed Care & Specialty Pharmacy
182. Journal of Microencapsulation
183. Journal of Natural Medicines
184. Journal of Natural Products
185. Journal of Neuroimmune Pharmacology
186. Journal of Ocular Pharmacology and Therapeutics
187. Journal of Oncology Pharmacy Practice
188. Journal of Pharmaceutical Analysis
189. Journal of Pharmaceutical and Biomedical Analysis
190. Journal of Pharmaceutical Innovation
191. Journal of Pharmaceutical Investigation
192. Journal of Pharmaceutical Sciences
193. Journal of Pharmacokinetics and Pharmacodynamics
194. Journal of Pharmacological and Toxicological Methods
195. Journal of Pharmacological Sciences
196. Journal of Pharmacology and Experimental Therapeutics
197. Journal of Pharmacy and Pharmaceutical Sciences
198. Journal of Pharmacy and Pharmacology
199. Journal of Psychopharmacology
200. Journal of the American Pharmacists Association
201. Journal of Veterinary Pharmacology and Therapeutics
202. Korean Journal of Physiology & Pharmacology
203. Life Sciences
204. Marine Drugs
205. Medical Letter on Drugs and Therapeutics
206. Medicinal Research Reviews
207. Microbial Drug Resistance
208. Molecular Diagnosis & Therapy
209. Molecular Pharmaceutics
210. Molecular Pharmacology
211. Nature Reviews Drug Discovery
212. Naunyn-Schmiedebergs Archives of Pharmacology
213. Neuropharmacology
214. Neuropsychopharmacology
215. Neurotherapeutics
216. NeuroToxicology
217. Pakistan Journal of Pharmaceutical Sciences
218. Pediatric Drugs
219. Peptides
220. Personalized Medicine
221. Pharmaceutical Biology
222. Pharmaceutical Chemistry Journal
223. Pharmaceutical Development and Technology
224. Pharmaceutical Research
225. Pharmaceutical Statistics
226. Pharmaceuticals
227. Pharmaceutics
228. PharmacoEconomics
229. Pharmacoepidemiology and Drug Safety
230. Pharmacogenetics and Genomics
231. Pharmacogenomics
232. Pharmacogenomics & Personalized Medicine
233. Pharmacogenomics Journal
234. Pharmacological Reports
235. Pharmacological Research
236. Pharmacological Reviews
237. Pharmacology
238. Pharmacology & Therapeutics
239. Pharmacology Biochemistry and Behavior
240. Pharmacology Research & Perspectives
241. Pharmacopsychiatry
242. Pharmacotherapy
243. Pharmazie
244. Phytomedicine
245. Phytotherapy Research
246. Planta Medica
247. Progress in Neuro-Psychopharmacology & Biological Psychiatry
248. Psychiatry and Clinical Psychopharmacology
249. Psychopharmacology
250. Pulmonary Pharmacology & Therapeutics
251. Recent Patents on Anti-Cancer Drug Discovery
252. Regulatory Toxicology and Pharmacology
253. Revista Brasileira de Farmacognosia-Brazilian Journal of Pharmacognosy
254. Revista Espanola de Quimioterapia
255. Saudi Pharmaceutical Journal
256. Skin Pharmacology and Physiology
257. Therapeutic Advances in Chronic Disease
258. Therapeutic Advances in Drug Safety
259. Therapeutic Advances in Psychopharmacology
260. Therapeutic Drug Monitoring
261. Therapeutic Innovation & Regulatory Science
262. Therapie
263. Toxicology
264. Toxicology and Applied Pharmacology
265. Toxicon
266. Trends in Pharmacological Sciences
267. Vascular Pharmacology
268. Xenobiotica
269. Yakugaku Zasshi-Journal of the Pharmaceutical Society of Japan
270. Zeitschrift für Naturforschung Section C-a Journal of Biosciences

<a id="scie-physics-applied"></a>

### Physics, Applied

期刊数：160

1. 2D Materials
2. ACS Photonics
3. Advanced Electronic Materials
4. Advanced Energy Materials
5. Advanced Functional Materials
6. Advanced Materials
7. AIP Advances
8. APL Materials
9. APL Photonics
10. Applied Physics A-Materials Science & Processing
11. Applied Physics B-Lasers and Optics
12. Applied Physics Express
13. Applied Physics Letters
14. Applied Physics Reviews
15. Applied Sciences-Basel
16. Applied Surface Science
17. Atomization and Sprays
18. Beilstein Journal of Nanotechnology
19. Chalcogenide Letters
20. Coatings
21. Cryogenics
22. Current Applied Physics
23. Current Opinion in Solid State & Materials Science
24. Diamond and Related Materials
25. Discover Nano
26. ECS Journal of Solid State Science and Technology
27. Electronics
28. European Physical Journal E
29. European Physical Journal-Applied Physics
30. Flexible and Printed Electronics
31. Fluctuation and Noise Letters
32. Granular Matter
33. High Temperature
34. IEEE Journal of Photovoltaics
35. IEEE Journal of Quantum Electronics
36. IEEE Journal of Selected Topics in Quantum Electronics
37. IEEE Magnetics Letters
38. IEEE Photonics Journal
39. IEEE Photonics Technology Letters
40. IEEE Sensors Journal
41. IEEE Transactions on Applied Superconductivity
42. IEEE Transactions on Device and Materials Reliability
43. IEEE Transactions on Dielectrics and Electrical Insulation
44. IEEE Transactions on Electron Devices
45. IEEE Transactions on Magnetics
46. IEEE Transactions on Nanotechnology
47. IEEE Transactions on Semiconductor Manufacturing
48. IEEE Transactions on Terahertz Science and Technology
49. Infrared Physics & Technology
50. Integrated Ferroelectrics
51. International Journal of Applied Electromagnetics and Mechanics
52. International Journal of Modern Physics B
53. International Journal of Surface Science and Engineering
54. International Journal of Thermophysics
55. Japanese Journal of Applied Physics
56. Journal of Applied Mechanics and Technical Physics
57. Journal of Applied Physics
58. Journal of Computational Electronics
59. Journal of Crystal Growth
60. Journal of Electromagnetic Waves and Applications
61. Journal of Electronic Materials
62. Journal of Experimental Nanoscience
63. Journal of Infrared Millimeter and Terahertz Waves
64. Journal of Laser Applications
65. Journal of Laser Micro Nanoengineering
66. Journal of Low Temperature Physics
67. Journal of Magnetics
68. Journal of Materials Chemistry C
69. Journal of Materials Science-Materials in Electronics
70. Journal of Materiomics
71. Journal of Microelectromechanical Systems
72. Journal of Micromechanics and Microengineering
73. Journal of Nano Research
74. Journal of Nanoelectronics and Optoelectronics
75. Journal of Nonlinear Optical Physics & Materials
76. Journal of Optoelectronics and Advanced Materials
77. Journal of Ovonic Research
78. Journal of Photonics for Energy
79. Journal of Physics D-Applied Physics
80. Journal of Physics-Materials
81. Journal of Semiconductor Technology and Science
82. Journal of Superconductivity and Novel Magnetism
83. Journal of Synchrotron Radiation
84. Journal of the Society for Information Display
85. Journal of Vacuum Science & Technology A
86. Journal of Vacuum Science & Technology B
87. Journal of X-Ray Science and Technology
88. Journal of Zhejiang University-Science A
89. Laser & Photonics Reviews
90. Laser and Particle Beams
91. Laser Physics
92. Laser Physics Letters
93. Low Temperature Physics
94. Mapan-Journal of Metrology Society of India
95. Materials
96. Materials Letters
97. Materials Science & Engineering R-Reports
98. Materials Science in Semiconductor Processing
99. Materials Today Physics
100. Metrologia
101. Microelectronic Engineering
102. Microelectronics Reliability
103. Micromachines
104. Microsystem Technologies-Micro-and Nanosystems-Information Storage and Processing Systems
105. Modelling and Simulation in Materials Science and Engineering
106. Modern Physics Letters B
107. MRS Bulletin
108. Nano
109. Nano Convergence
110. Nano Energy
111. Nano Futures
112. Nano Letters
113. Nano Research
114. Nano-Micro Letters
115. Nanomaterials
116. Nanomaterials and Nanotechnology
117. Nanophotonics
118. Nanoscale
119. Nanoscale and Microscale Thermophysical Engineering
120. Nanotechnology
121. Nanotechnology Reviews
122. Nature Materials
123. Nature Photonics
124. Nature Reviews Physics
125. Npj 2D Materials and Applications
126. Npj Quantum Information
127. Npj Quantum Materials
128. Optics and Laser Technology
129. Opto-Electronics Review
130. Organic Electronics
131. Philosophical Magazine
132. Philosophical Magazine Letters
133. Photonics and Nanostructures-Fundamentals and Applications
134. Physica C-Superconductivity and Its Applications
135. Physica Status Solidi a-Applications and Materials Science
136. Physica Status Solidi-Rapid Research Letters
137. Physical Review Applied
138. Physical Review B
139. Plasma Chemistry and Plasma Processing
140. Plasma Processes and Polymers
141. Progress in Electromagnetics Research-Pier
142. Progress in Photovoltaics
143. Progress in Quantum Electronics
144. PRX Quantum
145. Quantitative InfraRed Thermography Journal
146. Radiophysics and Quantum Electronics
147. Recent Patents on Nanotechnology
148. Review of Scientific Instruments
149. Romanian Journal of Information Science and Technology
150. Small
151. Solar Energy Materials and Solar Cells
152. Solid-State Electronics
153. Spin
154. Superconductor Science & Technology
155. Surface & Coatings Technology
156. Surfaces and Interfaces
157. Technical Physics
158. Technical Physics Letters
159. Thin Solid Films
160. Vacuum

<a id="scie-physics-atomic-molecular-chemical"></a>

### Physics, Atomic, Molecular & Chemical

期刊数：33

1. Applied Magnetic Resonance
2. Atomic Data and Nuclear Data Tables
3. Chemical Physics
4. Chemical Physics Letters
5. Chemical Physics Reviews
6. ChemPhysChem
7. Chinese Journal of Chemical Physics
8. Concepts in Magnetic Resonance Part A
9. EPJ Quantum Technology
10. European Journal of Mass Spectrometry
11. European Physical Journal D
12. Fullerenes Nanotubes and Carbon Nanostructures
13. International Journal of Mass Spectrometry
14. International Journal of Photoenergy
15. International Journal of Quantum Chemistry
16. International Reviews in Physical Chemistry
17. Journal of Chemical Physics
18. Journal of Chemical Theory and Computation
19. Journal of Magnetic Resonance
20. Journal of Molecular Spectroscopy
21. Journal of Physical Chemistry A
22. Journal of Physical Chemistry Letters
23. Journal of Physics B-Atomic Molecular and Optical Physics
24. Molecular Physics
25. Molecular Simulation
26. Npj Quantum Information
27. Nuclear Instruments & Methods in Physics Research Section B-Beam Interactions with Materials and Atoms
28. Physical Chemistry Chemical Physics
29. Physical Review A
30. Progress in Nuclear Magnetic Resonance Spectroscopy
31. Radiation Physics and Chemistry
32. Solid State Nuclear Magnetic Resonance
33. Structural Dynamics-US

<a id="scie-physics-condensed-matter"></a>

### Physics, Condensed Matter

期刊数：67

1. ACS Photonics
2. Advanced Energy Materials
3. Advanced Functional Materials
4. Advanced Materials
5. Advances in Condensed Matter Physics
6. Advances in Physics
7. Annual Review of Condensed Matter Physics
8. Applied Surface Science
9. Condensed Matter Physics
10. Critical Reviews in Solid State and Materials Sciences
11. Current Opinion in Solid State & Materials Science
12. Diamond and Related Materials
13. European Physical Journal B
14. Ferroelectrics
15. Ferroelectrics Letters Section
16. IEEE Transactions on Semiconductor Manufacturing
17. Integrated Ferroelectrics
18. International Journal of Modern Physics B
19. Ionics
20. Journal of Low Temperature Physics
21. Journal of Magnetics
22. Journal of Magnetism and Magnetic Materials
23. Journal of Materials Science-Materials in Electronics
24. Journal of Physics and Chemistry of Solids
25. Journal of Physics-Condensed Matter
26. Journal of Superconductivity and Novel Magnetism
27. Journal of the Mechanics and Physics of Solids
28. Laser & Photonics Reviews
29. Materials
30. Materials Science and Engineering B-Advanced Functional Solid-State Materials
31. Materials Science in Semiconductor Processing
32. Micro and Nanostructures
33. Modern Physics Letters B
34. Nano Letters
35. Nature Materials
36. Npj Quantum Information
37. Npj Quantum Materials
38. Phase Transitions
39. Philosophical Magazine
40. Philosophical Magazine Letters
41. Physica B-Condensed Matter
42. Physica C-Superconductivity and Its Applications
43. Physica E-Low-Dimensional Systems & Nanostructures
44. Physica Status Solidi a-Applications and Materials Science
45. Physica Status Solidi B-Basic Solid State Physics
46. Physica Status Solidi-Rapid Research Letters
47. Physical Review B
48. Physics and Chemistry of Liquids
49. Physics of the Solid State
50. Plasma Processes and Polymers
51. Progress in Surface Science
52. Radiation Effects and Defects in Solids
53. Semiconductor Science and Technology
54. Semiconductors
55. Small
56. Solid State Communications
57. Solid State Ionics
58. Solid State Nuclear Magnetic Resonance
59. Solid State Sciences
60. Solid-State Electronics
61. Superconductor Science & Technology
62. Surface Review and Letters
63. Surface Science
64. Surface Science Reports
65. Surfaces and Interfaces
66. Synthetic Metals
67. Thin Solid Films

<a id="scie-physics-fluids-plasmas"></a>

### Physics, Fluids & Plasmas

期刊数：34

1. Annual Review of Fluid Mechanics
2. Biomicrofluidics
3. Communications in Nonlinear Science and Numerical Simulation
4. Contributions to Plasma Physics
5. European Journal of Mechanics B-Fluids
6. Experimental Thermal and Fluid Science
7. Fluid Dynamics
8. Fluid Dynamics Research
9. High Energy Density Physics
10. IEEE Transactions on Plasma Science
11. International Journal for Numerical Methods in Fluids
12. International Journal of Computational Fluid Dynamics
13. Journal of Fluid Mechanics
14. Journal of Mathematical Fluid Mechanics
15. Journal of Plasma Physics
16. Journal of Turbulence
17. Magnetohydrodynamics
18. Microfluidics and Nanofluidics
19. Nonlinear Processes in Geophysics
20. Nuclear Fusion
21. Physica D-Nonlinear Phenomena
22. Physical Review E
23. Physical Review Fluids
24. Physics of Fluids
25. Physics of Plasmas
26. Plasma Chemistry and Plasma Processing
27. Plasma Physics and Controlled Fusion
28. Plasma Physics Reports
29. Plasma Processes and Polymers
30. Plasma Science & Technology
31. Plasma Sources Science & Technology
32. Radiation Effects and Defects in Solids
33. Radiophysics and Quantum Electronics
34. Theoretical and Computational Fluid Dynamics

<a id="scie-physics-mathematical"></a>

### Physics, Mathematical

期刊数：56

1. Advances in Applied Clifford Algebras
2. Advances in Mathematical Physics
3. Advances in Theoretical and Mathematical Physics
4. Annales Henri Poincare
5. Annals of PDE
6. Chaos
7. Chaos Solitons & Fractals
8. Communications in Analysis and Mechanics
9. Communications in Applied Mathematics and Computational Science
10. Communications in Computational Physics
11. Communications in Mathematical Physics
12. Communications in Nonlinear Science and Numerical Simulation
13. Communications in Number Theory and Physics
14. Computational Mathematics and Mathematical Physics
15. Computer Physics Communications
16. Dynamical Systems-an International Journal
17. Infinite Dimensional Analysis Quantum Probability and Related Topics
18. International Journal of Geometric Methods in Modern Physics
19. International Journal of Modern Physics B
20. International Journal of Modern Physics C
21. International Journal of Quantum Information
22. Inverse Problems
23. Inverse Problems and Imaging
24. Journal of Computational and Theoretical Transport
25. Journal of Computational Physics
26. Journal of Geometry and Physics
27. Journal of Hyperbolic Differential Equations
28. Journal of Mathematical Physics
29. Journal of Mathematical Physics Analysis Geometry
30. Journal of Noncommutative Geometry
31. Journal of Nonlinear Complex and Data Science
32. Journal of Nonlinear Mathematical Physics
33. Journal of Nonlinear Science
34. Journal of Physics A-Mathematical and Theoretical
35. Journal of Statistical Mechanics-Theory and Experiment
36. Journal of Statistical Physics
37. Letters in Mathematical Physics
38. Mathematical Physics Analysis and Geometry
39. Modern Physics Letters A
40. Modern Physics Letters B
41. Multiscale Modeling & Simulation
42. Nonlinearity
43. Open Systems & Information Dynamics
44. Physica D-Nonlinear Phenomena
45. Physical Review E
46. Quantum Information & Computation
47. Quantum Information Processing
48. Random Matrices-Theory and Applications
49. Regular & Chaotic Dynamics
50. Reports on Mathematical Physics
51. Reviews in Mathematical Physics
52. Russian Journal of Mathematical Physics
53. SIAM Journal on Applied Dynamical Systems
54. SIAM-ASA Journal on Uncertainty Quantification
55. Symmetry Integrability and Geometry-Methods and Applications
56. Theoretical and Mathematical Physics

<a id="scie-physics-multidisciplinary"></a>

### Physics, Multidisciplinary

期刊数：84

1. Acta Physica Polonica A
2. Acta Physica Polonica B
3. Acta Physica Sinica
4. Advances in Physics-X
5. American Journal of Physics
6. Annalen der Physik
7. Annales Henri Poincare
8. Annals of Physics
9. Brazilian Journal of Physics
10. Bulletin of the Lebedev Physics Institute
11. Canadian Journal of Physics
12. Cell Reports Physical Science
13. Chaos Solitons & Fractals
14. Chinese Journal of Physics
15. Chinese Physics B
16. Chinese Physics Letters
17. Classical and Quantum Gravity
18. Communications in Theoretical Physics
19. Communications Physics
20. Comptes Rendus Physique
21. Contemporary Physics
22. Doklady Physics
23. Entropy
24. EPL
25. European Journal of Physics
26. European Physical Journal H
27. European Physical Journal Plus
28. European Physical Journal-Special Topics
29. Few-Body Systems
30. Fortschritte der Physik-Progress of Physics
31. Foundations of Physics
32. Frontiers in Physics
33. Frontiers of Physics
34. General Relativity and Gravitation
35. High Pressure Research
36. Indian Journal of Physics
37. Indian Journal of Pure & Applied Physics
38. International Journal of Theoretical Physics
39. JETP Letters
40. Journal of Contemporary Physics-Armenian Academy of Sciences
41. Journal of Experimental and Theoretical Physics
42. Journal of Physical and Chemical Reference Data
43. Journal of Physics A-Mathematical and Theoretical
44. Journal of the Korean Physical Society
45. Journal of the Physical Society of Japan
46. Lithuanian Journal of Physics
47. Matter and Radiation at Extremes
48. Moscow University Physics Bulletin
49. Nature Physics
50. Nature Reviews Physics
51. New Journal of Physics
52. Open Physics
53. Physica A-Statistical Mechanics and Its Applications
54. Physica D-Nonlinear Phenomena
55. Physica Scripta
56. Physical Review Letters
57. Physical Review X
58. Physics Letters A
59. Physics of Wave Phenomena
60. Physics Reports-Review Section of Physics Letters
61. Physics Teacher
62. Physics Today
63. Physics World
64. Physics-Uspekhi
65. Pramana-Journal of Physics
66. Progress of Theoretical and Experimental Physics
67. PRX Quantum
68. Quantum
69. Quantum Information Processing
70. Quantum Science and Technology
71. Reports on Progress in Physics
72. Reviews of Modern Physics
73. Revista Mexicana de Fisica
74. Rivista del Nuovo Cimento
75. Romanian Journal of Physics
76. Romanian Reports in Physics
77. Russian Physics Journal
78. Science China-Physics Mechanics & Astronomy
79. SciPost Physics
80. Soft Matter
81. Theoretical and Mathematical Physics
82. University Politehnica of Bucharest Scientific Bulletin-Series A-Applied Mathematics and Physics
83. Wave Motion
84. Zeitschrift für Naturforschung Section A-a Journal of Physical Sciences

<a id="scie-physics-nuclear"></a>

### Physics, Nuclear

期刊数：19

1. Annual Review of Nuclear and Particle Science
2. Atomic Data and Nuclear Data Tables
3. Chinese Physics C
4. European Physical Journal A
5. International Journal of Modern Physics A
6. International Journal of Modern Physics E
7. Journal of Physics G-Nuclear and Particle Physics
8. Modern Physics Letters A
9. Nuclear Data Sheets
10. Nuclear Instruments & Methods in Physics Research Section A-Accelerators Spectrometers Detectors and Associated Equipment
11. Nuclear Instruments & Methods in Physics Research Section B-Beam Interactions with Materials and Atoms
12. Nuclear Physics A
13. Nuclear Science and Techniques
14. Nukleonika
15. Physical Review Accelerators and Beams
16. Physical Review C
17. Physics Letters B
18. Physics of Atomic Nuclei
19. Progress in Particle and Nuclear Physics

<a id="scie-physics-particles-fields"></a>

### Physics, Particles & Fields

期刊数：29

1. Advances in High Energy Physics
2. Advances in Theoretical and Mathematical Physics
3. Annales Henri Poincare
4. Annual Review of Nuclear and Particle Science
5. Astroparticle Physics
6. Chinese Physics C
7. Classical and Quantum Gravity
8. European Physical Journal A
9. European Physical Journal C
10. General Relativity and Gravitation
11. International Journal of Modern Physics A
12. International Journal of Modern Physics E
13. International Journal of Quantum Information
14. Journal of Cosmology and Astroparticle Physics
15. Journal of High Energy Physics
16. Journal of Physics G-Nuclear and Particle Physics
17. Living Reviews in Relativity
18. Modern Physics Letters A
19. Nuclear Instruments & Methods in Physics Research Section A-Accelerators Spectrometers Detectors and Associated Equipment
20. Nuclear Physics B
21. Physical Review Accelerators and Beams
22. Physical Review D
23. Physics Letters B
24. Physics of Atomic Nuclei
25. Physics of Particles and Nuclei
26. Progress in Particle and Nuclear Physics
27. Progress of Theoretical and Experimental Physics
28. Quantum Information & Computation
29. Universe

<a id="scie-physiology"></a>

### Physiology

期刊数：79

1. Acta Physiologica
2. Advances in Physiology Education
3. American Journal of Physiology-Cell Physiology
4. American Journal of Physiology-Endocrinology and Metabolism
5. American Journal of Physiology-Gastrointestinal and Liver Physiology
6. American Journal of Physiology-Heart and Circulatory Physiology
7. American Journal of Physiology-Lung Cellular and Molecular Physiology
8. American Journal of Physiology-Regulatory, Integrative and Comparative Physiology
9. American Journal of Physiology-Renal Physiology
10. Annual Review of Physiology
11. Applied Physiology Nutrition and Metabolism
12. Archives of Insect Biochemistry and Physiology
13. Archives of Physiology and Biochemistry
14. Biological Rhythm Research
15. Canadian Journal of Physiology and Pharmacology
16. Cell Calcium
17. Chemical Senses
18. Chronobiology International
19. Clinical and Experimental Pharmacology and Physiology
20. Clinical Journal of Sport Medicine
21. Clinical Physiology and Functional Imaging
22. Comparative Biochemistry and Physiology A-Molecular & Integrative Physiology
23. Comprehensive Physiology
24. Conservation Physiology
25. Cryobiology
26. Cryoletters
27. Ecological and Evolutionary Physiology
28. European Journal of Applied Physiology
29. Exercise and Sport Sciences Reviews
30. Experimental Physiology
31. Fish Physiology and Biochemistry
32. Frontiers in Physiology
33. General Physiology and Biophysics
34. Hypertension in Pregnancy
35. International Journal of Behavioral Nutrition and Physical Activity
36. International Journal of Biometeorology
37. International Journal of Psychophysiology
38. International Journal of Sports Physiology and Performance
39. Journal of Applied Physiology
40. Journal of Biological Rhythms
41. Journal of Cellular Physiology
42. Journal of Comparative Physiology A-Neuroethology Sensory Neural and Behavioral Physiology
43. Journal of Comparative Physiology B-Biochemical Systems and Environmental Physiology
44. Journal of Electromyography and Kinesiology
45. Journal of Evolutionary Biochemistry and Physiology
46. Journal of General Physiology
47. Journal of Insect Physiology
48. Journal of Mammary Gland Biology and Neoplasia
49. Journal of Membrane Biology
50. Journal of Musculoskeletal & Neuronal Interactions
51. Journal of Neurophysiology
52. Journal of Physiological Anthropology
53. Journal of Physiological Investigation
54. Journal of Physiological Sciences
55. Journal of Physiology and Biochemistry
56. Journal of Physiology and Pharmacology
57. Journal of Physiology-London
58. Journal of Pineal Research
59. Journal of Vascular Research
60. Kidney & Blood Pressure Research
61. Klinische Neurophysiologie
62. Korean Journal of Physiology & Pharmacology
63. Lymphatic Research and Biology
64. Lymphology
65. Neurophysiologie Clinique-Clinical Neurophysiology
66. Neurophysiology
67. Pediatric Exercise Science
68. Pesticide Biochemistry and Physiology
69. Pflugers Archiv-European Journal of Physiology
70. Physiological Genomics
71. Physiological Measurement
72. Physiological Research
73. Physiological Reviews
74. Physiology
75. Physiology International
76. Psychophysiology
77. Quarterly Journal of Experimental Psychology
78. Respiratory Physiology & Neurobiology
79. Zhurnal Vysshei Nervnoi Deyatelnosti Imeni i P Pavlova

<a id="scie-plant-sciences"></a>

### Plant Sciences

期刊数：238

1. Acta Amazonica
2. Acta Biologica Colombiana
3. Acta Biologica Cracoviensia Series Botanica
4. Acta Botanica Brasilica
5. Acta Botanica Croatica
6. Acta Botanica Mexicana
7. Acta Physiologiae Plantarum
8. Acta Phytotaxonomica et Geobotanica
9. Acta Societatis Botanicorum Poloniae
10. Adansonia
11. Advances in Weed Science
12. African Biodiversity & Conservation
13. Agronomy-Basel
14. Algae
15. Alpine Botany
16. American Fern Journal
17. American Journal of Botany
18. Anales del Jardin Botanico de Madrid
19. Annales Botanici Fennici
20. Annali di Botanica
21. Annals of Botany
22. Annals of the Missouri Botanical Garden
23. Annual Review of Phytopathology
24. Annual Review of Plant Biology
25. AoB Plants
26. Applications in Plant Sciences
27. Applied Vegetation Science
28. Aquatic Botany
29. Australasian Plant Pathology
30. Australian Journal of Botany
31. Australian Systematic Botany
32. Bangladesh Journal of Botany
33. Bangladesh Journal of Plant Taxonomy
34. Biologia Plantarum
35. Blumea
36. BMC Plant Biology
37. Boletin de la Sociedad Argentina de Botanica
38. Botanica Marina
39. Botanical Journal of the Linnean Society
40. Botanical Review
41. Botanical Sciences
42. Botanical Studies
43. Botany
44. Botany Letters
45. Bradleya
46. Brazilian Journal of Botany
47. Breeding Science
48. Brittonia
49. Bryologist
50. Caldasia
51. Canadian Journal of Plant Pathology
52. Canadian Journal of Plant Science
53. Candollea
54. Castanea
55. Communications in Soil Science and Plant Analysis
56. Comparative Cytogenetics
57. Comprehensive Plant Biology
58. Critical Reviews in Plant Sciences
59. Crop Journal
60. Cryptogamie Algologie
61. Cryptogamie Bryologie
62. Current Opinion in Plant Biology
63. Czech Journal of Genetics and Plant Breeding
64. Environmental and Experimental Botany
65. Ethnobotany and Economic Botany
66. Euphytica
67. European Journal of Phycology
68. European Journal of Plant Pathology
69. European Journal of Taxonomy
70. Flora
71. Folia Geobotanica
72. Food and Energy Security
73. Fottea
74. Frontiers in Plant Science
75. Functional Plant Biology
76. Gayana Botanica
77. Genetic Resources and Crop Evolution
78. GM Crops & Food-Biotechnology in Agriculture and the Food Chain
79. Gorteria
80. Grana
81. Haseltonia
82. Herzogia
83. Horticultural Plant Journal
84. Horticulture Research
85. Iheringia Serie Botanica
86. In Vitro Cellular & Developmental Biology-Plant
87. Indian Journal of Genetics and Plant Breeding
88. Indian Journal of Traditional Knowledge
89. International Journal of Plant Sciences
90. Invasive Plant Science and Management
91. Israel Journal of Plant Sciences
92. Journal of Applied Botany and Food Quality
93. Journal of Applied Research on Medicinal and Aromatic Plants
94. Journal of Aquatic Plant Management
95. Journal of Asian Natural Products Research
96. Journal of Berry Research
97. Journal of Bryology
98. Journal of Ecology
99. Journal of Essential Oil Bearing Plants
100. Journal of Ethnobiology and Ethnomedicine
101. Journal of Ethnopharmacology
102. Journal of Experimental Botany
103. Journal of General Plant Pathology
104. Journal of Integrative Plant Biology
105. Journal of Natural Products
106. Journal of Phycology
107. Journal of Phytopathology
108. Journal of Plant Biochemistry and Biotechnology
109. Journal of Plant Biology
110. Journal of Plant Diseases and Protection
111. Journal of Plant Ecology
112. Journal of Plant Growth Regulation
113. Journal of Plant Interactions
114. Journal of Plant Nutrition
115. Journal of Plant Nutrition and Soil Science
116. Journal of Plant Pathology
117. Journal of Plant Physiology
118. Journal of Plant Registrations
119. Journal of Plant Research
120. Journal of Soil Science and Plant Nutrition
121. Journal of Systematics and Evolution
122. Journal of the Torrey Botanical Society
123. Journal of Vegetation Science
124. Kew Bulletin
125. Lichenologist
126. Maydica
127. Mediterranean Botany
128. Molecular Breeding
129. Molecular Horticulture
130. Molecular Plant
131. Molecular Plant Pathology
132. Molecular Plant-Microbe Interactions
133. Mycorrhiza
134. Nature Plants
135. New Phytologist
136. New Zealand Journal of Botany
137. Nordic Journal of Botany
138. Notulae Botanicae Horti Agrobotanici Cluj-Napoca
139. Nova Hedwigia
140. Novon
141. Pakistan Journal of Botany
142. Palynology
143. Perspectives in Plant Ecology Evolution and Systematics
144. Pharmaceutical Biology
145. Photosynthesis Research
146. Photosynthetica
147. Phycologia
148. Physiologia Plantarum
149. Physiological and Molecular Plant Pathology
150. Physiology and Molecular Biology of Plants
151. Phytobiomes Journal
152. Phytochemical Analysis
153. Phytochemistry
154. Phytochemistry Letters
155. Phytochemistry Reviews
156. Phytocoenologia
157. PhytoKeys
158. Phytomedicine
159. Phyton-Annales Rei Botanicae
160. Phyton-International Journal of Experimental Botany
161. Phytoparasitica
162. Phytopathologia Mediterranea
163. Phytopathology
164. Phytopathology Research
165. Phytoprotection
166. Phytotaxa
167. Plant and Cell Physiology
168. Plant and Soil
169. Plant Biology
170. Plant Biosystems
171. Plant Biotechnology
172. Plant Biotechnology Journal
173. Plant Biotechnology Reports
174. Plant Breeding
175. Plant Cell
176. Plant Cell and Environment
177. Plant Cell Reports
178. Plant Cell Tissue and Organ Culture
179. Plant Communications
180. Plant Direct
181. Plant Disease
182. Plant Diversity
183. Plant Ecology
184. Plant Ecology & Diversity
185. Plant Ecology and Evolution
186. Plant Foods for Human Nutrition
187. Plant Genetic Resources-Characterization and Utilization
188. Plant Genome
189. Plant Growth Regulation
190. Plant Journal
191. Plant Methods
192. Plant Molecular Biology
193. Plant Molecular Biology Reporter
194. Plant Pathology
195. Plant Pathology Journal
196. Plant Phenomics
197. Plant Physiology
198. Plant Physiology and Biochemistry
199. Plant Protection Science
200. Plant Reproduction
201. Plant Science
202. Plant Signaling & Behavior
203. Plant Species Biology
204. Plant Systematics and Evolution
205. Planta
206. Planta Medica
207. Plants People Planet
208. Plants-Basel
209. Preslia
210. Protoplasma
211. Records of Natural Products
212. Review of Palaeobotany and Palynology
213. Rhizosphere
214. Rhodora
215. Rice Science
216. Russian Journal of Plant Physiology
217. Seed Science and Technology
218. Seed Science Research
219. Soil Science and Plant Nutrition
220. South African Journal of Botany
221. Systematic Botany
222. Taiwania
223. Taxon
224. Telopea
225. Theoretical and Applied Genetics
226. Theoretical and Experimental Plant Physiology
227. Trends in Plant Science
228. Tropical Plant Biology
229. Tropical Plant Pathology
230. Tuexenia
231. Turkish Journal of Botany
232. Vegetation History and Archaeobotany
233. Weed Biology and Management
234. Weed Research
235. Weed Science
236. Weed Technology
237. Willdenowia
238. Zeitschrift fur Arznei- & Gewurzpflanzen

<a id="scie-polymer-science"></a>

### Polymer Science

期刊数：86

1. ACS Applied Polymer Materials
2. ACS Macro Letters
3. Acta Polymerica Sinica
4. Advances in Polymer Technology
5. Biomacromolecules
6. Carbohydrate Polymers
7. Cellular Polymers
8. Cellulose
9. Chinese Journal of Polymer Science
10. Colloid and Polymer Science
11. Designed Monomers and Polymers
12. E-Polymers
13. European Physical Journal E
14. European Polymer Journal
15. eXPRESS Polymer Letters
16. Fibers and Polymers
17. Gels
18. Green Materials
19. High Performance Polymers
20. International Journal of Biological Macromolecules
21. International Journal of Polymer Analysis and Characterization
22. International Journal of Polymer Science
23. International Journal of Polymeric Materials and Polymeric Biomaterials
24. International Polymer Processing
25. Iranian Polymer Journal
26. Journal of Applied Polymer Science
27. Journal of Bioactive and Compatible Polymers
28. Journal of Biomaterials Science-Polymer Edition
29. Journal of Cellular Plastics
30. Journal of Elastomers and Plastics
31. Journal of Fiber Science and Technology
32. Journal of Inorganic and Organometallic Polymers and Materials
33. Journal of Macromolecular Science Part A-Pure and Applied Chemistry
34. Journal of Macromolecular Science Part B-Physics
35. Journal of Membrane Science
36. Journal of Photopolymer Science and Technology
37. Journal of Polymer Engineering
38. Journal of Polymer Materials
39. Journal of Polymer Research
40. Journal of Polymer Science
41. Journal of Polymers and the Environment
42. Journal of Reinforced Plastics and Composites
43. Journal of Rubber Research
44. Journal of Vinyl & Additive Technology
45. Kgk-Kautschuk Gummi Kunststoffe
46. Korea-Australia Rheology Journal
47. Macromolecular Bioscience
48. Macromolecular Chemistry and Physics
49. Macromolecular Materials and Engineering
50. Macromolecular Rapid Communications
51. Macromolecular Reaction Engineering
52. Macromolecular Research
53. Macromolecular Theory and Simulations
54. Macromolecules
55. Mechanics of Composite Materials
56. Membranes
57. Nihon Reoroji Gakkaishi
58. Plasma Processes and Polymers
59. Plastics Rubber and Composites
60. Polimeros-Ciencia e Tecnologia
61. Polimery
62. Polymer
63. Polymer Bulletin
64. Polymer Chemistry
65. Polymer Composites
66. Polymer Degradation and Stability
67. Polymer Engineering and Science
68. Polymer International
69. Polymer Journal
70. Polymer Reviews
71. Polymer Science Series A
72. Polymer Science Series B
73. Polymer Science Series C
74. Polymer Testing
75. Polymer-Korea
76. Polymer-Plastics Technology and Materials
77. Polymers
78. Polymers & Polymer Composites
79. Polymers for Advanced Technologies
80. Progress in Polymer Science
81. Progress in Rubber Plastics and Recycling Technology
82. Reactive & Functional Polymers
83. Rubber Chemistry and Technology
84. Sen-i Gakkaishi
85. Soft Matter
86. Synthetic Metals

<a id="scie-primary-health-care"></a>

### Primary Health Care

期刊数：18

1. American Family Physician
2. Annals of Family Medicine
3. Atencion Primaria
4. Australian Journal of General Practice
5. Australian Journal of Primary Health
6. BMC Primary Care
7. British Journal of General Practice
8. Canadian Family Physician
9. European Journal of General Practice
10. Family Medicine
11. Family Practice
12. Journal of the American Board of Family Medicine
13. Npj Primary Care Respiratory Medicine
14. Physician and Sportsmedicine
15. Primary Care
16. Primary Care Diabetes
17. Primary Health Care Research & Development
18. Scandinavian Journal of Primary Health Care

<a id="scie-psychiatry"></a>

### Psychiatry

期刊数：153

1. Acta Neuropsychiatrica
2. Acta Psychiatrica Scandinavica
3. Actas Espanolas de Psiquiatria
4. Addiction
5. Aging & Mental Health
6. Alpha Psychiatry
7. American Journal of Geriatric Psychiatry
8. American Journal of Medical Genetics Part B-Neuropsychiatric Genetics
9. American Journal of Psychiatry
10. Annales Medico-Psychologiques
11. Annals of Clinical Psychiatry
12. Annals of General Psychiatry
13. Archives of Psychiatric Nursing
14. Archives of Womens Mental Health
15. Arquivos de Neuro-Psiquiatria
16. Asia-Pacific Psychiatry
17. Asian Journal of Psychiatry
18. Australasian Psychiatry
19. Australian and New Zealand Journal of Psychiatry
20. Behavioral Medicine
21. Behavioral Sleep Medicine
22. Biological Psychiatry
23. Biological Psychiatry-Cognitive Neuroscience and Neuroimaging
24. Biopsychosocial Science and Medicine
25. Bipolar Disorders
26. BJPsych Open
27. BMC Psychiatry
28. BMJ Mental Health
29. Borderline Personality Disorder and Emotion Dysregulation
30. Brain Behavior and Immunity
31. Brazilian Journal of Psychiatry
32. British Journal of Psychiatry
33. Cambridge Prisms-Global Mental Health
34. Canadian Journal of Psychiatry-Revue Canadienne de Psychiatrie
35. Child and Adolescent Mental Health
36. Child and Adolescent Psychiatry and Mental Health
37. Clinical Child Psychology and Psychiatry
38. Clinical EEG and Neuroscience
39. Clinical Gerontologist
40. Clinical Psychological Science
41. CNS Drugs
42. CNS Spectrums
43. Cognitive Neuropsychiatry
44. Comprehensive Psychiatry
45. Current Opinion in Psychiatry
46. Current Psychiatry Reports
47. Dementia and Geriatric Cognitive Disorders
48. Depression and Anxiety
49. Drug and Alcohol Dependence
50. Early Intervention in Psychiatry
51. Eating and Weight Disorders-Studies on Anorexia Bulimia and Obesity
52. Eating Disorders
53. Encephale-Revue de Psychiatrie Clinique Biologique et Therapeutique
54. Epidemiology and Psychiatric Sciences
55. Epilepsy & Behavior
56. European Addiction Research
57. European Archives of Psychiatry and Clinical Neuroscience
58. European Child & Adolescent Psychiatry
59. European Neuropsychopharmacology
60. European Psychiatry
61. Experimental and Clinical Psychopharmacology
62. Fortschritte der Neurologie Psychiatrie
63. Frontiers in Psychiatry
64. General Hospital Psychiatry
65. Geriatrie et Psychologie Neuropsychiatrie du Vieillissement
66. Harvard Review of Psychiatry
67. Human Psychopharmacology-Clinical and Experimental
68. Indian Journal of Psychiatry
69. International Clinical Psychopharmacology
70. International Journal of Bipolar Disorders
71. International Journal of Eating Disorders
72. International Journal of Geriatric Psychiatry
73. International Journal of Mental Health and Addiction
74. International Journal of Mental Health Nursing
75. International Journal of Methods in Psychiatric Research
76. International Journal of Neuropsychopharmacology
77. International Journal of Psychiatry in Clinical Practice
78. International Journal of Psychiatry in Medicine
79. International Psychogeriatrics
80. Internet Interventions-the Application of Information Technology in Mental and Behavioural Health
81. Issues in Mental Health Nursing
82. JAMA Psychiatry
83. JMIR Mental Health
84. Journal of Affective Disorders
85. Journal of Attention Disorders
86. Journal of Behavioral Addictions
87. Journal of Child and Adolescent Psychopharmacology
88. Journal of Child Psychology and Psychiatry
89. Journal of Clinical Psychiatry
90. Journal of Clinical Psychopharmacology
91. Journal of Eating Disorders
92. Journal of Ect
93. Journal of Geriatric Psychiatry and Neurology
94. Journal of Nervous and Mental Disease
95. Journal of Neurology Neurosurgery and Psychiatry
96. Journal of Neuropsychiatry and Clinical Neurosciences
97. Journal of Obsessive-Compulsive and Related Disorders
98. Journal of Psychiatric and Mental Health Nursing
99. Journal of Psychiatric Practice
100. Journal of Psychiatric Research
101. Journal of Psychiatry & Neuroscience
102. Journal of Psychopharmacology
103. Journal of Psychosomatic Obstetrics & Gynecology
104. Journal of Psychosomatic Research
105. Journal of the Academy of Consultation-Liaison Psychiatry
106. Journal of the American Academy of Child and Adolescent Psychiatry
107. Journal of the American Psychiatric Nurses Association
108. Journal of the International Neuropsychological Society
109. Lancet Psychiatry
110. Molecular Psychiatry
111. Nervenarzt
112. Neurocase
113. Neuropsychiatric Disease and Treatment
114. Neuropsychobiology
115. Neuropsychopharmacology
116. Nordic Journal of Psychiatry
117. Perspectives in Psychiatric Care
118. Pharmacopsychiatry
119. Progress in Neuro-Psychopharmacology & Biological Psychiatry
120. Psychiatria Polska
121. Psychiatric Services
122. Psychiatrie de l Enfant
123. Psychiatry and Clinical Neurosciences
124. Psychiatry and Clinical Psychopharmacology
125. Psychiatry Investigation
126. Psychiatry Research
127. Psychiatry Research-Neuroimaging
128. Psychiatry-Interpersonal and Biological Processes
129. Psychogeriatrics
130. Psychological Medicine
131. Psychology and Psychotherapy-Theory Research and Practice
132. Psychoneuroendocrinology
133. Psychopathology
134. Psychopharmacology
135. Psychotherapy and Psychosomatics
136. Recht & Psychiatrie
137. Rivista di Psichiatria
138. Schizophrenia
139. Schizophrenia Bulletin
140. Schizophrenia Research
141. Social Psychiatry and Psychiatric Epidemiology
142. South African Journal of Psychiatry
143. Spanish Journal of Psychiatry and Mental Health
144. Stress and Health
145. Substance Use & Misuse
146. Suchttherapie
147. Therapeutic Advances in Psychopharmacology
148. Translational Psychiatry
149. Verhaltenstherapie
150. World Journal of Biological Psychiatry
151. World Journal of Psychiatry
152. World Psychiatry
153. Zeitschrift für Psychosomatische Medizin und Psychotherapie

<a id="scie-psychology"></a>

### Psychology

期刊数：80

1. Advances in Methods and Practices in Psychological Science
2. Anales de Psicologia
3. Annales Medico-Psychologiques
4. Annual Review of Clinical Psychology
5. Annual Review of Psychology
6. Applied Neuropsychology-Adult
7. Applied Neuropsychology-Child
8. Archives of Clinical Neuropsychology
9. Attention Perception & Psychophysics
10. Biological Psychology
11. Biopsychosocial Science and Medicine
12. Clinical Child Psychology and Psychiatry
13. Clinical EEG and Neuroscience
14. Clinical Neuropsychologist
15. Clinical Psychological Science
16. Clinical Psychologist
17. Cognitive Neuropsychology
18. Cognitive Psychology
19. Depression and Anxiety
20. Developmental Neuropsychology
21. Developmental Psychobiology
22. Eating Disorders
23. Ergonomics
24. Experimental Aging Research
25. Frontiers in Human Neuroscience
26. Geriatrie et Psychologie Neuropsychiatrie du Vieillissement
27. Health Psychology
28. Human Factors
29. Human Movement Science
30. Human Psychopharmacology-Clinical and Experimental
31. International Journal of Eating Disorders
32. International Journal of Psychophysiology
33. International Journal of Sport Psychology
34. International Psychogeriatrics
35. Journal of Applied Sport Psychology
36. Journal of Child Psychology and Psychiatry
37. Journal of Clinical and Experimental Neuropsychology
38. Journal of Comparative Psychology
39. Journal of Experimental Psychology-Animal Learning and Cognition
40. Journal of Experimental Psychology-Human Perception and Performance
41. Journal of Experimental Psychology-Learning Memory and Cognition
42. Journal of Genetic Psychology
43. Journal of Memory and Language
44. Journal of Motor Behavior
45. Journal of Neuropsychology
46. Journal of Sport & Exercise Psychology
47. Journal of Studies on Alcohol and Drugs
48. Journal of the Academy of Consultation-Liaison Psychiatry
49. Journal of the International Neuropsychological Society
50. Journals of Gerontology Series B-Psychological Sciences and Social Sciences
51. Multisensory Research
52. Neurobiology of Learning and Memory
53. Neurocase
54. Neuropsychobiology
55. Neuropsychological Rehabilitation
56. Neuropsychology
57. Perception
58. Pratiques Psychologiques
59. Psycho-Oncologie
60. Psycho-Oncology
61. Psychological Bulletin
62. Psychological Medicine
63. Psychological Review
64. Psychology and Psychotherapy-Theory Research and Practice
65. Psychology of Sexual Orientation and Gender Diversity
66. Psychology of Sport and Exercise
67. Psychophysiology
68. Psychotherapy and Psychosomatics
69. Quarterly Journal of Experimental Psychology
70. Research Quarterly for Exercise and Sport
71. Social Cognitive and Affective Neuroscience
72. Social Neuroscience
73. Spanish Journal of Psychology
74. Sport Psychologist
75. Stress and Health
76. Substance Use & Misuse
77. Travail Humain
78. Vision Research
79. Zeitschrift für Neuropsychologie
80. Zeitschrift für Psychosomatische Medizin und Psychotherapie

<a id="scie-public-environmental-occupational-health"></a>

### Public, Environmental & Occupational Health

期刊数：208

1. Aerospace Medicine and Human Performance
2. AJAR-African Journal of AIDS Research
3. American Journal of Epidemiology
4. American Journal of Industrial Medicine
5. American Journal of Infection Control
6. American Journal of Preventive Medicine
7. American Journal of Public Health
8. American Journal of Tropical Medicine and Hygiene
9. Anales del Sistema Sanitario de Navarra
10. Annali dell Istituto Superiore di Sanita
11. Annals of Agricultural and Environmental Medicine
12. Annals of Epidemiology
13. Annals of Global Health
14. Annals of Human Biology
15. Annals of Work Exposures and Health
16. Annual Review of Public Health
17. Antimicrobial Resistance and Infection Control
18. Archives des Maladies Professionnelles et de l Environnement
19. Archives of Environmental & Occupational Health
20. Archives of Public Health
21. Arhiv za Higijenu Rada i Toksikologiju-Archives of Industrial Hygiene and Toxicology
22. Asia-Pacific Journal of Public Health
23. Asian Pacific Journal of Tropical Medicine
24. Australian and New Zealand Journal of Public Health
25. Australian Journal of Primary Health
26. Australian Journal of Rural Health
27. Biomedical and Environmental Sciences
28. BMC Public Health
29. BMJ Global Health
30. Bulletin of the World Health Organization
31. Bundesgesundheitsblatt-Gesundheitsforschung-Gesundheitsschutz
32. Cadernos de Saude Publica
33. Cancer Causes & Control
34. Cancer Epidemiology
35. Cancer Epidemiology Biomarkers & Prevention
36. Central European Journal of Public Health
37. China CDC Weekly
38. Chronic Illness
39. Clinical Epidemiology
40. Community Dentistry and Oral Epidemiology
41. Conflict and Health
42. Current Environmental Health Reports
43. Current Epidemiology Reports
44. Current Pollution Reports
45. Digital Health
46. Disability and Health Journal
47. Disaster Medicine and Public Health Preparedness
48. Diving and Hyperbaric Medicine
49. Drug Safety
50. Eastern Mediterranean Health Journal
51. Economics & Human Biology
52. Environmental Geochemistry and Health
53. Environmental Health
54. Environmental Health and Preventive Medicine
55. Environmental Health Perspectives
56. Environmental Research
57. Epidemiologia & Prevenzione
58. Epidemiologic Reviews
59. Epidemiology
60. Epidemiology & Infection
61. Epidemiology and Health
62. Ethiopian Journal of Health Development
63. Ethnicity & Disease
64. Ethnicity & Health
65. European Journal of Contraception and Reproductive Health Care
66. European Journal of Epidemiology
67. European Journal of Public Health
68. Evolution Medicine and Public Health
69. Families Systems & Health
70. Fluoride
71. Frontiers in Public Health
72. Gaceta Sanitaria
73. GeoHealth
74. Geospatial Health
75. Global Health Action
76. Global Health-Science and Practice
77. Globalization and Health
78. Health & Place
79. Health Expectations
80. Health Physics
81. Health Promotion and Chronic Disease Prevention in Canada-Research Policy and Practice
82. Health Promotion International
83. Health Reports
84. High Altitude Medicine & Biology
85. Indian Journal of Public Health
86. Indoor Air
87. Indoor and Built Environment
88. Industrial Health
89. Infection Control & Hospital Epidemiology
90. Injury Epidemiology
91. Injury Prevention
92. International Archives of Occupational and Environmental Health
93. International Health
94. International Journal of Circumpolar Health
95. International Journal of Environmental Health Research
96. International Journal of Epidemiology
97. International Journal of Health Geographics
98. International Journal of Hygiene and Environmental Health
99. International Journal of Occupational Medicine and Environmental Health
100. International Journal of Public Health
101. International Journal of Technology Assessment in Health Care
102. International Journal of Transgender Health
103. Iranian Journal of Public Health
104. JAMA Health Forum
105. JANAC-Journal of the Association of Nurses in AIDS Care
106. JMIR Public Health and Surveillance
107. JMIR Serious Games
108. Journal of Adolescent Health
109. Journal of Agromedicine
110. Journal of Arthropod-Borne Diseases
111. Journal of Behavioral Health Services & Research
112. Journal of Cancer Education
113. Journal of Clinical Epidemiology
114. Journal of Developmental Origins of Health and Disease
115. Journal of Environmental Health
116. Journal of Environmental Science and Health Part B-Pesticides Food Contaminants and Agricultural Wastes
117. Journal of Epidemiology
118. Journal of Epidemiology and Community Health
119. Journal of Epidemiology and Global Health
120. Journal of Epidemiology and Population Health
121. Journal of Exposure Science and Environmental Epidemiology
122. Journal of Global Health
123. Journal of Health Population and Nutrition
124. Journal of Hospital Infection
125. Journal of Infection and Public Health
126. Journal of Medical Screening
127. Journal of Mens Health
128. Journal of Occupational and Environmental Hygiene
129. Journal of Occupational and Environmental Medicine
130. Journal of Occupational Health
131. Journal of Occupational Medicine and Toxicology
132. Journal of Public Health
133. Journal of Public Health Dentistry
134. Journal of Public Health Policy
135. Journal of Radiological Protection
136. Journal of Rural Health
137. Journal of School Health
138. Journal of Toxicology and Environmental Health-Part A-Current Issues
139. Journal of Toxicology and Environmental Health-Part B-Critical Reviews
140. Journal of Travel Medicine
141. Journal of Tropical Medicine
142. Journal of Urban Health-Bulletin of the New York Academy of Medicine
143. Journal of Womens Health
144. Lancet Global Health
145. Lancet Planetary Health
146. Lancet Public Health
147. Lancet Regional Health-Europe
148. Lancet Regional Health-Western Pacific
149. LGBT Health
150. Malawi Medical Journal
151. Medical Care
152. Medicina del Lavoro
153. Medycyna Pracy-Workers Health and Safety
154. MMWR Recommendations and Reports
155. MMWR Surveillance Summaries
156. MMWR-Morbidity and Mortality Weekly Report
157. Neuroepidemiology
158. Nicotine & Tobacco Research
159. Noise & Health
160. Occupational and Environmental Medicine
161. Occupational Medicine-Oxford
162. One Health
163. Paediatric and Perinatal Epidemiology
164. Palliative Medicine
165. Pathogens and Global Health
166. Patient Education and Counseling
167. Pharmacoepidemiology and Drug Safety
168. Prehospital Emergency Care
169. Preventing Chronic Disease
170. Preventive Medicine
171. Preventive Medicine Reports
172. Psychiatric Services
173. Psychology Health & Medicine
174. Public Health
175. Public Health Ethics
176. Public Health Genomics
177. Public Health Nursing
178. Public Health Nutrition
179. Public Health Reports
180. Puerto Rico Health Sciences Journal
181. Quality of Life Research
182. Radiation Protection Dosimetry
183. Radioprotection
184. Reproductive Health
185. Reviews on Environmental Health
186. Revista de Saude Publica
187. Rural and Remote Health
188. Safety and Health at Work
189. Sante Publique
190. Scandinavian Journal of Public Health
191. Scandinavian Journal of Work Environment & Health
192. Sexual Health
193. Social Science & Medicine
194. Southeast Asian Journal of Tropical Medicine and Public Health
195. SSM-Population Health
196. Statistics in Medicine
197. Tobacco Control
198. Tobacco Induced Diseases
199. Toxicology and Industrial Health
200. Traffic Injury Prevention
201. Transactions of the Royal Society of Tropical Medicine and Hygiene
202. Transgender Health
203. Translational Behavioral Medicine
204. Travel Medicine and Infectious Disease
205. Tropical Doctor
206. Tropical Medicine & International Health
207. Vector-Borne and Zoonotic Diseases
208. Wilderness & Environmental Medicine

<a id="scie-quantum-science-technology"></a>

### Quantum Science & Technology

期刊数：18

1. Advanced Quantum Technologies
2. Classical and Quantum Gravity
3. EPJ Quantum Technology
4. IEEE Journal of Quantum Electronics
5. IEEE Journal of Selected Topics in Quantum Electronics
6. Infinite Dimensional Analysis Quantum Probability and Related Topics
7. International Journal of Quantum Chemistry
8. International Journal of Quantum Information
9. Npj Quantum Information
10. Npj Quantum Materials
11. Optical and Quantum Electronics
12. Progress in Quantum Electronics
13. PRX Quantum
14. Quantum
15. Quantum Information & Computation
16. Quantum Information Processing
17. Quantum Science and Technology
18. Quantum Topology

<a id="scie-radiology-nuclear-medicine-medical-imaging"></a>

### Radiology, Nuclear Medicine & Medical Imaging

期刊数：136

1. Abdominal Radiology
2. Academic Radiology
3. Acta Radiologica
4. American Journal of Neuroradiology
5. American Journal of Roentgenology
6. Annals of Nuclear Medicine
7. Applied Radiation and Isotopes
8. Biomedical Optics Express
9. BMC Medical Imaging
10. Brachytherapy
11. British Journal of Radiology
12. Canadian Association of Radiologists Journal-Journal de l Association Canadienne des Radiologistes
13. Cancer Biotherapy and Radiopharmaceuticals
14. Cancer Imaging
15. Cancer Radiotherapie
16. CardioVascular and Interventional Radiology
17. Circulation-Cardiovascular Imaging
18. Clinical and Translational Imaging
19. Clinical and Translational Radiation Oncology
20. Clinical Imaging
21. Clinical Neuroradiology
22. Clinical Nuclear Medicine
23. Clinical Radiology
24. Computerized Medical Imaging and Graphics
25. Concepts in Magnetic Resonance Part A
26. Current Medical Imaging
27. Current Radiopharmaceuticals
28. Dentomaxillofacial Radiology
29. Diagnostic and Interventional Imaging
30. Diagnostic and Interventional Radiology
31. Dose-Response
32. EJNMMI Physics
33. EJNMMI Research
34. European Heart Journal-Cardiovascular Imaging
35. European Journal of Nuclear Medicine and Molecular Imaging
36. European Journal of Radiology
37. European Radiology
38. Health Physics
39. Hellenic Journal of Nuclear Medicine
40. Human Brain Mapping
41. IEEE Transactions on Medical Imaging
42. Insights into Imaging
43. International Journal of Cardiovascular Imaging
44. International Journal of Computer Assisted Radiology and Surgery
45. International Journal of Hyperthermia
46. International Journal of Radiation Biology
47. International Journal of Radiation Oncology Biology Physics
48. International Journal of Radiation Research
49. Interventional Neuroradiology
50. Investigative Radiology
51. Iranian Journal of Radiology
52. JACC-Cardiovascular Imaging
53. Japanese Journal of Radiology
54. Journal of Applied Clinical Medical Physics
55. Journal of Biomedical Optics
56. Journal of Cardiovascular Computed Tomography
57. Journal of Cardiovascular Magnetic Resonance
58. Journal of Clinical Ultrasound
59. Journal of Computer Assisted Tomography
60. Journal of Contemporary Brachytherapy
61. Journal of Imaging Informatics in Medicine
62. Journal of Innovative Optical Health Sciences
63. Journal of Magnetic Resonance Imaging
64. Journal of Medical Imaging and Radiation Oncology
65. Journal of Medical Ultrasonics
66. Journal of Neuroimaging
67. Journal of Neuroradiology
68. Journal of Nuclear Cardiology
69. Journal of Nuclear Medicine
70. Journal of Radiation Research
71. Journal of Radiological Protection
72. Journal of the American College of Radiology
73. Journal of the Belgian Society of Radiology
74. Journal of Thoracic Imaging
75. Journal of Ultrasound in Medicine
76. Journal of Vascular and Interventional Radiology
77. Korean Journal of Radiology
78. Magnetic Resonance Imaging
79. Magnetic Resonance Imaging Clinics of North America
80. Magnetic Resonance in Medical Sciences
81. Magnetic Resonance in Medicine
82. Magnetic Resonance Materials in Physics Biology and Medicine
83. Medical Dosimetry
84. Medical Image Analysis
85. Medical Physics
86. Medical Ultrasonography
87. Molecular Imaging
88. Molecular Imaging and Biology
89. NeuroImage
90. Neuroimaging Clinics of North America
91. Neuroradiology
92. NMR in Biomedicine
93. Nuclear Medicine and Biology
94. Nuclear Medicine Communications
95. Nuklearmedizin-Nuclear Medicine
96. Pediatric Radiology
97. Photoacoustics
98. Physica Medica-European Journal of Medical Physics
99. Physical and Engineering Sciences in Medicine
100. Physics in Medicine and Biology
101. Practical Radiation Oncology
102. Quantitative Imaging in Medicine and Surgery
103. Quarterly Journal of Nuclear Medicine and Molecular Imaging
104. Radiation and Environmental Biophysics
105. Radiation Oncology
106. Radiation Protection Dosimetry
107. Radiation Research
108. Radiographics
109. Radiologia Medica
110. Radiologic Clinics of North America
111. Radiologie
112. Radiology
113. Radiology and Oncology
114. Radiology-Artificial Intelligence
115. Radioprotection
116. Radiotherapy and Oncology
117. Revista Espanola de Medicina Nuclear e Imagen Molecular
118. RöFo-Fortschritte auf dem Gebiet der Rontgenstrahlen und der Bildgebenden Verfahren
119. Seminars in Interventional Radiology
120. Seminars in Musculoskeletal Radiology
121. Seminars in Nuclear Medicine
122. Seminars in Radiation Oncology
123. Seminars in Roentgenology
124. Seminars in Ultrasound CT and MRI
125. Skeletal Radiology
126. Strahlentherapie und Onkologie
127. Surgical and Radiologic Anatomy
128. Tomography
129. Ultraschall in der Medizin
130. Ultrasonic Imaging
131. Ultrasonics
132. Ultrasonography
133. Ultrasound in Medicine and Biology
134. Ultrasound in Obstetrics & Gynecology
135. Ultrasound Quarterly
136. Zeitschrift für Medizinische Physik

<a id="scie-rehabilitation"></a>

### Rehabilitation

期刊数：68

1. Adapted Physical Activity Quarterly
2. American Journal of Physical Medicine & Rehabilitation
3. American Journal of Speech-Language Pathology
4. Annals of Physical and Rehabilitation Medicine
5. Aphasiology
6. Archives of Physical Medicine and Rehabilitation
7. Australian Occupational Therapy Journal
8. BMC Sports Science Medicine and Rehabilitation
9. Brain Impairment
10. Brain Injury
11. Brazilian Journal of Physical Therapy
12. British Journal of Occupational Therapy
13. Canadian Journal of Occupational Therapy-Revue Canadienne d Ergotherapie
14. Chiropractic & Manual Therapies
15. Clinical Linguistics & Phonetics
16. Clinical Rehabilitation
17. Developmental Neurorehabilitation
18. Disability and Health Journal
19. Disability and Rehabilitation
20. European Journal of Cancer Care
21. European Journal of Physical and Rehabilitation Medicine
22. Folia Phoniatrica et Logopaedica
23. Geriatric Orthopaedic Surgery & Rehabilitation
24. Hong Kong Journal of Occupational Therapy
25. IEEE Transactions on Neural Systems and Rehabilitation Engineering
26. International Journal of Language & Communication Disorders
27. International Journal of Osteopathic Medicine
28. International Journal of Rehabilitation Research
29. International Journal of Speech-Language Pathology
30. Journal of Back and Musculoskeletal Rehabilitation
31. Journal of Communication Disorders
32. Journal of Electromyography and Kinesiology
33. Journal of Fluency Disorders
34. Journal of Geriatric Physical Therapy
35. Journal of Hand Therapy
36. Journal of Head Trauma Rehabilitation
37. Journal of Manipulative and Physiological Therapeutics
38. Journal of NeuroEngineering and Rehabilitation
39. Journal of Neurologic Physical Therapy
40. Journal of Orthopaedic & Sports Physical Therapy
41. Journal of Physiotherapy
42. Journal of Rehabilitation Medicine
43. Journal of Speech Language and Hearing Research
44. Journal of Sport Rehabilitation
45. Kinesiology
46. Musculoskeletal Science and Practice
47. NeuroRehabilitation
48. Neurorehabilitation and Neural Repair
49. Occupational Therapy International
50. Pediatric Physical Therapy
51. Physical & Occupational Therapy in Pediatrics
52. Physical Medicine and Rehabilitation Clinics of North America
53. Physical Therapy
54. Physical Therapy in Sport
55. Physikalische Medizin Rehabilitationsmedizin Kurortmedizin
56. Physiotherapy
57. Physiotherapy Canada
58. Physiotherapy Theory and Practice
59. Pm&R
60. Prosthetics and Orthotics International
61. Rehabilitation
62. Rehabilitation Nursing
63. Scandinavian Journal of Occupational Therapy
64. Seminars in Speech and Language
65. Spinal Cord
66. Supportive Care in Cancer
67. Topics in Stroke Rehabilitation
68. Turkish Journal of Physical Medicine and Rehabilitation

<a id="scie-remote-sensing"></a>

### Remote Sensing

期刊数：36

1. Canadian Journal of Remote Sensing
2. Drones
3. Egyptian Journal of Remote Sensing and Space Sciences
4. European Journal of Remote Sensing
5. Geo-Spatial Information Science
6. Geocarto International
7. Geomatics Natural Hazards & Risk
8. GIScience & Remote Sensing
9. GPS Solutions
10. IEEE Geoscience and Remote Sensing Letters
11. IEEE Geoscience and Remote Sensing Magazine
12. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing
13. IEEE Transactions on Geoscience and Remote Sensing
14. International Journal of Applied Earth Observation and Geoinformation
15. International Journal of Digital Earth
16. International Journal of Remote Sensing
17. ISPRS International Journal of Geo-Information
18. ISPRS Journal of Photogrammetry and Remote Sensing
19. Journal of Applied Remote Sensing
20. Journal of Geodesy
21. Journal of Spatial Science
22. Journal of the Indian Society of Remote Sensing
23. Marine Geodesy
24. Navigation-Journal of the Institute of Navigation
25. PFG-Journal of Photogrammetry Remote Sensing and Geoinformation Science
26. Photogrammetric Engineering and Remote Sensing
27. Photogrammetric Record
28. Plant Phenomics
29. Radio Science
30. Remote Sensing
31. Remote Sensing in Ecology and Conservation
32. Remote Sensing Letters
33. Remote Sensing of Environment
34. Satellite Navigation
35. Spatial Statistics
36. Survey Review

<a id="scie-reproductive-biology"></a>

### Reproductive Biology

期刊数：31

1. American Journal of Reproductive Immunology
2. Animal Reproduction Science
3. Biology of Reproduction
4. European Journal of Obstetrics & Gynecology and Reproductive Biology
5. Fertility and Sterility
6. Human Fertility
7. Human Reproduction
8. Human Reproduction Open
9. Human Reproduction Update
10. Invertebrate Reproduction & Development
11. Journal of Assisted Reproduction and Genetics
12. Journal of Ovarian Research
13. Journal of Reproduction and Development
14. Journal of Reproductive Immunology
15. Molecular Human Reproduction
16. Molecular Reproduction and Development
17. Placenta
18. Plant Reproduction
19. Reproduction
20. Reproduction Fertility and Development
21. Reproduction in Domestic Animals
22. Reproductive Biology
23. Reproductive Biology and Endocrinology
24. Reproductive BioMedicine Online
25. Reproductive Medicine and Biology
26. Reproductive Sciences
27. Reproductive Toxicology
28. Seminars in Reproductive Medicine
29. Systems Biology in Reproductive Medicine
30. Theriogenology
31. Zygote

<a id="scie-respiratory-system"></a>

### Respiratory System

期刊数：66

1. American Journal of Physiology-Lung Cellular and Molecular Physiology
2. American Journal of Respiratory and Critical Care Medicine
3. American Journal of Respiratory Cell and Molecular Biology
4. Annals of the American Thoracic Society
5. Annals of Thoracic Medicine
6. Annals of Thoracic Surgery
7. Archivos de Bronconeumologia
8. BMC Pulmonary Medicine
9. BMJ Open Respiratory Research
10. Canadian Respiratory Journal
11. Chest
12. Chronic Obstructive Pulmonary Diseases-Journal of the COPD Foundation
13. Chronic Respiratory Disease
14. Clinical Respiratory Journal
15. Clinics in Chest Medicine
16. COPD-Journal of Chronic Obstructive Pulmonary Disease
17. Current Opinion in Pulmonary Medicine
18. ERJ Open Research
19. European Journal of Cardio-Thoracic Surgery
20. European Respiratory Journal
21. European Respiratory Review
22. Experimental Lung Research
23. Expert Review of Respiratory Medicine
24. Heart & Lung
25. Interdisciplinary CardioVascular and Thoracic Surgery
26. International Journal of Chronic Obstructive Pulmonary Disease
27. International Journal of Tuberculosis and Lung Disease
28. Jornal Brasileiro de Pneumologia
29. Journal of Aerosol Medicine and Pulmonary Drug Delivery
30. Journal of Asthma
31. Journal of Asthma and Allergy
32. Journal of Breath Research
33. Journal of Cardiothoracic and Vascular Anesthesia
34. Journal of Cystic Fibrosis
35. Journal of Heart and Lung Transplantation
36. Journal of Thoracic and Cardiovascular Surgery
37. Journal of Thoracic Disease
38. Journal of Thoracic Oncology
39. Lancet Respiratory Medicine
40. Lung
41. Lung Cancer
42. Npj Primary Care Respiratory Medicine
43. Paediatric Respiratory Reviews
44. Pediatric Allergy Immunology and Pulmonology
45. Pediatric Pulmonology
46. Pulmonary Circulation
47. Pulmonary Pharmacology & Therapeutics
48. Pulmonology
49. Respiration
50. Respiratory Care
51. Respiratory Medicine
52. Respiratory Medicine and Research
53. Respiratory Physiology & Neurobiology
54. Respiratory Research
55. Respirology
56. Revue des Maladies Respiratoires
57. Sarcoidosis Vasculitis and Diffuse Lung Diseases
58. Seminars in Respiratory and Critical Care Medicine
59. Sleep and Breathing
60. Therapeutic Advances in Respiratory Disease
61. Thoracic and Cardiovascular Surgeon
62. Thoracic Cancer
63. Thoracic Surgery Clinics
64. Thorax
65. Translational Lung Cancer Research
66. Tuberculosis

<a id="scie-rheumatology"></a>

### Rheumatology

期刊数：34

1. Advances in Rheumatology
2. Aktuelle Rheumatologie
3. Annals of the Rheumatic Diseases
4. Archives of Rheumatology
5. ARP Rheumatology
6. Arthritis & Rheumatology
7. Arthritis Care & Research
8. Arthritis Research & Therapy
9. Best Practice & Research in Clinical Rheumatology
10. BMC Musculoskeletal Disorders
11. Clinical and Experimental Rheumatology
12. Clinical Rheumatology
13. Current Opinion in Rheumatology
14. Current Rheumatology Reports
15. International Journal of Rheumatic Diseases
16. JCR-Journal of Clinical Rheumatology
17. Joint Bone Spine
18. Journal of Rheumatology
19. Lancet Rheumatology
20. Lupus
21. Lupus Science & Medicine
22. Modern Rheumatology
23. Nature Reviews Rheumatology
24. Osteoarthritis and Cartilage
25. Pediatric Rheumatology
26. Rheumatic Disease Clinics of North America
27. Rheumatology
28. Rheumatology and Therapy
29. Rheumatology International
30. RMD Open
31. Scandinavian Journal of Rheumatology
32. Seminars in Arthritis and Rheumatism
33. Therapeutic Advances in Musculoskeletal Disease
34. Zeitschrift für Rheumatologie

<a id="scie-robotics"></a>

### Robotics

期刊数：31

1. Advanced Intelligent Systems
2. Advanced Robotics
3. Annual Review of Control Robotics and Autonomous Systems
4. Applied Bionics and Biomechanics
5. Autonomous Robots
6. Bioinspiration & Biomimetics
7. Cyborg and Bionic Systems
8. Frontiers in Neurorobotics
9. IEEE Robotics & Automation Magazine
10. IEEE Robotics and Automation Letters
11. IEEE Transactions on Cognitive and Developmental Systems
12. IEEE Transactions on Robotics
13. Industrial Robot-the International Journal of Robotics Research and Application
14. Intelligent Service Robotics
15. International Journal of Advanced Robotic Systems
16. International Journal of Humanoid Robotics
17. International Journal of Robotics & Automation
18. International Journal of Robotics Research
19. International Journal of Social Robotics
20. Journal of Bionic Engineering
21. Journal of Field Robotics
22. Journal of Intelligent & Robotic Systems
23. Journal of Mechanisms and Robotics-Transactions of the ASME
24. Mechatronics
25. Revista Iberoamericana de Automatica e Informatica Industrial
26. Robotica
27. Robotics and Autonomous Systems
28. Robotics and Computer-Integrated Manufacturing
29. Science Robotics
30. Soft Robotics
31. Swarm Intelligence

<a id="scie-soil-science"></a>

### Soil Science

期刊数：38

1. Acta Agriculturae Scandinavica Section B-Soil and Plant Science
2. Agrochimica
3. Applied Soil Ecology
4. Archives of Agronomy and Soil Science
5. Arid Land Research and Management
6. Biochar
7. Biology and Fertility of Soils
8. Canadian Journal of Soil Science
9. Catena
10. Clays and Clay Minerals
11. Communications in Soil Science and Plant Analysis
12. Compost Science & Utilization
13. Eurasian Soil Science
14. European Journal of Soil Biology
15. European Journal of Soil Science
16. Geoderma
17. Geoderma Regional
18. International Soil and Water Conservation Research
19. Journal of Plant Nutrition and Soil Science
20. Journal of Soil and Water Conservation
21. Journal of Soil Science and Plant Nutrition
22. Journal of Soils and Sediments
23. Land Degradation & Development
24. Nutrient Cycling in Agroecosystems
25. Pedobiologia
26. Pedosphere
27. Plant and Soil
28. Revista Brasileira de Ciencia do Solo
29. Rhizosphere
30. Soil
31. Soil & Tillage Research
32. Soil and Water Research
33. Soil Biology & Biochemistry
34. Soil Research
35. Soil Science and Plant Nutrition
36. Soil Science Society of America Journal
37. Soil Use and Management
38. Vadose Zone Journal

<a id="scie-spectroscopy"></a>

### Spectroscopy

期刊数：40

1. Analytical Methods
2. Annual Review of Analytical Chemistry
3. Applied Magnetic Resonance
4. Applied Spectroscopy
5. Applied Spectroscopy Reviews
6. Atomic Spectroscopy
7. Biomolecular NMR Assignments
8. Concepts in Magnetic Resonance Part A
9. European Journal of Mass Spectrometry
10. International Journal of Mass Spectrometry
11. Journal of Analytical Atomic Spectrometry
12. Journal of Applied Spectroscopy
13. Journal of Biomolecular NMR
14. Journal of Chemical Crystallography
15. Journal of Cultural Heritage
16. Journal of Electron Spectroscopy and Related Phenomena
17. Journal of Magnetic Resonance
18. Journal of Mass Spectrometry
19. Journal of Molecular Spectroscopy
20. Journal of Near Infrared Spectroscopy
21. Journal of Quantitative Spectroscopy & Radiative Transfer
22. Journal of Raman Spectroscopy
23. Journal of Spectroscopy
24. Journal of the American Society for Mass Spectrometry
25. Magnetic Resonance in Chemistry
26. Mass Spectrometry Reviews
27. NMR in Biomedicine
28. Npj Heritage Science
29. Optics and Spectroscopy
30. Progress in Nuclear Magnetic Resonance Spectroscopy
31. Rapid Communications in Mass Spectrometry
32. Solid State Nuclear Magnetic Resonance
33. Spectrochimica Acta Part A-Molecular and Biomolecular Spectroscopy
34. Spectrochimica Acta Part B-Atomic Spectroscopy
35. Spectroscopy
36. Spectroscopy and Spectral Analysis
37. Spectroscopy Letters
38. Studies in Conservation
39. Vibrational Spectroscopy
40. X-Ray Spectrometry

<a id="scie-sport-sciences"></a>

### Sport Sciences

期刊数：86

1. ACSMS Health & Fitness Journal
2. Adapted Physical Activity Quarterly
3. American Journal of Physical Medicine & Rehabilitation
4. American Journal of Sports Medicine
5. Applied Physiology Nutrition and Metabolism
6. Archives of Budo-Journal of Innovative Agonology
7. Archives of Physical Medicine and Rehabilitation
8. Arthroscopy-the Journal of Arthroscopic and Related Surgery
9. Biology of Sport
10. BMC Sports Science Medicine and Rehabilitation
11. British Journal of Sports Medicine
12. Clinical Biomechanics
13. Clinical Journal of Sport Medicine
14. Clinics in Sports Medicine
15. Current Sports Medicine Reports
16. European Journal of Applied Physiology
17. European Journal of Sport Science
18. Exercise and Sport Sciences Reviews
19. Exercise Immunology Review
20. Gait & Posture
21. High Altitude Medicine & Biology
22. Human Movement Science
23. International Journal of Performance Analysis in Sport
24. International Journal of Sport Nutrition and Exercise Metabolism
25. International Journal of Sport Psychology
26. International Journal of Sports Medicine
27. International Journal of Sports Physiology and Performance
28. Isokinetics and Exercise Science
29. Journal of Aging and Physical Activity
30. Journal of Applied Biomechanics
31. Journal of Applied Physiology
32. Journal of Applied Sport Psychology
33. Journal of Athletic Training
34. Journal of Electromyography and Kinesiology
35. Journal of Exercise Science & Fitness
36. Journal of Human Kinetics
37. Journal of Motor Behavior
38. Journal of Orthopaedic & Sports Physical Therapy
39. Journal of Orthopaedic Trauma
40. Journal of Rehabilitation Medicine
41. Journal of Science and Medicine in Sport
42. Journal of Shoulder and Elbow Surgery
43. Journal of Sport & Exercise Psychology
44. Journal of Sport and Health Science
45. Journal of Sport Management
46. Journal of Sport Rehabilitation
47. Journal of Sports Medicine and Physical Fitness
48. Journal of Sports Science and Medicine
49. Journal of Sports Sciences
50. Journal of Strength and Conditioning Research
51. Journal of Teaching in Physical Education
52. Journal of the International Society of Sports Nutrition
53. Kinesiology
54. Knee
55. Knee Surgery Sports Traumatology Arthroscopy
56. Measurement in Physical Education and Exercise Science
57. Medicina Dello Sport
58. Medicine & Science in Sports & Exercise
59. Motor Control
60. Operative Techniques in Sports Medicine
61. Orthopaedic Journal of Sports Medicine
62. Pediatric Exercise Science
63. Physical Therapy in Sport
64. Physician and Sportsmedicine
65. Physikalische Medizin Rehabilitationsmedizin Kurortmedizin
66. Pm&R
67. Proceedings of the Institution of Mechanical Engineers Part P-Journal of Sports Engineering and Technology
68. Psychology of Sport and Exercise
69. Qualitative Research in Sport Exercise and Health
70. Quest
71. Research in Sports Medicine
72. Research Quarterly for Exercise and Sport
73. Scandinavian Journal of Medicine & Science in Sports
74. Science & Sports
75. Science and Medicine in Football
76. Sociology of Sport Journal
77. Sport Education and Society
78. Sport Psychologist
79. Sports Biomechanics
80. Sports Health-A Multidisciplinary Approach
81. Sports Medicine
82. Sports Medicine and Arthroscopy Review
83. Sports Medicine-Open
84. Sportverletzung-Sportschaden
85. Strength and Conditioning Journal
86. Wilderness & Environmental Medicine

<a id="scie-statistics-probability"></a>

### Statistics & Probability

期刊数：126

1. Advances in Applied Probability
2. Advances in Data Analysis and Classification
3. Alea-Latin American Journal of Probability and Mathematical Statistics
4. American Statistician
5. Annales de l Institut Henri Poincare-Probabilites et Statistiques
6. Annals of Applied Probability
7. Annals of Applied Statistics
8. Annals of Probability
9. Annals of Statistics
10. Annals of the Institute of Statistical Mathematics
11. Annual Review of Statistics and Its Application
12. Applied Stochastic Models in Business and Industry
13. AStA-Advances in Statistical Analysis
14. ASTIN Bulletin-the Journal of the International Actuarial Association
15. Australian & New Zealand Journal of Statistics
16. Bayesian Analysis
17. Bernoulli
18. Biometrical Journal
19. Biometrics
20. Biometrika
21. Biostatistics
22. Brazilian Journal of Probability and Statistics
23. British Journal of Mathematical & Statistical Psychology
24. Canadian Journal of Statistics-Revue Canadienne de Statistique
25. Chemometrics and Intelligent Laboratory Systems
26. Combinatorics Probability and Computing
27. Communications in Statistics-Simulation and Computation
28. Communications in Statistics-Theory and Methods
29. Computational Statistics
30. Computational Statistics & Data Analysis
31. Econometric Reviews
32. Econometric Theory
33. Econometrica
34. Econometrics Journal
35. Electronic Communications in Probability
36. Electronic Journal of Probability
37. Electronic Journal of Statistics
38. Environmental and Ecological Statistics
39. Environmetrics
40. ESAIM-Probability and Statistics
41. Extremes
42. Finance and Stochastics
43. Fuzzy Sets and Systems
44. Hacettepe Journal of Mathematics and Statistics
45. IEEE Transactions on Computational Biology and Bioinformatics
46. Infinite Dimensional Analysis Quantum Probability and Related Topics
47. Insurance Mathematics & Economics
48. International Journal of Biostatistics
49. International Journal of Game Theory
50. International Statistical Review
51. Journal of Agricultural Biological and Environmental Statistics
52. Journal of Applied Probability
53. Journal of Applied Statistics
54. Journal of Biopharmaceutical Statistics
55. Journal of Business & Economic Statistics
56. Journal of Chemometrics
57. Journal of Classification
58. Journal of Computational and Graphical Statistics
59. Journal of Computational Biology
60. Journal of Multivariate Analysis
61. Journal of Nonparametric Statistics
62. Journal of Official Statistics
63. Journal of Quality Technology
64. Journal of Statistical Computation and Simulation
65. Journal of Statistical Planning and Inference
66. Journal of Statistical Software
67. Journal of Survey Statistics and Methodology
68. Journal of the American Statistical Association
69. Journal of the Korean Statistical Society
70. Journal of the Royal Statistical Society Series A-Statistics in Society
71. Journal of the Royal Statistical Society Series B-Statistical Methodology
72. Journal of the Royal Statistical Society Series C-Applied Statistics
73. Journal of Theoretical Probability
74. Journal of Time Series Analysis
75. Law Probability & Risk
76. Lifetime Data Analysis
77. Markov Processes and Related Fields
78. Mathematical Population Studies
79. Methodology and Computing in Applied Probability
80. Metrika
81. Multivariate Behavioral Research
82. Open Systems & Information Dynamics
83. Oxford Bulletin of Economics and Statistics
84. Pharmaceutical Statistics
85. Probabilistic Engineering Mechanics
86. Probability and Mathematical Statistics-Poland
87. Probability in the Engineering and Informational Sciences
88. Probability Theory and Related Fields
89. Quality Engineering
90. Quality Technology and Quantitative Management
91. R Journal
92. Random Matrices-Theory and Applications
93. Revstat-Statistical Journal
94. Scandinavian Actuarial Journal
95. Scandinavian Journal of Statistics
96. Sequential Analysis-Design Methods and Applications
97. Sort-Statistics and Operations Research Transactions
98. Spatial Statistics
99. Stat
100. Stata Journal
101. Statistica Neerlandica
102. Statistica Sinica
103. Statistical Analysis and Data Mining-an ASA Data Science Journal
104. Statistical Applications in Genetics and Molecular Biology
105. Statistical Methods and Applications
106. Statistical Methods in Medical Research
107. Statistical Modelling
108. Statistical Papers
109. Statistical Science
110. Statistics
111. Statistics & Probability Letters
112. Statistics and Computing
113. Statistics in Biopharmaceutical Research
114. Statistics in Medicine
115. Stochastic Analysis and Applications
116. Stochastic Environmental Research and Risk Assessment
117. Stochastic Models
118. Stochastic Processes and Their Applications
119. Stochastics and Dynamics
120. Stochastics and Partial Differential Equations-Analysis and Computations
121. Stochastics-an International Journal of Probability and Stochastic Processes
122. Survey Methodology
123. Technometrics
124. Test
125. Theory of Probability and Its Applications
126. Wiley Interdisciplinary Reviews-Computational Statistics

<a id="scie-substance-abuse"></a>

### Substance Abuse

期刊数：21

1. Addiction
2. Addiction Biology
3. Addiction Science & Clinical Practice
4. Addictive Behaviors
5. Adicciones
6. Alcohol
7. Alcohol and Alcoholism
8. Alcohol-Clinical and Experimental Research
9. American Journal of Drug and Alcohol Abuse
10. Drug and Alcohol Dependence
11. European Addiction Research
12. International Journal of Mental Health and Addiction
13. Journal of Addiction Medicine
14. Journal of Addictions Nursing
15. Journal of Ethnicity in Substance Abuse
16. Journal of Studies on Alcohol and Drugs
17. Nicotine & Tobacco Research
18. Substance Use & Addiction Journal
19. Substance Use & Misuse
20. Tobacco Control
21. Tobacco Induced Diseases

<a id="scie-surgery"></a>

### Surgery

期刊数：212

1. Acta Chirurgica Belgica
2. Acta Cirurgica Brasileira
3. Acta Neurochirurgica
4. Advances in Skin & Wound Care
5. Aesthetic Plastic Surgery
6. Aesthetic Surgery Journal
7. American Journal of Surgery
8. American Journal of Surgical Pathology
9. American Journal of Transplantation
10. American Surgeon
11. Annales de Chirurgie Plastique Esthetique
12. Annali Italiani di Chirurgia
13. Annals of Cardiothoracic Surgery
14. Annals of Plastic Surgery
15. Annals of Surgery
16. Annals of Surgical Oncology
17. Annals of Surgical Treatment and Research
18. Annals of the Royal College of Surgeons of England
19. Annals of Thoracic and Cardiovascular Surgery
20. Annals of Thoracic Surgery
21. Annals of Transplantation
22. Annals of Vascular Surgery
23. ANZ Journal of Surgery
24. Archives of Orthopaedic and Trauma Surgery
25. Arthroscopy-the Journal of Arthroscopic and Related Surgery
26. Asian Journal of Surgery
27. Bariatric Surgical Practice and Patient Care
28. BJS Open
29. BJS-British Journal of Surgery
30. BMC Surgery
31. Bone & Joint Journal
32. Brazilian Journal of Cardiovascular Surgery
33. British Journal of Neurosurgery
34. British Journal of Oral & Maxillofacial Surgery
35. Burns
36. Burns & Trauma
37. Canadian Journal of Surgery
38. Ceska a Slovenska Neurologie a Neurochirurgie
39. Childs Nervous System
40. Chirurgie
41. Cirugia Espanola
42. Cirugia y Cirujanos
43. Cleft Palate Craniofacial Journal
44. Clinical Neurology and Neurosurgery
45. Clinical Orthopaedics and Related Research
46. Clinical Transplantation
47. Clinics in Colon and Rectal Surgery
48. Clinics in Plastic Surgery
49. Colorectal Disease
50. Computer Assisted Surgery
51. Current Problems in Surgery
52. Dermatologic Surgery
53. Digestive Endoscopy
54. Digestive Surgery
55. Diseases of the Colon & Rectum
56. Ejso
57. Endoscopy
58. European Journal of Cardio-Thoracic Surgery
59. European Journal of Pediatric Surgery
60. European Journal of Vascular and Endovascular Surgery
61. European Surgery-Acta Chirurgica Austriaca
62. European Surgical Research
63. Facial Plastic Surgery
64. Facial Plastic Surgery & Aesthetic Medicine
65. Facial Plastic Surgery Clinics of North America
66. Frontiers in Surgery
67. General Thoracic and Cardiovascular Surgery
68. Geriatric Orthopaedic Surgery & Rehabilitation
69. Gland Surgery
70. Hand Surgery & Rehabilitation
71. Handchirurgie Mikrochirurgie Plastische Chirurgie
72. Head and Neck-Journal for the Sciences and Specialties of the Head and Neck
73. Heart Surgery Forum
74. HepatoBiliary Surgery and Nutrition
75. Hernia
76. Hpb
77. HSS Journal
78. Indian Journal of Surgery
79. Injury-International Journal of the Care of the Injured
80. Interdisciplinary CardioVascular and Thoracic Surgery
81. International Journal of Colorectal Disease
82. International Journal of Computer Assisted Radiology and Surgery
83. International Journal of Lower Extremity Wounds
84. International Journal of Medical Robotics and Computer Assisted Surgery
85. International Journal of Oral and Maxillofacial Surgery
86. International Journal of Surgery
87. International Journal of Surgical Pathology
88. International Surgery
89. International Wound Journal
90. JAMA Otolaryngology-Head & Neck Surgery
91. JAMA Surgery
92. Joint Diseases and Related Surgery
93. Journal of Bone and Joint Surgery-American Volume
94. Journal of Burn Care & Research
95. Journal of Cardiac Surgery
96. Journal of Cardiothoracic Surgery
97. Journal of Cardiovascular Surgery
98. Journal of Cataract and Refractive Surgery
99. Journal of Cosmetic and Laser Therapy
100. Journal of Cranio-Maxillofacial Surgery
101. Journal of Craniofacial Surgery
102. Journal of Endovascular Therapy
103. Journal of Foot & Ankle Surgery
104. Journal of Gastrointestinal Surgery
105. Journal of Hand Surgery-American Volume
106. Journal of Hand Surgery-European Volume
107. Journal of Hand Therapy
108. Journal of Heart and Lung Transplantation
109. Journal of Hepato-Biliary-Pancreatic Sciences
110. Journal of Investigative Surgery
111. Journal of Korean Neurosurgical Society
112. Journal of Laparoendoscopic & Advanced Surgical Techniques
113. Journal of Minimal Access Surgery
114. Journal of NeuroInterventional Surgery
115. Journal of Neurological Surgery Part A-Central European Neurosurgery
116. Journal of Neurological Surgery Part B-Skull Base
117. Journal of Neurology Neurosurgery and Psychiatry
118. Journal of Neurosurgery
119. Journal of Neurosurgery-Pediatrics
120. Journal of Neurosurgery-Spine
121. Journal of Neurosurgical Anesthesiology
122. Journal of Neurosurgical Sciences
123. Journal of Orthopaedic Surgery
124. Journal of Pediatric Surgery
125. Journal of Plastic Reconstructive and Aesthetic Surgery
126. Journal of Plastic Surgery and Hand Surgery
127. Journal of Reconstructive Microsurgery
128. Journal of Refractive Surgery
129. Journal of Robotic Surgery
130. Journal of Shoulder and Elbow Surgery
131. Journal of Surgical Education
132. Journal of Surgical Oncology
133. Journal of Surgical Research
134. Journal of the American Academy of Orthopaedic Surgeons
135. Journal of the American College of Surgeons
136. Journal of Thoracic and Cardiovascular Surgery
137. Journal of Trauma and Acute Care Surgery
138. Journal of Vascular Surgery
139. Journal of Vascular Surgery-Venous and Lymphatic Disorders
140. Journal of Visceral Surgery
141. JSLS-Journal of the Society of Laparoendoscopic Surgeons
142. Knee
143. Knee Surgery Sports Traumatology Arthroscopy
144. Langenbecks Archives of Surgery
145. Lasers in Medical Science
146. Lasers in Surgery and Medicine
147. Liver Transplantation
148. Microsurgery
149. Minerva Surgery
150. Minimally Invasive Therapy & Allied Technologies
151. Neurochirurgie
152. Neurocirugia
153. Neurologia Medico-Chirurgica
154. Neurospine
155. Neurosurgery
156. Neurosurgery Clinics of North America
157. Neurosurgical Focus
158. Neurosurgical Review
159. Obesity Surgery
160. Operative Neurosurgery
161. Operative Techniques in Sports Medicine
162. Ophthalmic Plastic and Reconstructive Surgery
163. Ophthalmic Surgery Lasers & Imaging Retina
164. Orthopaedics & Traumatology-Surgery & Research
165. Otolaryngology-Head and Neck Surgery
166. Pediatric Neurosurgery
167. Pediatric Surgery International
168. Perioperative Medicine
169. Photobiomodulation Photomedicine and Laser Surgery
170. Plastic and Reconstructive Surgery
171. Plastic Surgery
172. Progress in Transplantation
173. Scandinavian Journal of Surgery
174. Seminars in Pediatric Surgery
175. Seminars in Plastic Surgery
176. Seminars in Vascular Surgery
177. Shock
178. South African Journal of Surgery
179. Stereotactic and Functional Neurosurgery
180. Surgeon-Journal of the Royal Colleges of Surgeons of Edinburgh and Ireland
181. Surgery
182. Surgery for Obesity and Related Diseases
183. Surgery Today
184. Surgical and Radiologic Anatomy
185. Surgical Clinics of North America
186. Surgical Endoscopy and Other Interventional Techniques
187. Surgical Infections
188. Surgical Innovation
189. Surgical Laparoscopy Endoscopy & Percutaneous Techniques
190. Surgical Oncology Clinics of North America
191. Surgical Oncology-Oxford
192. Techniques in Coloproctology
193. Thoracic and Cardiovascular Surgeon
194. Thoracic Surgery Clinics
195. Transplant International
196. Transplantation
197. Transplantation Proceedings
198. Turk Gogus Kalp Damar Cerrahisi Dergisi-Turkish Journal of Thoracic and Cardiovascular Surgery
199. Turkish Neurosurgery
200. Unfallchirurgie
201. Updates in Surgery
202. Vascular and Endovascular Surgery
203. Videosurgery and Other Miniinvasive Techniques
204. Visceral Medicine
205. World Journal of Emergency Surgery
206. World Journal of Gastrointestinal Surgery
207. World Journal of Surgery
208. World Journal of Surgical Oncology
209. World Neurosurgery
210. Wound Repair and Regeneration
211. Wounds-A Compendium of Clinical Research and Practice
212. Zentralblatt fur Chirurgie

<a id="scie-telecommunications"></a>

### Telecommunications

期刊数：90

1. ACM Transactions on Sensor Networks
2. Ad Hoc & Sensor Wireless Networks
3. Ad Hoc Networks
4. AEU-International Journal of Electronics and Communications
5. Annals of Telecommunications
6. Applied Computational Electromagnetics Society Journal
7. China Communications
8. Computer Communications
9. Computer Networks
10. Digital Communications and Networks
11. ETRI Journal
12. ICT Express
13. IEEE Access
14. IEEE Antennas and Propagation Magazine
15. IEEE Antennas and Wireless Propagation Letters
16. IEEE Communications Letters
17. IEEE Communications Magazine
18. IEEE Communications Surveys and Tutorials
19. IEEE Consumer Electronics Magazine
20. IEEE Internet of Things Journal
21. IEEE Journal on Selected Areas in Communications
22. IEEE Microwave Magazine
23. IEEE Network
24. IEEE Pervasive Computing
25. IEEE Systems Journal
26. IEEE Transactions on Aerospace and Electronic Systems
27. IEEE Transactions on Antennas and Propagation
28. IEEE Transactions on Broadcasting
29. IEEE Transactions on Cognitive Communications and Networking
30. IEEE Transactions on Communications
31. IEEE Transactions on Consumer Electronics
32. IEEE Transactions on Electromagnetic Compatibility
33. IEEE Transactions on Emerging Topics in Computing
34. IEEE Transactions on Green Communications and Networking
35. IEEE Transactions on Microwave Theory and Techniques
36. IEEE Transactions on Mobile Computing
37. IEEE Transactions on Multimedia
38. IEEE Transactions on Networking
39. IEEE Transactions on Signal and Information Processing over Networks
40. IEEE Transactions on Sustainable Computing
41. IEEE Transactions on Vehicular Technology
42. IEEE Transactions on Wireless Communications
43. IEEE Vehicular Technology Magazine
44. IEEE Wireless Communications
45. IEEE Wireless Communications Letters
46. IEICE Transactions on Communications
47. IET Microwaves Antennas & Propagation
48. IET Optoelectronics
49. IET Radar Sonar and Navigation
50. IETE Journal of Research
51. IETE Technical Review
52. International Journal of ad Hoc and Ubiquitous Computing
53. International Journal of Antennas and Propagation
54. International Journal of Communication Systems
55. International Journal of Distributed Sensor Networks
56. International Journal of Microwave and Wireless Technologies
57. International Journal of Network Management
58. International Journal of Satellite Communications and Networking
59. International Journal of Sensor Networks
60. Internet of Things
61. Internet Research
62. IT Professional
63. Journal of Ambient Intelligence and Smart Environments
64. Journal of Communications and Networks
65. Journal of Communications Technology and Electronics
66. Journal of Internet Technology
67. Journal of Lightwave Technology
68. Journal of Network and Systems Management
69. Journal of Optical Communications and Networking
70. Journal on Wireless Communications and Networking
71. KSII Transactions on Internet and Information Systems
72. Microwave Journal
73. Mobile Networks & Applications
74. Nano Communication Networks
75. Navigation-Journal of the Institute of Navigation
76. Optical Fiber Technology
77. Optical Switching and Networking
78. Peer-to-Peer Networking and Applications
79. Pervasive and Mobile Computing
80. Photonic Network Communications
81. Physical Communication
82. Progress in Electromagnetics Research-Pier
83. Radio Science
84. Satellite Navigation
85. Telecommunication Systems
86. Telecommunications Policy
87. Transactions on Emerging Telecommunications Technologies
88. Vehicular Communications
89. Wireless Networks
90. Wireless Personal Communications

<a id="scie-thermodynamics"></a>

### Thermodynamics

期刊数：63

1. Advances in Mechanical Engineering
2. Applied Thermal Engineering
3. Ashrae Journal
4. ASME Journal of Heat and Mass Transfer
5. Building Simulation
6. Calphad-Computer Coupling of Phase Diagrams and Thermochemistry
7. Case Studies in Thermal Engineering
8. Combustion and Flame
9. Combustion Explosion and Shock Waves
10. Combustion Science and Technology
11. Combustion Theory and Modelling
12. Continuum Mechanics and Thermodynamics
13. Cryogenics
14. Energy
15. Energy Conversion and Management
16. Experimental Heat Transfer
17. Experimental Thermal and Fluid Science
18. Flow Turbulence and Combustion
19. Fluid Phase Equilibria
20. Heat and Mass Transfer
21. Heat Transfer Engineering
22. Heat Transfer Research
23. High Temperatures-High Pressures
24. International Communications in Heat and Mass Transfer
25. International Journal of Engine Research
26. International Journal of Exergy
27. International Journal of Green Energy
28. International Journal of Heat and Fluid Flow
29. International Journal of Heat and Mass Transfer
30. International Journal of Low-Carbon Technologies
31. International Journal of Numerical Methods for Heat & Fluid Flow
32. International Journal of Refrigeration
33. International Journal of Spray and Combustion Dynamics
34. International Journal of Thermal Sciences
35. International Journal of Thermophysics
36. Isi Bilimi ve Teknigi Dergisi-Journal of Thermal Science and Technology
37. Journal of Applied Fluid Mechanics
38. Journal of Chemical and Engineering Data
39. Journal of Chemical Thermodynamics
40. Journal of Engineering Thermophysics
41. Journal of Enhanced Heat Transfer
42. Journal of Non-Equilibrium Thermodynamics
43. Journal of Porous Media
44. Journal of Thermal Analysis and Calorimetry
45. Journal of Thermal Science
46. Journal of Thermal Science and Engineering Applications
47. Journal of Thermal Science and Technology
48. Journal of Thermal Stresses
49. Journal of Thermophysics and Heat Transfer
50. Microgravity Science and Technology
51. Nanoscale and Microscale Thermophysical Engineering
52. Numerical Heat Transfer Part A-Applications
53. Numerical Heat Transfer Part B-Fundamentals
54. Proceedings of the Combustion Institute
55. Proceedings of the Institution of Mechanical Engineers Part A-Journal of Power and Energy
56. Progress in Computational Fluid Dynamics
57. Progress in Energy and Combustion Science
58. Propulsion and Power Research
59. Science and Technology for the Built Environment
60. Thermal Science
61. Thermal Science and Engineering Progress
62. Thermochimica Acta
63. Thermophysics and Aeromechanics

<a id="scie-toxicology"></a>

### Toxicology

期刊数：94

1. Alcohol
2. Annual Review of Pharmacology and Toxicology
3. Aquatic Toxicology
4. Archives of Environmental Contamination and Toxicology
5. Archives of Toxicology
6. Arhiv za Higijenu Rada i Toksikologiju-Archives of Industrial Hygiene and Toxicology
7. Basic & Clinical Pharmacology & Toxicology
8. Biomarkers
9. Birth Defects Research
10. BMC Pharmacology & Toxicology
11. Bulletin of Environmental Contamination and Toxicology
12. Cardiovascular Toxicology
13. Cell Biology and Toxicology
14. Chemical Research in Toxicology
15. Chemico-Biological Interactions
16. Clinical Toxicology
17. Comparative Biochemistry and Physiology C-Toxicology & Pharmacology
18. Critical Reviews in Toxicology
19. Cutaneous and Ocular Toxicology
20. DNA Repair
21. Drug and Chemical Toxicology
22. Drug Safety
23. Drugs
24. Ecotoxicology
25. Ecotoxicology and Environmental Safety
26. Environmental and Molecular Mutagenesis
27. Environmental Health Perspectives
28. Environmental Pollutants and Bioavailability
29. Environmental Toxicology
30. Environmental Toxicology and Chemistry
31. Environmental Toxicology and Pharmacology
32. Expert Opinion on Drug Metabolism & Toxicology
33. Fluoride
34. Food Additives & Contaminants Part B-Surveillance
35. Food Additives and Contaminants Part A-Chemistry Analysis Control Exposure & Risk Assessment
36. Food and Agricultural Immunology
37. Food and Chemical Toxicology
38. Forensic Toxicology
39. Genes and Environment
40. Human & Experimental Toxicology
41. Immunopharmacology and Immunotoxicology
42. Industrial Health
43. Inflammopharmacology
44. Inhalation Toxicology
45. Integrated Environmental Assessment and Management
46. International Journal of Toxicology
47. Journal of Analytical Toxicology
48. Journal of Applied Toxicology
49. Journal of Biochemical and Molecular Toxicology
50. Journal of Environmental Pathology Toxicology and Oncology
51. Journal of Environmental Science and Health Part C-Toxicology and Carcinogenesis
52. Journal of Exposure Science and Environmental Epidemiology
53. Journal of Food Safety and Food Quality-Archiv für Lebensmittelhygiene
54. Journal of Immunotoxicology
55. Journal of Medical Toxicology
56. Journal of Pharmacological and Toxicological Methods
57. Journal of Toxicologic Pathology
58. Journal of Toxicological Sciences
59. Journal of Toxicology and Environmental Health-Part A-Current Issues
60. Journal of Toxicology and Environmental Health-Part B-Critical Reviews
61. Journal of Venomous Animals and Toxins Including Tropical Diseases
62. Marine Environmental Research
63. Molecular & Cellular Toxicology
64. Mutagenesis
65. Mutation Research-Fundamental and Molecular Mechanisms of Mutagenesis
66. Mutation Research-Genetic Toxicology and Environmental Mutagenesis
67. Mutation Research-Reviews in Mutation Research
68. Mycotoxin Research
69. Nanotoxicology
70. NeuroToxicology
71. Neurotoxicology and Teratology
72. Particle and Fibre Toxicology
73. Regulatory Toxicology and Pharmacology
74. Reproductive Toxicology
75. Reviews of Environmental Contamination and Toxicology
76. SAR and QSAR in Environmental Research
77. Therapeutic Drug Monitoring
78. Toxicologic Pathology
79. Toxicological and Environmental Chemistry
80. Toxicological Research
81. Toxicological Sciences
82. Toxicology
83. Toxicology and Applied Pharmacology
84. Toxicology and Industrial Health
85. Toxicology in Vitro
86. Toxicology Letters
87. Toxicology Mechanisms and Methods
88. Toxicology Research
89. Toxicon
90. Toxics
91. Toxin Reviews
92. Toxins
93. World Mycotoxin Journal
94. Xenobiotica

<a id="scie-transplantation"></a>

### Transplantation

期刊数：25

1. American Journal of Transplantation
2. Annals of Transplantation
3. Artificial Organs
4. ASAIO Journal
5. Bone Marrow Transplantation
6. Cell Transplantation
7. Clinical Transplantation
8. Current Opinion in Organ Transplantation
9. Experimental and Clinical Transplantation
10. International Journal of Artificial Organs
11. Journal of Artificial Organs
12. Journal of Heart and Lung Transplantation
13. Liver Transplantation
14. Nephrology Dialysis Transplantation
15. Pediatric Transplantation
16. Progress in Transplantation
17. STEM Cells and Development
18. Transplant Immunology
19. Transplant Infectious Disease
20. Transplant International
21. Transplantation
22. Transplantation and Cellular Therapy
23. Transplantation Proceedings
24. Transplantation Reviews
25. Xenotransplantation

<a id="scie-transportation-science-technology"></a>

### Transportation Science & Technology

期刊数：42

1. Communications in Transportation Research
2. Computer-Aided Civil and Infrastructure Engineering
3. eTransportation
4. European Transport Research Review
5. Green Energy and Intelligent Transportation
6. IEEE Intelligent Transportation Systems Magazine
7. IEEE Transactions on Intelligent Transportation Systems
8. IEEE Transactions on Intelligent Vehicles
9. IEEE Transactions on Transportation Electrification
10. IEEE Transactions on Vehicular Technology
11. IEEE Vehicular Technology Magazine
12. IET Electrical Systems in Transportation
13. IET Intelligent Transport Systems
14. International Journal of Automotive Technology
15. International Journal of Engine Research
16. International Journal of Heavy Vehicle Systems
17. International Journal of Rail Transportation
18. International Journal of Vehicle Design
19. Ite Journal-Institute of Transportation Engineers
20. Journal of Advanced Transportation
21. Journal of Intelligent Transportation Systems
22. Journal of Transportation Engineering Part A-Systems
23. Journal of Transportation Engineering Part B-Pavements
24. Networks & Spatial Economics
25. Proceedings of the Institution of Civil Engineers-Transport
26. Proceedings of the Institution of Mechanical Engineers Part D-Journal of Automobile Engineering
27. Proceedings of the Institution of Mechanical Engineers Part F-Journal of Rail and Rapid Transit
28. PROMET-Traffic & Transportation
29. Transport
30. Transportation
31. Transportation Letters-the International Journal of Transportation Research
32. Transportation Planning and Technology
33. Transportation Research Part A-Policy and Practice
34. Transportation Research Part B-Methodological
35. Transportation Research Part C-Emerging Technologies
36. Transportation Research Part D-Transport and Environment
37. Transportation Research Part E-Logistics and Transportation Review
38. Transportation Research Record
39. Transportation Science
40. Transportmetrica A-Transport Science
41. Transportmetrica B-Transport Dynamics
42. Vehicular Communications

<a id="scie-tropical-medicine"></a>

### Tropical Medicine

期刊数：25

1. Acta Tropica
2. American Journal of Tropical Medicine and Hygiene
3. Asian Pacific Journal of Tropical Biomedicine
4. Asian Pacific Journal of Tropical Medicine
5. Biomedica
6. Infectious Diseases of Poverty
7. Journal of Tropical Medicine
8. Journal of Tropical Pediatrics
9. Journal of Vector Borne Diseases
10. Journal of Venomous Animals and Toxins Including Tropical Diseases
11. Leprosy Review
12. Malaria Journal
13. Memorias do Instituto Oswaldo Cruz
14. Parasites & Vectors
15. Pathogens and Global Health
16. PLOS Neglected Tropical Diseases
17. Revista da Sociedade Brasileira de Medicina Tropical
18. Revista do Instituto de Medicina Tropical de Sao Paulo
19. Southeast Asian Journal of Tropical Medicine and Public Health
20. Transactions of the Royal Society of Tropical Medicine and Hygiene
21. Tropical Biomedicine
22. Tropical Doctor
23. Tropical Medicine & International Health
24. Tropical Medicine and Health
25. Tropical Medicine and Infectious Disease

<a id="scie-urology-nephrology"></a>

### Urology & Nephrology

期刊数：88

1. Actas Urologicas Espanolas
2. Advances in Kidney Disease and Health
3. Aging Male
4. Aktuelle Urologie
5. American Journal of Kidney Diseases
6. American Journal of Nephrology
7. American Journal of Physiology-Renal Physiology
8. Archivos Espanoles de Urologia
9. Asian Journal of Andrology
10. BJU International
11. Bladder Cancer
12. Blood Purification
13. BMC Nephrology
14. BMC Urology
15. Canadian Journal of Urology
16. Cardiorenal Medicine
17. Clinical and Experimental Nephrology
18. Clinical Genitourinary Cancer
19. Clinical Journal of the American Society of Nephrology
20. Clinical Kidney Journal
21. Clinical Nephrology
22. Cuaj-Canadian Urological Association Journal
23. Current Opinion in Nephrology and Hypertension
24. Current Opinion in Urology
25. Current Urology Reports
26. European Urology
27. European Urology Focus
28. European Urology Oncology
29. European Urology Open Science
30. French Journal of Urology
31. Hemodialysis International
32. International Braz J Urol
33. International Journal of Impotence Research
34. International Journal of Urology
35. International Neurourology Journal
36. International Urogynecology Journal
37. International Urology and Nephrology
38. Investigative and Clinical Urology
39. Iranian Journal of Kidney Diseases
40. Journal of Endourology
41. Journal of Nephrology
42. Journal of Pediatric Urology
43. Journal of Renal Care
44. Journal of Renal Nutrition
45. Journal of Sexual Medicine
46. Journal of the American Society of Nephrology
47. Journal of Urology
48. Kidney & Blood Pressure Research
49. Kidney Diseases
50. Kidney International
51. Kidney International Reports
52. Kidney International Supplements
53. Kidney Research and Clinical Practice
54. LUTS-Lower Urinary Tract Symptoms
55. Minerva Urology and Nephrology
56. Nature Reviews Nephrology
57. Nature Reviews Urology
58. Nefrologia
59. Nephrologie & Therapeutique
60. Nephrology
61. Nephrology Dialysis Transplantation
62. Nephrology Nursing Journal
63. Nephron
64. Neurourology and Urodynamics
65. Pediatric Nephrology
66. Peritoneal Dialysis International
67. Prostate
68. Prostate Cancer and Prostatic Diseases
69. Prostate International
70. Renal Failure
71. Revista de Nefrologia Dialisis y Trasplante
72. Scandinavian Journal of Urology
73. Seminars in Dialysis
74. Seminars in Nephrology
75. Sexual Medicine
76. Sexual Medicine Reviews
77. Therapeutic Advances in Urology
78. Therapeutic Apheresis and Dialysis
79. Translational Andrology and Urology
80. Urolithiasis
81. Urologia Internationalis
82. Urologic Clinics of North America
83. Urologic Oncology-Seminars and Original Investigations
84. Urologie
85. Urology
86. Urology Journal
87. World Journal of Mens Health
88. World Journal of Urology

<a id="scie-veterinary-sciences"></a>

### Veterinary Sciences

期刊数：142

1. Acta Parasitologica
2. Acta Scientiae Veterinariae
3. Acta Veterinaria Brno
4. Acta Veterinaria Hungarica
5. Acta Veterinaria Scandinavica
6. Acta Veterinaria-Beograd
7. American Journal of Veterinary Research
8. Anatomia Histologia Embryologia
9. Animal
10. Animal Health Research Reviews
11. Animal Nutrition
12. Animal Reproduction Science
13. Animal Welfare
14. Animals
15. Ankara Universitesi Veteriner Fakultesi Dergisi
16. Annual Review of Animal Biosciences
17. Anthrozoos
18. Applied Animal Behaviour Science
19. Arquivo Brasileiro de Medicina Veterinaria e Zootecnia
20. Austral Journal of Veterinary Sciences
21. Australian Veterinary Journal
22. Avian Diseases
23. Avian Pathology
24. Berliner und Munchener Tierarztliche Wochenschrift
25. BMC Veterinary Research
26. Canadian Journal of Veterinary Research-Revue Canadienne de Recherche Veterinaire
27. Canadian Veterinary Journal-Revue Veterinaire Canadienne
28. Cattle Practice
29. Comparative Immunology Microbiology and Infectious Diseases
30. Developmental and Comparative Immunology
31. Diseases of Aquatic Organisms
32. Equine Veterinary Education
33. Equine Veterinary Journal
34. Experimental Animals
35. Fish & Shellfish Immunology
36. Fish Pathology
37. Frontiers in Veterinary Science
38. In Practice
39. INRAE Productions Animales
40. Iranian Journal of Veterinary Research
41. Irish Veterinary Journal
42. Israel Journal of Veterinary Medicine
43. Italian Journal of Animal Science
44. Japanese Journal of Veterinary Research
45. Javma-Journal of the American Veterinary Medical Association
46. Journal of Animal and Plant Sciences-Japs
47. Journal of Animal Physiology and Animal Nutrition
48. Journal of Animal Science and Technology
49. Journal of Applied Animal Welfare Science
50. Journal of Aquatic Animal Health
51. Journal of Avian Medicine and Surgery
52. Journal of Comparative Pathology
53. Journal of Equine Veterinary Science
54. Journal of Exotic Pet Medicine
55. Journal of Feline Medicine and Surgery
56. Journal of Fish Diseases
57. Journal of Medical Entomology
58. Journal of Medical Primatology
59. Journal of Small Animal Practice
60. Journal of Swine Health and Production
61. Journal of the American Animal Hospital Association
62. Journal of the American Association for Laboratory Animal Science
63. Journal of the Hellenic Veterinary Medical Society
64. Journal of the South African Veterinary Association
65. Journal of Veterinary Behavior-Clinical Applications and Research
66. Journal of Veterinary Cardiology
67. Journal of Veterinary Dentistry
68. Journal of Veterinary Diagnostic Investigation
69. Journal of Veterinary Emergency and Critical Care
70. Journal of Veterinary Internal Medicine
71. Journal of Veterinary Medical Education
72. Journal of Veterinary Medical Science
73. Journal of Veterinary Pharmacology and Therapeutics
74. Journal of Veterinary Research
75. Journal of Veterinary Science
76. Journal of Wildlife Diseases
77. Journal of Zoo and Wildlife Medicine
78. Kafkas Universitesi Veteriner Fakultesi Dergisi
79. Kleintierpraxis
80. Lab Animal
81. Laboratory Animals
82. Magyar Allatorvosok Lapja
83. Medical and Veterinary Entomology
84. Medical Mycology
85. Medycyna Weterynaryjna-Veterinary Medicine-Science and Practice
86. New Zealand Veterinary Journal
87. Onderstepoort Journal of Veterinary Research
88. Pakistan Veterinary Journal
89. Pesquisa Veterinaria Brasileira
90. Pferdeheilkunde
91. Polish Journal of Veterinary Sciences
92. Porcine Health Management
93. Preventive Veterinary Medicine
94. Reproduction in Domestic Animals
95. Research in Veterinary Science
96. Revista Brasileira de Parasitologia Veterinaria
97. Revista Brasileira de Zootecnia-Brazilian Journal of Animal Science
98. Revista Cientifica-Facultad de Ciencias Veterinarias
99. Revue Scientifique et Technique-Office International des Epizooties
100. Scandinavian Journal of Laboratory Animal Science
101. Schweizer Archiv für Tierheilkunde
102. Slovenian Veterinary Research
103. Society & Animals
104. Thai Journal of Veterinary Medicine
105. Theriogenology
106. Tieraerztliche Praxis Ausgabe Grosstiere Nutztiere
107. Tieraerztliche Praxis Ausgabe Kleintiere Heimtiere
108. Tieraerztliche Umschau
109. Topics in Companion Animal Medicine
110. Transboundary and Emerging Diseases
111. Tropical Animal Health and Production
112. Turkish Journal of Veterinary & Animal Sciences
113. Veterinaria Italiana
114. Veterinaria Mexico
115. Veterinarni Medicina
116. Veterinarski Arhiv
117. Veterinary Anaesthesia and Analgesia
118. Veterinary and Comparative Oncology
119. Veterinary and Comparative Orthopaedics and Traumatology
120. Veterinary Clinical Pathology
121. Veterinary Clinics of North America-Equine Practice
122. Veterinary Clinics of North America-Food Animal Practice
123. Veterinary Clinics of North America-Small Animal Practice
124. Veterinary Dermatology
125. Veterinary Immunology and Immunopathology
126. Veterinary Journal
127. Veterinary Medicine and Science
128. Veterinary Microbiology
129. Veterinary Ophthalmology
130. Veterinary Parasitology
131. Veterinary Pathology
132. Veterinary Quarterly
133. Veterinary Radiology & Ultrasound
134. Veterinary Record
135. Veterinary Research
136. Veterinary Research Communications
137. Veterinary Sciences
138. Veterinary Surgery
139. Vlaams Diergeneeskundig Tijdschrift
140. Wiener Tierarztliche Monatsschrift
141. Zoo Biology
142. Zoonoses and Public Health

<a id="scie-virology"></a>

### Virology

期刊数：36

1. Acta Virologica
2. AIDS
3. AIDS Research and Human Retroviruses
4. Annual Review of Virology
5. Antiviral Research
6. Antiviral Therapy
7. Archives of Virology
8. Cell Host & Microbe
9. Current HIV Research
10. Current Opinion in Virology
11. Food and Environmental Virology
12. Future Virology
13. Influenza and Other Respiratory Viruses
14. International Journal of Medical Microbiology
15. Intervirology
16. Journal of Clinical Virology
17. Journal of General Virology
18. Journal of Medical Virology
19. Journal of NeuroVirology
20. Journal of Viral Hepatitis
21. Journal of Virological Methods
22. Journal of Virology
23. Journal of Virus Eradication
24. PLOS Pathogens
25. Retrovirology
26. Reviews in Medical Virology
27. Southern African Journal of HIV Medicine
28. Viral Immunology
29. Virologica Sinica
30. Virologie
31. Virology
32. Virology Journal
33. Virus Evolution
34. Virus Genes
35. Virus Research
36. Viruses-Basel

<a id="scie-water-resources"></a>

### Water Resources

期刊数：99

1. Advances in Water Resources
2. Agricultural Water Management
3. Applied Water Science
4. Aqua-Water Infrastructure Ecosystems and Society
5. Aquatic Conservation-Marine and Freshwater Ecosystems
6. Canadian Water Resources Journal
7. Catena
8. China Ocean Engineering
9. Clean-Soil Air Water
10. Desalination
11. Desalination and Water Treatment
12. Ecohydrology
13. Ecohydrology & Hydrobiology
14. Engenharia Sanitaria e Ambiental
15. Environmental Earth Sciences
16. Environmental Fluid Mechanics
17. Environmental Geochemistry and Health
18. Environmental Modelling & Software
19. Environmental Science-Water Research & Technology
20. Environmental Toxicology
21. Exposure and Health
22. Geomatics Natural Hazards & Risk
23. Ground Water Monitoring and Remediation
24. Groundwater
25. Grundwasser
26. Hydrogeology Journal
27. Hydrological Processes
28. Hydrological Sciences Journal
29. Hydrologie und Wasserbewirtschaftung
30. Hydrology and Earth System Sciences
31. Hydrology Research
32. International Journal of Disaster Risk Reduction
33. International Journal of Disaster Risk Science
34. International Journal of Sediment Research
35. International Journal of Water Resources Development
36. International Soil and Water Conservation Research
37. Irrigation and Drainage
38. Irrigation Science
39. Journal Awwa
40. Journal of Contaminant Hydrology
41. Journal of Flood Risk Management
42. Journal of Hydraulic Engineering
43. Journal of Hydraulic Research
44. Journal of Hydro-Environment Research
45. Journal of Hydroinformatics
46. Journal of Hydrologic Engineering
47. Journal of Hydrology
48. Journal of Hydrology and Hydromechanics
49. Journal of Hydrology-Regional Studies
50. Journal of Irrigation and Drainage Engineering
51. Journal of Pipeline Systems Engineering and Practice
52. Journal of Soil and Water Conservation
53. Journal of the American Water Resources Association
54. Journal of Water and Climate Change
55. Journal of Water Process Engineering
56. Journal of Water Resources Planning and Management
57. Journal of Water Sanitation and Hygiene for Development
58. Journal of Waterway Port Coastal and Ocean Engineering
59. Lake and Reservoir Management
60. Lhb-Hydroscience Journal
61. Maritime Engineering
62. Membrane and Water Treatment
63. Mine Water and the Environment
64. Natural Hazards
65. Natural Hazards and Earth System Sciences
66. Natural Hazards Review
67. Nature Water
68. Npj Clean Water
69. Ocean & Coastal Management
70. Physics and Chemistry of the Earth
71. Proceedings of the Institution of Civil Engineers-Water Management
72. River Research and Applications
73. Soil and Water Research
74. Stochastic Environmental Research and Risk Assessment
75. Tecnologia y Ciencias del Agua
76. Urban Water Journal
77. Vadose Zone Journal
78. Wasserwirtschaft
79. Water
80. Water Air and Soil Pollution
81. Water Alternatives-an Interdisciplinary Journal on Water Politics and Development
82. Water and Environment Journal
83. Water Economics and Policy
84. Water Environment Research
85. Water International
86. Water Policy
87. Water Quality Research Journal
88. Water Research
89. Water Research X
90. Water Resources
91. Water Resources and Economics
92. Water Resources and Industry
93. Water Resources Management
94. Water Resources Research
95. Water Reuse
96. Water sa
97. Water Science and Technology
98. Wetlands Ecology and Management
99. Wiley Interdisciplinary Reviews-Water

<a id="scie-zoology"></a>

### Zoology

期刊数：175

1. Acta Amazonica
2. Acta Biologica Colombiana
3. Acta Chiropterologica
4. Acta Ethologica
5. Acta Herpetologica
6. Acta Ichthyologica et Piscatoria
7. Acta Parasitologica
8. Acta Zoologica
9. Acta Zoologica Bulgarica
10. African Invertebrates
11. African Journal of Herpetology
12. African Journal of Wildlife Research
13. African Zoology
14. American Journal of Primatology
15. American Malacological Bulletin
16. American Museum Novitates
17. Amphibia-Reptilia
18. Amphibian & Reptile Conservation
19. Animal Behaviour
20. Animal Biology
21. Animal Cells and Systems
22. Animal Cognition
23. Animal Taxonomy and Ecology
24. Animal Welfare
25. Annales Zoologici Fennici
26. Annals of Carnegie Museum
27. Annual Review of Animal Biosciences
28. Aquatic Mammals
29. Asian Herpetological Research
30. Australian Journal of Zoology
31. Australian Mammalogy
32. Behavioral Ecology
33. Behavioral Ecology and Sociobiology
34. Behaviour
35. Behavioural Processes
36. Belgian Journal of Zoology
37. Bioacoustics-the International Journal of Animal Sound and Its Recording
38. BMC Zoology
39. Boletim do Instituto de Pesca
40. Brain Behavior and Evolution
41. Caldasia
42. California Fish and Wildlife Journal
43. Canadian Journal of Zoology
44. Chelonian Conservation and Biology
45. Cladistics
46. Comparative Biochemistry and Physiology A-Molecular & Integrative Physiology
47. Comparative Biochemistry and Physiology B-Biochemistry & Molecular Biology
48. Comparative Biochemistry and Physiology C-Toxicology & Pharmacology
49. Comparative Cytogenetics
50. Comparative Parasitology
51. Contributions to Zoology
52. Current Herpetology
53. Current Zoology
54. Cybium
55. Developmental and Comparative Immunology
56. Ecological and Evolutionary Physiology
57. Ethology
58. Ethology Ecology & Evolution
59. European Journal of Taxonomy
60. European Journal of Wildlife Research
61. European Zoological Journal
62. Experimental Animals
63. Folia Primatologica
64. Frontiers in Zoology
65. Gayana
66. General and Comparative Endocrinology
67. Helminthologia
68. Herpetologica
69. Herpetological Conservation and Biology
70. Herpetological Journal
71. Herpetological Monographs
72. Herpetozoa
73. Hystrix-Italian Journal of Mammalogy
74. Ichthyological Exploration of Freshwaters
75. Ichthyological Research
76. Ichthyology and Herpetology
77. Iheringia Serie Zoologia
78. Integrative and Comparative Biology
79. Integrative Organismal Biology
80. Integrative Zoology
81. International Journal of Primatology
82. Invertebrate Biology
83. Invertebrate Reproduction & Development
84. Invertebrate Systematics
85. Isj-Invertebrate Survival Journal
86. Journal of Animal Ecology
87. Journal of Comparative Neurology
88. Journal of Comparative Physiology A-Neuroethology Sensory Neural and Behavioral Physiology
89. Journal of Comparative Physiology B-Biochemical Systems and Environmental Physiology
90. Journal of Comparative Psychology
91. Journal of Conchology
92. Journal of Crustacean Biology
93. Journal of Ethology
94. Journal of Experimental Biology
95. Journal of Experimental Psychology-Animal Learning and Cognition
96. Journal of Experimental Zoology Part A-Ecological and Integrative Physiology
97. Journal of Experimental Zoology Part B-Molecular and Developmental Evolution
98. Journal of Helminthology
99. Journal of Herpetology
100. Journal of Ichthyology
101. Journal of Invertebrate Pathology
102. Journal of Mammalian Evolution
103. Journal of Mammalogy
104. Journal of Medical Primatology
105. Journal of Molluscan Studies
106. Journal of Natural History
107. Journal of Nematology
108. Journal of the American Association for Laboratory Animal Science
109. Journal of Thermal Biology
110. Journal of Vertebrate Biology
111. Journal of Wildlife Management
112. Journal of Zoological Systematics and Evolutionary Research
113. Journal of Zoology
114. Laboratory Animals
115. Learning & Behavior
116. Malacologia
117. Mammal Research
118. Mammal Review
119. Mammal Study
120. Mammalia
121. Mammalian Biology
122. Marine Mammal Science
123. Molluscan Research
124. Nauplius
125. Nautilus
126. Nematology
127. Nematropica
128. Neotropical Ichthyology
129. New Zealand Journal of Zoology
130. North-Western Journal of Zoology
131. Organisms Diversity & Evolution
132. Pachyderm
133. Pacific Science
134. Phyllomedusa
135. Primates
136. Raffles Bulletin of Zoology
137. Records of the Australian Museum
138. Redia-Journal of Zoology
139. Reproduction Fertility and Development
140. Revue Suisse de Zoologie
141. Russian Journal of Herpetology
142. Russian Journal of Nematology
143. Russian Journal of Theriology
144. Salamandra
145. South American Journal of Herpetology
146. Spixiana
147. Studies on Neotropical Fauna and Environment
148. Subterranean Biology
149. Tropical Zoology
150. Turkish Journal of Zoology
151. Ursus
152. Vertebrate Zoology
153. Veterinary and Comparative Orthopaedics and Traumatology
154. Veterinary Research Forum
155. Wildlife Biology
156. Wildlife Monographs
157. Wildlife Research
158. Zebrafish
159. Zoo Biology
160. ZooKeys
161. Zoologia
162. Zoologica Scripta
163. Zoological Journal of the Linnean Society
164. Zoological Letters
165. Zoological Research
166. Zoological Science
167. Zoological Studies
168. Zoologichesky Zhurnal
169. Zoologischer Anzeiger
170. Zoology
171. Zoology in the Middle East
172. Zoomorphology
173. Zoosystema
174. Zoosystematics and Evolution
175. Zootaxa

<a id="scie-unclassified"></a>

### Unclassified

期刊数：2

1. Ethics and Society
2. Journal on Image and Video Processing

<!-- SOURCE_END: Science Citation Index Expanded_20260715.md -->
