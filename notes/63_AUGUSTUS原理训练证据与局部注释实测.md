# AUGUSTUS：原理、训练、证据与局部注释

学习日期：2026-11-04（Asia/Shanghai）。用户要求系统学习经典基因预测软件，重点补全基因结构注释，而非只认识上层流程名称。

本批固定 **AUGUSTUS v3.5.0，commit `99e04771a7dc2feac4a62a60e88fd2f790c7bb3a`**。证据包括官方手册指定章节、经典论文分层阅读、关键源码静态核查及官方小数据组件执行。完整记录见[实验目录](../tests/augustus_learning_2026-11-04/README.md)。**未执行目标多毛类注释、TBtools/GSAman GUI、完整BRAKER/GALBA流程或生产验收。** 本文的训练/测试统计不是目标物种准确率。

## 1. 为什么经典，实际在预测什么

2003年方法论文提出AUGUSTUS及其内含子长度、剪接信号和GC相关建模；2006年扩展外部hints和可变转录本；2008年进一步整合本物种及共线映射的cDNA。这里不以引用次数或“经典”推断它对任意物种优于其他工具。

基因组FASTA给出的是DNA，软件需要把序列解释为编码外显子、内含子、基因间区及适用时的UTR。AUGUSTUS的核心是广义隐马尔可夫模型（GHMM）：结合序列内容、起止密码子、剪接信号、长度分布、阅读框和物种参数，对可行结构评分，再解码得到预测。可把任务概括为寻找给定DNA、模型及外部证据下最合理的结构；这不是简单挑最长ORF，也不是把同源蛋白对齐结果原样输出。

静态核查：`src/intronmodel.cc`中的`lenDist`和长内含子的几何尾部处理说明内含子长度不是一个统一固定值；剪接两侧的编码框也参与约束。`src/augustus.cc`区分FASTA预测和GenBank预测加评估；`src/hints.cc`解释证据属性；`src/gene.cc`负责不同输出与终止密码子约定。仅核查相关函数，未审计全部算法或证明实现正确。

预测概率是模型内部的不确定性，不是经过本物种独立校准的“真实正确率”。边界满足剪接信号、蛋白可翻译，也仍可能是旁系同源串贴、融合、漏外显子或错误异构体。

## 2. 基本接口及容易混淆的对象

```bash
augustus --species=MODEL --gff3=on --softmasking=on genome.softmasked.fa > predicted.gff3
```

这是接口模板，`MODEL`要替换为已验证的参数集。运行时记录FASTA SHA256、参数目录及配置哈希，不能只存软件版本号。

| 对象/参数 | 实际含义与使用边界 |
|---|---|
| `--species` | 选择统计模型目录；不是给输出贴物种名，也不自动训练 |
| `AUGUSTUS_CONFIG_PATH` | 包含species、extrinsic等子目录的配置根目录；训练需可写副本 |
| `--softmasking=on` | 解释小写重复区域；保留原坐标。不是删除重复，也不等于重叠重复的预测一律无效 |
| `--strand=both/forward/backward` | 搜索的链；负链结构需按转录方向解释 |
| `--genemodel=partial` | 允许输入边缘的不完整基因；局部窗口常需保留这种可能性 |
| `complete/atleastone/exactlyone` | 加强结构约束；强制得到一个完整模型不构成基因存在证据 |
| `--UTR=on` | 必须有匹配的UTR参数；有预测UTR也不等于有RNA末端验证 |
| `--print_utr=on` | 在本次人类模型试验中显式输出UTR特征 |
| `--sample=0` | 本批确定性Viterbi试验不做概率采样；不据此声称已估计可信后验概率 |
| `--alternatives-from-evidence` | 根据hints产生候选异构体；不是所有组织实际异构体目录 |
| `--alternatives-from-sampling` | 采样潜在结构，须区分模型候选与RNA证实异构体 |
| `--gff3=on` | 显式GFF3输出；默认输出不可凭扩展名当作标准GFF3 |

本批例子中多个CDS行可以共享同一`ID=*.cds`，属于一个不连续特征的多段表示；验证器不能简单要求所有GFF3行的ID全局互异。应验证gene/transcript/CDS关系、Parent存在、坐标、链和phase。

## 3. 训练：模型参数与超参数分开

