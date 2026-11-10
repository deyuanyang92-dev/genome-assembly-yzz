# HapHiC：论文问题、算法机制、输入契约与排错补充

核查日期：2026-11-02。该记录是本轮定向补充，不表示重新完成全部学习。

## 证据状态与版本

- **此前已有**：notes12、notes31、notes35、notes45；官方README，pipeline/cluster入口与build检查的局部静态阅读；issue87/174可见正文/讨论；未运行HapHiC。不能把这批旧记录说成本轮新学。
- **本轮新增**：复读固定README的四阶段/FAQ/GFA/refsort；定向阅读`HapHiC_cluster.py:419–430,474–630,695–710`及CLI默认值；核对作者论文书目信息、摘要与可见扩展图说明。本地HapHiC执行新增0、真实样本验证0、完整论文复现0。
- 本地源码commit：`74f1cb27d7753ce061ee673c0d62fdd44187060e`；`scripts/_version.py`为`1.0.7`、更新`2025.10.30`。此前版本账本观察release1.0.7指向短SHA`df0f5ac`，属于不同提交；本地未含`v1.0.7`tag（本轮`rev-parse v1.0.7`失败），不能冒称重新锁定了release完整SHA。复现至少记录完整commit＋环境＋参数，版本字符串不足。
- 作者论文：Zeng et al., **Chromosome-level scaffolding of haplotype-resolved assemblies using Hi-C data without reference genomes**, Nature Plants 10:1184–1200 (2024), DOI https://doi.org/10.1038/s41477-024-01755-3 ，2024-08-05在线发表。https://pubmed.ncbi.nlm.nih.gov/39103456/ 摘要可读；Nature正文直开本轮遇身份跳转，搜索索引可读扩展图2/3/5/6的说明。没有据此宣称全文、补充全文或全部benchmark已精读。作者资料入口 https://www.nature.com/articles/s41477-024-01755-3 。

## 1. 论文解决的问题及组装器边界

单倍型解析初装包含多套彼此相似的同源染色体片段。Hi-C可跨长距离提供归组证据，但同源相似序列误比对、switch error、嵌合或塌缩contig，可产生把不同同源染色体粘成一组的接触图。只按接触强度合并至指定组数，会得到组数正确、内部结构错误的结果。HapHiC的目标是无需参考序列完成等位感知的染色体归组、组内排序与定向。论文摘要还提供异源三倍体芒草案例；案例成功不等于任意倍性/文库都保证成功。

HapHiC输入是已有assembly FASTA＋Hi-C比对，**不是从HiFi/ONT/Illumina原始WGS拼出contig的组装器**。它可以利用已分相contig或unitig及其GFA标签，也可用于collapsed diploid/allopolyploid初装。它改善染色体归组不代表重新计算了每个contig内部的正确碱基相位；不能把其“allele-aware”直接解释成修复所有switch error，或承诺亲本来源相位。

## 2. 从接触图到染色体：机制而非标签

1. **预处理并降低不良图边影响**。可选基于Hi-C spanning coverage识别低跨度支持区并切断；默认`--correct_nrounds 0`，高质量长contig不自动切断。按长度Nx、限制位点、接触密度、read-depth/GFA和rank-sum等筛选会暂时排除不可靠组件，不能理解成这些序列都被最终删除。扩展图2/3分别描述跨度覆盖切断和rank-sum识别嵌合/塌缩。
2. **等位接触识别是有条件的机制**。固定源码`cal_concordance_ratio`计算两contig上成对坐标的`y-x`与`y+x`分箱，取众数所占比例最大值，识别近似正向/反向共线排列的接触分布。启用`--remove_allelic_links PLOIDY`后，对足够读对的contig pair依据cutoff判断；同源识别依赖接触模式与阈值，不是获得无误差等位真值。源码还使用等位组、clique拆分与Hungarian最大二分匹配删除非最大匹配链接。参数值为输入assembly的相关倍性，绝不是`nchrs`。
3. **GFA相位先验是另一条路径**。一个GFA主要提供深度辅助识别塌缩；多个GFA被视为haplotype-specific。固定`reduce_inter_hap_HiC_links`将不同GFA/hap标签之间的link乘以`1-phasing_weight`；默认weight1可完全去除这些links，0表示不采用这项相位先验。它不能识别GFA相位标签本来是否正确；过强先验也可能降低挂载率，官方明确提示。
4. **MCL聚类而非直接硬切N组**。inflation控制聚类粒度，通常越大组越多。程序扫描范围，根据`nchrs`和组长分布推荐候选。因而其“推荐best inflation”受核型先验及染色体长度差异影响，不能当数据证明的最优真值。
5. **Reassign救回/调整组件**。救回初始过滤或未归组contig、重新分配，并在必要时AHC合并超量groups。必须检查救回的长度/接触支持和合并冲突，不能为了达到目标数量无限放宽阈值。
6. **组内排序定向**。先使用加速的3D-DNA迭代策略fast sorting，再以该解初始化修改版ALLHiC优化；最终构建FASTA和两种AGP。不是另运行一套从reads的从头组装。fast-sort与优化解也需要比较，不应假定优化后永远更好。

上述属于选定函数/README机制核查，并非全图算法正确性证明或对性能的独立验证。

## 3. nchrs到底填什么

官方定义为**assembly中所表示的染色体数，也即预期输出的主scaffolds数**，不是物种名称决定的固定n或2n。

例如仅为说明语义：一个`n=10`二倍体，单条hap集合完整表示一套时预期10组；两个hap合并且两套均完整表示时预期20组。性染色体、非整倍体、部分塌缩/缺失、亚基因组表示不一致时不能机械套公式。`--remove_allelic_links`的倍性设置也不能只按FASTA文件个数猜。

