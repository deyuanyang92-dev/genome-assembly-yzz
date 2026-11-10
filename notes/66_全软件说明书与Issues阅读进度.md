# 全软件说明书与 Issues 阅读进度（第一轮）

记录时间：2026-11-10（Asia/Shanghai）。这是软件覆盖矩阵的分组只读学习进度账，不等于软件掌握认证。第一批来源见[核心工具账本](sources/software_manual_issue_review_2026-11-10.json)，第二批逐软件状态见[机器账本](sources/software_manual_issue_review_2026-11-10_round2.json)、[重复序列与注释工具账本](sources/software_manual_issue_review_annotation_2026-11-10.json)和[转录组/功能注释工具账本](sources/software_manual_issue_review_transcript_2026-11-10.json)。**本轮没有安装、运行软件或测试。**

用户要求按项目软件逐一学习说明书和 GitHub issues，供后续本地 debug。此处把“issue 已学习”限定为实际打开、阅读具体 issue 正文/讨论；仅看到 issue 列表或标题标为“目录初筛”，具体页面待读。目标是覆盖软件覆盖矩阵中实际用到或作为生产候选的软件，不是读完每个仓库数百条历史 issue。无 GitHub tracker 的项目记录其官方 issue/支持渠道，不臆造 issue。

## 已读说明书/源码并逐个查过的 issue

| 软件 | 项目版本边界 | 已读内容与问题线索 | 状态 |
|---|---|---|---|
| hifiasm | 0.25.0-r726；README/FAQ 为滚动页面 | CLI/输出/Bin 复用；#933 purge_dups 后停（关闭但未见复跑证明）、#798 segfault（多项同时改动，根因未定）、#756 分批纠错无等价确认 | 定向 issue 正文已读；非全量 |
| Verkko | 2.3.2，Snakemake 7.x（<8） | #224 `--reason` 版本冲突；#308 时间戳影响恢复 DAG；#348 可能 I/O-bound 长阶段 | 定向 issue 正文已读 |
| Flye | 2.9.6 | 手册/FAQ；#687 手工提高 min-overlap 与复杂度/资源上涨个案 | 定向 issue 正文已读 |
| SPAdes | 4.3.0 文档；既有实测只到4.0.0 | #1444 Error 12/内存限制参数误读；Discussion #1433 `/tmp`容量、临时目录/配额/I/O | 定向正文已读；版本边界写明 |
| MaSuRCA | 4.1.4 | restart/产物验收；#357墙钟中断、#362 overlap/unitig信息需求、#369 旧版 wrapper 假成功风险 | 定向 issue 正文已读；#369 是4.1.1个案 |
| ABySS | 2.3.10 | Bloom内存、线程/MPI参数；#499 Error 137 无确定根因 | 定向正文已读，信息有限 |
| YaHS | 1.2.2；本地 commit 与 release 不同 | name-sorted BAM；#119 容器缺参数、#120 QV下降，两者根因均未确认 | 定向正文已读 |
| HapHiC | 1.0.7；本地 commit 与 release 不同 | #87 refsort只改整个 scaffold 顺序/方向；#174 降 MAPQ 后出现疑似 chimeric 巨组，无确认根因 | 定向正文已读 |
| Juicer | 项目固定稳定版/commit，见65账本 | #350 pairs列数；#198 HiCCUPS resolution flags | 定向正文已读 |
| 3D-DNA | commit `cb63403c329dd45d0fdc4851746b5a8587528132` | #179 post-review 总长异常，讨论未确认根因 | 定向正文已读 |

## 说明书已读或部分已读，但 issues 还未完成逐案审阅

