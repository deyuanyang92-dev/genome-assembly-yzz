# Capitella 最新参考基因组实操（2026-11-02）

## 目的与数据来源

使用官方 NHGRI Capitella teleta 下载页列出的 2026 年 7 月更新资源，实测真实多毛类的基因组、GFF3、蛋白和重复区注释如何相互校验。来源：[NHGRI 下载页](https://research.nhgri.nih.gov/capitella/downloads.html)、[NHGRI 项目更新](https://research.nhgri.nih.gov/capitella/about.html)。下载页称更新于 2026-07-17，并提到用 Micro-C 重新 scaffold、修复 chr3；文件服务器对本次五个文件返回 Last-Modified 2026-07-12。原始 gzip 文件与 SHA256 保存在 `public_reference_capitella_2026-07/` 和 `capitella_reference_validation.json`。

这批文件：核基因组 `Ctel_Nuclear_v300125.fasta.gz`、注释 `Ctel_Nuclear_annotation_v300125.gff3.gz`、蛋白 `Ctel_Nuclear_annotation_v300125.prot.fasta.gz`、重复区 `Ctel_Nuclear_repeats_v200624.cleaned.bed.gz`、功能注释表 `Ctel_annotation_v240626.xlsx.gz`。文件名内部版本看起来早于网页日期，故按官网同页实际提供的发布包和 HTTP 元数据记录，不把文件名误解为 2026 年之外的独立发布。

## 结果

- 5 个 gzip 文件均通过 `gzip -t`。核基因组 452 条序列、277,327,828 bp；N50 25,735,969 bp、L50 5。最长 10 条序列均命名为 chrom_1 至 chrom_10，合计 257,460,751 bp（92.84%），另有 442 条较短序列。这个结果与 2026 年论文报告的约 277.13 Mb、10 条 pseudochromosome 接近；单靠名字和统计不能证明每条染色体组装正确。
- GFF3 有 gene 26,584、transcript 34,669、exon 277,120、CDS 269,556 条；34669 个蛋白 FASTA 记录，恰与转录本记录数相同。全部 GFF3 seqid 均存在于组装、坐标合法、ID 唯一、Parent 引用均可解析。
- Repeat BED 有 512,766 行；所有序列名和 0-based 区间都在组装范围内。注释中另有 `cds` 小写 104 条、`stop_codon` 2 条，说明解析和统计时不可只硬编码大小写敏感的 `CDS` 类型。
- 使用 miniprot 0.18-r281，把同一发布包的 34,669 条蛋白回贴核基因组：34,665 条至少有一个 mRNA 模型；输出 41,294 个 mRNA 模型、265,806 个 CDS 区段，覆盖 308 条 contig。回贴有多个候选模型的蛋白并不少，所以不能简单把模型数等同基因数。该结果是同源文件之间的内部一致性检查，不是独立完整度或注释准确率证据。
- miniprot 蛋白对组装的检查耗时约 115 秒，峰值 RSS 1.839 GB。压缩后的完整 GFF 输出和运行日志与汇总保存在本目录，便于复查；解压后的 277 Mb FASTA 和索引留在 `/tmp/capitella-july2026/`，不会复制进归档。

## 实操结论：可迁移到自己的多毛类项目

1. 先固定并校验数据发布包：保存来源 URL、下载时间、HTTP Last-Modified/ETag、字节数和 SHA256；对 gzip 做完整性检查。网页更新日期、文件服务器日期和文件名内部版本应分别记录。
2. 组装与注释按 seqid 做连接：GFF3 每条记录的 seqid 必须在 FASTA；检查 1-based 闭区间坐标是否越界，BED 用 0-based 半开区间，不能套用同一边界规则；校验 GFF3 ID/Parent 图完整性。
3. 校验蛋白 FASTA 与转录本 ID/数量，留意同一基因有多个转录本；多对多不能通过行数配对。跨文件应以稳定 ID 关联，并分别报告缺失、重复、无匹配。
4. 用 BUSCO、Merqury/QV、污染检查和原始长读长/Hi-C 证据补充评价。用同一注释导出的蛋白重新映射回同一基因组，只能检查格式和内部一致性，不能作为独立验证。
5. 下载页列出的 GFF3 和功能 XLSX 版本字符串不一致（v300125 vs v240626）。实测 Trinotate 的 34,669 个 transcript ID 与当前 GFF3 完全一致，但其中 131 个嵌入 peptide 序列与当前 protein FASTA 不同（另有 3 行 peptide 为空）。Panther 表是多行稀疏结果：36,471 行、30,322 个唯一 ID，13 个 ID 不在当前 GFF3，4,360 个当前转录本没有 Panther 行。NHGRI 明确说明新版本蛋白编码注释从旧组装 lift over、保留 gene ID，且官网已不再提供旧版；这可能解释 peptide 残留，但不能仅凭此认定 131 条差异的来源。官网当前不提供前版，故暂时不能在本地对照证实。数据库整理时按 transcript ID 关联功能字段，同时把 peptide 序列视为单独的有版本序列数据；将 131 条不一致和 13 个 Panther orphan 隔离审核，并把 Panther 无行解释为“未提供该表记录”，不能填成阴性功能。来源：[NHGRI 更新说明](https://research.nhgri.nih.gov/capitella/about.html)。

## 文献背景

Davies et al. 2026 报告约 277.13 Mb、10 条拟染色体、92% 组装长度 scaffolded，BUSCO metazoan odb10 为 95.7%；论文项目为 PRJEB101787。论文：[Genome Biology and Evolution](https://academic.oup.com/gbe/article/18/3/evag041/8495731)，[PubMed](https://pubmed.ncbi.nlm.nih.gov/41732109/)。论文指标是论文所用的早期发布版，不自动等于 NHGRI 2026-07 下载页更新后的本地文件指标。

## 复现文件

- 校验脚本：`scripts/validate_capitella_reference.py`
- gzip 文件、字节数、SHA256 及逐项统计：`capitella_reference_validation.json`
- miniprot 汇总：`capitella_miniprot_summary.json`
- miniprot 全量回贴：`capitella_miniprot_alignment.gff.gz`、`capitella_miniprot.log`
- 功能注释 XLSX 与 GFF3/蛋白的 ID 和 peptide 校验：`scripts/validate_capitella_functional_xlsx.py`、`capitella_functional_xlsx_validation.json`（openpyxl 3.1.5）
- 软件和方法的学习版本账本：`software_learning_ledger.tsv`
