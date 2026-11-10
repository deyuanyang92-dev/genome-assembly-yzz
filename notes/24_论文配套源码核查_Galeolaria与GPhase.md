# 论文配套源码核查：Galeolaria 与 GPhase

核查日期2026-11-01。两仓库已下载到pipelines并冻结提交。本轮是论文方法与部分源码静态核查，未运行其生物数据，不计入新增完整工作流复现。

## GaleolariaReferenceGenome

[上游](https://github.com/moniquevdor/GaleolariaReferenceGenome)，提交`01c252196c6a8ba7c8fd93376ded2bb266eb3e7e`。

阅读README、目录清单、MitoHifi和BRAKER入口，并检索全仓库核组装/挂载相关命令。当前检出的实质内容是AnnotationPipeline：RNA处理、重复注释、BRAKER/GeneMark/TSEBRA、功能注释与线粒体组装。没有找到覆盖论文hifiasm→YaHS→人工校正的完整核组装脚本链。因此分类为**论文分析脚本**，不能因为README提到assembly便计作第七套完整核组装流程。

脚本包含`{your_path}`占位符、集群module及Singularity绑定路径；复用前需替换环境、数据路径、版本与数据库。没有逐行审计全部注释脚本，也没有证明其在本机可运行。

论文对海洋环节动物的样本组织、两hap比较和人工审查有参考价值，但Omni-C k-mer调查及按长度重新分配hap染色体，不能自动迁移为独立WGS准确度验证或父母来源分型。论文方法与仓库覆盖范围必须分别记账。详细论文信息见[22](22_近期组装论文与对标地图.md)。

## GPhase

[上游](https://github.com/panlab-bioinfo/GPhase)，提交`a9221035274e7397fc05dc5be693270c2758528c`。

阅读README、环境定义、pipeline shell的输入/执行入口和末尾产物汇总、`scaffold_hap/scaffold_hap_v2.py`输出常量及重命名相关段落；未审完所有算法实现。分类为**多倍体分型挂载工具/局部管线**，不是包括样本调查、污染清理、最终全面QC的完整项目流程。

### 接入条件

- 输入是原始且相互匹配的hifiasm `*.p_utg.fa`和`*.p_utg.gfa`。不能随意重命名、过滤、purge、polish或换成最终scaffolds后仍沿用旧图；还需具有可利用的杂合信息。
- PopCNV可利用HiFi估计拷贝数；`n_chr`、`n_hap`和拷贝信息应由生物学与数据调查决定，不是调到结果好看的旋钮。
- BAM路线不同阶段采用不同MAPQ：当前README示例为Chromap-q0，内部cluster_q1、scaffold_q0。pairs路线不能在各阶段重新设置同样的过滤，不能把所有Hi-C工具强行统一为MAPQ30，也不能忽略各路线说明直接复制-q0。
- 工具有意复制并重命名部分collapsed unitigs来表示拷贝；我们19中的普通无损挂载“每段仅出现一次”约束不能原样套用，需要额外的拷贝关系与来源映射。
- 染色体内的hap分组不自动构成全基因组父母来源标记；必须说明分型证据。

### 输出与静态风险

README及Python当前命名包括`gphase_final.unitig.fasta`、`.unitig.scaffold.agp`、`.unitig.scaffold.fasta`，以及`.contig.fasta`、`.contig.scaffold.agp`、`.contig.scaffold.fasta`和`.ctg2utg.txt`。构建接触图时须选择一致的一组FASTA/AGP，并将原始联系重新映射到选定参考。

shell约454–461行末尾汇总仍检查`gphase_final.agp`、`gphase_final.fasta`、`gphase_final_contig.*`等旧命名，缺失时打印MISSING警告；Python约26–39行、1198–1205行及后续使用新命名并有部分文件检查。这是**汇总命名可能滞后的静态发现**，不能据此断言整个管线已产生假成功；尚需官方样例集成核查。我们的接入验收应核对实际最终文件、AGP重建与序列来源，而非只解析最后的OK或MISSING字样。

仓库环境有版本约束，容器示例中的latest仍需固定镜像摘要。外部示例数据入口已查，未下载和运行；不能把提供测试入口记成我们已经通过测试。

## 转为我们自己的开发要求

以上两例支持本项目独立提出的要求：代码开放必须逐阶段核查；输入图与FASTA绑定版本；正常拷贝表示与错误重复区别处理；检查真正最终产物并保存变换记录；容器和数据库版本可追溯。新论文、新工具和公开GitHub都不能替代样本适用性与实际运行验证。
