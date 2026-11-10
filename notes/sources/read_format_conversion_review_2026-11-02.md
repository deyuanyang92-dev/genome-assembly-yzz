# PacBio/SAM/BAM → FASTQ(.gz) 官方接口核查

日期：2026-11-02。本文件仅记录官方文档核查；本分工没有运行二进制或验证生物数据。pbtk 未锁定具体版本/commit，不称“最新版本已验证”。samtools 在线手册此次明确标注 **1.25，2026-10-27发布**；不能将该在线版本等同本机已有二进制版本。

## 1. 先识别数据，格式转换不会生成HiFi

SAM是文本容器，BAM是相同记录体系的二进制压缩容器，里面可以装原始subreads、CCS、HiFi，也可以是比对结果。不能凭.sam/.bam后缀判断是否HiFi。核查测序交付说明、BAM `@RG` 中 `DS:READTYPE`、读名与质量/标签；CCS/HiFi常见读名为`movie/zmw/ccs`，仅名称不能替代质量判定。

- **subreads → FASTQ** 只是导出每次通过分子的读段，不是产生共识；不能改名为HiFi后交给HiFi专用路线。
- 适用平台及数据条件下，`ccs` 将同一分子的多条subreads计算为共识；Sequel IIe/Revio可在仪器端产生HiFi。需要按平台/化学版本选流程，不能默认所有现代交付都可本地重跑旧版ccs。
- PacBio格式规范13.0定义HiFi为QV≥20的共识；较新的fail_reads还可能含残留接头、控制、单链或未形成共识的代表subread，不能只靠导出或一个名称筛选全部问题。
- 原始BAM含read-group、条形码、预测准确度、pass数、kinetics与甲基化等信息；普通FASTQ不能等价保留这些内容，必须保留原BAM和来源。

依据：[CCS官方原理与执行说明](https://ccs.how/)、[PacBio格式规范13.0](https://pacbiofileformats.readthedocs.io/en/13.0/BAM.html)。本次不尝试重现ccs。

## 2. PacBio原生BAM优先核对pbtk的bam2fastq

旧 `PacificBiosciences/bam2fastx` 仓库在2023-03-14归档，README指向 **pbtk**；新流程不应仅沿用旧仓库安装说明。

官方明确支持多个PacBio BAM和/或DataSet XML，默认输出gzip压缩FASTQ：

```bash
# 模板；本分工未执行。-o 后是输出前缀，不是完整.fastq.gz文件名。
bam2fastq -o sample.hifi sample.hifi_reads.bam
# 预期输出 sample.hifi.fastq.gz

# 多个已确认同样本、无重复数据的交付文件可一次导出
bam2fastq -o sample.hifi movie1.hifi_reads.bam movie2.hifi_reads.bam
```

- `-u` 关闭压缩，输出扩展名去掉`.gz`；`-c <int>`控制gzip等级。
- `-p/--seqid-prefix`改变每条读名的前缀，默认不随意使用，以免破坏读名可追踪性。
- `--split-barcodes` 支持按条形码拆文件；混样必须核对样本对应关系。
- 本次README只确认BAM/XML，不将SAM当作bam2fastq已验证输入。
- `extracthifi in.bam out.bam`官方简述为按预测准确度提取超过QV20的reads；不能把它视为能从subreads计算共识，或等同完整的各版HiFi交付过滤流程。

依据：[pbtk官方README](https://github.com/PacificBiosciences/pbtk)、[旧bam2fastx归档声明及迁移指向](https://github.com/PacificBiosciences/bam2fastx)。上述参数需要在实际锁定安装版`--help`下复核。

## 3. 通用SAM/BAM可用samtools fastq，但需明确丢失信息

```bash
# 模板；适用于已确认是一条记录对应一条单端HiFi read的输入。
# 统一从stdout导出再gzip，避免只接收paired类别而漏掉HiFi类别0。
set -o pipefail
samtools fastq -n -T rq,np input.sam | gzip -c > sample.hifi.fastq.gz
# BAM同样使用上述命令，将输入改为input.bam。
```

这里`-n`保持QNAME，避免根据READ1/READ2标志自动追加`/1`或`/2`；`-T rq,np`仅把存在的指定标签写进FASTQ头部注释，不执行质量筛选，也不让全部下游程序自动使用这些标签。若确有保留所有标签的需求，1.25手册支持`-T '*'`，星号必须引号保护；这仍不能把FASTQ变成BAM的等价保存形式。

1.25手册还明确：默认排除secondary/supplementary（`-F 0x900`）；同QNAME同read类别只输出一个序列；soft-clipped碱基仍可导出，但hard-clipped已不在SAM记录中的碱基无法恢复。缺失QUAL时可能按默认值生成质量，不能把生成的占位质量解释为真实HiFi质量。完整比对BAM不是无条件优于原生未比对HiFi BAM的转换输入。

普通二代PE需另走按QNAME collate/name-sort后分R1/R2/singleton/category0的导出方案，不要套用单端HiFi模板后假定配对仍正确。samtools线程`-@`指输入输出压缩的附加线程，不能描述成组装计算线程。

依据：[samtools fastq/fasta 1.25官方手册](https://www.htslib.org/doc/samtools-fasta.html)。本轮只核对转换相关选项，不保证旧版本具有所有1.25选项。

## 4. 后续自动化验收（设计）

记录实际版本/命令、输入与输出hash、数据类别与样本；检查gzip完整性、FASTQ解析、序列和质量长度一致、read数/总碱基、QNAME唯一性及与预期保留记录匹配。对有比对记录的输入检查secondary/supplementary、缺SEQ/QUAL、hard clipping，不能把“命令成功”视为无损恢复。对标签用途另列必需标签和转换后消费者的解析支持。禁止删除原始BAM。
