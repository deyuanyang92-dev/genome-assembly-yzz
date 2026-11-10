# 全基因组组装流程与 bioSkills 学习库

2026-11-03功能规划：[QS019 Hi-C测序采购与挂载充分性指导](notes/62_HiC测序采购与挂载充分性规划_QS019.md)。优先支持只有HiFi时制定首批采购方案，再接实际QC更新和挂载充分性复核。已保存功能规格、输入与报告模板，尚未实现。

2026-11-03追加：固定RagTag v2.1.0已完成3个人工挂载分支；默认/推断gap、独立AGP重建、未定位保留及参考重排偏倚已检查。见[实测记录](tests/ragtag_scaffold_2026-11-03/README.md)。没有新增真实样本、Hi-C或完整初装流程；历史批次计数保留。

## 2026-11-02 本轮纠错与补齐

新增[59参考辅助方法与选择](notes/59_参考辅助组装方法体系与工具选择.md)、[60格式转换](notes/60_组装格式转换与数据交接.md)、[61 Hi-C选型与HapHiC](notes/61_HiC挂载选型与HapHiC机制.md)。[全历史20类请求审计](notes/sources/full_request_gap_audit_2026-11-02.md)逐项区分完成部分与缺口；不能称全部学习完成。新增samtools1.21合成格式交接证据，未增加目标生物组装验收。

后续实际补齐：HapHiC官方113页补充材料已保存并复核选定方法/命令；Sanger两份培训PDF文本及12个关键图文页已审阅；gfatools固定源码已编译并保存成功/失败例。详见[本轮交付索引及模型分工](notes/sources/reference_hic_batch_2026-11-02.md)，所有阅读和运行范围分开记录。

## 知识库当前入口

[50 知识库导航与32专题覆盖账本](notes/50_全基因组知识库导航与覆盖账本.md)；[51 组装原理与证据判断](notes/51_组装原理与证据驱动判断手册.md)；[52 Juicer/BUSCO/Flye源码补充](notes/52_Juicer_BUSCO_Flye接口源码与排错补充.md)。

当前实测口径（2026-11-02）：已保存1套Colora测试配置的功能闭环记录，24项默认DAG目标有输出；QUAST单独执行后接回，可选FCS-GX关闭。目标物种生产级生物学验收为0，不能称原生未修改全流程通过。详见[测试记录](tests/colora_functional_2026-11-01/README.md)。

当前副本：`/mnt/p/yzz-全基因组工作流程/genome-assembly-yzz`，即 Windows `P:\yzz-全基因组工作流程\genome-assembly-yzz`。核查日期：2026-11-01。

**已下载 26 个上游仓库，其中 6 套完整组装工作流/集合。bioSkills 全库 63 类、561 个技能已建立索引；重点阅读 25 个技能正文，仍有 536 个未通读。截至早期清点尚无完整工作流实测；当前测试配置记录见下。** hifiasm/YaHS 等单工具不计入完整工作流数。

## 优先阅读

- [49任务范围与数据路由总纲](notes/49_全基因组组装任务范围与数据路由总纲.md)：覆盖二代、长读、混合、Hi-C/图谱及参考辅助；按输入和目标选择完整路线。

- [21 组装基础与质量判断](notes/21_组装基础与质量判断.md)：如何判断准确/完整/结构正确，只有 HiFi 及不同个体 Hi-C 的处理。
- [19 编程与验收规范](notes/19_全基因组组装编程与验收规范.md)、[20 源码追踪与能力验证](notes/20_源码追踪与能力验证.md)：后续开发的数据模型、阶段交接和版本风险。
- [CONTEXT 项目上下文](CONTEXT.md)：后续会话恢复学习成果和待办的入口。
- [00 学习进度和证据边界](notes/00_学习进度清单.md)：究竟下载了多少、读到哪里、哪些实际运行过。
- [15 六套完整组装工作流源码核查](notes/15_完整组装工作流源码核查.md)：Sanger、VGP、nf-core、CLAWS、EBP-Nor、Colora 的输入、执行链和缺口。
- [16 Colora 论文流程与复现入口](notes/16_Colora流程与复现入口.md)：较紧凑的 Snakemake 全流程、配置与官方测试准备。
- [17 bioSkills 系统学习与使用](notes/17_bioSkills系统学习与使用.md)：架构、目录、技能路由、安装器、9 个组装技能和完整流程的对应关系。
- [18 bioSkills 源码勘误](notes/18_bioSkills源码勘误与使用边界.md)：Hi-C 输出前缀、Omni-C 空酶配置、YaHS 排序/MAPQ、污染清理等问题。

## 六套完整流程

