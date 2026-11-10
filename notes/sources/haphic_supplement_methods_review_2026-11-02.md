# HapHiC 2024 公开补充材料：方法、命令、真值与配置核查

日期：2026-11-02。**本轮新增范围**，不覆盖或追改之前仅摘要/README核查的证据记录。

材料：[官方补充PDF的本地副本](haphic_2024/supplementary_information.pdf)及[提取文本](haphic_2024/supplementary_information.txt)，来源为作者论文关联的Springer官方公开补充链接。本轮独立复核下列选定章节；`pdfinfo`确认PDF为**113页**，不是113页均已阅读。本文“页”指**印刷页码**，PDF封面使PDF物理页多1页；如印刷页2为PDF第3页。

实际阅读与本轮复核：Supplementary Methods 1–4，印刷页2–6；Software Commands 1.1–1.11，页7–11；2.1–2.3及3.1，页11–15；3.4–3.7，页18–20；4.1–4.7，页20–23。ALLHiC/LACHESIS详细配置（3.2–3.3）未逐行审查；5 Genome assembly未纳入本分工；未读全部图、表和补充数据。最终文本已延伸至印刷页112；先前“提取中、止于38页”的临时观察不再适用于当前文件。文本提取完成不等于全部内容已审读。本轮没有运行论文代码、下载全部测序数据或重现图表。

本次校验（2026-11-02）SHA256：PDF为`7ad2cf9b9c226305f623faeaa3e0206418dd3cdc13a939b7e80d152bd427f4ea`；TXT为`2be1957572454499734b1fea10e27dcfc24cc5df602c547d375d8528f178921f`。`pdfinfo`同时发出optional-content-group语法警告，仍返回113页元数据；本轮未逐页渲染检查，不能据此保证所有图形均无显示问题。

## 1. 模拟为什么这样设计，能说明和不能说明什么

**页2–3。** 作者指出，把水稻两个亚种的genome和Hi-C直接合并，会缺少它们在同一细胞核里的真实同源染色体背景相互作用，从而人为降低同源分离难度；二倍体或仅一对同源染色体也不能代表多倍体全基因组。作者改用苜蓿XinJiangDaYe已发表的同源四倍体组装，人工移除明显错误后，以32条染色体约2.0Gb为模拟模板。这个ground truth是作者修订的模板，不等于未带假设的生物学真值。

- 改变片段N50、长度CV和有效Hi-C深度；深度抽样来自过滤后的真实SRR9026577/78数据。高连续度模拟保留模板内N，因此文中的“contigs”可能仍含gap；不可把该N50直接当无gap真contig N50。
- 嵌合包含同源间、非同源间、染色体内三类，比例7:2:1。塌缩由2/3/4条hap形成，默认比例同为7:2:1。这是实验生成分布，不是所有物种真实错误分布。
- 新hap由SNP/indel生成，比例10:0.5:0.5，转换/颠换2:1，并在100kb bins按CV0.5不均匀分布；switch由hap间变异随机交换产生。还组合每类5%错误测试2–16倍体。
- 模拟Hi-C使用sim3C，按倍性调整读对数和trans-rate以固定交互强度。具体每倍性数值在Table9，本分工没有读取该表，不擅自填数值。十个并行任务使用不同seed；community profile让所有染色体同细胞且等丰度/拷贝1。

**工程含义（本项目推导）**：复现必须保存模板、源染色体/hap/坐标/错误类型标签、seed、实际抽样比例、每倍性模拟设置和输入N含量。不能用任意随机切参考/随意混两份Hi-C就声称重现同一难度。

## 2. 评分定义及容易过度解释的地方

### 模拟归组，页3–4

- 多组件才算scaffold，单组件算unanchored；anchoring rate为进入这些scaffolds的contig长度/全部contig长度。这项定义对原本近完整单条染色体的输入不能原样套用。
- 不以scaffold N50代表正确性。作者按每个scaffold中各来源染色体的累积长度确定dominant chromosome，再以该scaffold中dominant来源长度/所有scaffolds已挂载的同一来源总长度求比，最后对scaffolds平均，衡量来源染色体是否被拆散（与挂载率分开）。**该比本身不等于纯度**：混入其他来源可未充分惩罚，必须同时报告misassignment。

  **对原文解释的限制（公式推导，未执行评分器）**：原文将比值1解释为scaffold完全来自某条染色体，但这一点不能由该公式单独推出。例如同一个scaffold包含A的全部100 bp及B的全部50 bp，A为dominant，A的该比值仍为1，而非dominant的B占50/150。故“contiguity=1”必须与misassignment等联合解读，不能翻译成“全部连接正确”或“纯度100%”。
