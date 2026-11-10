# 用户指定论文：Hi-C scaffolders benchmark

记录日期：2026-11-01。

用户给出的题名 **A benchmark of Hi-C scaffolders using reference genomes and de novo assemblies** 对应 [2022 年预印本](https://doi.org/10.1101/2022.04.20.488415)。正式版题为 **Benchmarking Hi-C scaffolders using reference genomes and de novo assemblies**，Sur、Noble、Myler，Genome Biology 27:133 (2026)，[DOI](https://doi.org/10.1186/s13059-026-03978-3)。本次核对正式版 Methods，并直接阅读作者代码；未逐版本比较预印本与正式版差异。

## 研究范围和解读

研究比较 Lachesis、HiRise、3D-DNA、SALSA、ALLHiC，涵盖酵母、L. tarentolae、拟南芥及人，设置参考切片与 Canu de novo 两种输入。工具筛选截止 2020-09-15，**未比较 YaHS、HapHiC**。它提供历史工具在这些条件下的证据，不构成当前所有 scaffolders 的排名。

值得借鉴的是：既比较碎片化也比较高连续度输入，保留不挂载基线，并把错误分成分组、顺序、方向。过度连接能使 N50 上升而结构变差。论文提出的约 50 aligned reads/kb 经验边界只适用于其测试条件；采购数据前必须统一过滤和计数口径，不能直接理解成 50× 碱基覆盖度。原文出处见上方 DOI。

## 直接读过的代码

源码：`pipelines/Noble-Lab_hic_scaffolder_benchmarks/`，精确 SHA 见 [source_manifest.json](sources/source_manifest.json)。作者 [GitHub](https://github.com/Noble-Lab/hic_scaffolder_benchmarks)，归档 [Zenodo](https://doi.org/10.5281/zenodo.18043349)。

| 文件 | 从实现确认的行为 |
|---|---|
| `main/submit.py` | 生成模板，调用 `sbatch`；使用 `afterok` 串接依赖，以文件是否存在决定跳过阶段 |
| `main/defaults.json` | 固定作者 `/mmfs1/...` 与 `/gscratch/...` 路径、Slurm 队列、内存及镜像位置 |
| `main/generate_defaults.py` | 调度比对/下采样/挂载；HiRise 取 coordinate 排序文件，其他分支取 `alpha`；MboI/GATC 在模板中预设 |
| `main/alignment/alignment.sh`、`alpha.sh` | `bwa mem -SP5`、samblaster，随后 `samtools sort -n`，说明排序是工具接口的一部分 |
| `main/alignment/sample_rate.py`、`downsample.sh` | 按 flagstat 的 mapped/2 与 FASTA 总长估计接触密度，生成抽样概率并调用 samtools |
| `main/scaffolding/salsa.sh`、`3d_dna.sh` | BED 按第 4 列 read name 排序；3D-DNA 使用 merged_nodups 和专用格式转换；都会删除自己的 run 目录 |
| `main/distance/edit_distance.py` | FASTA 输入先拆 scaffold、比对分配；AGP 输入可跳过 MUMmer；保存 JSON |
| `main/distance/scaffold_distance.py` | 由 contig 两端、邻接关系及端点构造图，数 cycle/odd path 计算 DCJ |
| `main/distance/grouping.py`、`ordering.py`、`main/utils/agp.py` | 分组的加权 Jaccard、邻接边权、AGP 解析和坐标处理 |

## 评分应如何理解

从代码观察，grouping 为参考染色体与输出 scaffold 的交集/并集，取每条参考染色体的最佳匹配并按长度加权。Ordering 比较无方向的相邻 contig 对；orientation 进一步比较端点，整条染色体反向互补并不等同于局部方向错误。邻接分数的分母来自参考边的长度权重，因此应同时检查额外错误连接、未挂载序列和 DCJ。

DCJ：`d = N - C - I/2`，N 是共同 contig 数，C 是 cycle 数，I 是 odd path 数。代码中的 overall accuracy 是其邻接图路径长度加权得分，**不是碱基准确率，也不是 Merqury QV**。

AGP 比较要求双方具有相同 contig 集合。常规单倍型重复序列、一个 component 被拆成多段、参考与样本真实结构差异，都可能使简单比较失去前提。不能直接把 raw YaHS AGP 和整条参考 FASTA 扔入 AGP 模式。

## 实际运行的小例子

本地 `tests/learning_smoke/results/benchmark/` 构造两条染色体，每条两个 100 bp contig，先计算自身对照，再把 contig b 的方向翻转。执行作者原始 `main/distance/edit_distance.py -r reference.agp -a <input.agp> -o <outdir>`，未改作者源码。

| 输入 | Grouping | Ordering | Orientation | Overall accuracy | DCJ |
|---|---:|---:|---:|---:|---:|
| reference 对自身 | 100% | 100% | 100% | 100% | 0 |
| b 局部翻转 | 100% | 100% | 50% | 75% | 1 |

这个实验验证了不同指标能区分局部方向错误。它没有执行 scaffolders，也没有重现四物种 benchmark 的数值。

## 发现的复现隐患

1. **数据不足的抽样哨兵不一致（已实际触发）**：`sample_rate.py` 令 `sample_rate=False` 后仍使用 `f'{sample_rate:.12f}'`，输出 `0.000000000000`；`downsample.sh` 则与字符串 `False` 比较。用 1 kb FASTA、mapped=20、目标 50 构造输入，实际 stdout 正是该数值。此时无法进入原本“不足则退出”的分支；需在适配副本中统一输出约定并核查目标 samtools 版本的行为。尚未替作者修改源代码，也不能据此断定论文结果失效。
2. **AGP 实现需校验（静态发现）**：`agp.read` 只跳过 `N`，没有同时处理 `U`；空行检查和 component 重复出现的处理也不适合通用 AGP。`agp.write` 长度使用 `end-start`，同文件 read 及距离代码采用 `end-start+1`。迁移时用 AGP 规范验证并检查坐标，不能把该 writer 当成通用标准工具。
3. **无邻接边的极端情况（静态发现）**：`ordering.count` 分母来自参考内部边；若全是 singleton，分母可能为零。近染色体组装评测尤其需要覆盖此输入。
4. **命令行类型（静态发现）**：`--min-length`、`--min-coverage` 缺少显式 `type`，默认值与用户输入值可能类型不同。自定义阈值需验证传递下游后的行为。
5. **复用与清理**：仅凭同名文件存在跳过计算可能复用旧参数产物；shell 模板没有统一严格错误模式，并含 `rm -rf .../run`。必须先适配到独立运行目录，检查模板展开后的路径，不直接运行原始集群命令。

## 如何复用

已下载并读取期刊正文 Table 2 与 [补充 DOCX](https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-026-03978-3/MediaObjects/13059_2026_3978_MOESM1_ESM.docx) 中的三张表和图注，整理如下数据入口；BioProject 不是单个测序 run，仍须进一步筛选样本、文库与 SRR/ERR 清单，不能把整个项目全部下载混用。

| 物种 | Hi-C BioProject（正文 Table 2） | 长读长 BioProject（补充 Table S2） |
|---|---|---|
| S. cerevisiae | PRJNA525842 | PRJEB7245 |
| L. tarentolae | PRJNA818795 | PRJNA821548 |
| A. thaliana | PRJNA227546 | PRJNA314706 |
| H. sapiens | PRJNA268125 | PRJNA301527 |

补充表实际标题为 S1（汇总分数）、S2（长读长数据）、S3（Canu 输入深度与 contig N50）；正文对应处写 S3/S4，存在编号不一致，复现应按表内容识别。正文还将 L. tarentolae 参考条目标成 `processing`，正式复现前需要从作者数据/归档核实精确参考文件。这些信息尚不足以固定全部输入。原始补充文件本地保留在 `notes/sources/benchmark/`，其下载校验和见同级目录外的 `benchmark_access_record.json`。本次没有逐张提取/复算补充图的数据点。

先固定代码 SHA，补齐论文补充表中的 accession/参考版本，记录容器 digest；将默认目录、队列、module、镜像和酶模式改为本项目配置。先验证比对与抽样口径，再跑一种小基因组、一个输入连续度、一种 scaffolder，同时生成基线和全部未挂载序列统计；确认评分输入 contig 集合一致后才扩展实验。README 三条命令是集群入口示例，不能当作此机器上的可直接运行教程。

本次已完成源码检查、正文/补充表数据入口核对及上述微型验证；尚未下载全套四物种数据、固定全部 SRA run 和参考文件、运行全部容器或复现图表。后续可把该评分框架作为对照，但纳入 YaHS/HapHiC 时需要重新设计公平输入与版本控制。