| 流程 | 框架 | 本项目学习重点 | 详细笔记 |
|---|---|---|---|
| Sanger genomeassembly 1.0.1 | Nextflow | dataset/spec/stage、分型后分 hap 挂载、阶段 QC、细胞器 | [01](notes/01_sanger-tol_genomeassembly.md)、[15](notes/15_完整组装工作流源码核查.md) |
| VGP Galaxy/IWC | Galaxy 工作流集合 | 调查→组装/分型→挂载→去污染→人工校正前后评价 | [02](notes/02_VGP_Galaxy.md) |
| nf-core/genomeassembler 2.0.1 | Nextflow | 单倍体/近交系；组装、可选 polishing/scaffolding、多阶段报告 | [03](notes/03_nf-core_genomeassembler.md) |
| CNAG CLAWS v3.2 | Snakemake | 多组装器比较、polish/purge、Hi-C、Pretext；需本地化集群配置 | [04](notes/04_CNAG_CLAWS.md) |
| EBP-Nor GenomeAssembly | Snakemake | 分 hap k-mer 过滤 Hi-C、挂载、FCS、oatk、curation 轨道 | [05](notes/05_EBP-Nor_GenomeAssembly.md)、[15](notes/15_完整组装工作流源码核查.md) |
| Colora | Snakemake | HiFi + Hi-C ± ONT、核与细胞器组装、有论文/测试数据 | [16](notes/16_Colora流程与复现入口.md) |

固定提交以 [源码清单](notes/sources/source_manifest.json) 为准。01–08 是原仓库既有深入笔记；其中原机器绝对路径、测试结果和部分旧提交不能当作本机现状。本轮补充核查以00、14–31为准。原 README 已保存在 [历史说明](README_previous_machine.md)。

## 工具、论文和视频

- [06 Verkko](notes/06_Verkko.md)：组装核心工作流，单列学习。
- [07 Juicer + 3D-DNA](notes/07_Juicer_3D-DNA.md)：已有 contigs 后的 Hi-C 子流程。
- [08 核心工具速查](notes/08_核心工具速查.md)。
- [09 视频访问证据与 Skills 工作方法](notes/09_视频与Skills学习.md)：公众号页面与封面已取得，媒体仍要求微信客户端；**没有取得视频音轨/逐帧内容**。
- [10 论文和复现资源地图](notes/10_论文与复现资源地图.md)。
- [11 Hi-C scaffolders benchmark 精读](notes/11_HiC_scaffolders_benchmark.md)：用户指定论文、评分与复现障碍。
- [12 hifiasm、YaHS、HapHiC 使用说明](notes/12_组装与HiC挂载使用说明.md)。
- [13 去冗余、质量评价与流程选择](notes/13_质控与流程选择.md)。
- [14 本地源码与验证记录](notes/14_本地源码与验证记录.md)：此前 11 仓库阶段的实测记录；后新增 15 仓库见清单及15–31。

## 本地文件与复核

源码在 `pipelines/`，被 Git 忽略；可运行 `bash pipelines/fetch_pipelines.sh /新的目标目录` 按清单下载全部 26 仓库。已有仓库 SHA 不符会保留并停止，避免静默混用版本。只做恢复时须准备网络与磁盘空间，Colora 附带测试 reads；Verkko、KMC 子模块不由此脚本安装。

bioSkills [全库索引](notes/sources/bioskills_catalog.json)、[阅读范围](notes/sources/bioskills_reading_ledger.json)、[结构校验/安装预览](tests/bioskills_audit/validation.json)、[专项核查](tests/bioskills_audit/content_checks.json)均已保存。可在学习库根目录运行 `python3 tests/bioskills_audit/audit.py` 重查模板问题；它不安装技能，不运行组装。

此前 hifiasm/YaHS 官方小数据与 benchmark 微型评分验证见 [learning_smoke/validation.json](tests/learning_smoke/validation.json)。它们不能代表六套工作流跑通。大数据、容器、数据库、测试结果日志保留在本地且忽略提交；本轮没有提交或推送 GitHub，也没有全局安装 bioSkills。

追加的严格无损挂载契约检查：`python3 tests/assembly_contracts/check_contracts.py`，14个合成案例通过，覆盖反向互补、坐标、序列遗漏/重复等；见[结果](tests/assembly_contracts/validation.json)。这不验证真实染色体挂载准确性。新核查的生物学资料及适用范围见[来源记录](notes/sources/assembly_foundations_review.json)。

- [22 近期论文对标地图](notes/22_近期组装论文与对标地图.md)：6篇2025–2026正式论文、1篇预印本、2份EBP文件及VGP基线。
- [23 EBP 2026与项目验收](notes/23_EBP2026规范与本项目对标要求.md)：外部标准与本项目提升目标分开。
- [24 新增源码核查](notes/24_论文配套源码核查_Galeolaria与GPhase.md)：新增2仓库，完整工作流仍6套，端到端实测仍0套。

- [25 近期标准论文及项目动作](notes/25_近期标准论文与项目高标准验收.md)：新增2026年标准/细胞遗传综述和ERGA实证核查。
- [26 追加学习与边界](notes/26_追加学习与适用边界.md)：bioSkills正文25篇、VGP14个接口、Colora运行准备及阻碍。
- **用户要求高于最低标准：**默认按[23高标准验收表](notes/23_EBP2026规范与本项目对标要求.md)规划；选择HiFi路线时有效HiFi≥50×为硬门槛，QV≥50争取60，完整度/挂载98%争取99%，结合产品角色、独立证据和物种适用性。未达目标和缺数据必须明示。