`etraining`从已标注的GenBank基因结构估计编码区、内含子和基因间区参数；`optimize_augustus.pl`反复训练和评估，调整剪接窗口等元参数；两者不同。训练不是直接喂一份RNA BAM，也不是把已有物种模型目录改名。

训练标签应来源明确、结构可靠、含足够多外显子基因，并尽量覆盖目标基因结构特点。官方教程的约200个训练结构、100–200个测试结构及更多高质量结构的建议是经验指引，不是所有物种的普适验收线。传统训练格式要求每基因选一个转录本、避免重叠；标签序列和基因组版本必须匹配。

```bash
# 在独立可写配置中创建目标模型；示意，未针对Travisia执行
new_species.pl --species=target_model
etraining --species=target_model genes.train.gb
optimize_augustus.pl --species=target_model genes.train.gb
etraining --species=target_model genes.train.gb
augustus --species=target_model genes.test.gb > heldout.out
```

这组模板须先设定正确的终止密码子约定和模型配置。优化过程仅用训练集内部交叉验证，最终测试集不能参与调参。按蛋白同源簇、重复窗口和位点等检查泄漏；随机分文件不保证旁系/等位同源独立。生产测试还应避免把用于生成训练标签的同一蛋白/RNA当作完全独立验证证据。

本版本脚本默认`--kfold=8`、`--rounds=5`；旧HTML说明段写10折，与实际脚本有差异。优先记录固定版本源码和实际命令，不能混用教程年代。`randomSplit.pl`固定随机种子4；本批使用上游已经分好的392/100位点，没有宣称重新做同源簇隔离。

### 必须先核对终止密码子

`--stopCodonExcludedFromCDS=true`表示输入CDS不包含终止密码子；`false`表示包含。它同时影响训练标注解释和输出，不能只当显示开关。不同格式或上游产物要分别检查。

本批旧教程的`true`不适合仓库`examples/chr2L/genes.gb.*`：独立提取发现训练392条CDS末端均为TAA/TAG/TGA，测试100条也均包含终止密码子。错误选项下`etraining`退出0，但stderr出现大量末端错误；不能验收为成功训练。改为`false`后训练stderr为空，整基因匹配恢复。记录了错误与修正，未删除反例。

## 4. hints：把外部证据变成有语义的结构约束

```bash
augustus --species=MODEL --gff3=on \
  --hintsfile=evidence.hints.gff \
  --extrinsicCfgFile=matched.extrinsic.cfg genome.fa > evidence.predicted.gff3
```

普通注释GFF、Miniprot GFF和RNA BAM均不能仅改文件名后充当hints。hints仍是9列，但第三列和属性的含义要匹配AUGUSTUS；染色体ID、坐标体系、链和外部配置必须一致。

| hint/属性 | 含义 |
|---|---|
| `intron` | 精确内含子范围，通常来自跨剪接比对；不是任意两个覆盖峰之间的空白 |
| `exon` / `exonpart` | 完整外显子边界／外显子内部的一段；后者不证明两端边界 |
| `CDS` / `CDSpart` | 编码区精确片段／部分编码区；RNA外显子不一定都是CDS |
| `start` / `stop` | 翻译起止；不要与转录起止`tss/tts`混淆 |
| `src=E`等 | 外部证据来源类别，需在extrinsic配置中有定义；GFF第二列不能代替此属性 |
| `grp` | 属于同一个证据对象的一组约束；保留同一转录本/比对的关联 |
| `mult` | 重复支持数量的模型输入；不自动代表独立分子、独立文库或真实表达量 |
| `pri` | 证据组优先级；不等于统一可移植的可靠性分数 |

extrinsic配置对兼容结构给予bonus，对缺少相应支持的特征施加malus，另可按来源/分数类别修改。部分惩罚按碱基累积，数值影响可能随长度放大。不能把任意“RNA=10、蛋白=5”直接当通用参数。RNA未取样或低表达时缺少支持并不证明该基因不存在。

`src=M`常被配置为强人工约束，应仅用于已审查结论；人为拖动后把错误边界强制喂回，也可能强迫得到错误结构。矛盾证据、序列不兼容证据和不确定末端要保留审查记录。

