# 软件说明书、issues 与源码诊断知识库

核查：2026-11-02。用途：后续组装软件开发与故障定位。**当前是知识库和开发规格，尚未实现自动诊断器。**

## 1. 已学习到什么程度

之前已有说明书、参数和部分源码阅读，见[20](20_源码追踪与能力验证.md)、[28](28_基因组调查源码与脚本使用说明.md)、[34](34_ONT数据量充分性与高覆盖软件说明核查.md)、[36](36_去冗余软件说明书与参数核查.md)。此前没有统一的 issue 诊断库，不能称已系统读完各软件全部 issues 或源码。

本轮定向核查 **6 个核心项目、10 个具体 issue 主题**：hifiasm #742/#756/#798；Verkko #224/#308；YaHS #119/#120；HapHiC #87/#174；purge_dups #166。Sanger 使用 changelog 与本地模块源码，未把打不开的 PR #159 计为已读。issue 的公开正文/可见讨论已读，附件和分页隐藏评论未完整取得；不是全量历史审查。#122、Verkko #367 仅发现链接而正文访问失败，不计已读。

核查上游当前发布信息与本地固定源码分开记录：

| 工具 | 本轮上游可核实的发布版本 | 实际阅读的本地 commit | 范围/注意事项 |
|---|---|---|---|
| hifiasm | 0.25.0-r726 | ec9a8b222d149d25b7355e83765698640d59b189 | README、CLI、缓存入口及指定函数；与 release 一致，未通读所有图算法 |
| Verkko | 2.3.2 | 39e9fb22816da30b22426ad1914034bc3a2d0cfa | README、verkko.sh 的配置与 Snakemake 启动段；未遍历全部依赖内部算法 |
| YaHS | 1.2.2 | 6c46061ea1665073068cccbed81c6707e3bd07bf | version.h 标记1.2.2；是 release 后源码，发布页指向9b2cc15，不能说两者相同 |
| HapHiC | 1.0.7 | 74f1cb27d7753ce061ee673c0d62fdd44187060e | 源码内部更新日期2025.10.30；release 指向df0f5ac，main 后续修改仍标1.0.7 |
| purge_dups | 1.2.6 | f14dae13b7f41559bafd058f7278e8f5ac2813da | release 指向e2a94b6；本地是后续提交；README、cutoff读取、get_seqs选项及既有提取测试 |
| sanger-tol/genomeassembly | changelog最新列1.0.1（2026-09-11） | 131f0ea272bb2fce9869d57f684f20f645467e34 | 本地manifest1.0.1；release端点访问失败，以changelog为据，不声称完整API枚举 |

“最新”仅表示本次官方页面能核实的发布信息，不代表main HEAD，更不保证搜索缓存实时。新项目应选固定稳定版并记录其依赖锁，不自动追main。未覆盖所有全基因组软件；其他工具仍按既有笔记版本使用，首次纳入生产前补同样审查。