- [27 测序数据调查及100×二代决策](notes/27_测序数据预判组装难度与二代补充策略.md)：HiFi-only调查、跨平台核查、有效HiFi≥50×和重复困难证据。
- [28 已收集的调查源码与脚本](notes/28_基因组调查源码与脚本使用说明.md)：新增6个单工具源码及命令/风险/验证状态；不是新增完整流程。
- [29 后续开发清单](notes/29_基因组调查开发待办.md)：6项集成缺口与验收要求，尚未实现。

- [30 ONT质控与三类数据联合组装](notes/30_ONT质控与HiFi_HiC联合组装.md)：普通/超长ONT、过滤前后和长尾覆盖、hifiasm/Verkko接口及验证边界。
- [31 非同个体Hi-C贡献与干扰评估](notes/31_非同个体HiC贡献与干扰评估.md)：固定初装对照、逐连接支持/冲突、目标个体证据和未知范围。

- [32 跨个体Hi-C直接进入hifiasm的风险与对照](notes/32_跨个体HiC直接参与hifiasm分型的风险与对照.md)：分型与挂载的区别、相位不匹配机制、独立证据和两分支比较。

- [QS010 自动评估功能需求](notes/33_跨个体HiC自动评估功能需求_QS010.md)：用户要求后续开发；对照hifiasm两分支，分开报告收益、干扰与无法确认，尚未实现。

- [34 ONT量与高覆盖的软件规则](notes/34_ONT数据量充分性与高覆盖软件说明核查.md)：5种组装器阶段阈值、长尾与区域证据、QS011；无真实ONT覆盖试验。
- [35 EBP/Sanger Hi-C挂载与人工校正](notes/35_EBP与Sanger_HiC挂载及人工校正指南.md)：YaHS→图谱/轨道→人工审阅→AGP恢复→重新比对/QC；官方网页已读，PDF/视频及培训实操未完成；QS012待开发。

- [36 去冗余工具说明与参数](notes/36_去冗余软件说明书与参数核查.md)、[37 文献与流程实际用法](notes/37_去冗余文献与公开流程实际用法.md)、[38 QS013开发验收](notes/38_去冗余流程开发与验收需求.md)：5类工具/实现，6篇方法/比较及4个用法案例；7例提取合成检查，真实purge实验0；不同资料阅读深度已逐项标注。

- [39 完整性判断与缺口定位](notes/39_组装完整性判断与缺口定位.md)：区分基因/序列拷贝/染色体完整性，显式gap与隐性缺失定位、T2T证据及QS014需求；无真实样本鉴定。

- [40 注释软件与论文调查](notes/40_基因组注释软件与文献调研.md)、[41 二代/三代RNA证据](notes/41_二代三代RNA注释证据处理规范.md)、[42 自动配置/整合QS015](notes/42_自动多方法注释流程开发与验收_QS015.md)：新旧BRAKER区别、Helixer/EviAnn互补、证据整合及QA；仅资料/静态核查与模板，新增安装和真实注释运行均0。

- [43 现成自动注释流程核查](notes/43_现成自动注释流程核查与开发复用.md)：9种架构，RAGNAROK部分调度源码、GETA入口与其余文档/论文分层核查；新增clone/实测0。
- [44 公开环节动物数据、核心基因与机器学习](notes/44_公开环节动物基因组核心基因与机器学习可行性.md)：AnnelidaDB及23种重注释先例、跨库状态、核心/特有/必需概念、训练标签/防泄漏与QS016；实际资产普查和训练尚未执行。


## 2026-11-02追加记录

- [45 软件说明书、issues与源码诊断库](notes/45_软件说明书Issues与源码诊断知识库.md)：6个核心项目、10个issue主题、18条诊断设计规则；固定commit和源码指纹；不是已实现诊断器。
- [46 二代与HiFi估G比较](notes/46_二代与HiFi估计基因组大小的比较.md)：偏倚、多k/独立验证、50×保守判定和LVgs候选；无目标reads实测。
- [47 最近两年规范论文续读](notes/47_最近两年组装规范论文续读.md)：2024-11-02至2026-11-02，4篇补查+2篇既有复用；标准/建议/项目要求分开。

- [48 二代与参考辅助染色体组装](notes/48_二代数据与参考辅助染色体组装路线.md)：二代初装、参考/Hi-C/图谱挂载、共识与补洞的区别；版本、证据验收和QS018；本轮无生物运行。

- [53 二代/混合原理、源码与实测](notes/53_二代与混合组装方法源码及实测.md)、[54 bioSkills短读纠错](notes/54_bioSkills短读专题复核与纠错.md)：SPAdes实际4.0.0与审查4.3.0区分；官方小例1、人工4、负例3，真实物种生产验收0。

- [多agent本批汇总](tests/multi_agent_learning_2026-11-02/README.md)：新增55–58四篇专题；短读源码、Hi-C编辑回写、标准验收及RNA路由，分别保存阅读与实测边界。