| 软件 | 当前可确认的用途/版本线索 | issues 状态 |
|---|---|---|
| fastp | 官方release列表已检查到1.4.0；项目已有1.3.1运行记录。多文件 gzip 输入、JSON/HTML报告需绑定版本与输入 | #711 为近期多 gzip 输入漏读报告（用户个案）；#721 hang fixed。定向页已查，非穷尽 |
| SeqKit | 上游 v2.14.0；`.seqkit.fai` header key 与 samtools fai 的 ID key 不同；某些操作全量读内存 | 手册已读，具体 issue 待补 |
| NanoPlot | 官方release页当前1.48.0，1.47.4曾修复 Plotly API 移除兼容；项目已有1.46.2运行 | 手册/版本已读，issue正文待补 |
| chopper | stdin→stdout 流式过滤；`--update-mods`处理 MM/ML/MN 标签不是 mod-aware trimming | README已读，版本与 issues 待补 |
| KMC | KMC k-mer数据库/多样本使用手册初读 | issue列表发现内存/输出数据库及multi-sample主题，具体页未完整读 |
| FastK | 扩展名决定输入类型；`.ktab.#`隐藏分片和scratch需完整保留；`-M/-T/-P`影响资源 | README已读，issues待补 |
| GenomeScope2 | README建议低错误读段与约15×起始覆盖；高频截断、污染和叶绿体等会影响拟合 | #93直方图 cutoff/`-m`；#144 heterozygote peak fit 个案已定向读 |
| Smudgeplot | 0.5.4 使用 FastK 数据；不能照搬旧 KMC 后端命令；低覆盖下信号弱 | #21低覆盖意义及#133咨询定向读 |
| LRGE | 当前1.0.0与论文/旧版0.3.x估计结果不可直接比较；默认参数偏细菌校准 | README已读，issues待补 |
| RagTag | 项目2.1.0源码；官方 release 与 PyPI 版本身份需区分 | #86预计算 PAF 复用；#94 AGP 顺序报告未核实；#92映射不一致需附件/版本 |
| purge_dups | 1.2.6；深度、self-alignment 和 cutoff 联合；需追踪输出/删除清单 | #150参数文档、#79 cutoff/BUSCO、#82 core dump；此前#166过删报告亦无明确因果 |
| purge_haplotigs | 版本未锁，官方 issue tracker 实际在 Bitbucket | 仅定位 tracker，具体问题未读 |
| Pilon | release 1.24；Java 11+，实验性threads移除 | #174–176 OOM报告簇、#178 QV下降已定位但未逐案核正文 |
| NextPolish | README说明当前新数据边界：噪声读长用 NextDenovo，HiFi consensus 关注 NextPolish2 | 具体issue待读 |
| SAMtools | 项目本地实测1.21；develop manual 1.25；FASTA名称唯一、BGZF索引和普通gzip需区别 | #1783 FASTA首行格式报告仅初步核查 |
| gfatools | GFA/rGFA字段和稳定坐标；S/L及 `SN/SO/SR` 语义需区别 | #20 GFA2转换问题已定位，版本/输入格式适用边界待细化 |
| pbtk bam2fastq | README 接口阅读；版本未锁、未运行 | 没有查到具体 issue 正文；不能记为“没有问题” |
| RepeatMasker / RepeatModeler | 官网列版本4.2.4 / 2.0.9；项目安装版未知。RepeatModeler对 assembly 建库，不宜拆批后简单合库 | issue 正文待读 |
| BRAKER | 当前官方仓库提示 BRAKER deprecated 并推荐 BRAKER4；不要把滚动文档当已安装版 | 已知 `braker.log`、hints、GeneMark日志等debug入口；issue正文待读 |
| StringTie | manual要求坐标排序比对和 strand/XS tag；`-e`需要`-G`且只估计给定模型 | 只浏览 issue 列表（merge/strand tag主题），正文待读 |
| HISAT2 | paired输入文件/record须匹配；`--met-file`可用于性能诊断 | issue列表见 segfault/SIGKILL主题，正文待读 |
| IsoQuant | 官方release 4.1.0（2026-10-20）；resume 行为更新；支持长RNA多种输入形式 | 项目版未知，issue正文待读 |
| eggNOG-mapper | v3应匹配eggNOG DB v7；软件/数据库都须锁定 | issues列表提到数据库下载/格式等，正文待核 |
| InterProScan | 官方EMBL-EBI文档入口已定位 | issue/support具体条目未查 |

## 仍待逐软件核查

以下矩阵候选目前还没有足够的具体说明书 + issue 证据：compleasm、Merqury、QUAST、gfastats、FCS-GX、Oatk、minimap2；BRAKER及上表“issue待读”项需继续补 issue 正文；注释组还需补 MAKER、EVM、funannotate、GALBA、GeneMark、miniprot、STAR、PASA、tRNAscan-SE、Infernal 的逐版本说明书和问题来源。注意软件别名、版本未知和无 GitHub tracker 不应被模糊成“读过”。