RNA路线：剪接比对BAM及其质量筛查→`bam2hints`提取支持→用匹配配置预测。`bam2hints`不是RNA比对器或完整转录本组装器；本版本默认只输出内含子hints。蛋白路线可借助适用的转换工具/流程准备hints，或AUGUSTUS-PPX使用特定蛋白profile；PPX的profile不等同一份普通蛋白FASTA，本批只读其入口、未执行PPX。

## 5. 局部预测与坐标恢复

方式一：对**单条目标染色体**输入使用原坐标区间：

```bash
augustus --species=MODEL --gff3=on \
  --predictionStart=START --predictionEnd=END chromosome.fa > local.gff3
```

输出保留输入染色体的坐标。v3.5.0的`cutRelevantPiece`先获得序列再截取，释放完整序列并保存偏移；因此能减少核心预测的区间规模，不能承诺启动时不读完整序列或内存始终等于窗口大小。对多FASTA直接加这两个参数，该函数会警告并只保留第一条；它们不是“在所有染色体中自动找到目标区间”的选择器。

方式二：先把目标区间`[S,E]`取成新FASTA，给新ID，预测后回填。常规1-based闭区间下，正向截取的局部`[a,b]`恢复为`[S+a-1,S+b-1]`。若截取后反向互补，则恢复为`[E-b+1,E-a+1]`，并翻转链。负链上的多个CDS按转录方向排序，phase不能按正向排序重算。BED的0-based半开区间、BAM内部位置和GFF闭区间要明确转换。

hints也必须截取、改ID并平移；BAM浏览器轨道必须保持与当前参考一致。跨窗口的证据不能随意剪短后仍宣称是完整intron/exon。记录原染色体、S/E、方向、FASTA哈希及输出ID映射。

窗口须包含合理侧翼，并在候选触及边缘时扩展复查；截得太紧可能丢启动/终止、遗漏外显子、拆开一个基因或混入邻近基因。没有适用于所有多毛类的固定侧翼长度。

## 6. 接到用户提出的人工矫正场景

以下为证据组织与验收设计；**未验证TBtools/GSAman具体版本的菜单、插件调用参数或导出行为**。

| 环节 | 可以贡献什么 | 需要重点审查 |
|---|---|---|
| 同源蛋白与Miniprot定位 | 候选基因区、编码片段和同源覆盖 | 旁系同源串贴、片段命中、frameshift、蛋白物种距离；ARF植物案例不能直接代表多毛类 |
| RNA BAM轨道 | reads覆盖和跨剪接支持 | 比对质量、多重比对、链特异性、组织来源；一个junction不证明整个异构体 |
| 局部转录本组装/BLAT | 重建并回贴转录模型 | 融合、截短、保留内含子、局部旁系同源混淆；重新比对不是自动纠正基因组序列 |
| AUGUSTUS局部预测 | 给定模型/证据下补充或比较候选结构 | 模型选择、hints、窗口边缘、相邻基因融合/拆分 |
| 拖动外显子、CDS预测 | 形成可审查的编辑模型及ORF | RNA边界、相位、起止、翻译、同源覆盖、UTR/CDS区别 |

修订后至少保存：原模型、新模型、位点版本、每次边界变化、证据轨道/来源与支持和冲突、编辑理由、CDS/蛋白序列。完整ORF检查包含阅读框、内部终止、起止完整性；但不为满足完整ORF而凭空补外显子或掩盖真实假基因/组装错误。假基因、非经典剪接、不完整末端和证据冲突应作为明确状态保存。

单/少数位点的计算量可以远低于全基因组训练和批量RNA处理；本批仅报告小例的实际时间/RSS，不外推“任何普通笔记本都能完成全物种注释”。GUI载入整套轨道、BAM索引和底层调用也有独立资源成本。

## 7. 本批实测及如何解释

完整命令、stderr、时间/RSS、输入与二进制哈希见实验目录JSON/TSV。

