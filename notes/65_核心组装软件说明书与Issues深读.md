# 核心组装软件说明书与 Issues 定向深读

阅读日期：2026-11-10（Asia/Shanghai）。本轮仅阅读论文、官方说明书、版本记录、源码入口和 GitHub issues；**未安装、未运行软件、未运行测试或生物分析流程**。这是一轮高价值问题定向审查，不等于逐条读完各仓库全部 issue。

机器账本：[来源、版本、issue 和证据边界](sources/software_manual_issue_review_2026-11-10.json)。本笔记聚焦本轮阅读的软件与论文；适用时必须锁定精确 release/tag/commit，滚动 README、issues 中的用户猜测和已关闭标签都不能代替目标版本的确认。

## 用户指定论文：Colora

### 论文身份与证据

本地 PDF 为 Obinu et al.《Colora: A Snakemake Workflow for Complete Chromosome-scale De Novo Genome Assembly》的 bioRxiv 版本，DOI [10.1101/2024.09.10.612003](https://doi.org/10.1101/2024.09.10.612003)，25 页，SHA256：`1ed915e8060998f2d1226b52e13555e0098905c4e794b31eb40711656d336970`。作者随后发表正式版 [Bioinformatics 2025, btaf175](https://doi.org/10.1093/bioinformatics/btaf175)；预印本、正式论文和当前 GitHub `main` 不是可互换的版本证据。本库此前已对固定提交做过功能流程记录，本轮没有重跑。

论文描述的主线为：HiFi/Hi-C 输入检查与 NanoPlot/fastp → KMC/GenomeScope2 调查 → hifiasm primary 或 Hi-C 分相组装（ONT 可选）→ 可选 FCS-GX/去污染与 primary 路线的 purge_dups → Arima 比对和 YaHS 挂载 → BUSCO/QUAST；细胞器支路用 Oatk、Bandage 和 gfastats。PretextView 人工检查 Hi-C 图是重要审阅环节，不能以流程成功或 N50 上升代替。

论文示例本身揭示了结构风险：Hi-C 错误 join 可抬高连续性指标；拟南芥和苹果示例中，预期染色体数与组装 L50 不一致，Hi-C 图显示错误连接。FCS-GX 不负责移除线粒体污染；purge_dups 可能损失 BUSCO。故工作流的“染色体级”输出是待验证产物，不是对任意物种、个体和数据组合的结构正确保证。论文以植物为主要开发对象，Oatk 等植物工具的适用性要单独评估。

### 对应源码与使用接口

仓库：[LiaOb21/colora](https://github.com/LiaOb21/colora)，本轮源码核对固定提交 `d6569edaff8da51739688b246dda2dfb2da13d7a`。主要入口为 `workflow/Snakefile`；配置 `config/config.yaml`；规则位于 `workflow/rules/*.smk`；每规则环境在 `workflow/envs/`，冻结环境在 `workflow/frozen_envs/`。既有工作区曾记录过运行证据，但本次未重新核查或运行。

README 的使用模式是编辑配置中的输入、资源、数据库和可选模块，再以 Snakemake 和 Conda 环境部署运行；集群执行还需要匹配的 Snakemake profile。仓库示例 test-config 命令已被记录，但本轮没有执行。调试时优先核对：

- Hi-C 文件 glob /命名与样本 ID 推断；命名不匹配会影响样本发现。
- `phased_assembly` 对应的 DAG 分支；phased 路线跳过 purge_dups，primary 路线才可选运行。
- `include_fcsgx`、`include_purge_dups`、HiFi/ONT/Hi-C 路径、线程/内存配置、YaHS 参数和 BUSCO lineage。
- 数据库路径是否可读；FCS-GX 数据库尤其大。ONT 输入按说明须预先整理，工作流并不自动执行所有过滤/合并假设。
- 每步日志和预期文件是否存在且可解析；Snakemake 退出码为 0 不证明 FASTA/AGP 结构正确。

该仓库当前 issue/PR 页面没有公开条目；这只能说明此仓库没有可供本轮审阅的 issue 记录，不能外推到它调用的 hifiasm、YaHS 等组件。故障排查应继续查依赖软件各自的固定版本 issues。

## 组装器

### hifiasm 0.25.0-r726

资料入口：[README](https://github.com/chhylp123/hifiasm)、[FAQ](https://github.com/chhylp123/hifiasm/blob/master/docs/source/faq.rst)、[release](https://github.com/chhylp123/hifiasm/releases)。本库已有固定版本和选定源码范围，但滚动 README/FAQ 不保证与该 release 完全相同。本轮核查的源码接口包括 `CommandLines.cpp`（CLI 选项/校验）和 `Assembly.cpp`（组装入口）；不能据此声称通读全部图算法源码。

README/FAQ 将 HiFi 常规、ONT、Hi-C、trio 和不同倍性模式分开说明。输出 GFA 的 `p_ctg`、`a_ctg`、`p_utg`、`r_utg` 各有不同语义；不要只按文件名推断“primary”即一套完整且已相位的单倍型。纠错/overlap bin 可能复用；诊断重跑时需记录前缀、bin 身份和时间戳，不能无差别清除缓存。`--purge-max` 等去冗余相关选项会改变真实重复/等位序列保留结果，必须作为新分支比较。

定向 issues：[#933](https://github.com/chhylp123/hifiasm/issues/933)（大基因组在 purge_dups 阶段停止，遗留巨大 bin；发起者关闭，但公开页面未显示复跑验证，根因未确认）；[#798](https://github.com/chhylp123/hifiasm/issues/798)（HiFi+Hi-C 索引后 segfault，转换压缩格式、QC 和 trim 等操作同时改变，不能确诊单一原因）；[#756](https://github.com/chhylp123/hifiasm/issues/756)（高覆盖分批纠错后合并的等价性没有得到确认）。诊断包至少应保留完整 hifiasm 日志、输入格式/完整性、reads 路径及身份、所有 bin 的大小/时间、作业退出信号和 MaxRSS。段错误不等于 OOM；issue 中“成功”的多变量尝试不构成因果证明。

### Verkko 2.3.2

资料入口：[README](https://github.com/marbl/verkko)、[v2.3.2 release](https://github.com/marbl/verkko/releases/tag/v2.3.2)。它是 Snakemake 工作流，不只是单一组装二进制；组合 HiFi 类高准确读长和 ONT ultra-long，内部调用多种图构建、读段映射、纠缠消解和 consensus 组件。输出包括 assembly FASTA、GFA、覆盖与 scaffold map 等，phasing 路线另有相位文件。v2.3.2 对 Snakemake 要求 `>=7,<8`，版本不匹配要先核查依赖锁；不要只删除未知参数就宣布兼容。

[#224](https://github.com/marbl/verkko/issues/224)：Snakemake 8 删除 `--reason` 后启动失败，与 v2.3.2 的 Snakemake 版本限制相符。 [#308](https://github.com/marbl/verkko/issues/308)：`--paths` 等恢复方式受中间文件时间戳影响；维护者建议 dry-run 核对 DAG。 [#348](https://github.com/marbl/verkko/issues/348)：`layoutContigs` 长时间无明显进度，维护者说明该阶段可能受磁盘 I/O 约束，个案后来完成。排错需同时保存 `verkko.yml`、Snakemake DAG、rule 日志、依赖版本、工作目录/中间件时间戳、存储吞吐和调度器资源；CPU 低或耗时长本身不足以诊断死锁。

### Flye 2.9.6

资料入口：[USAGE](https://github.com/mikolmogorov/Flye/blob/flye/docs/USAGE.md)、[FAQ](https://github.com/mikolmogorov/Flye/blob/flye/docs/FAQ.md)、[2.9.6 release](https://github.com/mikolmogorov/Flye/releases/tag/2.9.6)。按平台和纠错状态选择 `--pacbio-raw/corr/hifi` 或 `--nano-raw/corr/hq`；同次输入不能混不同读长类型。`--meta` 是不均匀覆盖/宏基因组模式；`--scaffold` 非默认；`--resume`/`--resume-from`/`--stop-after` 提供阶段控制。Genome size 通常不是必填，使用 `--asm-coverage` 时另需估计。自动 min-overlap 与手工覆盖的选择会影响重复图复杂度，且参数必须结合读段长度/覆盖解释。

[#687](https://github.com/mikolmogorov/Flye/issues/687)：大麦 ONT 个案手工设 `--min-overlap 1000` 后重复阶段耗时、耗内存；维护者检查日志认为 OOM，建议使用自动选择的 overlap；用户随后报告约 500 GB 内存并完成。该个案支持“过高手工 overlap 可能增大图复杂度”的排查方向，不证明自动值在所有数据上更优。应保存 `flye.log`、阶段名/耗时、实际参数和作业资源记录。

## 短读组装与 Hi-C

### SPAdes 4.3.0

入口：[官方手册](https://ablab.github.io/spades/running.html)、[v4.3.0 release](https://github.com/ablab/spades/releases/tag/v4.3.0)、[README](https://github.com/ablab/spades)。主要面向 Illumina/IonTorrent 短读；hybrid 模式的长读是补充证据，不应直接泛化为大型杂合真核的常规最优方案。4.3 加入 `--frugal`，调整内存行为和错误码。项目实测仍仅 SPAdes 4.0.0 小型/合成案例，不能写成 4.3 已运行。

[#1444](https://github.com/ablab/spades/issues/1444)（v4.0.0）里日志报告 `mmap` Error 12；维护者发现请求的内存限制仍为 250 GB，而用户把线程误设为 1600，故先核对 `params.txt`/日志中的真实参数与内存上限。 [Discussion #1433](https://github.com/ablab/spades/discussions/1433) 报 `/tmp` 太小或临时目录写入失败的案例；`--tmp-dir` 应指向空间、配额和 I/O 合适的目录。issue 给的是系统层返回错误和个案解释，不可由“机器总 RAM/磁盘很大”推断作业可用量。故障包保留 `params.txt`、`spades.log`、`--tmp-dir`、文件系统/配额信息、线程和容器/conda 约束。

### MaSuRCA 4.1.4

入口：[release](https://github.com/alekseyzimin/masurca/releases/tag/v4.1.4)、[上游仓库与 restart 文档](https://github.com/alekseyzimin/masurca)。release 指定使用附件完整包，不能用 GitHub 自动生成的 Source 压缩包替代。它按配置生成阶段脚本；重启时重看最后可信阶段的产物、日志和退出状态。

[#357](https://github.com/alekseyzimin/masurca/issues/357) 是旧版/用户报告的时限中断；[#362](https://github.com/alekseyzimin/masurca/issues/362) 要求提供 `CA/` 与 `runCA1.out` 诊断 overlap/unitig 失败；[#369](https://github.com/alekseyzimin/masurca/issues/369) 报告 CA8 bogart segfault 后 wrapper 仅因日志文件存在而误报成功。后者的直接 debug 教训是核对退出码和真正的 unitig/assembly 产物，日志文件存在不等于阶段成功；该 issue 用的旧版，不能说 4.1.4 已复现相同缺陷。

### ABySS 2.3.10

入口：[官方仓库/README](https://github.com/BirolLab/abyss)、[2.3.10 release](https://github.com/BirolLab/abyss/releases/tag/2.3.10)。注意参数含义随模式变化：Bloom filter 内存预算 `B`、单节点线程 `j`、MPI 进程数 `np` 不可混为一个“资源参数”；paired de Bruijn 模式下 `K`/`k` 语义不同；`TMPDIR` 可能影响临时文件空间。[#499](https://github.com/BirolLab/abyss/issues/499) 的 Error 137 没有确认根因/维护者结论。应查调度器终止原因、作业内存限制、临时目录及多库参数；不能仅凭 137 判定是 ABySS 软件缺陷或 OOM。

### YaHS 1.2.2 与 HapHiC 1.0.7

YaHS 文档/README 要求 name-sorted Hi-C BAM；需核验实际 BAM header 和 records。release 与本地阅读源码 commit 不同，报告时同时记录版本号和 SHA。 [#119](https://github.com/c-zhou/yahs/issues/119)：Docker 标签称 1.2 但缺少 `--telo-motif`，问题未确认；核对容器 digest、实际 PATH 程序与功能 help。 [#120](https://github.com/c-zhou/yahs/issues/120)：挂载后 Merqury QV 下降，维护者指出 YaHS 应只断开已有 contig 并插 gap，要求确认运行成功和前后统计；用户称重新 polish 后恢复，但根因未确认。不要写成“YaHS 会改碱基”或“多行 FASTA 是确定原因”。

HapHiC 标称 1.0.7 也必须附本地源码 SHA。 [#87](https://github.com/zengxiaofei/HapHiC/issues/87)：维护者说明 `refsort` 调整 scaffold 整体顺序/方向，不更改内部结构；参考排序不构成结构验证。 [#174](https://github.com/zengxiaofei/HapHiC/issues/174)：用户将 MAPQ 降至 0 后挂载率上升但形成巨大疑似嵌合组；页面没有维护者确诊。不可自动放宽 MAPQ，需检查有效对、倍性、同源关系、图谱冲突并人工检查图。

### Juicer / 3D-DNA

Juicer 是 Hi-C 预处理链（reads 到去重 pairs / `.hic`），不是 scaffolder；官方仓库 [aidenlab/juicer](https://github.com/aidenlab/juicer)。[#350](https://github.com/aidenlab/juicer/issues/350) 报 `pre` 阶段列数错误，排查方向为 pairs header/格式/列数；[#198](https://github.com/aidenlab/juicer/issues/198) 指自定义 HiCCUPS resolution 需要完整对应参数组合，单给 `-r` 不足以确认所选分辨率生效。

3D-DNA 本地固定 commit `cb63403c329dd45d0fdc4851746b5a8587528132`。[#179](https://github.com/aidenlab/3d-dna/issues/179) 报 post-review 后序列总长异常缩小，但讨论中没有证实根因。排查应保留原 FASTA、review assembly、liftover、日志，并比对 AGP/序列总长；“内存不足”只是用户猜测，不能照抄为已知缺陷。

## 后续共用排错记录规范

每个 issue 记录：精确版本/commit、数据类型、命令参数、错误阶段、原始 stderr/stdout/log、ExitCode/Signal、MaxRSS 与调度器资源限额、scratch/TMPDIR 容量/配额/inode/I/O、输入文件身份/格式、issue 讨论的结论状态和是否有维护者确认/版本修复。用户报告、关闭状态、被提及的可能原因不自动升级为根因。版本未锁定或 issue 超出目标版本时，必须明写适用边界。

本轮首批已学习的工具范围不是全软件表。其他软件后续批次的逐项状态见[66 全软件阅读进度](66_全软件说明书与Issues阅读进度.md)，需继续补读其官方手册和高价值 issues。没有软件运行、安装、测试或生物验证。
