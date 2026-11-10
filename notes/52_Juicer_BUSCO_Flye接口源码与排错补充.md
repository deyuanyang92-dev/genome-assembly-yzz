# Juicer、BUSCO、Flye：接口、源码与排错补充

日期：2026-11-02。复用本地07、21、34、45及Colora实测账本，再定向核查上游。新增阅读不等于新增生物运行；本轮没有重跑组装、BUSCO或人工审图。版本和源码SHA256见[来源账本](sources/core_tools_review_2026-11-02.json)。

## 1. 各组件应放在哪一步

| 名称 | 作用 | 版本证据与本地执行边界 |
|---|---|---|
| Juicer pipeline | Hi-C比对、处理、去重、统计及图谱生成的流程 | 稳定release页标1.6；本地固定commit f866383d66f780d98de2c1267703b4d3473f6250。本轮重读CPU入口选项/阶段/输出；未执行整套Juicer |
| JuicerTools | Java命令行工具，包含生成/处理.hic等操作 | 官方release API返回v3.0.0，发布时间2021-12-19；并非Juicer pipeline版本号，也不能据当前发布页假定适配所有JBAT流程；未执行此JAR |
| Juicebox / JBAT | 联系图查看及组装人工审阅 | 独立软件和版本；本轮未新核实GUI发布版，未完成GUI校正实操 |
| YaHS附带`juicer pre/post` | YaHS到JBAT的准备/坐标转换及审阅结果恢复 | 不等同于上述pipeline/Java工具；此前完成未编辑AGP往返测试，不等于运行过JuicerTools或完成GUI人工审阅 |
| 3D-DNA | Hi-C挂载/修正及审阅后重建的候选流程 | 既有07记录固定201008分支；不能将该分支和论文常用180922混为同版；本轮未更新全部源码 |
| BUSCO | 指定谱系保守基因的完整度评价；基因组/转录本/蛋白模式有区别 | 既有Colora测试实际运行6.0.0；此次按6.1.0文档及标签源码复核，不冒称6.1.0已安装运行 |
| Flye | CLR/ONT等长读及其支持模式的组装器 | release2.9.6；完整commit 886b8c17412cdf3a2868a28237bca6c5ad1da156；此次部分入口/手册阅读，新增运行0次 |

