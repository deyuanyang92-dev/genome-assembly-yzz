# 参考辅助组装综述：分类、机制及选择规则

核查日期：2026-11-02。证据级别：下列三篇综述的指定章节已阅读；没有执行软件、没有复现整篇论文。综述用于建立方法框架，版本、CLI和默认行为必须回查当前工具官方说明。本文不是“所有组装路线已学习完成”的声明。

## 1. 准确文献与实际阅读范围

| 文献 | 类型与发表信息 | 本轮阅读范围 | 时间与适用限制 |
|---|---|---|---|
| Jay Ghurye, Mihai Pop. **Modern technologies and algorithms for scaffolding assembled genomes** | Review；PLoS Computational Biology 15(6):e1006994；2019-06-05；DOI [10.1371/journal.pcbi.1006994](https://doi.org/10.1371/journal.pcbi.1006994) | Background、Sources of information、Practical considerations、Leveraging synteny—A missed opportunity | 重点是已组装片段的连接证据与算法，不能覆盖所有 reads 阶段的参考引导组装；早于RagTag方法论文及当前长读技术 |
| Edward S. Rice, Richard E. Green. **New Approaches for Genome Assembly and Scaffolding** | Review；Annual Review of Animal Biosciences 7（2019）；DOI [10.1146/annurev-animal-020518-115344](https://doi.org/10.1146/annurev-animal-020518-115344) | 摘要、Genome Contig Assembly开头、Synteny-Based Methods（作者PDF第15–16页）、Future Challenges；作者PDF为2018-11-28 advance稿 | 综述从短读连续性问题展开，synteny是合法组装改进路线；平台成本和错误率属于当时背景，不能当作2026数据 |
| Kunpeng Li, Xin Yi, Yu Wang, Yuannian Jiao. **Toward high-quality genomes: Standards, challenges, and strategies for assembly and annotation** | Review；Journal of Systematics and Evolution 64(5):895–910；首次在线2026-09-16；DOI [10.1111/jse.70118](https://doi.org/10.1111/jse.70118) | 2.2.3 correctness、2.3 challenges、2.4 strategies；已获得Wiley HTML所选章节，未逐篇复核其全部引文 | 是近期质量与组装策略框架，主要围绕长读与复杂真核；不能由其重点在长读，推导只有二代就不能组装 |

原始来源：

- [PLOS全文](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006994)。
- [Rice & Green作者托管PDF](https://pgl.soe.ucsc.edu/riceAnnRev19.pdf)。
- [Li等Wiley全文](https://onlinelibrary.wiley.com/doi/full/10.1111/jse.70118)。

未纳入已读综述：2017 **Approaches for in silico finishing of microbial genome sequences**，DOI10.1590/1678-4685-gmb-2016-0230；检索得到scaffolding、assembly integration、gap closing、error correction及evaluation的分类片段，但PMC正文遇验证页、SciELO访问失败，作者元数据及完整相关章节尚未完成核实，不计为本轮全文学习。

## 2. 从综述提炼的机制，不把工具名字当方法

Ghurye & Pop的关键区别是连接信息来自何处。实验数据可支持样本内相邻关系；synteny利用进化保守性推断相邻关系。单参考排序主要寻找与该参考一致的方向和次序；多参考算法处理不同参考给出的冲突。MeDuSa采用加权图及路径覆盖近似，Ragout采用共线块、断点图及进化简约模型。推断的支架关系并没有给出缺口真实碱基。因此连接、补洞、碱基校正必须作为不同步骤和不同证据输出。

**综述存在需要回查的概括**：PLOS的synteny章节把MeDuSa和Ragout一起描述为使用多参考和系统树。不能据此给MeDuSa强加必需系统树输入；应以MeDuSa方法论文和官方CLI为准。综述可帮助发现算法类别，但不能替代接口审核。

Rice & Green说明参考同源关系确实可以减少新增实验的需求；RACA用参考加外群，Ragout用多个参考及进化关系来减轻单参考特有重排的影响。由此导出的项目选择规则是：**先看候选参考间的结构保守性和目标支持，再选择单参考排序还是多参考重排推断；不能只按同属/同种标签自动通过**。多个参考一致仍可能共享同一偏差，没有成为目标样本的独立长程测量。

Li等2026综述把连续性、完整性、准确性分开，并区分串联重复塌缩和散在重复产生的图连接歧义；其2.4.3把reads补洞与从另一套assembly获取候选片段分开。由此对软件接口的要求是保留每段新增序列的来源、不能把RagTag scaffold与patch混用，也不能把BUSCO或N50单独作为准确性结论。该综述涉及的长读策略不能原样移植到只有二代的输入。

以上为简要转述及项目推导，未大段复制综述文字。

## 3. 建议方法层次（本项目综合设计，不声称是某一综述的原始分类）

| 参考介入层次 | 实际问题 | 应追溯证据 | 所需补充原始方法 |
|---|---|---|---|
| 组装前/组装中 | 参考坐标帮助reads分组、局部组装或约束图路径 | reads分配歧义、未比对reads恢复、分块边界覆盖、目标特有序列 | Lischer & Shimizu2017参考引导局部组装等；不在上面两篇scaffolding综述主要范围内 |
| 初装后二次组装 | 参考与reads共同辅助延伸或连接 | 延伸碱基及路径的reads支持、参考诱导错连 | AlignGraph等原始算法论文与接口 |
| 初装后挂载 | 排序、定向、连接contigs | AGP逐连接来源、共线块歧义、参考间冲突、样本支持 | RagTag、Ragout、MeDuSa等工具手册 |
| 参考坐标共识 | 在参考结构上表示目标差异 | mask规则、变异表示、无覆盖区、参考外序列 | 变异检测与共识工具手册；单独交付类型 |
| 修正/补洞/整合 | 切断、reads补洞或使用其他assembly片段 | 断点或新增片段来源、未解决gap、真实SV误改风险 | 各具体子命令；不能靠软件名猜能力 |

“从头组装”可以是参考引导大流程内的局部步骤。相反，“reference-guided assembly”在不同论文可能仅指挂载，也可能指直接共识；知识库必须用输入与操作定义，而不是仅按术语归档。

## 4. 应变成软件选择与验收的规则

1. 用户已有参考，路由必须显式调查参考用途：引导局部组装、二次组装、挂载或坐标共识；不能默认只谈最后一步排序。
2. 记录参考身份、组装版本、质量、倍性及共线性；比较覆盖和唯一锚定，保留目标未比对与未定位序列。参考来源与目标实验支持分列。
3. 单参考方法的便捷性、多参考方法的计算负担与冲突处理要比较；多参考数量不是可靠性的充分条件。
4. 非N碱基恢复、contig连续性、scaffold组织、拷贝表示和逐连接证据分别报告，参考排序后的N50上升不能替代其他维度。
5. 具体生物数据上哪个方法更好仍需实测；三篇综述不支持通用相似度阈值、不保证100×短读可恢复全部重复、不保证参考辅助结果自动达到T2T。

本文件未增加任何生产运行、源码全审或benchmark完成计数。

## 5. 另一个综述条目的类型核实（本轮仅摘要）

Jang-Il Sohn, Jin-Wu Nam. **The present and future of de novo whole-genome assembly**. Briefings in Bioinformatics 19(1):23–40（2018卷期）；DOI [10.1093/bib/bbw096](https://doi.org/10.1093/bib/bbw096)。[PubMed](https://pubmed.ncbi.nlm.nih.gov/27742661/)明确标为Review；不是benchmark标题。摘要涉及de Bruijn图、短读歧义、长读与混合组装，不能仅因这次核实题录摘要就声称全文已学。本轮未将其作为参考辅助工具能力的直接证据。
