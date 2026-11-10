# 二代 reads＋参考：参考介入组装的机制复核

日期：2026-11-02。证据等级：所列原论文选定方法段、摘要及官方 README 复核；安装0、运行0、完整流程复现0。此文件不宣称覆盖所有方法，未锁定源码提交的工具均不能称“最新版已学习”。

## 1. 修正方法分类

“使用从头组装器”不等于“整个流程不使用参考”。应分别记录参考影响：reads 分区、重叠/布局推断、图构建/遍历、跨contig连接、错误切断、序列填补。用户提供参考时，必须解释这些候选介入阶段；不能只列独立初装后排序，也不能因此承诺参考引导一定胜过独立初装。

| 方法／工具 | 真实输入和参考介入位置 | 碱基与连接来源 | 场景与边界 |
|---|---|---|---|
| Lischer & Shimizu 2017 reference-guided de novo pipeline | 目标短reads＋近缘参考；先比对定义连续块/重叠superblocks，按块分别组装，合并，再救回分化区 | 目标reads组装出局部序列，参考用于分区和合并定位；未比对reads也进入组装 | 研究包含拟南芥相关种；不同于把参考换几个SNP。历史依赖需复现，不能据论文直接套任意高杂合多倍体 |
| 原版 AlignGraph | 目标PE reads（FASTA）＋初装contigs/scaffolds＋近缘参考 | reads和初装的参考比对进入PE multipositional de Bruijn graph，参考辅助再组装延伸/连接 | 初装仍是必要输入，但参考参与重构实际序列；AlignGraph2为长读用途，不能混用 |
| AMOScmp | 目标序列的AMOS message／bank＋参考；以参考比对推断布局，再多序列比对求共识 | alignment-layout-consensus；不是单纯将参考未覆盖碱基保留为样本碱基的变异替换 | 原论文以Sanger细菌数据为核心；其短读变体与默认实现不能混同；2017流程还把较长初装contigs当作合并对象 |
| RACA | 目标初装、参考、外群/系统发育、目标成对reads比对等 | 同源块邻接推断＋目标paired-read支持；主要产生染色体片段顺序/方向 | 属参考辅助挂载，不是原始reads到contig的组装器；真实成对文库跨度限制连接可验证范围 |
| IMAP | 短读FASTQ、参考和外群等配置；多个初装→RACA→DESCHRAMBLER→Pilon/GATK | 多组装的结构整合＋参考/外群引导＋reads校正 | 论文验证酵母并应用其他真菌；是用户所说整套流程实例，但不得视为任意复杂真核的现成生产保证 |
| optimized-insilico（2023） | 目标短reads和候选参考；初装比参考排序候选，利用参考产生人工mate-pairs，并以第二参考筛选保守关系 | 连接信息由参考推断，人工mate-pair不能标记为目标样本的实测长插入文库 | 降解DNA／古DNA等无长分子场景的候选；参考一致性不构成目标独立结构验证 |

以上不是要求全部串联的工具链。参考引导组装、参考辅助再组装、参考辅助挂载、参考坐标共识是可比较的产品路线；同一个软件包可能包含多种操作，必须按子命令判断。

## 2. 逐项原始依据与版本范围

### A. Lischer & Shimizu

