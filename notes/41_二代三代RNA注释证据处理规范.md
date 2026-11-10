# 二代/三代RNA作为基因组注释证据

2026-11-01；配合[40软件调查](40_基因组注释软件与文献调研.md)与[42自动配置/整合](42_自动多方法注释流程开发与验收_QS015.md)。当前为官方手册核查与实施规范，命令未在本机运行。

## 输入不能只按扩展名判断

每个文库至少记录：sample/library/individual、物种taxid、组织/时期/性别、平台、建库试剂/类型、SE/PE、链特异性、读段方向、原始/已处理状态、UMI/条码、对应reads及校验和。来自另一同种个体的RNA可用于表达/剪接结构证据，但记录变异、性别/组织与潜在结构差异；不能当目标个体相位真值。远缘RNA或蛋白明确标记跨物种。

FASTQ可识别格式、长度、质量、配对和部分平台线索；无法可靠恢复所有建库类型、组织、是否去除引物/polyA或转录方向。BAM头和标签、测序报告有用但不绝对可靠。自动推断必须附证据、置信度和来源；关键冲突阻止对应分支，其他已满足条件的分支继续。

10x 3'等端部富集文库不能当均匀全长bulk RNA；single-cell长RNA还涉及细胞条码/UMI，不能套bulk去重。DNA HiFi不可塞入IsoSeq模式。RNA低表达或未表达不等于基因不存在。

## 二代RNA

1. 文件/配对一致性和样本身份检查→接头/质量、rRNA/污染评估→保存处理前后统计；不为凑质量分无条件大量截短。
2. STAR或HISAT2做剪接比对，保留各文库/组织BAM及junction；不要先无记录合并所有样本。链特异性结合建库报告和数据验证，缺少参考时保留不确定性。
3. StringTie逐文库/组织重建→有来源映射的合并；或让固定BRAKER4自身管理其匹配的比对/组装。若外部生成BAM，不能同时重复传入同批FASTQ作为新证据。
4. 需要补充转录本时可评估Trinity，但已具高质量基因组时不是强制再做de novo transcriptome assembly；其融合/冗余和算力成本需验收，本轮未审完Trinity手册。

最大内含子、索引参数、链特异性与read groups应依据类群和数据设置；不把人类、真菌或某篇文章默认值套全部物种。

## PacBio Iso-Seq / Kinnex

先确认提供的是原始RNA CCS BAM、分段后S-reads、FLNC、聚类转录本还是已比对模型。Kinnex/MAS拼接reads需相应分段，不可把多个串接cDNA当一条天然融合转录本。普通IsoSeq根据引物方案做lima、refine，保留各阶段数量与方向；已处理数据不重复剪切。

[官方IsoSeq CLI](https://github.com/PacificBiosciences/IsoSeq/blob/master/docs/clustering/cli-workflow.md)当前推荐cluster2取代cluster；cluster2与旧cluster的文件名/低高质量分类不同，默认聚类输出涉及至少2条FLNC支持，singleton是否保留需单独记录。低支持候选不等于应一概删除，需其他证据和敏感度检查。

映射可用适用版本pbmm2 ISOSEQ或minimap2 splice:hq；是否强制转录正向取决于实际处理后方向。然后选定主重建路线（IsoSeq collapse或IsoQuant等）并保留替代比较，不将同批reads的不同产物统计为独立实验。

特别注意：refine会按协议剪polyA；[IsoQuant当前手册](https://github.com/ablab/IsoQuant)期望reads保留polyA以利模型构建。因此须按下游选择保留适用的原始/中间分支，记录tail状态，不能所有RNA统一trim后再声称满足各工具最佳输入；已去尾数据的能力/限制需按安装版验证。

## ONT direct RNA / cDNA

原始POD5/FAST5与已basecall FASTQ不同：前者需要记录适用的basecaller、模型和化学版本；后者不重复basecall。dRNA与cDNA的接头、方向、polyA、截短、PCR/RT伪影不同；同一条“ONT”开关不足以表达。

[IsoQuant](https://github.com/ablab/IsoQuant)明确支持ONT dRNA/cDNA和PacBio，可不提供现有注释而基于基因组发现转录本。它可使用二代比对矫正长RNA剪接，但短reads不用于其模型发现/丰度计算；不能宣称这一选项已经完成短长RNA全面联合组装。

[Minimap2官方示例](https://github.com/lh3/minimap2)分别列IsoSeq的splice:hq、ONT cDNA的splice、dRNA的splice加方向/敏感度选项；实际由文库方向和错误水平决定，不能所有三代RNA都用map-hifi或所有ONT都强制-uf。最大内含子与split/chimeric比对也要检查。

## 短长RNA结合：不同用途分别建模

[StringTie官方手册](https://github.com/gpertea/stringtie/wiki/Manual)规定：长RNA单独组装用-L；--mix输入按短BAM在前、长BAM在后，两者分别保存且坐标排序，不能先samtools merge成一个BAM，也不把--mix与-L机械叠加。不同组织的短长数据不冒充同一sample混合输入。无旧注释时不强制-G。

以下仅为官方接口的示意；需要已安装匹配版本、两个BAM与同一冻结FASTA，尚未运行：

```bash
stringtie -L -o long.transcripts.gtf long.sorted.bam
stringtie --mix -o mixed.transcripts.gtf short.sorted.bam long.sorted.bam
```

BRAKER4的dual和EviAnn的mix有各自输入语义，不能与StringTie --mix简单视为完全相同算法。EviAnn reads清单的fastq/bam/isoseq/mix/bam_mix标签、文件数及sample要求按固定版手册检查；ONT原始文本具体入口在实装时验证，不自创ont标签。

## 长RNA模型审查

[SQANTI3](https://github.com/ConesaLab/SQANTI3)及[当前版本QC手册](https://conesalab.github.io/SQANTI3/v6.0.2/Running-SQANTI3-Quality-Control/)用于转录本分类与伪影审查。当前README、版本化网页及旧论文接口存在差异，配置不能混用；QC、filter、rescue分别固定版本。内含子非经典、RT-switch、internal priming、截短、可疑融合和缺失末端都应记录，不能以单一read支持把模型认作完整转录本。

SQANTI类别依赖reference annotation。新物种可使用明确标记为临时的注释及原始剪接/ORF等证据，但“与自己刚预测模型一致”不构成独立验证。FSM不等于该模型在生物学上一定正确，novel也不等于错误。无合适reference时应验证工具输入策略并报告限制，不能生成假的独立金标准。

## 如何判断RNA数据够不够

RNA覆盖高度不均，不能使用全基因组D/G=50×或统一100×作注释门槛。记录有效非rRNA量、可比对/剪接比率、组织/时期覆盖、完整转录本和CDS、独立分子数及junction支持；做按文库/组织的下采样饱和分析，观察新增可靠junction、完整模型和表达基因的变化。数量饱和也不证明未取样组织的基因被覆盖。

保留未表达/无RNA支持但由蛋白或从头预测支持的候选及置信度，不为了“RNA支持率100%”全部删除。增加多个相关组织/发育时期可能比在同一组织无限加深更有价值，但按物种目标和现有结果决定，不许诺任何固定量即可全注释。

所有RNA分支输出必须附FASTA SHA、样本/组织映射、处理状态和参数，避免修改组装后沿用旧BAM/GTF。组装HiFi≥50×仍属于上游验收，和RNA充分性分别报告。
