# hifiasm、YaHS 与 HapHiC 使用说明

日期：2026-11-01。以下生产命令是适配模板，除 notes/14 记载的小例子外没有在本机执行。版本以 [源码清单](sources/source_manifest.json) 为准。FASTA、BAM 和图文件必须来自同一个阶段，修改 contig 名称或序列后应重新建立索引/比对。

## hifiasm：先确定输出的生物学含义

来源：[官方 README](https://github.com/chhylp123/hifiasm)、本地 `CommandLines.cpp` 以及 notes/10 的方法论文。当前编译版本 0.25.0-r726。

方法核心是对准确长读长构建保留等位差异的重叠/string graph，使不同等位序列不被过早合并；primary/alternate 输出解决代表性组装问题，Hi-C 或亲本信息进一步帮助跨杂合区域选择一致路径。Hi-C 分相利用长距离接触构建分区，分相不等于输出序列已经按染色体挂载。

```bash
# 在独立运行目录执行；参数按测序类型和数据规模调整
hifiasm -o sample -t 32 hifi.fastq.gz >hifiasm.stdout.log 2>hifiasm.stderr.log

# Hi-C 输入是原始配对 FASTQ；--h1/--h2 不是两套 hap contig
hifiasm -o sample_hic -t 32 --h1 hic_R1.fastq.gz --h2 hic_R2.fastq.gz hifi.fastq.gz \
  >hifiasm_hic.stdout.log 2>hifiasm_hic.stderr.log

# 示例：GFA 中有序列的 segment 导出 FASTA
awk '$1=="S" && $3!="*" {print ">"$2; print $3}' sample.bp.p_ctg.gfa >sample.primary.fa
```

`bp.p_ctg` 是 primary；`hic.hap1.p_ctg`、`hic.hap2.p_ctg` 是 Hi-C 辅助分相输出，具体后缀要与该版本实际产物核对。没有亲本标签时，hap1 不能直接称“母本”，不同染色体的亲本方向未必一致。Trio 的 `-1/-2` 接受亲本 yak 数据库，与 `--h1/--h2` 的 Hi-C FASTQ 是不同接口。

小基因组演示使用 `-f0` 可减少 Bloom filter 的固定开销；真实大型基因组不能照搬为性能最优设置。`-l0` 在近交材料中有用途，普通高杂合样本不能不加判断地关闭原有去冗余。当前版本支持 ONT 选项，但平台、读长准确度、FASTQ 需求需按对应说明确认，不能把普通 HiFi 命令直接套到所有 ONT 数据。

同前缀生成的 `.bin` 会被复用；输入或影响图构建的参数变化时应换新输出目录/前缀，或按版本说明使用 `-i` 重算，避免复用错误缓存。检查 stderr 的版本、命令、覆盖峰、图统计和结束信息，保留 GFA。不要对两条完整 hap 无条件再跑 purge_dups。

## YaHS：一般 contig 挂载与显式人工校正交接

来源：[README 与示例](https://github.com/c-zhou/yahs)、本地 `yahs.c` help、`link.c` BAM 读取分支、`scripts/run_test.sh`。当前 1.2.2。

YaHS 使用不同分辨率的接触统计和挂载图逐轮连接，同时可检查/断开可疑连接。窗口尺度、有效接触和 contig 连续度共同影响结果。它不要求输入染色体数，不意味着自动结果一定正确。

```bash
samtools faidx contigs.fa
# 从与此 FASTA 匹配、已恰当去重复/过滤的比对建立 name-sorted 文件
samtools sort -n -@ 8 -o hic.namesorted.bam hic.filtered.bam
yahs -o sample contigs.fa hic.namesorted.bam >yahs.stdout.log 2>yahs.stderr.log
```

初始比对应使用适合 Hi-C 的参数，例如 HapHiC 官方的 `bwa mem -5SP` 路径；不能用常规短片段文库的 proper-pair 条件 `-f 2` 丢弃大量真实长程接触。去重复工具和 duplicate flag 的处理必须记录。

源码的 name-sorted 与非 name-sorted BAM 分支存在不同的配对位置/质量处理，因此推荐显式保留 queryname 排序约定。`-q` 默认 10；不能假设坐标排序分支与 name 排序时等价地应用这一阈值。BED 作为输入时每对 read 要相邻，按 read name（标准 BED 第 4 列）排序；不能只按第 1 列染色体排序。

主要参数：`-e` 提供限制性酶识别序列（依据真实建库）；`-r` 提供挂载分辨率序列，较小窗口更细；`-l` 调整短 contig 阈值；`--no-contig-ec`、`--no-scaffold-ec` 分别关闭相应纠错。关闭纠错应有长读长/图和接触图证据，不以期望更大 N50 为理由。不要从版本不同的博客复制参数。

保留 `sample.bin`、最终 `sample_scaffolds_final.agp/.fa` 和轮次 AGP。AGP 是输入 contig 到输出坐标的可追踪关系，不能只交付一个 FASTA。

```bash
# 这里的 juicer 是 YaHS 自带辅助程序，区别于 Aidenlab Juicer 比对流程
juicer pre -a -o sample.JBAT sample.bin sample_scaffolds_final.agp contigs.fa.fai \
  >juicer_pre.stdout.log 2>juicer_pre.stderr.log
# 按日志给出的规模和坐标尺度运行 juicer_tools pre 生成 .hic
# 大基因组可能需要缩放，遵循当前版本日志，不固定套用别人的坐标

# 在 Juicebox/JBAT 审阅并保存 .review.assembly 后
juicer post -o sample.curated sample.JBAT.review.assembly sample.JBAT.liftover.agp contigs.fa
```

`juicer pre` 成功不等于 `.hic` 已生成，更不等于人工审阅完成。真实人工校正应保存原始 `.assembly`、修改后版本、liftover AGP、异常位置和修改原因。notes/14 的回环使用未修改 `.assembly`，只检验格式转换。

## HapHiC：先理解倍性与分组目标

来源：[HapHiC README](https://github.com/zengxiaofei/HapHiC)、`haphic`、`scripts/HapHiC_pipeline.py`、`scripts/HapHiC_cluster.py`。本地版本文件记录 1.0.7；尚未安装全套依赖/运行。

四阶段为 cluster → reassign → sort → build。初始阶段对较长 contig 构建接触图并尝试 MCL inflation 分组；reassign 补充分配；sort 确定组内顺序/方向；build 输出坐标和序列。等位同源序列的错误接触会干扰分组，需要结合倍性、分相状态及图信息处理。

以下保持官方示例的处理次序；线程仅为示例，各管道进程资源会叠加：

```bash
bwa index asm.fa
bwa mem -5SP -t 28 asm.fa hic_R1.fastq.gz hic_R2.fastq.gz | \
  samblaster | samtools view - -@ 14 -S -h -b -F 3340 -o HiC.bam
# 假设 HAPHIC_DIR 已设为实际安装路径；filter_bam 是项目自带工具
"$HAPHIC_DIR/utils/filter_bam" HiC.bam 1 --nm 3 --threads 14 | \
  samtools view - -b -@ 14 -o HiC.filtered.bam
"$HAPHIC_DIR/haphic" pipeline asm.fa HiC.filtered.bam NCHRS --threads 32
```

`filter_bam ... 1 --nm 3` 是 MAPQ/NM 筛选；官方说明 NM < 3，不写成 ≤3。注意这是 HapHiC 推荐路径，不能把过滤参数机械视为全部挂载工具的统一最佳方案。该版本源码明确拒绝 coordinate-sorted BAM，接受 unsorted/queryname；不能先为浏览器建坐标索引后直接把同一 BAM 送入 HapHiC。

`NCHRS` 指输入组装所对应的预期染色体/分组数：单条 hap 与两条 hap 合并输入的含义不同，需依据倍性、核型和所用流程决定；拟南芥示例的数字不能用于未知环节动物。不要把工具要求的分组数直接等同于物种的 n 或 2n。

`--RE` 默认 GATC，应匹配建库；`--Nx` 默认 80 用于初始聚类，短 contig 仍可在 reassign 阶段处理；`--correct_nrounds` 默认 0，高质量长 contig 不宜无条件强制切断。`--remove_allelic_links` 需要倍性相关设置，适用于相应的等位误连情形；`--gfa` 应提供与此 FASTA 匹配的 hifiasm 图，不能混用旧图或别的 hap。

检查各 inflation 候选组数、组大小、未分配序列和与已知核型是否相符。最终 `04.build/scaffolds.agp` 与 `.raw.agp` 使用的 corrected/original component ID 坐标体系不同，后处理时核对；保留 `scaffolds.fa`、`juicebox.sh` 及整个分组/排序输出。出现异常跨组接触时，先检查污染、重复/等位链接、switch error 与建库质量，再调整聚类参数。

## 三者如何衔接

hifiasm 负责从 reads 建图和组装/分相；YaHS 或 HapHiC 负责对指定的 contig 集合进行挂载。若分别挂载 hap1、hap2，每次比对与过滤都必须围绕对应输入设计，不能忽略两条 hap 相似导致的跨单倍型误比对。若把两条 hap 合并交给 HapHiC，分组数和等位链接处理也随之变化。这两种实验不能仅靠替换一个输出文件名互换。

正式交付前至少检查：序列总量及未挂载量、AGP 区间/方向/复用、接触图局部异常、长读长跨连接支持、完整性与污染、分相质量。一个漂亮的对角线或较大的 N50 只能提供部分证据。
