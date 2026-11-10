# EBP与Sanger：组装后Hi-C挂载及人工校正指南

**2026-11-02后续更新**：下文下载失败是早期批次状态。两份Sanger官方PDF现已取得，读完抽取文本并实际查看12个关键图文页，已核对固定commit文件哈希；详见[培训图文审查](sources/sanger_curation_training_review_2026-11-02.md)。没有完成全部页面逐图培训、视频或GUI实操。

2026-11-01。目标是后续能指导从contig到可交付染色体组装；不是只运行一个挂载软件。当前阅读官方网页说明、已固定的本地YaHS/HapHiC/Sanger代码与已有笔记；未运行TreeVal/curationpretext/Pretext人工校正真实样本。PDF图谱教程本轮未成功取得内容，视频未观看，不能宣称完成这些培训。

## 1. 找到的权威指导链与用途

用户描述很可能指下列相互衔接的资源，但不能确认就是用户记忆中的具体页面。

| 资源 | 在工作流中的职责 | 本轮阅读范围与状态 |
|---|---|---|
| [EBP Assembly Recommendations](https://www.earthbiogenome.org/report-on-assembly-recommendations) | 组织级策略：contig质控、Hi-C挂载、再比对/人工审阅及交付 | 网页挂载/curation相关段落；建议YaHS，链接GRIT Rapid Curation/TreeVal；不是所有物种一条固定命令 |
| [Sanger curation-resources](https://github.com/sanger-tol/curation-resources)，旧rapid-curation地址重定向 | 人工校正的操作入口、训练资源和导出路线 | README工作顺序/标签/坐标与重建图；未完整clone；不计新增完整流程 |
| [TreeVal](https://pipelines.tol.sanger.ac.uk/treeval) | 生成curation所需接触图、覆盖、gap、重复、端粒、基因/共线性等辅助证据 | 官方介绍及阶段列表；网页标有1.4.7而源链接1.4.8，需实施时冻结一致版本；未核验完整YAML/schema与全部源码 |
| [curationpretext](https://pipelines.tol.sanger.ac.uk/curationpretext/usage) | 校正前后生成/重建Pretext图和辅助轨道 | usage、output；在线output链接指1.6.1。FASTA、Hi-C CRAM目录及索引、可选长reads fasta.gz、read_type和端粒motif等接口；不能当自动挂载器 |
| [agp-tpf-utils](https://github.com/sanger-tol/agp-tpf-utils) | pretext-to-asm把编辑AGP映射回原输入组装并输出序列/AGP等 | README说明；并非任意AGP/TPF语法的通用支持保证；未安装或读完实现 |
| [YaHS](https://github.com/c-zhou/yahs)＋PretextView或Juicebox | 自动挂载＋交互校正 | 本地固定源码及12/14已有小例；本轮再次核对输入排序、AGP和JBAT交接；工具小例不等于人工训练完成 |
| [Aiden Lab Genome Assembly Cookbook](https://aidenlab.org/assembly/manual_180322.pdf) | 自动流程与Juicebox人工审核的配套培训 | 本轮只取得概述；2018指南的历史软件和测序成本不作为2026配置，图文训练待补 |

当前curation-resources README的RAPID_CURATION_TRAINING_MANUAL及一个图谱指南链接含错误路径并返回404；正确仓库里存在[Interpreting_HiC_Maps_guide.pdf](https://github.com/sanger-tol/curation-resources/blob/main/Interpreting_HiC_Maps_guide.pdf)和[PretextView-Tutorial.pdf](https://github.com/sanger-tol/curation-resources/blob/main/PretextView-Tutorial.pdf)。本轮浏览器只取得PDF文件页面，raw解析失败；培训网站需要JavaScript，尚未读取视频内容。终端clone/download受当前代理不可达影响；不把在线阅读说成已下载这些仓库。

## 2. 开始挂载前先固定生物学目标

1. 登记物种、倍性、核型、个体关系和Hi-C建库方法。HiFi A/Hi-C B单列风险，按31–33保留A-only与A+B对照。B的图不能证明A的相位/结构真值。
2. 确定要交付primary、两套hap还是多倍体多套hap。hifiasm Hi-C分型不等于染色体挂载；hap1/hap2无亲本标签不能称父/母。
3. 固定输入FASTA及GFA、contig ID、长度、SHA、hap角色。检查G、总长度、污染/细胞器、重复拷贝和相位，必要处理嵌合；不能为更高N50无证据地purge一套真实hap。HiFi有效覆盖≥50×单独验收。
4. 核染色体、细胞器和污染处理留追踪清单。改变序列/ID使索引、比对和旧图失效；复杂混合hap输入需明确竞争比对和等位链接策略。

两套hap分别挂载时，应设计针对两hap相似导致的错误/歧义比对的过滤或分配，不把单hap独立mapping当成天然无偏。HapHiC等另一条路线还需根据输入套数、倍性和核型定义分组数，不是填一个物种n就结束。

## 3. Hi-C质控、比对与输入契约

原始量仅是规划指标。EBP建议Hi-C按单套基因组>50×作规划；还要记录成对reads数、每端长度、建库、有效唯一非重复pairs、成对比对率、多重比对、重复率和长程接触分布，不能把有效pairs当普通均匀核覆盖。R1/R2碱基应各计一次，两端总量不得再乘2。

按真实试剂盒走官方比对路径，例如YaHS列出的Arima或Omni-C指南。不能把普通短插入片段proper-pair筛选(-f 2)、mate rescue或插入片段模型机械用于Hi-C。保留PCR/光学重复处理、MAPQ、多重/补充比对、read pair完整性及过滤计数。不同文库不能硬编码同一个酶切位点；Omni-C不能臆造限制性酶。

YaHS的queryname BAM与其他排序分支在link位置和MAPQ应用上不同，详见12；本项目显式准备queryname-sorted BAM并核实预过滤。BED必须使同一read pair相邻，按read name列排序，不能按染色体列来保证配对。HapHiC输入规则不同，不能复用浏览器的坐标排序BAM而不核对。

## 4. 自动挂载不是终点

一般二倍体/单套高质量contig以YaHS为优先候选；复杂等位/多倍体另评估HapHiC等。参数和预处理都应与固定版本、真实文库及生物学目标一致。不要通过不断合并直到达到预期染色体数来证明结果正确。

```bash
# 适配模板，依赖已正确过滤且与contigs.fa一致的hic.filtered.bam；本轮未运行
samtools faidx contigs.fa
samtools sort -n -@ 8 -o hic.namesorted.bam hic.filtered.bam
yahs -o sample contigs.fa hic.namesorted.bam
```

保存各轮AGP、最终FASTA/AGP、BIN、日志和参数。YaHS可能断开原contig，应检查切断位置是否获得Hi-C与长reads/图支持；缺覆盖、重复和文库偏倚也会制造假断点。保留默认纠错不意味着其所有断点正确；关闭纠错也需要证据。

## 5. 生成图谱与辅助证据

TreeVal适用于较完整的curation证据准备；curationpretext主要用于图谱与轨道及校正后的复核，两者不是另外两个de novo组装器。先按所选版本官方test profile验证本机容器、路径和数据接口，再实际运行；当前未完成。

curationpretext在线文档要求Hi-C CRAM及.crai，长reads用.fasta.gz。这只是该流程接口，不表示FASTQ不能做Hi-C分析。CRAM类型和转换命令必须经对应samtools/流程小例验证，不从旧说明盲搬。网页示例还存在缺续行与`for i in .fasta`不匹配文件等问题，应依据固定源码/schema重写可运行命令；不直接把整段示例当生产脚本。AUTO aligner、multi_mapping及端粒默认值同样先按固定版本核验；默认TTAGGG不是所有物种事实。

Juicebox路线详见12：YaHS自带juicer pre -a产生JBAT文件，再由兼容版juicer_tools pre生成.hic；它与Aidenlab Juicer比对流程不是同一个程序。加载对应.hic/.assembly，核对大组装坐标缩放；不能把缺失的.hic当成已生成图。

## 6. 如何审阅，不凭一张漂亮对角线通过

以下为结合已有本地证据整理的审核策略；不是声称已看完上述PDF的图例。

| 可疑图像/现象 | 竞争解释与核查 | 可采取动作 |
|---|---|---|
| 一个scaffold内部接触突变、两段几乎独立 | 错误连接，也可能低覆盖/重复/真实结构差异；核对原contig边界、HiFi/ONT和局部可比对性 | 足够证据后切断；证据不足先标记 |
| 一段与邻域呈反向接触几何/常见蝴蝶结样式 | 可能方向错误；重复、多倍体或B个体倒位也可造成 | 检查两侧端接触和A分子，再翻转并复核 |
| 一段离开主对角但与另一位置强联系 | 可能放错组/顺序，也可能重复或真实跨染色体空间接触 | 比较候选端点、映射质量/图/长reads后移动 |
| 同一序列联系多条染色体、重复条带 | 多重比对、重复、haplotig/污染、同源多倍体等 | 不强行归组，检查深度、分类和等位关系 |
| 很弱或无信号的小contig | 缺有效Hi-C、短片段或偏倚，不一定垃圾 | 可标unplaced；能归染色体但定位不定则unlocalised |

先全基因组分组，再每条染色体，再局部连接；同时看raw/适当归一化、多尺度与覆盖、gap、重复、端粒及基因/共线性。平衡归一化不能创造缺失证据；跨染色体相互作用本身不等于应连接。近缘参考可发现疑点，不能为了匹配参考而抹掉目标真实核型变化。

逐修改记录输入版本、坐标、切断/翻转/移动/连接、证据和置信度、操作者及前后截图。Hi-C通常不能给出真实缺口长度，scaffold里的N不等于已补齐序列；染色体级不等于T2T。

## 7. 导出、坐标恢复、重新验证和交付

Pretext路线：E编辑、M加元数据标签、S标记染色体，导出AGP；以与图一致的原始输入FASTA和编辑AGP使用pretext-to-asm，避免Pretext分辨率遗漏小scaffold或切点精度损失。保留contaminants/haplotigs、unlocalised/unplaced和hap分类输出，不静默丢序列。实际CLI及输出规则安装固定版本后再核对。

Juicebox路线：保存.review.assembly，通过YaHS juicer post＋相应liftover AGP＋原contig FASTA生成最终FASTA/AGP；具体命令见12，不混用Pretext AGP的后处理工具链。

对最终序列重新比对Hi-C并重建图，复查全部修改位置。AGP lifting旧links可快速预览，但最终重新mapping能检查新边界/序列变化带来的差异；使用相同Hi-C仍然是内部验证，跨个体尤其不能冒充独立A真值。

最终检查AGP区间合法/方向/意外重复或遗漏、总长度与N量、挂载比例（明确分母与排除集）、真实未定位序列、每hap完整性/QV、污染、结构与相位。参考23/25执行本项目高标准目标：挂载/完整度98%争取99%，QV≥50争取60，并记录适用性和独立证据。不能用N50/BUSCO单指标代替。

交付：最终FASTA+fai、AGP、输入及拆分坐标追踪、接触图及辅助轨道、全部改动清单和证据、软件/数据库版本、命令/资源、QC前后对比、未解决问题；染色体命名结合物种既有规则与核型，不能仅按最长scaffold臆造性染色体。

## 8. 后续学习与开发的具体未完成项

- 获取并逐图阅读Sanger的两个PDF、培训图谱/FASTA以及视频；保留页码/案例证据。目前没有完成图文/视频训练。
- 冻结TreeVal/curationpretext/agp-tpf-utils的匹配版本，完整阅读参数schema、YAML、调用源码和输出，运行官方test profile后用培训案例实际编辑、导出、重建图。没有样本真值前不声称掌握全部复杂情况。
- QS012拟开发“自动挂载→图谱准备→人工审查→坐标恢复→最终QC”交接模块，复用既有工具；结合QS008/010标记跨个体证据。自动检测只生成候选事件，人工/独立证据不足不能自动切断合并，不自动删除unplaced序列。当前仅记录需求，尚未实现。

来源范围及访问失败见[sources/hic_curation_manual_review.json](sources/hic_curation_manual_review.json)。
