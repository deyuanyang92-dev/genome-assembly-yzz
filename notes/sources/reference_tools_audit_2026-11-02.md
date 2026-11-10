# 二代初装与参考辅助工具：输入、操作和选择依据核查

日期：2026-11-02。证据状态：官方 README/手册和指定方法论文的局部核查；没有安装或运行这批软件，没有完成全源码审计。动态网页未锁定完整 commit；表中版本是页面明确给出的版本证据，不表示已证明截至今日的最新版本。

## 先明确任务边界

“二代数据＋参考基因组完成组装”是合法且应覆盖的全基因组路线。参考可以参与 reads 分区/局部组装、初装再组装、排序定向、切断、填洞或变异共识；这些操作不能用一个模糊的“参考组装”接口代替。以下工具多数接受 FASTA 初装，不接受原始 reads 建立初始序列；这不否定它们作为整套参考辅助组装流程组成部分的价值。

| 工具/操作 | 核心输入；原始 reads 角色 | 操作及碱基来源 | 使用场景与边界 | 版本/维护证据 |
|---|---|---|---|---|
| RagTag scaffold | reference FASTA＋query FASTA；无 reads 初装入口 | 基于全基因组比对排序、定向 query，用 N 分隔；不复制参考碱基、不延伸 query | 单个合适参考下的透明挂载基线；保存 AGP、未挂载序列、confidence。不同参考另开分支 | Wiki 标注 v2.1.0；此前账本记录 GitHub/PyPI 版本不一致，尚未解决，不擅称最新版 |
| RagTag correct | reference＋query；可选同基因型 reads，含 Illumina `-T sr` 验证覆盖异常 | 在疑似错误位置切断 query，不加减实际序列 | 参考不一致可能是真实 SV；不应对所有初装自动先 correct。reads 在这里作断点验证，不是初始组装 | Wiki v2.1.0 |
| RagTag patch | target assembly＋query donor assembly；非原始 reads | donor 片段填 gap 或实现连续连接，确实会引入 donor 碱基 | 同个体独立初装整合和跨个体参考填补必须分开；后者不能默认为目标实测序列 | Wiki v2.1.0 |
| RaGOO | 历史的 draft＋reference 比对挂载工具 | 参考引导排序定向；不能把历史论文功能自动套用到现有空简 README | 保留方法史和旧流程复现用途，新流程优先考察其作者替代项目 RagTag | 当前仓库明确写明停止支持并建议 RagTag；本次没有锁定历史版本 |
| Ragout 2 | contigs/scaffolds＋一或多个 complete/draft references；配方可提供进化树 | 同源共线块、重排模型和多参考推断邻接；可选 overlap graph refinement 纳入短/重复组件；非 reads 组装 | 多参考、允许重排的染色体结构推断；支持复杂大基因组，官网明确高多态基因组有局限。refine 对大基因组效果有限，不能等同 reads 重组装或补出未测序碱基 | 官网显示2.0；未将旧 releases 抓取结果当作今日维护活跃证明 |
| MeDuSa 原版 | target draft FASTA＋目录内多个 auxiliary genomes FASTA；无 reads 或用户提供系统树要求 | MUMmer 比对获得图邻接，路径覆盖决定排序定向；组件间默认100 N，可估距 | 多个参考可以是草图；适合与单参考结果比较。算法无系统树要求不等于无参考偏差 | 官方 releases 页面可见1.6（2015）；README仍含旧“未发表”文字，与已发表2015论文不符；依赖含旧 Python/Java，需实际环境验证 |
| MeDuSa2 | input assembly＋reference directory；可复用 coords/PAF；README未列原始 reads | 原 MeDuSa 思路的另一个仓库实现；提供 MUMmer/Minimap2 路由 | 作为新增候选记录，不因名字带2就当成全面验证的替代版。尚未核对源码、精确差异、发表证据、正式版本或可执行性 | `combogenomics/medusa2` README要求 Python>3.6；本次无完整commit、无正式release证据 |
| Chromosomer | 组件与参考染色体的比对、组件长度、gap参数；随后原始组件 FASTA；不需要 mate-pair | fragmentmap 生成坐标图，assemble 从原组件生成染色体草图；含注释坐标转移/统计辅助功能 | 以清晰fragment map构建染色体草图；不应视为目标新碱基恢复器；参考染色体的可靠性直接影响布局 | 2016 GigaScience方法；本次仅确认README和论文输入机制，没有核实当前软件版本/维护状态 |
| ntJoin | target assembly＋一个或多个 reference assemblies（也可其他 draft），支持权重；无原始 reads | minimizer graph 取代高成本全基因组比对；线性路径转成 target 组件区域；可切疑似错误，且默认检测/修剪重叠 | 多初装/多参考整合候选；不能把它等同只重排完整contig的 RagTag scaffold。必须审核裁切、重叠修剪、gap和权重敏感性 | 当前README安装例指定1.1.7，重叠功能说明始于1.1.0；未锁定README commit、未证明1.1.7为所有发布渠道最新版 |