- 非dominant来源按同源间/非同源间分开计误分配率，分母为已挂载基因组长度；嵌合和塌缩contig排除，因为无法视为在任一scaffold完全正确。这使指标的评价对象受排除规则限制，不能直接当全部输入的总准确率。
- ALLHiC所用近缘M.truncatula参考的chr4/8有结构差异，作者又计算排除这两条后的结果；需同时留存完整与排除版，不能只摘表现更好的子集。

### 排序/定向，页3–4、10

水稻、拟南芥、CHM13noY参考切片后，**先按来源真实染色体分成groups**，各工具再组内排序，纠错关闭。因此该部分测的是给定正确归组下的ordering/orientation能力，不是未知核型下端到端scaffolding能力。

指标为Lin CCC和修改DERANGE II的有符号排列编辑cost；cost取正反整体方向较小值。权重inversion/transposition/transversion为1/1/2，look-ahead3。不同工具需输出适配：SALSA2/YaHS多scaffold被连接后评分，3D-DNA使用`0.assembly`中间结果。复现必须记录这些适配，不能拿各工具默认最终FASTA直接横比便声称相同实验。

### 真实案例，页4–6

Hi-C方法以已发表染色体组装为ground truth，将其与待评scaffolds划为500kb bins，比较距离相关的组内links上下界和组间频率，产生discordant intra/inter scaffold bin-pairs及links。该指标**不是仅靠一份未知样本BAM即可获得无参考绝对正确率**；使用相同Hi-C进行挂载和评价也存在证据依赖。

另一组ground-truth评分使用已发表基因组断N后组件的已知坐标/方向。先做reciprocal-best染色体/scaffold匹配，再区分unanchored/newly-anchored/translocated；剩余用长度加权LIS分类syntenic、inverted、relocated和两者兼具。初始无定位片段或真T2T单条染色体有特别处理；误分类/遗漏的来源应一并报告。

## 3. 预处理版本与接口：论文不等于当前CLI

**页11–12。** 论文明确：fastp0.21.0；BWA-MEM0.7.17-r1198-dirty `-5SP`；samblaster0.1.26；samtools1.11 `-F3340`；再去MAPQ0及NM≥3。这里samblaster先mark duplicate，再由flag过滤，不能把它仅写成未处理PCR重复。

论文的过滤入口是Python脚本 `filter_bam.py`，参数 **`--NM 3`大写**；当前固定README模板为compiled `utils/filter_bam ... --nm 3`小写。迁移流程需核对安装版帮助，不应原样拼接两个时期的接口。HapHiC一节本身未给可唯一锁定的版本/commit，尚不能从2024文章日期自动推出本地2025更新的1.0.7就是论文执行版本。

Juicer用于论文3D-DNA分支（短commit827fe44）；一般用途BWA过滤分支和Juicer分支不同，不能以论文对照工具用了Juicer为由推断HapHiC也必须用该输入链。其Juicebox可视化为旧版matlock/phasegenomics脚本与3D-DNA529ccf4（页20）。固定README另有raw AGP对接路径，采用它需标明没有逐命令复现该补充段落；不能据此推断raw AGP在2024年尚不存在，README版本记录注明它在1.0.1（2023-11-30）已加入。

## 4. HapHiC并非全部场景默认参数

**页12–15。** 基准一般命令为 `haphic pipeline asm.fa filtered_HiC.bam nchrs --RE RE`，限制位点按建库，未知时保留GATC默认。以下是论文实际特例，不是对任意新样本的自动推荐：

