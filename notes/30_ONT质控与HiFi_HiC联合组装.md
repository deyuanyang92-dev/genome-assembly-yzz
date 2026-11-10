# ONT质控、单平台组装与HiFi/Hi-C联合组装

2026-11-01。基于本地hifiasm 0.25.0-r726（ec9a8b2）、Verkko v2.3.2（39e9fb2）、新增NanoPlot/chopper固定源码和官方资料。无用户真实数据，尚未跑通ONT或三类数据联合实例。旧[06 Verkko笔记](06_Verkko.md)中的旧机器路径不作为本机路径，当前源码均在本学习库pipelines下。

## 1. 数据角色与输入关系

| 数据 | 主要贡献 | 需要特别检查 |
|---|---|---|
| HiFi | 高准确序列、区分重复中的细微差异、构建组装图及共识 | 有效核覆盖≥50×仍是用户硬要求；局部覆盖、杂合/倍性与平台遗漏 |
| 普通ONT长reads | 提供不同长度/平台覆盖，可能补充HiFi遗漏区域 | 普通长read与ultra-long不能仅凭建库名称等同；记录长度×质量联合分布 |
| 超长ONT（UL） | 跨越长重复、连接唯一锚点，帮助解图和延长contig | 总量、≥50/100/200 kb各档的可用碱基量及目标区域桥接，不能只看最长read |
| Hi-C | 长程接触、染色体归组/排序/定向；同个体时可用于长程分型 | 文库有效pairs、重复/多重比对、样本个体与性别、结构差异；不能补出gap碱基 |

同一目标个体A的HiFi与ONT优先联合；不能默认把另一个个体B的ONT/HiFi并入A补足覆盖或补洞。Hi-C来自B时按[31的对照和逐连接审查](31_非同个体HiC贡献与干扰评估.md)处理，不直接套用同个体联合分型模板。ONT-only是另一条路线，不表示达到用户指定的HiFi50×门槛。

## 2. ONT质控的操作与判定

1. **身份与原始信息。** 记录个体、组织、提取/建库、barcode、flow cell/pore、试剂、采样速度、run ID、POD5清单/校验值、Dorado及完整model名称/版本。保留POD5和带标签BAM；仅有FASTQ则标记无法重basecall/部分标签丢失。
2. **Basecalling。** 根据实际化学选择兼容模型；组装优先评估SUP。正式运行固定完整模型或模型目录及校验值，避免`sup`自动随最新版变化。若已有合格basecall无需盲目重跑。Duplex与simplex分开记录，不能把同一分子的两条parent simplex和其duplex结果当三份独立覆盖。
3. **拆样/接头/嵌合。** 多样本先按正确kit拆样，接头修剪与拆样顺序按Dorado文档；Dorado默认修剪有kit适用范围。检查嵌合、内部接头和低质量段，保留处理日志；避免对超长reads一律固定截头尾，或为提升质量将全部长reads切成短段。
4. **统计过滤前后差异。** 每run/barcode记录read数、总bases、读长N50/中位数/分位数、长度–质量图、质量分布、保留率；另报≥50、100、200 kb的read数和bases。Q分数为basecaller预测，不等于真实比对错误率；比对identity也受参考错误/真实变异影响。N50与最长read不能单独代表可用性。
5. **按用途过滤。** chopper可按平均质量/长度过滤。阈值须结合模型、原始分布、组装器支持及桥接信息；本地hifiasm `--ont`默认短read阈值1000 bp、平均Q阈值10是该版本软件默认，不是通用最低标准，更不是所有UL混合输入的验收线。保留未过滤版本；过滤后重算长read档位覆盖。不要按固定GC区间自动删除真实偏GC核序列。
6. **污染与有效覆盖。** 分类命中、GC、深度和初装结果共同区分核/细胞器/共生体；未知有效核比例时不宣称有效覆盖达标。重复reads自然相似，不等于PCR重复；不能按相同序列机械去重。read ID/分段parent与duplex关系另行核查，避免重复导入。
7. **初装后回证。** 使用minimap2的匹配preset（普通噪声ONT常用map-ont；高准确ONT可按实测和官方文档评估lr:hq，HiFi用map-hifi）或适用的Winnowmap，检查局部缺口、分裂比对、重复区多重比对、异常深度和桥接。两hap竞争比对时注意MAPQ和等位序列，不能要求所有read只落一份hap。大基因组分段索引会影响MAPQ，需按工具文档配置。

### 覆盖口径和测序规划

