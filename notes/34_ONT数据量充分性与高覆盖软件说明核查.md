# ONT数据量充分性与高覆盖：软件说明核查

核查日期：2026-11-01。本文区分官方参数事实、工程建议和未验证的生物学判断。已核查5种组装工具的指定说明/部分源码；没有运行真实ONT样本或覆盖梯度组装。完整仓库仍26个，本轮另有4份ONT手册/源码快照，不计新增完整流程。

## 1. 什么叫ONT足够

先确定用途：ONT-only主体组装、HiFi组装的普通ONT补充、超长ONT解重复、追求T2T是不同问题。不是输入文件达到某个Gb就足够。

- 以目标个体、质控后、去除已确认非目标核序列并避免分子重复计数后的碱基量D，除以单套核基因组大小G：C=D/G；同时保存原始量。有效量或G未知则待评估，不能填达标。
- G有区间[Gmin,Gmax]时报告覆盖区间[D/Gmax,D/Gmin]；存在有效量区间也要传播。二倍体均衡的总50×平均约每hap25×，不代表每个位点足量。多倍体、性染色体、混样另行处理。
- 分开列总有效ONT覆盖、≥50kb/100kb/200kb碱基量与覆盖、read N50、长度分布和质量分布。这些是嵌套累计，不能相加。800Mb核基因组有80Gb ONT是100×，但若≥100kb只有8Gb，其该档长尾只有10×。
- 区分普通R10 simplex、duplex和ultra-long；记录建库、basecaller模型/版本、准确度、过滤留存率、批次/个体。duplex和parent不能重复统计为独立支持。
- 判断的是有效核覆盖和关键区域支持，不是线粒体超高覆盖、污染或PCR/计算重复造成的总量。

