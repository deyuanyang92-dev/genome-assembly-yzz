# bioSkills 系统学习与使用

核查日期：2026-11-01。[上游 GPTomics/bioSkills](https://github.com/GPTomics/bioSkills)，本地 `pipelines/GPTomics_bioSkills`，固定提交 `d91ed3d563019e649dc854c56ccd62551359488a`。README 已明确归档、不再修复；应维护自己的核查记录，不能把归档内容当成持续更新的官方工具文档。

## 1. 实际学了多少

| 层次 | 本轮完成范围 | 不包含的内容 |
|---|---|---|
| 全库目录与元数据 | 实际扫描 **63 类、561 个技能**，记录 name、description、tool_type、primary_tool、路径、行数、usage-guide 和 examples 数；见 [完整 JSON 索引](sources/bioskills_catalog.json) | 不等于逐篇精读 561 个技能 |
| 组装专项 | 阅读 `genome-assembly` **9 个 SKILL.md 正文**：profiling、short-read、long-read、HiFi、metagenome、polishing、contamination、scaffolding、QC | 没有逐个运行涉及的工具，没有审完全部算法实现 |
| 编排专项 | 阅读 **2 个总流程技能**：`workflows/genome-assembly-pipeline` 和 `workflows/hic-pipeline` | 其余 39 个 workflows 仅建目录索引 |
| 工作流引擎 | nextflow-pipelines、snakemake-workflows、nf-core-pipelines 三篇全文 | 没有执行模板，也未通读 CWL/WDL |
| 代码与补充说明 | 阅读 hifi、scaffolding、bacterial assembly 三个 shell 示例，以及 scaffolding usage-guide；核对 installer/common、README、CONTRIBUTING | 示例语法或目录检查不能证明实际生物结果正确 |

因此：**25个技能正文阅读；561个技能建立索引，536个正文未通读。** 新增长读3篇、比对5篇、Hi-C联系/矩阵/可视化3篇，详见[26追加记录](26_追加学习与适用边界.md)及阅读账本。不能把索引数量说成掌握数量，也不能把正文阅读说成全部命令已验证。TAD/loop等不是当前组装项目的主任务。

## 2. 架构与执行机制

每个领域技能通常有三层：

```text
genome-assembly/scaffolding/
  SKILL.md                    # 何时使用、决策、命令、失败模式、相关技能
  usage-guide.md              # 面向人的说明与提示词
  examples/yahs_scaffolding.sh # 供改写的代码示例
```

`SKILL.md` 前部 YAML 的 name/description 负责识别任务；正文负责执行规则和取舍；参考文档/脚本按需读取。bioSkills 的 `tool_type`、`primary_tool` 是自身元数据，**不会自动安装 YaHS、启动 hifiasm 或形成 Nextflow DAG**。

`workflows/genome-assembly-pipeline` 的 `depends_on` 列出其他技能，正文告诉 agent 去读取相应技能；源码并没有一个通用调度器根据此列表自动执行、缓存、检查输出。它的示例实际上是一个细菌 ONT + Illumina 脚本，不能当成二倍体真核 HiFi + Hi-C 的完整可运行实现。

Codex 官方说明采用渐进式加载：先看到 name/description，再在使用时读取全文；本地项目和用户技能目录包括 `.agents/skills`。[官方技能说明](https://learn.chatgpt.com/docs/build-skills)。**下载到 `pipelines/` 是源码学习，不等于已安装为活动技能。** 本轮没有将它写入全局或项目活动技能目录。

## 3. 全库如何检索与分层使用

索引按 63 个原分类保留，而非重新发明一个生物信息分类体系。可按任务分层查找：

| 项目阶段/问题 | 优先查的类别 | 作用 |
|---|---|---|
| 输入与格式 | sequence-io、sequence-manipulation、alignment-files、genome-intervals | FASTA/FASTQ/BAM/BED 等数据契约 |
| reads 与平台 | read-qc、read-alignment、long-read-sequencing | 平台/模型、质量、比对；需与实际软件版本对照 |
| 本项目核心 | genome-assembly 9、hi-c-analysis 9、phasing-imputation 4 | 组装、分型、挂载和三维分析的边界 |
| 下游解释 | genome-annotation 7、comparative-genomics 13、phylogenetics 8、population-genetics 7 | 注释、共线性、系统发育、群体问题；本轮只索引 |
| 其他组学 | single-cell、spatial-transcriptomics、proteomics、metabolomics、methylation-analysis 等 | 可借鉴结构，本轮未进行领域精读或实测 |
| 编排与交付 | workflows 41、workflow-management 5、reporting 6、data-visualization 20 | 找任务路线、引擎配置与报告；模板须落实成可复现执行 |

在学习库根目录可检索：

```bash
rg -n 'Hi-C|YaHS|hifiasm|purge_dups' \
  pipelines/GPTomics_bioSkills/genome-assembly \
  pipelines/GPTomics_bioSkills/workflows/genome-assembly-pipeline
```

不要仅靠 `primary_tool` 选择技能：polishing 的 primary_tool 仍写 Pilon，但正文涉及多种新工具；contamination 写 CheckM2，但真核核基因组应走 FCS/BlobToolKit 路线。这是元数据摘要与实际使用范围的差别。

## 4. 组装类九个技能，分别学到了什么

| 技能 | 核心决策与输入输出 | 使用时的核查点 |
|---|---|---|
| genome-profiling | 准确 reads → k-mer 直方图 → GenomeScope/Smudgeplot；预估大小、杂合、倍性 | k-mer depth 与 base depth 不同；GenomeScope 的峰/模型参数不能机械当作 hifiasm hom-cov；调查不稳定时保留不确定性 |
| short-read-assembly | 短读长 DBG；SPAdes 等按 isolate/meta/单细胞选择 | 大型高杂合真核的重复不可被加深短读长自动解决；主组装大小和两个 hap 总和要分开 |
| long-read-assembly | ONT/CLR 的数据误差模型影响 Flye/Canu 等选择 | 记录真实建库、basecaller、模式和版本；不能把所有 ONT 都强制走同一 polishing 链 |
| hifi-assembly | hifiasm 的 HiFi-only、Hi-C、trio；Verkko 补充；GFA 导出 FASTA | primary ≠ 全局分型 hap；Hi-C 输出文件名有勘误；Hi-C phasing 后仍要分别 scaffold |
| metagenome-assembly | 群落组装 → binning → MAG 评价 | 与单个环节动物核基因组目标不同；CheckM2/GUNC 和 MIMAG 不能直接套到宿主核组装 |
| assembly-polishing | 按数据类型与模型，比较修改前后 QV 决定是否 polishing | 不把 HiFi 自动反复 polish；细菌经验不能直接推广到杂合真核；保留独立验证数据和原版组装 |
| contamination-detection | 单物种外源筛查与 MAG 质量是两条路线；细胞器单独处理 | taxid/数据库要正确；HGT、共生体、NUMT 不能靠命中颜色一键删除；脚本 high_quality 标签需完整定义 |
| scaffolding | contigs + linking data → AGP/FASTA → contact map → 人工审阅 | 酶与文库协议、BAM 排序和 MAPQ；参考引导结果不能当作独立结构证据 |
| assembly-qc | 连续性、完整性、碱基/结构正确性，另加分型质量 | BUSCO 不代表整个基因组完整；QV 不验证排列；两端端粒和无 N 也不能单独证明序列/重复结构都正确 |

可保留其优点：明确适用边界、把质量控制穿插到每步、解释失败机制、跨技能路由。需修正的部分见 [专项勘误](18_bioSkills源码勘误与使用边界.md)。未经核查的经验阈值不能变成本物种的硬性验收标准。

## 5. Hi-C 的两条任务路线

**染色体组装**：HiFi → hifiasm 分型（如有 Hi-C/trio）→ 每 hap contigs → Hi-C 比对/去重/过滤 → YaHS/HapHiC 等 → AGP/FASTA → contact map/人工校正 → 再评价。主技能是 `genome-assembly/scaffolding`。

**三维基因组研究**：已有坐标系统的参考 → Hi-C mapping → pairtools → pairs → cooler/mcool → balancing/expected → compartment/TAD/loop → 统计比较。主技能是 `workflows/hic-pipeline`。它不会从 contigs 自动拼成染色体。文中的深度和分辨率经验主要基于相应研究场景，不能直接用作本物种组装 Hi-C 的测序量判据。

用于组装审阅的 contact map 必须准确对应当前 FASTA/AGP 坐标。改完结构后应重建或正确转换图；不能拿旧图证明新版 final 正确。Hi-C 未提供亲本标签时，hap1/hap2 也不能自动命名为父本/母本。

## 6. 安装器实际做什么、验证了什么

已执行：`bash install-codex.sh --validate`，退出码 0，**561/561 通过**。校验内容是字段、`Use when` 描述、usage-guide 与非空 examples 等结构检查，不会跑例子，不检验参数、生物学断言或数据库适配。

已执行安装预览：

```bash
bash install-codex.sh \
  --categories genome-assembly,hi-c-analysis,workflows,workflow-management \
  --dry-run --project /tmp/bioskills-review-only
```

结果 **Would install: 64 skills**，没有写入目标技能目录。预览末尾仍打印 “Skills are now available”，这是安装器共用结束文案，不能据此说已安装。命令与结果保存在 [validation.json](../tests/bioskills_audit/validation.json)。

从 `install-codex.sh`、`install-common.sh` 读到：默认全局 `~/.agents/skills`；项目模式为目标项目 `.agents/skills`；目录名 `bio-类别-技能`。Codex 复制过程将 tool_type/primary_tool 移入 metadata，将 examples 复制到 scripts，将 usage-guide 放进 references。复制不等于安装生物软件/数据库。`--validate` 独立退出、不会继续安装；它的全库校验循环也不按 categories 缩小。`--uninstall` 会遍历目标下的 `bio-*`，不应在未核对范围时使用。

若以后实际安装，宜选择当前项目所需的少量技能，并复核转换后的引用路径。64 个整类安装会同时带入 41 个其他组学 workflow；初次不需要全部启用。此处仅说明机制，本轮没有执行安装、卸载或依赖下载。

## 7. 与六套完整工作流怎么配合

| 环节 | bioSkills 用来做什么 | 可执行工作流依据 |
|---|---|---|
| 数据调查与设计 | profiling/HiFi 帮助列出数据与倍性假设 | Sanger specs、VGP1/2、Colora config 的真实字段 |
| 组装与分型 | 解释为何选择 Hi-C/trio/primary | Sanger、VGP4/5、EBP-Nor、Colora 对应执行分支 |
| polishing/purge | 用证据判断是否启用，定义前后检查 | 具体流程参数、阈值和输入版本；不用模板默认值代替 |
| Hi-C 挂载 | 解释 mapping、重复、酶、排序、AGP 与图 | Sanger/CLAWS/VGP8/EBP-Nor 实际 mapping → YaHS 接口 |
| 去污染与细胞器 | 学会分别交付和审阅 | VGP9、EBP-Nor 或 Colora；Sanger 的外部去污染补充 |
| 验收与 curation | 建立多指标报告和失败退出条件 | VGP 人工校正前后流程、Sanger 阶段 QC，加 AGP/FASTA 核查 |

可复用的提示词（不要求先安装整个库）：

> 阅读本地 bioSkills 的 genome-assembly-pipeline、hifi-assembly、scaffolding 和 assembly-qc；用本项目已固定版本的 Sanger 工作流实施。先报告输入数据清单、平台、倍性假设、基因组大小、Hi-C 协议、数据库/软件版本和资源。逐个把建议映射到真实 schema 字段，并核对笔记18勘误。生成可审阅的配置与启动命令；记录实际执行、日志、QC、失败条件。hap1/hap2 分别挂载，保留 GFA、AGP、原始与修改后 FASTA、contact map 和人工编辑记录。没有执行的步骤明确标记未运行。

每次产出至少包括输入校验和、源码 SHA、参数/环境、每阶段 FASTA/AGP 身份、统计/QV/BUSCO/k-mer 完整性、Hi-C 比对/有效联系、污染处理记录、分型证据和人工校正状态。没有亲本或其他可用分型真值时，不编造 switch error。小数据通过仅证明所覆盖接口，不能宣称本物种或论文全复现。