- 原论文：[Reference-guided de novo assembly approach improves genome reconstruction for related species](https://link.springer.com/article/10.1186/s12859-017-1911-6)，BMC Bioinformatics 18:474 (2017)，DOI 10.1186/s12859-017-1911-6。
- 本次阅读：Background关于策略区分与偏差、参考分区/未比对reads组装/非冗余合并/额外救回的流程方法、代码可用性声明。
- 作者代码声明：[Bitbucket原入口](https://bitbucket.org/HeidiLischer/refguideddenovoassembly_pipelines/)。本次未核实原仓库当前可用性或锁定提交；GitHub第三方移植不是作者原版，应另列来源。
- 不自动现代化旧依赖：更换局部组装器或合并器后必须检验配对保留、重叠块冗余、同源拷贝误合并、重复区错误布局和未比对序列恢复。

### B. AlignGraph

- [原版官方仓库及手册](https://github.com/baoe/AlignGraph)，默认分支README，完整commit／发布版本未锁定；[原论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC4058956/)，Bao, Jiang & Girke，Bioinformatics (2014)。
- 本次阅读输入、安装、CLI及算法三阶段。README要求Bowtie2与BLAT/PBLAT/NUCMER，BLAT兼容性提示v34或更早；未验证当前替代依赖。
- 输出延伸序列和未延伸序列均需保留。`--misassemblyRemoval`涉及切断/移除，不能无记录启用。建议至少比较初装与再组装的非N碱基、k-mer保留、异常PE和真实重排；参考相似性增高本身不足以证明改善。

### C. AMOScmp

- [作者原论文PDF：Comparative genome assembly](https://ccb.jhu.edu/people/salzberg/docs/AMOScmp-reprint.pdf)，Pop, Phillippy, Delcher & Salzberg (2004)，Briefings in Bioinformatics 5(3):237–248。读摘要及alignment-layout-consensus方法段。
- [AMOS官方Getting Started](https://amos.sourceforge.net/wiki/index.php/AMOS_Getting_Started)，读bank/message与Running AMOScmp部分：TGT与REF输入、bank、FASTA和布局输出；本次未锁定软件版本。
- 软件架构确实是比较组装，而非仅挂载。原文是Sanger时代细菌实例，不能因为工具能读取某格式就认定现代Illumina大真核适用。bank版本不向后兼容、异常中断锁和格式转换属于待运行核查项。

### D. RACA

- [原论文：Reference-assisted chromosome assembly](https://pmc.ncbi.nlm.nih.gov/articles/PMC3562798/)，Kim et al. (2013)，PNAS，DOI 10.1073/pnas.1220349110，读方法摘要与邻接证据机制。
- [官方仓库](https://github.com/ma-compbio/RACA) README声明为原PNAS论文版本，未锁定commit；读输入配置、输出坐标及命名警告。
- 目标成对reads与比较基因组证据是不同证据列。输出“预测染色体片段”不能解释成已填出所有间隔序列。染色体名含点会与内部物种/染色体分隔规则冲突，是配置预检候选；尚未运行复现。

### E. IMAP（新增完整流程实例）

- [原论文](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0221858)，Song et al. (2019)，*Integrative Meta-Assembly Pipeline (IMAP): Chromosome-level genome assembler combining multiple de novo assemblies*，PLOS ONE 14(8):e0221858。
- [作者代码入口](https://github.com/jkimlab/IMAP)当前重定向至ibclab-hub/IMAP；读README概要，未锁commit／镜像digest，未验证Docker镜像可拉取。
- 阅读原论文流程方法及验证对象；三套初装示例MaSuRCA、SPAdes、SOAPdenovo2，后接RACA和DESCHRAMBLER、再校正。属于参考引导＋meta-assembly整套流程，不是新的短读图组装算法。每个输入初装和整合结果需保留，不能把不同初装对同一错误的一致继承当独立验证。

### F. 参考产生人工长程约束

- [原论文](https://onlinelibrary.wiley.com/doi/10.1002/ece3.9745)，Zhou, Lu & Li (2023)，*Optimization of the “in-silico” mate-pair method improves contiguity and accuracy of genome assembly*，Ecology and Evolution 13:e9745。读摘要、3.6流程描述及结论；论文是方法研究，不能标为综述。
- [作者仓库](https://github.com/TaoZhou2021/optimized-insilico)，读README/目录概要，未锁发布版或commit，未运行。
- 论文对RagTag的数值比较限定于其数据、配置与评价定义，不能转述成RagTag通用错误率。人工mate-pair写入未来证据表时必须标记`reference_inferred`，不得伪装成测序文库。

## 3. 没有证据的名字不得补造

本次没有找到能以原论文／官方代码确认的“IMPROVER参考引导基因组组装工具”。检索出现sbv IMPROVER系统生物学验证与膜蛋白工具，均不因此纳入组装器清单。名称保持未确认，不用IMAP、iMetAMOS或普通“assembly improver”字样冒名顶替。

## 4. 后续软件开发可执行的设计约束（尚未实现）

- 输入模型保留reads、初装、参考/外群、倍性和文库方向/跨度，按真正的输入签名做路由。
- 对每个序列片段记录target-read-assembled／reference-copied／unknown-gap；对连接记录target-pair／reference-inferred／multi-reference-conserved／conflict／unknown。
- 自动对比guided与unguided分支，用来发现参考偏差；独立分支是比较依据，不应代替用户指定参考参与的路线。
- 无匹配reads、软剪切／未比对reads和unplaced初装需有去向；禁止因无参考同源关系而自动丢弃。
- 需验收用例：目标新插入、参考专有插入、真实倒位、重复拷贝差异、同源染色体差异、人工mate-pairs跨错误参考连接、局部块合并边界重复/缺失。未执行这些用例，不能写“自动减少用户debug已实现”。