`C_ONT,核 = D_ONT,有效核 / G`；`C_ONT,≥100kb = D_ONT,有效核且长度≥100kb / G`。各长度档为嵌套累计，不相加，长度都按过滤/拆段后的实际产物统计。进一步记录独立分子数、目标重复两侧唯一锚点、方向与比对可靠性；总体覆盖不能替代局部跨越证据。

例：G=800 Mb，ONT总80 Gb为100×，其中≥100 kb仅8 Gb则该长度档仅10×，不能称“超长100×”。若目标为带两侧锚点的120 kb区段，100 kb的read仍可能不够长，需检查更长尾部与真实路径。

EBP 2026给出的二倍体T2T规划示例是HiFi>60×、超长ONT>40×、Hi-C>50×；这是特定高级目标的数据建议，不能保证所有物种T2T，也不能把普通ONT总覆盖当作满足超长部分。实际采购需单列建库预期、实际长度分布及≥100 kb有效量，不用一个总Gb值验收。本项目HiFi最低50×仍保留，追求T2T时按更高目标规划。

## 3. 工具使用模板

以下为接口核查后的模板，未处理用户reads；先准备隔离环境。输入输出分开，新建专用工作目录，执行管道时启用`set -euo pipefail`。

```bash
# 已有POD5且确需basecall：模型目录须匹配实际化学，并提前固定版本。
dorado basecaller /models/compatible_pinned_sup_model /data/pod5 > calls.bam
# calls.selected.bam须已按拆样/duplex策略选择，避免parent与duplex重复导入。
samtools fastq -@ 8 calls.selected.bam | gzip -c > ont.basecalled.fastq.gz
seqkit stats -a -T ont.basecalled.fastq.gz > ont.before.stats.tsv
NanoPlot --fastq ont.basecalled.fastq.gz --loglength --tsv_stats -t 8 -o nanoplot.before

# 仅演示过滤接口；Q10和1000bp不是预先批准的生产阈值。
chopper -q 10 -l 1000 -i ont.basecalled.fastq.gz | gzip -c > ont.qc.fastq.gz
seqkit stats -a -T ont.qc.fastq.gz > ont.after.stats.tsv
NanoPlot --fastq ont.qc.fastq.gz --loglength --tsv_stats -t 8 -o nanoplot.after
# 按需计算长尾各档，stdin统计不保存大型中间FASTQ。
seqkit seq -m 50000 ont.qc.fastq.gz | seqkit stats -a -T > ont.ge50kb.tsv
seqkit seq -m 100000 ont.qc.fastq.gz | seqkit stats -a -T > ont.ge100kb.tsv
seqkit seq -m 200000 ont.qc.fastq.gz | seqkit stats -a -T > ont.ge200kb.tsv
```

NanoPlot是统计/绘图工具，不替代写出过滤reads的chopper。其`--maxlength`/`--drop_outliers`等会影响展示，`--minqual`会改变所分析的集合，不能用隐藏长尾后的图当作全量证据。SeqKit总bases与NanoPlot统计可交叉核查，差异须解释。FASTQ导出不保留BAM全部信息，原BAM/POD5应保留；修剪修改碱基后，甲基化及其他依赖原坐标的标签需重算，不能直接当仍然有效。

### 路线A：ONT单独组装

```bash
hifiasm --ont -t 32 -o ont_only ont.qc.fastq.gz 2> ont_only.log
```

此模板适用于固定版本支持的R10 simplex FASTQ，不把旧R9或任意ONT数据一概视为适用。组装后依然执行G/拷贝数/污染、k-mer QV和完整性、BUSCO、局部read支持与结构检查；必要时再选有验证依据的纠错/共识模型。只有普通噪声ONT时，不默认用未经评估的原始k-mer谱直接替代HiFi/二代GenomeScope调查。

### 路线B：HiFi＋UL-ONT＋同个体Hi-C，以hifiasm为主干

```bash
hifiasm -t 32 -o hybrid \
  --ul ont.ul.qc.fastq.gz \
  --h1 hic.R1.fastq.gz --h2 hic.R2.fastq.gz \
  hifi.qc.fastq.gz 2> hybrid.log
# 核对实际GFA文件、非空和S行内容后，分别导出两hap。
awk '$1=="S" {print ">"$2; print $3}' hybrid.hic.hap1.p_ctg.gfa > hap1.contigs.fa
awk '$1=="S" {print ">"$2; print $3}' hybrid.hic.hap2.p_ctg.gfa > hap2.contigs.fa
```