- 官方人类短序列：无证据、官方hints、UTR预测均实际运行。无证据2个模型16段CDS；hints仍2个模型16段CDS，但坐标和翻译结构改变，说明只看基因数不能判断一致。hints分支有不完整末端，不能宣称所有预测均完整。
- 区间`HS04636:501–8953`：区间输出与截取后坐标回填一致；反向互补窗口恢复坐标与链后结构一致。这是一个例子的交接检验，不证明所有窗口预测均不受上下文影响。
- GFF Parent、坐标、CDS相位及独立翻译检查已执行。终止/不完整状态逐模型记录，未强制把所有不完整模型当失败。
- 官方GenBank位点的预测加评估运行；不存在的模型与倒置区间返回非零，为预期失败例。
- 基础训练392位点，评估100位点。使用正确的包含stop约定后，新训练模型整基因Sn=0.47，输出表称specificity的列为0.301；预装fly对应0.59和0.373。此处后者含义为预测精确率TP/(TP+FP)，不是TN/(TN+FP)。不同模型训练史及同源泄漏未完全审计，不作独立公平benchmark，更不能当多毛类准确率。
- `bam2hints`用官方小BAM输出6条内含子hints，与上游预期文件逐字节一致；从中取chr2R窗口的一条hint平移后实际运行局部预测。未重做上游reads质控/比对，也没有独立人工真值评判改善。
- `blat2hints.pl`对仓库现成EST PSL执行转换；BLAT本体没有运行，不称完整BLAT重构实测。
- 有界元参数优化只演示`/Constant/dss_end`、两折、一轮：原值4的交叉验证目标0.6550，高于候选2的0.6251和候选3的0.6545，因此保留4。重训后100位点的整基因Sn/精确率仍为0.47/0.301，没有取得提升。不能等同默认全参数优化完成；详见实验目录。

## 8. 多毛类应用与尚未完成项

固定v3.5.0物种目录未见Travisia或Capitella命名模型；不能因为有schistosoma、caenorhabditis或名称含“worm”就认定适用环节动物。Argopecten是软体动物、Notospermus是纽形动物，也不是已有多毛类训练的证明。此目录核查不代表外部不存在可用模型。

实际应用应从目标组装、重复软屏蔽、同物种多组织RNA及有来源的近缘蛋白出发，建立可审查训练标签与独立评估，再比较现有/自训模型及证据路线。BRAKER/GALBA可以承担部分自动训练和证据准备，但须固定其自身版本和输入语义；多条共享AUGUSTUS和同一RNA的结果不构成独立投票。参见[40调查](40_基因组注释软件与文献调研.md)、[41 RNA证据](41_二代三代RNA注释证据处理规范.md)、[42整合验收](42_自动多方法注释流程开发与验收_QS015.md)。

未完成：目标物种训练与盲测、完整默认元参数优化、PPX/CGP/CRF模式、真实多毛类全基因组结构注释、长RNA hints全链验证、TBtools/GSAman GUI及人工编辑导出往返。AUGUSTUS也不独自承担重复、ncRNA及功能注释的全部任务。

## 9. 一手来源与阅读深度

1. [固定官方仓库v3.5.0](https://github.com/Gaius-Augustus/Augustus/tree/99e04771a7dc2feac4a62a60e88fd2f790c7bb3a)：README/ABOUT、RUNNING的基本/采样/hints/训练章节，INSTALL相关构建选项；训练和预测教程；关键脚本/源码指定段。归档文件及哈希见`source_review.json`。
2. [2003基础模型论文](https://pubmed.ncbi.nlm.nih.gov/14534192/)，doi:10.1093/bioinformatics/btg1080：元数据和摘要，未声称全文精读。
3. [2006外部证据GHMM论文](https://link.springer.com/article/10.1186/1471-2105-7-62)：方法中GHMM、hints兼容性、奖励/惩罚、依赖性部分；未复现原论文实验。
4. [2006可变转录本论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC1538822/)，doi:10.1093/nar/gkl200：摘要及采样/后验/替代转录本方法；未复现评测。
5. [2008证据整合论文](https://pubmed.ncbi.nlm.nih.gov/18218656/)，doi:10.1093/bioinformatics/btn013：出版信息/摘要与官方引用，出版社正文访问失败，不称全文已读。
6. [官方训练教程](https://bioinf.uni-greifswald.de/augustus/binaries/tutorial/training.html)、[预测教程](https://bioinf.uni-greifswald.de/augustus/binaries/tutorial/prediction.html)：按固定版源码与样例纠正年代/输入差异，不照抄其物种泛化和速度数字。