来源：[Juicer发布页](https://github.com/aidenlab/juicer/releases)、[JuicerTools API](https://api.github.com/repos/aidenlab/JuicerTools/releases/latest)、[BUSCO手册](https://busco.ezlab.org/busco_userguide)、[Flye发布页](https://github.com/mikolmogorov/Flye/releases)。不同工具版本不能由同一套流程的版本号推定。

## 2. Juicer：软件输入和组装证据要同时正确

本轮核查`pipelines/aidenlab_juicer/CPU/juicer.sh`：

- `-z`指定的FASTA与`-p`长度文件必须同源；限制性位点文件若适用，也须对应同一FASTA。参考改变后重建对应索引和图谱，不以相同文件名判断兼容。
- getopts和阶段选项以所选CPU/集群脚本实际实现为准，不能把SLURM脚本参数照搬到CPU版。调度队列、module、线程和Java内存单独审查。
- 新运行遇到已有aligned输出目录会退出。恢复要核对已完成产物与所选`-S`阶段，不通过删除旧目录掩盖输入/缓存不一致。
- 该固定CPU版`-e`/early模式在统计计算之后退出，不生成最终.hic；帮助文字与实际执行位置需要区分。缺少.hic是否失败取决于请求的阶段。
- 经典版`merged_nodups.txt`、Juicer 2开发版的BAM/merged1/merged30等产物不能凭后缀互换。Juicer 2的`--assembly`接口属于另一实现，既有07记载的历史main提交不能当作今天最新HEAD。

排错实例：[Juicer #350](https://github.com/aidenlab/juicer/issues/350)正文展示合并`.pairs.gz`后遇到“列数不符”，随后出现“没有有效reads/可能MAPQ太高”。可见页面未提供明确修复结论。**先检查第一处格式失败，而不是按最后提示自动降低MAPQ。** 检查真实压缩格式、列结构、坐标约定、同一参考字典、排序要求和命令是否成功；`sort -m`要求输入已按相同键排序，也不负责正确解压文件。上述是可证伪的检查路径，不是已复现该用户故障的确诊。

对新组装，Juicer比对参考通常是本次草图，而不是随意选的近缘物种参考。后续连接还要看有效独立分子、唯一可定位区域、文库类型、跨个体关系和图谱结构；输出文件成功生成不代表Hi-C确实改善了组装。

## 3. BUSCO：固定可比较条件

比较S0、purge后、挂载后和注释后结果时，锁定软件/依赖、输入FASTA角色、谱系名称、数据库代际与创建日期、模式、预测后端及参数。选择当前列表中与物种分类相符的合适具体谱系，不把旧笔记某个库名称当作所有环节动物的永久规定。

`C=S+D`；C/S/D/F/M和总marker数均保存，附`full_table.tsv`、missing列表、summary JSON和各后端日志。genome模式和proteins模式不直接混为同一评价：前者受预测后端影响，后者受提交的基因模型/异构体选择影响。两hap联合后的D较高不能直接触发去冗余。

6.1.0手册的重要兼容约束：odb12.2需要BUSCO≥6.1.0；不能用已运行过的6.0.0直接评价新库并假设兼容。旧odb10、odb12与odb12.2的分类规则和marker集合不完全相同，分数变化可能来自数据库或算法，不一定是组装变好/变坏。真核genome模式默认Miniprot，不能沿用旧版默认MetaEuk的假设。[官方说明](https://busco.ezlab.org/busco_userguide)

### 独立动作与无输出排查

固定6.1.0的`run_BUSCO.py:main`先执行绘图后退出；若无绘图，则执行下载动作后退出；仅无这些动作时进入BuscoMaster分析。`Actions.py`负责保存动作参数，不能只读此文件就误以为会完成分析后再绘图。

因此下载/分析/绘图分成不同命令；不要把`--plot`、`--download`与正式分析选项堆在一起期待全部执行。分析模板（未执行，具体路径和谱系必须按项目选择）：

```bash
busco -i assembly.fa -m genome -l /absolute/path/pinned_lineage \
  --offline -o sample_S0 --out_path results/busco -c 8
busco --plot results/busco
```

不默认`-f`覆盖旧结果。离线自动谱系选择还涉及额外资源，不能仅预下载一个谱系就保证auto-lineage成功。保留下载索引/创建日期/校验值；404不等于软件坏了，更不能静默换库。

### 手册与实现存在疑问时怎么办

[BUSCO #855](https://gitlab.com/ezlab/busco/-/issues/855)询问6.1.0对odb12.2使用目标蛋白长度`tlen`还是HMM匹配长度。下载的6.1.0 `hmmer.py:_sort_matches`确实在存在lengths_cutoff的分支把size设为`tlen`；另有margin常量与注释/手册描述需要进一步对照。可见issue正文没有维护者澄清，**不能据此宣称已确认bug、擅自修补阈值或重写上游评分**。记录版本、库文件、候选marker及代码位置；未来用最小例子核查，并区分上游算法问题与用户组装缺失。

### 本地已执行的是什么

Colora账本保存BUSCO6.0.0四套离线结果和成功日志；下载库为`saccharomycetaceae_odb12`、日期2026-05-22，并记录官方MD5。测试是约1.25 Mb子集、跨菌株Hi-C，不能将低BUSCO解释为全物种缺基因，也不能把功能测试成功当成质量达标。证据见[Colora实测收尾](../tests/colora_functional_2026-11-01/notes/06_完整Colora功能测试与软件账本.md)。

## 4. Flye：理解阶段和模式

Flye将长读信息组织为repeat graph，入口支持的读段模式有各自错误模型；这与普通二代de Bruijn图组装路线不同。不能因为FASTA格式相同，就把Illumina数据放进`--pacbio-hifi`。

固定2.9.6源码和手册核查结论：

- 输入类型是互斥组；入口说明不支持直接混合不同read类型。多文件同类型输入与混合平台不是一回事；HiFi＋ONT应选明确支持该组合的流程。
- `--asm-coverage`需同时提供`--genome-size`，且与`--meta`不兼容。它选最长reads用于初始disjointig阶段，不等于全流程下采样，也不代表后续阶段的数据充分性。手册的40×是阶段性经验起点，不是所有物种最终验收标准。
- `--keep-haplotypes`在源码中影响过滤，保留等位替代路径不等于完整染色体分相；普通Flye二倍体输出可能是mosaic/collapsed表示。
- `--meta`面向非均匀覆盖/群落模型，不因单物种组装难就自动开启；先核查覆盖、污染、倍性和文库偏倚。
- `--resume`与`--resume-from`依赖中间文件及阶段状态；修改输入/模式后另开对照并追踪影响，不能将存在状态文件视为科学上可复用。
- 2.9.6发布记录修复polishing罕见竞争问题，并调整nano-hq默认为R10参数。旧版经验参数不无条件搬到新版；不自动对所有运行追加polish。

依据：[固定版手册](https://github.com/mikolmogorov/Flye/blob/2.9.6/docs/USAGE.md)、[固定入口](https://github.com/mikolmogorov/Flye/blob/2.9.6/flye/main.py)、[方法论文](https://pubmed.ncbi.nlm.nih.gov/30936562/)。本轮只核查入口与阶段说明，未审完整C++图算法，未执行Flye故障复现。

## 5. 进入诊断库的范围

新增DBG019–DBG026设计记录覆盖：Juicer字典/阶段/格式，BUSCO动作/版本数据库/评分疑问，Flye阶段覆盖与表示模式。规则在[机器配置](../config/software_diagnostics_knowledge.json)中，仍是待实现、待回归验证的知识，不是已部署的自动诊断器。