| 触发条件/实验 | 论文配置方向或确切特例 | 后续配置应核对 |
|---|---|---|
| 模拟N50仅25kb | Nx70；min_link_density0.00002；min_links1 | Nx70减少初始聚类组件以节省资源，后两项放宽救回；不能解释为初始纳入更多短片段 |
| 低有效Hi-C深度1×到0.02× | 按深度降低min_links及min_link_density，给出了7组阈值 | 低深度成功依赖本模拟条件及调参；不能当普遍最低深度保障，也不映射为HiFi覆盖要求 |
| 人工嵌合 | correct_nrounds2 | 这是有已知嵌合实验，不等于所有高质量长contig默认切2轮 |
| 人工switch | remove_allelic_links=nhaps | 提升对错误接触的耐受；不能宣称修复contig内部全部switch |
| 低N50且大量塌缩甘蔗/苜蓿 | Nx70、density_upper/rank_sum_upper筛选，再用min_RE_sites/min_links等改善挂载 | 当前CLI与这些旧论文选项名及阈值解释必须逐项核对，不能无条件搬数值 |
| Potato C88近相同区域、接触集中 | normalize_by_nlinks＋remove_concentrated_links；v1再Nx100 | 接触归一化/集中接触处理是特定症状分支，并非所有polyploid默认 |
| HG002.v1性染色体高link density | remove_allelic_links2＋density_upper1＋remove_concentrated_links＋normalize_by_nlinks | 性染色体与常染色体阈值的生物学解释，不能仅用“高密度=塌缩” |
| 评估省去ALLHiC优化的整条pipeline效率 | skip_allhic | 此命令仍包含pipeline其他阶段，不能称为单独sort阶段计时；也不能把它算成包含优化的完整流程时间 |

rank-sum、link-density和concordance算法评估用了`--skip_clustering --verbose`及关闭/放宽其他过滤的诊断运行（页13）；这些不是生产scaffolding配置，也不能拿诊断log里保留/排除比例当最终结果。

低深度段落的7组`min_links`依次为20、10、4、2、1、1、1，`min_link_density`依次为0.0001、0.00005、0.00002、0.00001、0.000005、0.000003、0.000001。**原文括号“0.1到0.002倍默认值”与两端数值不能对应同一个默认值**：分别反推为0.001和0.0005。本轮保留原列绝对阈值，不擅自修订作者倍数，也不从这一段推出当前版默认值。具体7个深度与阈值的完整逐项对应尚需原实验配置/表格核验。

关于Nx70，固定源码`74f1cb27…`的cluster/pipeline默认Nx80，README说明增大Nx可纳入更多组件；减至70是缩小按长度累计选择的初始候选集合。论文“lower contig length threshold of N70”措辞不应被转写成“降低碱基长度门槛、纳入更多短contig”。该解释复用当前固定源码/README语义，论文当时准确commit仍未锁定。

## 5. 对照工具与评分复现风险

页18–20记录SALSA2短commit ed76685、3D-DNA529ccf4、YaHS42b8421。SALSA2一般不带assembly graph；纠错通常关闭，仅嵌合实验打开。3D-DNA低N50/高错误率还有polisher/editor阈值调整。YaHS一般`-q1 --no-contig-ec --no-mem-check`，低N50可指定resolution，过多contig另设长度门槛；发生OOM后有移除`--no-mem-check`的重试。这些条件应进入比较记录，不能用“所有工具都是默认参数”概括。

论文旧YaHS段落的45,000组件限制是当时commit范围，不能自动当当前最新版固定上限。其`drop_caches`系统命令不能作为软件默认OOM恢复：该操作影响共享系统，不是修复算法内存需求；本项目不执行、不封装这种全局操作。

评分入口（页20–23）：`result_statistics.py`归组、`draw_tour_file.py`CCC/DERANGE、工具专属`get_*_break_points.py`纠错、`correction_analysis.py`真实人工标注比较，以及`chimeric_contig_statistics.py`、`collapsed_contig_statistics.py`、`allelic_contig_statistics.py`机制评估。**有脚本入口不等于已收集/验证了相同commit脚本和全部依赖**。真值标签、组件命名、输出适配、排除列表、数据版号缺一项，均不称完整复现。

原文还有需要历史代码核验的命令歧义：1.2叙述写`sim_contig.py`但命令为`sim_contigs.py`；1.11叙述写`fasta_split.py`但命令为`split_fasta.py`；3.4从BAM生成BED的行写成`bedToBed -i <filtered_HiC.bam>`。这些名称不应直接进入可执行模板，本轮没有验证作者环境是否存在相应别名或自定义程序，不能把疑似笔误当已证实的运行失败。

## 6. 对后续自动配置的落实建议（设计，未实现）

分别记录：输入数据身份/倍性表示与nchrs来源；过滤前后有效Hi-C对；N50与短组件比例；rank-sum、深度、集中接触线索；每次改变的参数及被救回/排除的真实长度。按症状生成小规模候选配置，保存默认对照，再用接触图、AGP审计、目标样本支持及已知真值（仅benchmark场景）比较。不能自动以更高挂载率或更接近nchrs为胜出标准。

这份补充材料没有建立“同种非同个体Hi-C必然安全”的证明；其模拟同细胞模板及已发表组装真值不替代用户目标个体结构/相位证据。