## 记录和使用规则

1. 新故障先确认项目里实际二进制、容器 digest/commit、版本、运行参数和DB版本，不能按软件名猜。
2. 收集原始命令、stderr/stdout、主日志、阶段产物、退出信号、MaxRSS、配额、scratch/TMPDIR及存储状况；issue仅是单个报告时写明这个限制。
3. 对每个工具分别记录“文档已读、源码已读、issue正文已读、组件已运行、流程已运行”；本学习批只有前几项，不因此提升运行证据。
4. 逐issue全量阅读不作为现实验收标准；按当前生产路径、近期高影响 bug、未解决行为和版本变更定向取样，保留链接、日期与未覆盖项，遇到对应实际故障再回看完整讨论和附件。

## 2026-11-10 第二批追加：已读 issue 正文和新增缺口

以下信息更新/细化上表；来源和精确版号待整理到第二批机器账本。仍然是定向阅读，不是逐仓库穷尽审计。

- **SeqKit 2.14**：[#610](https://github.com/shenwei356/seqkit/issues/610) 报压缩输入截断后旧版本可能错误返回 0；作者提交 `c716eff` 修复并关闭。诊断损坏 gz/lz4 时须锁 tag 并检查退出状态；`head` 等早停操作不会验证未读后缀。
- **BUSCO 6.1.0**：官方文档与 GitLab tracker 已读；[#560](https://gitlab.com/ezlab/busco/-/issues/560) 报 AutoLineage 修改共享只读 lineage 数据目录。此类错误先核 metadata/data 目录权限和版本，不由此推断目标版本是否仍有缺陷。
- **compleasm 0.2.9**：[#6](https://github.com/huangnengCSU/compleasm/issues/6) 下载中断后残留 `.tmp`；维护者建议先运行 `download`，再对准备好的 lineage 用 `run -L`。这是 issue 中给出的解决建议，需按实际版本复核。
- **Merqury**：[#178](https://github.com/marbl/merqury/issues/178) 解释 k-mer completeness 与 BUSCO 不同：前者比较输入测序 k-mer 丢失，受测序个体及输入倍型影响；指标不同不自动等同相互矛盾。
- **QUAST**：5.3.0 文档/release 已读；[#298](https://github.com/ablab/quast/issues/298) Python 3.12+ 失败、#289 BLAST path、#280 disk storage 只读到标题，正文待核。参考存在与否、reference fragmentation、reads/k-mer 输入及 QV/连续性指标不能混着解释。
- **NanoPlot**：版本路径为 1.47.4 pin Plotly <7 修复 API 兼容；1.48.0增加离线 HTML 所需 JS。#266 只读到摘要，#437仅浏览列表，仍需 issue 正文。
- **InterProScan 6**：[#286](https://github.com/ebi-pf-team/interproscan6/issues/286) 与 [#289](https://github.com/ebi-pf-team/interproscan6/issues/289) 已读；维护者确认本地 metadata 为空导致 Nextflow version null，在该 v6 情境用 `--no-matches-api` 可绕开。此结论不能直接套到 InterProScan 5。
- **eggNOG-mapper 3**：[#613](https://github.com/eggnogdb/eggnog-mapper/issues/613) 已读，beta6 self-test 似乎涉及 v2/v3 输出格式差异，但超长 DIAMOND 子进程、multiprocessing timeout 都是未解决用户报告，无维护者确认根因。软件与 DB v7 必须匹配。
- **EVM**：官方 wiki 表示项目不再维护；[#91/#104] 只看列表/标题，不能作为已读 issue。MAKER、funannotate、GALBA 的 tracker 也仅做入口初筛；PASA 文档已读但其 GitHub issue 入口尚未确认适用。
- **miniprot**：官方 README/manpage 已读，蛋白到基因组含 splice/frameshift 支持，GFF3可能包含 `##PAF`；issue tracker 只定位。STAR、tRNAscan-SE、Infernal 手册入口已定位，issue 正文仍未完成。RepeatModeler/RepeatMasker、BRAKER、StringTie/HISAT2、IsoQuant 的文档已初读，issue 多为列表初筛。
- **Pilon 1.24**：[#174](https://github.com/broadinstitute/pilon/issues/174)–[#176](https://github.com/broadinstitute/pilon/issues/176) 为 Java heap OOM 用户报告，涵盖初始化、`--vcf`等路径；#178 是 QV 下降报告。均未有足够证据总结为统一根因或通用加堆修复。
- **NextPolish 1.4.1**：上游建议 noisy raw TGS 用 NextDenovo，HiFi polishing 考虑 NextPolish2。#130 是结果长度骤降报告无回复；#134 端粒丢失时的“缺少 reads 比对”是维护者提出的可能解释、未验证；#144 `Stale file handle` 更像 temp/挂载问题但未确认核心原因。
- **pbtk bam2fastq**：pbtk仓库没有Issues入口，支持问题在 pbbioconda。[#779](https://github.com/PacificBiosciences/pbbioconda/issues/779) checksum通过但解析BAM记录失败，关闭但根因未确定；[#681](https://github.com/PacificBiosciences/pbbioconda/issues/681) Kinnex header 多出标记影响下游识别，是具体读名兼容报告。pbtk changelog列到3.5.0，但本项目工具版未知。
- **purge_haplotigs**：tracker在 Bitbucket，本轮页面无法读取，版本未锁；保留为 `tracker located / issue review pending`。
- **FCS-GX / gfastats**：手册/README 初读。FCS-GX需核 assembly、taxid、数据库目录与共享内存；Action report是建议审阅，不是自动删除指令。gfastats支持FASTA/FASTQ/GFA及压缩输入。issues正文仍待查。
- **minimap2**：官方参数文档已读，#1359/#1353/#1354只看标题。`-x` preset、MAPQ、secondary/supplementary输出等须连同实际命令与版本记录；issue原因未确认。
- **Oatk**：此批仍未完成说明书与 issue 正文核查；版本未知。

当前只读已覆盖更多文档和若干具体 issue；仍需补 NanoPlot、chopper、KMC/FastK、QUAST、Pilon、NextPolish、purge_haplotigs、minimap2 等其余 issue 页，以及 Oatk、gfastats 等软件。只读标题/搜索摘要仍按“未读正文”处理。

### 注释软件 issue 正文补读

- **MAKER** [#26](https://github.com/Yandell-Lab/maker/issues/26)：MAKER 3.01.04 加入 GeneMark 后 Perl wrapper 报 `POSIX::_exit` 未定义，但直接运行 gmhmme3 子命令返回0；issue 无回复，不能归因到 GeneMark。
- **EVM** [#91](https://github.com/EVidenceModeler/EVidenceModeler/issues/91)：作者确认项目不再积极维护/支持；#104 网页正文未成功加载，未计作已读。
- **funannotate** [#810](https://github.com/nextgenusfs/funannotate/issues/810)：1.8.13 用户报告 `predict` 与测试任务启动后挂起，未获诊断/回复；版本是报告者环境，不是本地安装版。
- **GALBA** [#59](https://github.com/Gaius-Augustus/GALBA/issues/59)：Singularity 中 Augustus 后处理出现 Biopython `Seq` 类型错误，并有蛋白 header 格式警告；未有回复，根因未确认。
- **GeneMark-ETP** [#23](https://github.com/gatech-genemark/GeneMark-ETP/issues/23)：报告同时出现 sort 临时目录不存在、intron hints 为0/不足提示；无答复，不能指定单一根因。
- **RepeatModeler** [#316](https://github.com/Dfam-consortium/RepeatModeler/issues/316)：维护者确认 2.0.9 边缘情形中家族数少于阈值后空结果未捕获，导致下游找不到文件，并提及后续修复/临时补丁；[#318](https://github.com/Dfam-consortium/RepeatModeler/issues/318) 小基因组内存高是无结论报告。
- **RepeatMasker** [#70](https://github.com/Dfam-consortium/RepeatMasker/issues/70)：`.out` 与 `.tbl` summary 百分比不一致，页面关闭但无答案；不能视为修复完成。
- **BRAKER** [#958](https://github.com/Gaius-Augustus/BRAKER/issues/958)：GeneMark 安装路径/`gmetp.pl` PATH 问题有回复指向 `bin/gmetp.pl`；后续社区提及的旧 shebang 修复不能扩大成此 issue 根因已完整复现。官方 README 现提示弃用并推荐 BRAKER4。

以上都只对各链接中的一条或数条问题做了定向阅读，不代表各 repo issues 全读；报告者的旧版号不应当成本地版本。另：NanoPlot #266、chopper #79、FCS-GX #14、gfastats #54 正文已读；Oatk #24 页面的正文取回失败，不能推断原因。

### 调查/QC 与评价软件 issue 正文补读

以下记录补足上一段的部分“待补”状态；上表中列表初筛并不代表正文阅读，具体状态以这里为准。

- **NanoPlot**：[#266](https://github.com/wdecoster/NanoPlot/issues/266) 旧版 Kaleido 静态图导出失败、根因未确认；[#411](https://github.com/wdecoster/NanoPlot/issues/411) HTML 正常但 PNG 空白，维护者建议浏览器从 HTML 另存，后续用户在1.46.1观察到恢复但未定位哪个依赖更新；[#406](https://github.com/wdecoster/NanoPlot/issues/406) `--tsv_stats` 输出预期不清、无答复；[#437](https://github.com/wdecoster/NanoPlot/issues/437) 只读标题“empty HTML graphs”，正文无法取得。
- **SeqKit**：[#610](https://github.com/shenwei356/seqkit/issues/610) 旧版压缩输入截断可能错误 exit 0，修复提交 `c716eff`；[#593](https://github.com/shenwei356/seqkit/issues/593) 解释 `sample2 -p` 的近似单遍与 `-2` 两遍精确采样差异，文档更新后关闭。两条都须与本地实际版对照。
- **chopper** [#79](https://github.com/wdecoster/chopper/issues/79)：功能请求讨论剪切后 FASTQ header 内 SAM tags 和 MM/ML 修改标签；讨论提出的 typed BAM 需求未证明已实现，不要把功能请求当 bug 修复。
- **KMC** [#140](https://github.com/refresh-bio/KMC/issues/140)：维护者根据 macOS 文件创建失败日志指向文件描述符限制，原报告者确认提高 ulimit 后解决；只确认原环境个案，其他相似报告未必适用。
- **FastK** [#20](https://github.com/thegenemyers/FASTK/issues/20)：gzip内容被误命名为 `.fasta` 后 segmentation fault，用户确认输入扩展名/格式错误；debug先核文件 magic bytes 和扩展名，不能由 segfault 推断 OOM。
- **Oatk** [#23](https://github.com/c-zhou/oatk/issues/23)：用户对多条近似大小环状细胞器候选的解释求助，无答复，不能判污染或 heteroplasmy；[#24](https://github.com/c-zhou/oatk/issues/24) 只读标题与日期，正文读取失败。
- **gfastats** [#54](https://github.com/vgl-hub/gfastats/issues/54)：按单序列提取 BGZF `.fa.gz` 卡住而全文件运行可完成，根因未确认；[#38](https://github.com/vgl-hub/gfastats/issues/38) 询问 FASTG→GFA、无回复/结论。
- **QUAST**：[#289](https://github.com/ablab/quast/issues/289) `Mapped (%)>100%` 的读段报告缺少可充分判断的输入/分母信息；[#280](https://github.com/ablab/quast/issues/280) Python3.12 源码安装报告包含 bundled 旧 joblib Python2 语法错误；[#285](https://github.com/ablab/quast/issues/285) 是对 minimap2 版本提示措辞的疑问，评论者建议不算维护者结论。均需保存输入、report、依赖版并读完整日志。
- **minimap2**：[#1353](https://github.com/lh3/minimap2/issues/1353) 多版本在特定 barley 序列 + `-c` 路线出现 `mm_est_err` warning/assert，去掉 `-c` 不复现；没有维护者答复，不能确诊根因。[#1354](https://github.com/lh3/minimap2/issues/1354) 对 `-p` 比值和 `-N` 次数的语义误解；secondary score 不能直接等同于 AS 标签比较。
- **BUSCO** [#560](https://gitlab.com/ezlab/busco/-/issues/560)、**compleasm** [#6](https://github.com/huangnengCSU/compleasm/issues/6)、**Merqury** [#178](https://github.com/marbl/merqury/issues/178)、**FCS-GX** [#14](https://github.com/ncbi/fcs-gx/issues/14) 的正文状态/边界见上面的机器账本与先前追加；根因强度不超过来源文本。

本批尚未读 Oatk #24、NanoPlot #437 的正文；其余 pending 和具体源码阅读边界见[机器账本](sources/software_manual_issue_review_2026-11-10_round2.json)。

### 转录本与功能注释软件 issue 正文补读

- **miniprot 0.18-r281** [#75](https://github.com/lh3/miniprot/issues/75)：旧版0.17-r279的GFF输出遗漏in-frame stop codon，v0.18 release note确认修复。项目本地已有0.18-r281运行证据；此处是 issue + release note 对照，不是全源码审计。
- **STAR**：[#1731](https://github.com/alexdobin/STAR/issues/1731) 在高度重复的短 contig genomeGenerate 场景卡住；维护者建议设 `--genomeSuffixLengthMax 300`，用户在该案例确认解决，不能推广到一般STAR索引。
- **PASA 2.5.3** [#342](https://github.com/PASApipeline/PASApipeline/issues/342)：`--GENETIC_CODE=universal` 被注释比较阶段称不支持，报告者指出分支可能缺失；issue仍开，无维护者确认。
- **StringTie** [#468](https://github.com/gpertea/stringtie/issues/468)：用户报告 `--merge` 合并细菌不同链重叠转录本；未得到维护者诊断，需看链向、GTF和物种模型，不可认定是普遍bug。
- **HISAT2 2.2.1** [#451](https://github.com/DaehwanKimLab/hisat2/issues/451)：`-U -` 声称支持stdin，但wrapper把`-`当文件名检查；issue未见修复闭环，只能作该版本线索。
- **IsoQuant** [#327](https://github.com/ablab/IsoQuant/issues/327)：大染色体索引超BAI范围；release 3.7.1 changelog确认新增支持大染色体BAM索引。
- **InterProScan 6** [#286](https://github.com/ebi-pf-team/interproscan6/issues/286)/[#289](https://github.com/ebi-pf-team/interproscan6/issues/289)：本地metadata为空导致 Nextflow `version` null；维护者解释该情况可用 `--no-matches-api` 并完成关联修复。仅限v6，不外推到v5。
- **eggNOG-mapper 3.0.0-beta6** [#613](https://github.com/eggnogdb/eggnog-mapper/issues/613)：报告自检格式、DIAMOND子进程、annotation timeout多个症状，仍开且无维护者根因判断。`v3 + eggNOG DB7`是关键版本组合。
- **tRNAscan-SE 2.0.13** [#47](https://github.com/UCSC-LoweLab/tRNAscan-SE/issues/47)：GCC15编译legacy C regex出错；issue开放，v2.0.13发行说明称修复GCC15对部分legacy模式的影响，但未确认覆盖所有路径。
- **Infernal 1.1.5** [#44](https://github.com/EddyRivasLab/infernal/issues/44)：询问如何整合Infernal ncRNA、tRNAscan-SE与BRAKER GFF，无回复；不是缺陷证据。#33正文无法打开，但release note提到相应截短命中修复，不能把release note算作issue正文阅读。

以上版本号若标作“上游当前”，不代表本地环境安装版；除miniprot/BUSCO/Oatk/QUAST/NanoPlot/gfastats/minimap2等已有账本记录者外，仍需项目部署时以容器或二进制身份复核。

### Hi-C 可视化、细菌组装与遗传图谱工具补读

本节和[第三批机器账本](sources/software_manual_issue_review_2026-11-10_round3.json)更新前文待办状态。全程只读；没有运行软件、流程或测试。上游版本和 issue 状态均按本轮页面观察记录，不代表本地安装版或当前仍开放状态。

- **Unicycler**：README、`unicycler/unicycler.py` 入口及 release 页面已读。定位为细菌短读/长读/混合组装；调试优先保留 `assembly.gfa`、`assembly.fasta`、`unicycler.log`，需要时用 `--keep 3` 留下 SPAdes 与桥接中间件。`--spades_path` 应指向 `spades.py` 可执行文件；不宜将其泛化为大型真核组装器。上游 release 页列 v0.5.1，本地版本未知。[#39](https://github.com/rrwick/Unicycler/issues/39) 报告把 SPAdes 路径给成目录导致依赖查找失败；[#313](https://github.com/rrwick/Unicycler/issues/313) 报告 depth=0 时除零；[#348](https://github.com/rrwick/Unicycler/issues/348) 只核到 issue 列表标题/状态，正文取回失败。
- **GPhase**：README 和主要源码目录已读；此前已有静态源码快照 commit `a9221035274e7397fc05dc5be693270c2758528c`，但不是安装版本证据。核心输入必须是与原始 hifiasm `p_utg.fa` 完全对应的 `p_utg.gfa`，不能重命名、过滤或先 polish/scaffold；Hi-C/Omni-C/Pore-C/CiFi 支持路径各异，HiFi用于 collapsed-unitig copy-number 估计。输出需对照 FASTA、AGP、映射表核验；染色体/单倍型标签不表示跨染色体全基因组相位。[#26](https://github.com/panlab-bioinfo/GPhase/issues/26) 报 30.7 Gb/249,650 unitig 场景在 partig minimizer 阶段 SIGSEGV，维护者未测试该规模；[#25](https://github.com/panlab-bioinfo/GPhase/issues/25) 是绝对 `output_prefix` 导致 BAM/BAI symlink 相对路径错误；[#23](https://github.com/panlab-bioinfo/GPhase/issues/23) 说明当前 popcnv 的 HiFi 估计边界。#3/#5 正文取回失败。
- **ALLMAPS（JCVI assembly 模块）**：阅读 JCVI wiki、`jcvi.assembly.allmaps` 代码入口和使用步骤；它不是独立仓库。优先检查 marker ID/坐标与输入 FASTA 对应、统一 BED/LG 坐标、pivot map 权重是否可信，以及 anchored/oriented/unplaced 汇总。旧 wiki 的 Biopython 1.70 安装钉版不能不经核对照搬。JCVI [#179](https://github.com/tanghaibao/jcvi/issues/179) 是导入路径/环境混用；[#160](https://github.com/tanghaibao/jcvi/issues/160) 显示 Concorde 失败后可回退默认排序并继续产出，需区分可选优化器降级与全流程失败；无独立 ALLMAPS issue tracker。
- **JuicerTools**：官方 README、FAQ 和 HiCCUPS 配置 issue 已读。本地矩阵的 v3.0.0 只来自 release metadata，未检 JAR/源码/运行。`pre` 与 `addnorm` 应确认使用相同代际 JAR；KR normalization 缺失可能是区域不收敛。Juicebox [#1031](https://github.com/aidenlab/Juicebox/issues/1031) 记录 v2.20.00 对 assembly size `2147483648` 抛 `NumberFormatException`、`2147483647` 可通过；关闭状态不是修复证据。
- **Juicebox / JBAT**：官方手册和仓库 README 已读；本地版本与运行状态未知。交互修订依赖对应 `.hic`/`.assembly`，导出后还需校验 AGP/FASTA。代表问题包括 [Juicebox #991](https://github.com/aidenlab/Juicebox/issues/991)（可加载但编辑交互失效）、[#972](https://github.com/aidenlab/Juicebox/issues/972)（剪刀指针缺失）和 [Juicer #337](https://github.com/aidenlab/juicer/issues/337)（写 `.hic`/normalization 时 NullPointerException；需收集输入与 `PRE_C_SIZE` 日志）。
- **PretextView**：README/release/issues 已读，本地版未知；官方当前 release 页列 v1.0.7。它支持 `.pretext` 图审阅、编辑和 AGP 导出；小于单 texel 的序列可能无法从 AGP 导出，可用随附 `AGPCorrect` 按输入 FASTA 修正。大染色体编辑 segfault [#61](https://github.com/sanger-tol/PretextView/issues/61) 与 ultra map 加载崩溃 [#79](https://github.com/sanger-tol/PretextView/issues/79) 均为具体环境报告，排查时记录 map 类型、GUI进度、系统/显卡/驱动和日志；issue 页显示新建问题受限。

至此，coverage matrix 中本轮列出的软件均已获得至少一项官方文档/入口与针对性 issue 状态核查；这不是源码全审、完整 issue 历史审查或本地可运行性验收。仍有上文明确标记为无法读取正文/未确认 tracker 的单条记录，遇到相关故障应再打开原始线程核实。