官方发布入口：[hifiasm](https://github.com/chhylp123/hifiasm/releases)、[Verkko](https://github.com/marbl/verkko/releases/tag/v2.3.2)、[YaHS](https://github.com/c-zhou/yahs/releases)、[HapHiC](https://github.com/zengxiaofei/HapHiC/releases/tag/v1.0.7)、[purge_dups](https://github.com/dfguan/purge_dups/releases/tag/v1.2.6)、[Sanger changelog](https://github.com/sanger-tol/genomeassembly/blob/main/CHANGELOG.md)。精确文件SHA256和读取范围见[机器账本](sources/software_debug_review_2026-11-02.json)。

## 2. 具体问题如何用于排错

下表的检查与软件设计属于本项目推导；没有把上游讨论当作本地复现。完整结构化条目见[诊断规则草案](../config/software_diagnostics_knowledge.json)。

| ID / 场景 | 已查到的事实与证据等级 | 检查顺序和处理边界 |
|---|---|---|
| DBG001 hifiasm加载旧bin | 固定源码Assembly.cpp:2062和Overlaps.cpp:23590按prefix加载纠错reads/overlaps；0.25发布建议ONT升级后从头运行 | 包装层比对reads身份、模式、参数、程序/依赖摘要；变更时另建运行目录。不能见到bin就复用，也不默认删除旧文件 |
| DBG002 hifiasm段错误 | [#798](https://github.com/chhylp123/hifiasm/issues/798)：作者先怀疑OOM，用户反馈内存未耗尽；另一个用户同时转换压缩格式并剪切后成功 | 先取调度器OOM/退出信号、stderr、压缩magic和完整性、FASTQ记录/配对，再查二进制/版本。**segfault不等于OOM**；转换和剪切同时发生，不能确证单一原因 |
| DBG003 大数据纠错内存高 | [#756](https://github.com/chhylp123/hifiasm/issues/756)为用户询问分批纠错可否拼回，当前可见页无确认方案 | 先估G、有效量、质量、批次、资源；不自动将独立批次bin或纠错结果拼为等价全量组装。下采样另开对照并保留reads清单 |
| DBG004 ONT模式错误 | [#742](https://github.com/chhylp123/hifiasm/issues/742)可见答复区分R10 simplex带质量值和预纠错数据；0.25发布增加内部过滤并修正重复相关错误 | 记录basecaller/chemistry/纠错历史/FASTQ质量，分清--ont与HiFi+--ul。历史参数建议不自动套到所有新数据 |
| DBG005 Verkko未知--reason | [#224](https://github.com/marbl/verkko/issues/224)报告Snakemake8参数不兼容；2.3.2 release要求>=7,<8；启动源码仍传--reason | 启动前校验依赖锁。此固定版使用兼容7系；不要只删除一个未知参数后假定全流程兼容 |
| DBG006 Verkko恢复重跑 | [#308](https://github.com/marbl/verkko/issues/308)维护者说明--paths/--assembly受时间戳影响，建议先dry-run | 归档原工作目录，在新目录预演DAG，核对计划仅运行预期后段；禁止自动touch全目录或删原装配。需要核查时间戳和内容hash两者 |
| DBG007 磁盘/配额满 | 同[#308](https://github.com/marbl/verkko/issues/308)中Errno122经用户确认是工作目录之外空间不足 | 查工作目录、TMPDIR、实际用户缓存/日志路径的容量、inode及配额；df有空间不代表quota可用。释放空间须给出具体文件和影响，不能无差别清理 |
| DBG008 YaHS BAM排序 | 固定README NOTE1及bamlite.c:163、link.c:1281：按header排序类型分支，非name排序MAPQ行为不同 | 校验header和实际记录排列；本项目统一生成可追溯的name-sorted输入以控制行为，但不能说YaHS一律拒绝coordinate BAM |
| DBG009 YaHS缺少参数 | [#119](https://github.com/c-zhou/yahs/issues/119)用户报告镜像标1.2却缺--telo-motif；无已证实修复 | 查实际PATH程序、容器digest、--version及help的功能探针；不要仅比对镜像标签，也不要直接将用户报告判为官方镜像bug |
| DBG010 YaHS 1.2.1 juicer post | 1.2.2 release明确修复1.2.1引入的问题，1.2及更早不受此特定bug影响 | 若使用1.2.1人工校正恢复，应在固定新版另目录恢复并校验AGP/FASTA及liftover身份。不能宣称升级会改变或修好所有挂载结构 |
| DBG011 挂载后QV骤降 | [#120](https://github.com/c-zhou/yahs/issues/120)：维护者要求前后统计；一位用户反馈展开FASTA换行后恢复，未定位具体解析器和版本 | 同reads数据库/k/阈值复算；查工具是否完整退出、输入身份和非N碱基/AGP重建。必要时只改换行后复算，逐条序列归一hash应相同；不得立刻追加polish或称Merqury普遍不支持多行FASTA |
| DBG012 HapHiC坐标排序输入 | 固定README明确要求name排序；这与YaHS不同 | 进入昂贵任务前阻止不符输入并给出另存的samtools sort -n命令；排序临时空间/内存单独预算 |
| DBG013 HapHiC校正后AGP错误 | HapHiC_build.py:260–268有原始/校正FASTA与--corrected_ctgs组合检查 | 保留原FASTA、校正FASTA、断点表、raw.agp坐标身份；不把corrected.fa当raw.fa使用；文件名相同仍需内容hash核查 |
| DBG014 HapHiC聚类数不符 | README FAQ列inflation、同源/组装错误和染色体长度差异等原因；[#174](https://github.com/zengxiaofei/HapHiC/issues/174)是放宽MAPQ后挂载率高但出现巨组的用户报告，无可见解决答复 | 检查nchrs适用性、倍性、过滤前后有效对、图谱冲突；小范围参数对照/quick_view供审查。不能自动放宽MAPQ或强凑nchrs并算通过 |
| DBG015 refsort误解/同版本变更 | [#87](https://github.com/zengxiaofei/HapHiC/issues/87)维护者解释只整体调scaffold顺序方向、不改内部；当前本地README记录后续ID命名变化 | 精确commit决定ID规则；保留命名映射、来源和图谱。不能把参考排列当结构独立验证或自动修复scaffold内部错误 |
| DBG016 purge过度或几乎不删 | 官方README警告低杂合度cutoff可能偏大及ID中冒号问题；[#166](https://github.com/dfguan/purge_dups/issues/166)报告删掉大量序列但BUSCO相近，无明确答复 | 画覆盖直方图、复核产品/倍性、k-mer拷贝与丢失、被删序列；不能BUSCO没降就认为安全，不能按同物种别人的cutoff硬套 |
| DBG017 get_seqs内部删除 | 本地帮助默认-e关闭，README推荐显式-e只处理端部；见既有36/38和提取合成检查 | 参数必须显式；端部也需证据；保留removed/hap FASTA与BED。既有合成测试验证提取语义，不验证生物学冗余判断正确 |
| DBG018 Sanger假成功/旧接口 | conf/modules.config:64的MerquryFK errorStrategy=ignore；YaHS最终FASTA/AGP optional；changelog记录样本表改版 | 每个必需产物设独立验收和缺失状态；旧--input不可照抄。缓存ID不能替代输入内容hash；记录QC失败原始原因，Nextflow成功不等于项目验收通过 |

## 3. 自动诊断器的实现要求

1. **运行前预检**：物种/个体/倍性/产品角色，选择HiFi路线时有效HiFi覆盖≥50×，不同个体Hi-C身份；格式实际内容、reads配对、BAM与FASTA字典、版本功能探针、依赖及空间。覆盖未知标待评估；二代量不能补算HiFi。
2. **运行时采证**：argv数组（可脱敏）、运行ID、容器digest、环境锁、stderr/stdout、调度器jobid/State/ExitCode/MaxRSS/ReqMem、磁盘/配额与任务阶段。只看到137/139不能确诊OOM/软件缺陷，需额外证据。
3. **诊断输出**：规则ID、精确版本适用性、症状、事实证据、排序的候选原因、能证伪的下一步检查、建议操作、重跑范围和验证办法。区分确定/可能/证据不足；缺资料时不编造根因。
4. **恢复与重试**：输入/依赖/科学假设不变、已确认短暂基础设施故障才允许有次数上限的重试；格式、版本冲突先修复；purge、放宽过滤、改变phasing、改变科学参数只开新分支，不静默修改。不要自动通过删除缓存来“修复”。
5. **结果验收**：检查文件非空且可解析，AGP区间/方向和FASTA内容一致，阶段坐标/源hash一致，QC使用固定证据。成功退出不等于结果正确；科学冲突需要人工审阅。
6. **回归用例**：每条规则后续应有阳性/阴性日志fixture、近似错误消息不能误判的反例，以及新旧工具版本边界测试。生物学操作另需真实小样或官方样例；本轮没有把规则草案包装为已运行诊断器。

不收集凭证、无关用户路径或完整人类敏感reads进诊断包。运行数据按项目权限保管，诊断包优先保留必要统计和脱敏日志。

## 4. 后续扩大覆盖与版本更新

将GenomeScope2/FastK/KMC、minimap2/bwa-mem2/chromap/samtools、Merqury/MerquryFK/BUSCO、污染检查、Flye及选定注释引擎纳入同一账本。旧工具仅在实际流程有依赖或需复现时保留，不为“新”替换已验证实现。

每个生产依赖必须具备：官方来源→固定tag+完整commit→容器/二进制摘要→文档接口→高影响open/closed issues与fix release→指定源码函数→官方小例→故障回归→真实数据边界。条目增量更新，不能承诺一次学习后永远不用查新版。

本轮源码/issue学习没有新增完整流程端到端实测，也没有复现以上真实故障；机器账本只验证记录完整性。最近两年规范论文续读见[47](47_最近两年组装规范论文续读.md)，HiFi/二代G估计比较见[46](46_二代与HiFi估计基因组大小的比较.md)；各自阅读范围单独计数。


## 2026-11-02 接口补充

在本页原6项目/18规则的阶段记录之上，新增Juicer、BUSCO、Flye的选定手册/源码核查，见[52](52_Juicer_BUSCO_Flye接口源码与排错补充.md)。总诊断设计记录现为26条，DBG019–026本地未复现、禁止自动修复，不是已实现诊断器。软件版本和来源另入账。选择HiFi路线时执行用户有效HiFi≥50×要求；其他数据路线按自身证据评价，不因没有HiFi拒绝。