EBP当前建议的ONT主体组装规划量为每hap >20×、read N50约50kb；二倍体按D/G约>40×。这不是所有物种的质量保证。本项目如采用HiFi主路线，用户要求的有效HiFi≥50×仍独立执行，ONT不能补算。EBP的T2T示范配方进一步列出HiFi >60×、ultra-long ONT >40×、Hi-C >50×，应按原文口径和平台条件理解，不能把其中UL40×当成所有项目的通用充分条件。[EBP建议](https://www.earthbiogenome.org/report-on-assembly-recommendations)

## 2. 重复区域需要的是能解决歧义的分子

总覆盖高不等于有足够长的reads。检查目标重复长度、两侧可唯一定位的锚点、符合质量要求的独立分子及其对图路径的支持。20kb reads增加很多也不会直接成为跨越80kb重复及两侧锚点的单分子；其他变异/图证据仍可能帮助解重复，不能把没有全跨越read当作必然无法组装。

仅用于理解的均匀随机起点近似：对一个拷贝、重复加两侧锚点总跨度S，预期全跨越数约sum(max(Li-S,0))/G。混合的均衡二倍体若只讨论一条hap还需约除2。该式忽略端点离散效应、提取断裂偏倚、多拷贝/比对歧义，不是软件验收指标，更不能替代真实支持数。

初装后把ONT回贴到与FASTA/GFA版本一致的组装，检查局部有效深度、图分支、重复/着丝粒附近断点、锚定可信度及分子一致性。缺少唯一锚点应标记无法判断；read本身太短时，未跨越不是负证据。组装使用过的reads是自洽证据，并非完全独立的结构真值。联合k-mer完整性/QV、污染、塌缩/重复、相位和Hi-C结构检查，见21、27、30。

## 3. 五种软件如何使用高覆盖数据

| 工具与本轮版本/范围 | 官方参数实际作用 | 不能做的解释 |
|---|---|---|
| hifiasm 0.25.0-r726，固定ec9a8b222d149d25b7355e83765698640d59b189；CLI、man、参数文档、部分实现 | ONT-only用--ont；HiFi加UL用--ul。--ul-cut是UL最短长度，默认0；--ul-rate是UL比对误差容忍。-D控制高频k-mer筛选，-N限制重叠保留；--hom-cov是覆盖估计设置 | -D不是把输入降到D×；--ul-cut不是覆盖；不能把--ont的Q/长度过滤假设自动套到--ul。核查范围未找到适用于所有ONT的硬性最大覆盖 |
| Verkko 2.3.2，固定39e9fb22816da30b22426ad1914034bc3a2d0cfa；README、verkko.sh、部分Snakefiles/脚本 | --split-bases/--split-reads控制拆批；--hifi-coverage默认25传入MBG建图参数；后期提取参与补洞的ONT子集 | 拆批不是全局下采样；25不是输入只用25×；后期提取不是前期已限总ONT量。release中>200×导致MBG/磁盘压力、建议100×的警告明确指HiFi，不能改写成ONT上限 |
| Flye 2.9.6，固定886b8c17412cdf3a2868a28237bca6c5ad1da156，docs/USAGE.md | --asm-coverage选择最长reads用于初始disjointig组装，官方通常建议40×；需配合--genome-size。后续如重复解析仍用全部输入 | 40×不是最终所有阶段只用40×，也不是用户数据充分性门槛；只降低初始阶段负担不保证后续资源也受相同上限控制 |
| Canu：在线2.2参数文档与固定HEAD f96a4a2d2aa20fc1f461e877a437c4a92acc4e53的Defaults/SequenceStore；两者版本口径分列 | corOutCoverage默认40是选择待校正长reads的目标；maxInputCoverage是输入阶段覆盖限制，readSamplingBias影响长度偏向；stopOnLowCoverage默认10是软件停止规则 | corOutCoverage不是所有证据reads只留40×；10×不是合格组装标准。当前Defaults里maxInputCoverage声明值undef而说明写200，本轮未追完动态赋值，不能宣称已核实所有模式默认200 |
| NextDenovo：官方OPTION与固定0e5fa5dae1d0afa33846ff8ad87287ccbe5a1146示例run.cfg | genome_size参与深度与seed cutoff估算；seed_depth默认45，文档建议30–45，用于种子；read_cutoff默认1k是读长；blocksize是分块 | seed_depth不是原始输入45×上限，也不是所有项目的最低数据量；blocksize不是删掉超额reads。ONT配置应设置匹配的read_type，不能照抄clr模板 |

官方入口：[hifiasm](https://github.com/lh3/hifiasm)、[Verkko releases](https://github.com/marbl/verkko/releases)、[Flye USAGE](https://github.com/mikolmogorov/Flye/blob/flye/docs/USAGE.md)、[Canu参数](https://canu.readthedocs.io/en/latest/parameter-reference.html)、[Canu FAQ](https://github.com/marbl/canu/blob/master/documentation/source/faq.rst)、[NextDenovo参数](https://nextdenovo.readthedocs.io/en/latest/OPTION.html)。

Canu官方FAQ也说明提高最短长度/重叠过度会损失有效reads/重叠，降低组装质量；高覆盖相关误差阈值建议有其旧平台与算法背景，不能当作当前所有R10数据的一致配置。最长reads选择在非均匀覆盖时也可能损失小片段/低覆盖区域，不能无条件套用。

## 4. 很多数据会不会干扰

没有一个已核实的跨软件“超过100×就组错”的定律。更多同个体、合格且有新增信息的reads通常有帮助，但收益可饱和，CPU/RAM/磁盘会增加。加入污染、较差准确度批次、嵌合、重复分子、错误个体或极端不均匀覆盖，可能加重误比对、假重叠或错误覆盖估计；这是需检验的机制，不是已对用户数据确认的诊断。

资源问题、结果饱和、实际质量下降应分开报告。进程OOM/磁盘满不等于生物学组装错误，N50变大也不证明质量更好。

建议先QC并核实G/个体；优先使用软件已有的阶段选取与拆批机制。确需外部选取时保留原始文件、被排除清单、随机种子、实际保留碱基/长尾覆盖，不按read条数假称精确X覆盖。纯随机选取会同步损失UL尾部；只留最长又可能引入区域/质量偏倚，应按目标评估并考虑长度/质量分层。

若怀疑高覆盖有害，选择预算允许的2–3个覆盖档加全量对照，固定软件/参数和HiFi、Hi-C，复核实际ONT长尾、核比例和质量分布。避免把“改变覆盖”与“只取最长/更高质量”混为单一因果。比较可靠k-mer完整性/QV、长度总量、塌缩/冗余、关键区域支持、相位、Hi-C冲突与资源；部分重复seed评估不稳定性。未获独立证据前，只能报告某档在当前指标更优/更省资源。

## 5. 可执行模板与开发缺口

下面仅为Flye ONT-only适配模板，800m为示例G、40是该软件初始阶段目标；未执行，不适用于HiFi/ONT混合输入。R10高准确度模式须先核查误差范围。

```bash
flye --nano-hq ont.qc.fastq.gz --genome-size 800m --asm-coverage 40 \
  --threads 32 --out-dir flye_ont_run
```

未来QS011：复用QS001/QS007，按用途/软件版本生成覆盖区间、长尾和局部证据报告，区分“规划量不足”“长尾不足”“区域证据不足”“未知”“资源过量/收益饱和”；软件阶段阈值不可冒充质量通过。梯度试验需显式预算，原始数据不得自动删除。当前没有实现自动判定器，也没有用户样本可做充分性结论。

快照、版本和边界见[sources/ont_coverage_manual_review.json](sources/ont_coverage_manual_review.json)。