核型未知时可用`--quick_view`跳过聚类先看接触结构（此模式忽略nchrs，命令中的整数只是占位）。接触图估计仍受微染色体、弱信号、缺失/塌缩影响，必须标为推测；不可把快速排序输出数量当细胞学染色体数。

## 4. 官方模板与数据身份

以下与本地固定README及当前官方README相符；本轮没有执行，生产前锁定CLI和环境。示例资源会叠加，不直接照抄到小机器。

```bash
bwa index asm.fa
bwa mem -5SP -t 28 asm.fa hic_R1.fastq.gz hic_R2.fastq.gz | \
  samblaster | samtools view - -@ 14 -S -h -b -F 3340 -o HiC.bam
/path/to/HapHiC/utils/filter_bam HiC.bam 1 --nm 3 --threads 14 | \
  samtools view - -b -@ 14 -o HiC.filtered.bam
/path/to/HapHiC/haphic pipeline asm.fa HiC.filtered.bam NCHRS --threads 8 --processes 8
```

MAPQ≥1、NM<3是该README示例，不等于全部物种或全部挂载器的统一最佳值。官方要求**不要coordinate-sort**，若已按坐标排序，应另存`samtools sort -n`版本；这不同于给浏览器/随机访问准备的BAM。原始模板不经coordinate-sort可直接保持成对关系；不能仅用header的SO检查替代实际record组织验证。

若打开纠错，后续reassign/sort用corrected_asm.fa。单独build时模板为：

```bash
/path/to/HapHiC/haphic build corrected_asm.fa asm.fa HiC.filtered.bam \
  final_tours/group*.tour --corrected_ctgs corrected_ctgs.txt
```

前一个FASTA是校正组件，后一个是原FASTA；`scaffolds.agp`引用校正组件ID，`scaffolds.raw.agp`引用原组件区间。不能任意交换两者，也不能给校正ID的AGP配原BAM后把信号缺失归咎生物学。raw.agp路径可保留原BAM坐标一致性。

`haphic refsort`是独立的整条scaffold排序/整体翻转显示功能，官方明确**不是参考辅助scaffolding，也不改scaffold内部结构**。不能拿它与RagTag scaffold的contig级重排或参考引导再组装混为一谈。

## 5. 前检与故障决策（设计，至少在长任务前完成）

| 前检/症状 | 先查证据 | 不应自动执行 |
|---|---|---|
| 环境启动或排序阶段崩溃 | 完整commit、依赖构建、`haphic check`和真实stderr；官方提醒Bioconda包非官方维护且有已知中止问题 | 只按1.0.7名字覆盖环境或宣称版本一致 |
| FASTA/BAM/GFA混用 | BAM SQ名及长度与FASTA一致；GFA组件/深度/所属hap与同一FASTA匹配，记录hash | 换了初装却复用旧BAM/GFA/cache |
| BAM无有效pairs或坐标排序 | 实际read name组织、secondary/supplementary/duplicate过滤和过滤前后有效pairs | 把浏览器coordinate BAM直接投喂，或以proper-pair过滤全部Hi-C |
| 少组/巨组/找不到推荐inflation | nchrs的assembly表示语义、组长、每个inflation结果、接触背景、嵌合/塌缩、低质量文库 | 一律降低MAPQ、无限强合并或把nchrs强凑为通过 |
| 同源染色体粘连 | 相似区多重比对、switch、同源links、选用remove_allelic的倍性与阈值 | 把所有高强度边认作真实同染色体连接 |
| 挂载率下降 | Nx/RE/深度/link阈值淘汰原因；GFA先验权重；被淘汰序列长度和类别 | 丢弃unplaced以改善报告，或把所有阈值放到最宽 |
| 纠错过度或连续度变差 | correct_nrounds是否非零、原contig跨度图与目标长读跨断点支持 | 默认启用多轮纠错；尤其不能据异个体Hi-C自动切目标contig |
| 接触图校正组件无信号 | AGP坐标体系、corrected_ctgs、原/校正BAM配对身份 | 将缺信号解释为染色体断裂而不查ID |
| 长染色体/极长contig链路异常 | 本版HapHiC与BWA/Juicebox等上下游整数限制分别核对 | 因HapHiC支持更大坐标就认定整个链路支持 |
| 限制位点/文库不明 | 确认建库方案并记录RE选择；无RE/未知时官方允许默认但应保留来源不确定性 | 由物种猜酶切方案 |

**非同个体Hi-C不是自动安全的。** 等位链接过滤、MCL或GFA先验都不能保证另一个个体的SV、性染色体或相位与目标一致。仍需固定目标初装做有/无该Hi-C及不同参数分支，逐连接标记样本来源、支持/冲突/未知；异个体Hi-C不能直接作为目标个体内部相位真值。

## 6. 本次来源与未完成项

- 固定本地源码：`pipelines/zengxiaofei_HapHiC`，完整commit见上；原账本`sources/software_debug_review_2026-11-02.json`保存此前README/入口/build等SHA256。
- 官方仓库及示例/FAQ：https://github.com/zengxiaofei/HapHiC 。当前网页与本地可能在同版本字符串下存在变化，本轮不将当前main当锁定版。
- 作者论文及摘要/扩展图可见范围见开头；未取得全部正文及补充细节，尚未核查所有模拟条件、评价指标实现及真实数据SRA与代码对应关系。
- 本轮没有新增issue阅读，不把87/174再次计数；未运行cluster/reassign/sort/build、未验证同/异个体数据、未实现以上自动前检规则。