## 为什么这些工具不是互相随意替换

- **参考排序不等于参考填补。** RagTag scaffold 保留 query 的实际序列；patch 从 donor 取实际碱基。两者均可参与“参考辅助组装”，但交付来源和评估要求不同。
- **多参考不等于目标个体的独立证据。** Ragout 的重排建模、MeDuSa 的图优化、ntJoin 的权重 minimizer graph 都是不同的比较推断；多参考共同继承的结构也可能不适用于目标。
- **不能只比较 scaffold N50。** ntJoin 的切断和重叠修剪、RagTag correct 的切断、patch 的 donor 注入，都可能改变原组件的使用方式；至少核查非N长度变化、丢失/重复组件、各片段来源、未定位序列及逐连接依据。
- **不预设所有场景必须先从头初装、再挂载。** 当用户希望参考介入更早时，另评估已记录的 reference-guided local assembly（reads按参考分区后局部组装）以及 AlignGraph 的 PE＋初装＋参考再组装。这里不能给 RagTag 增加它没有的原始 reads 组装功能。

## 面向软件开发的选择与核查规则（设计，未实现）

1. 明确目标产品：目标个体序列组装、参考辅助布局、带donor的混合序列，或参考坐标共识。输入选择和输出命名应与产品一致。
2. 将参考作为有 accession、版本、分类身份、完整性和hash的输入；记录目标reads可比对比例、比对质量分布、覆盖均匀性和结构冲突。不存在一个可跨所有物种复用的“同属即可”或相似度万能阈值。
3. 单参考布局先考察 RagTag scaffold；多参考时比较 Ragout、ntJoin、MeDuSa类的机制和证据；这里只是按输入与功能的候选分流，不是基于本地benchmark得出的性能排名。
4. 原始 contigs、组装图和未定位序列全部保存；每个参考/方法独立目录，输出可比较的AGP/路径证据。ntJoin建议显式请求AGP，不能默认存在；其 `no_cut=False`、`overlap=True` 应显式记录。
5. 同一参考排序后再以相同参考共线性作唯一验收，属于循环验证。目标PE只能检验其分子跨度内的连接；无法覆盖的长连接标为未知，不能因无异常就认定正确。
6. 待开发验收样例：真实倒位不被自动改回参考；多参考冲突保持可追踪；donor填洞来源可见；重叠修剪后组件坐标一致；未定位组件不丢失；N量增加不计入真实恢复序列。

## 逐项原始来源及本次阅读范围

- RagTag scaffold： https://github.com/malonge/RagTag/wiki/scaffold ，页面标注v2.1.0；核对输入、序列保持、gap、AGP和未定位行为。
- RagTag correct： https://github.com/malonge/RagTag/wiki/correct ，页面标注v2.1.0；核对切断、同基因型reads及`-T sr`。
- RagTag patch： https://github.com/malonge/RagTag/wiki/patch ，页面标注v2.1.0；核对fill/join、donor来源和两FASTA输入。
- RaGOO官方停止支持声明： https://github.com/malonge/RaGOO 。历史完整手册未重读；历史方法论文 https://doi.org/10.1186/s13059-019-1829-6 仅作已有文献入口。
- Ragout官网： https://mikolmogorov.github.io/Ragout/ ，核对2.0、多参考和适用范围；手册 https://mikolmogorov.github.io/Ragout/usage.html ，核对graph refinement、links支持及局限。发布页 https://github.com/fenderglass/Ragout/releases 抓取较旧，未用于断言今日最新版。
- MeDuSa原版官方仓库： https://github.com/combogenomics/medusa ，核对输入输出、默认100 N、依赖与1.6发布记录；原始论文 https://doi.org/10.1093/bioinformatics/btv171 ，核对多draft/complete参考、无需用户提供系统树和图路径覆盖方法。
- MeDuSa2官方同组织仓库： https://github.com/combogenomics/medusa2 ，仅README输入和依赖，未代码审计。
- Chromosomer官方README： https://github.com/gtamazian/chromosomer ，及可读文本 https://raw.githubusercontent.com/gtamazian/chromosomer/master/README.rst ；论文 https://doi.org/10.1186/s13742-016-0141-6 ，核对fragment alignments、fragment map及原组件生成FASTA的两步机制。CHANGELOG抓取失败，版本未知。
- ntJoin官方README（原bcgsc链接重定向BirolLab）： https://github.com/BirolLab/ntJoin ，核对输入、权重、minimizer graph、切断/重叠默认行为、AGP开关及1.1.7安装示例；原始论文入口 https://doi.org/10.1093/bioinformatics/btaa253 。未执行安装测试脚本，未全源码阅读。