HiFi放位置参数，UL放`--ul`；此混合模式不因含ONT就加`--ont`，也不把两类FASTQ简单拼接交作HiFi。多批次文件列表按固定版帮助与样本清单传入，不错配Hi-C两端。保留原read ID及对应关系。不同模式使用独立前缀/目录，避免误用缓存。

这一步的Hi-C分型与染色体挂载分开评价；默认的hap contig输出不能直接称完整染色体。之后把Hi-C规范比对到对应装配、去重复/过滤，再用YaHS或适用的HapHiC挂载；保留两hap及unplaced，人工检查Pretext/Juicebox图。不能把所有hap拼成单份后按单倍体无差别挂载。hifiasm `--dual-scaf`是另一个可选方案，要单独记录引入的gap和同源信息；不默认开启，也不把scaffold当gap-free contig。端粒基序依物种确认，不机械用人的CCCTAA。

### 路线C：HiFi＋UL-ONT＋同个体Hi-C，以Verkko为主干

```bash
verkko -d verkko.hybrid \
  --hifi hifi.qc.fastq.gz \
  --nano ont.ul.qc.fastq.gz \
  --hic1 hic.R1.fastq.gz --hic2 hic.R2.fastq.gz
```

Verkko利用高准确reads建图、ONT解重复、Hi-C分型及挂载，最后生成共识。原始普通ONT不直接放`--hifi`；该参数还接受适用的Duplex/纠错后高准确ONT，必须明确预处理和数据重复关系。固定版不支持多倍体Hi-C分型/挂载，Hi-C模式不兼容`--haploid`，Hi-C与trio参数不能混用。非人类物种核查端粒、杂合、深度和rDNA假设，不能按默认人类设置解释所有结果。

保留`assembly.fasta`、`assembly.haplotype1.fasta`/`2.fasta`（有分型时）、GFA、paths/scfmap/colors与覆盖表。Verkko的HPC图坐标不是最终FASTA碱基坐标；局部验证需正确转换。Verkko已做scaffolding时，先评价实际输出，不默认再用YaHS重复挂载。没有分型输出不等于primary/alt产品。该源码未安装子模块/完整依赖，不是本机可直接运行的安装包。

## 4. 如何判断新增ONT是否有贡献

在同一HiFi、同一评价数据/参数下比较HiFi基线与HiFi＋ONT；若还要评估Hi-C，分别比较无Hi-C与有Hi-C，避免同时更换工具和数据后把变化都归因于ONT。报告新增gap-free序列、可靠k-mer/重复拷贝恢复、contig NG50变化、被解决的图分支/缺口，以及新增结构冲突、局部深度/分型问题、QV变化和资源成本。

ONT读段自己参与构建的连接再用相同reads验证是自洽性证据；需要同个体HiFi、留出ONT或其他实验增加独立支持。不能因N50变大就接受错误连接，也不能因BUSCO不变就说ONT无贡献（它可能主要改善重复区）。各hap与两hap并集的完整性口径分开，遵循[23高标准验收](23_EBP2026规范与本项目对标要求.md)。T2T逐条染色体核查无gap、适用端粒、重复/着丝粒拷贝与结构支持，不靠“有端粒＋高N50”宣布完成。

## 5. 收集与验证状态

新增NanoPlot 1.48.0（71af721）、chopper 0.15.0（ed2b694）源码，README用法及指定CLI/过滤逻辑选段核查；未安装完整依赖、未运行真实ONT。hifiasm本机`--version/-h`已核查，三输入接口与本地README一致；这不是三输入组装实测。完整范围、SHA和文件hash见[ONT证据清单](sources/ont_hic_resources.json)。开发缺口见29新增事项。

依据：[Dorado模型选择](https://software-docs.nanoporetech.com/dorado/latest/models/selection/)、[Duplex与dx标签](https://software-docs.nanoporetech.com/dorado/latest/basecaller/duplex/)、[接头修剪](https://software-docs.nanoporetech.com/dorado/1.0.0/basecaller/read_trimming/)、[NanoPlot](https://github.com/wdecoster/NanoPlot)、[chopper](https://github.com/wdecoster/chopper)、[hifiasm](https://github.com/chhylp123/hifiasm)、[Verkko固定版](https://github.com/marbl/verkko/tree/v2.3.2)、[minimap2手册](https://lh3.github.io/minimap2/minimap2.html)、[EBP v4](https://www.earthbiogenome.org/report-on-assembly-recommendations)。

ONT数据量是否充分和高覆盖处理规则，见[34](34_ONT数据量充分性与高覆盖软件说明核查.md)；Hi-C挂载与人工校正闭环见[35](35_EBP与Sanger_HiC挂载及人工校正指南.md)。
