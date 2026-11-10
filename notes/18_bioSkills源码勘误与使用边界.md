# bioSkills：已核实勘误与需限定的结论

2026-11-01；依据固定 bioSkills `d91ed3d`、hifiasm `ec9a8b2`、YaHS `6c46061`。**未修改上游源码副本**，以下供本项目使用时覆盖模板。不是对 561 个技能的全面正确性审计。

## 1. 已核实会改变执行行为的问题

### Hi-C 分型输出前缀错误

bioSkills 的 `genome-assembly/hifi-assembly/SKILL.md` 写 Hi-C 使用 `.bp.`；同目录 `examples/hifi_assembly_workflow.sh` 的 Hi-C 分支也设置 `PREFIX="${SAMPLE}.bp"`。本地 hifiasm `hifiasm.1` 的输出部分明确列出 `.hic.hap1.p_ctg.gfa`、`.hic.hap2.p_ctg.gfa`；Colora 当前 hifiasm_phased 规则同样使用这些文件。

因此对当前固定版本，应在 **Hi-C 分支**设置 `PREFIX="${SAMPLE}.hic"`，HiFi-only 仍用 `.bp`，trio 使用相应 `.dip` 输出。提取之前检查实际文件存在且非空，不要让错误文件名生成空 FASTA。模式与全局分型质量也不能只靠文件名保证。

依据：[hifiasm 官方手册固定版本](https://github.com/chhylp123/hifiasm/blob/ec9a8b222d149d25b7355e83765698640d59b189/hifiasm.1)、[bioSkills 示例固定版本](https://github.com/GPTomics/bioSkills/blob/d91ed3d563019e649dc854c56ccd62551359488a/genome-assembly/hifi-assembly/examples/hifi_assembly_workflow.sh)。

### Omni-C 空酶配置失效

scaffolding 示例注释说 `ENZYME=''` 可用于 Omni-C，但定义是：

```bash
ENZYME=${ENZYME:-GATC}
```

Bash 的 `:-` 在未设置**或空字符串**时都取默认值。因此空值仍变成 GATC，后面的“无酶”分支进不去。若约定未设置时默认 GATC、显式空值表示无酶，应改为：

```bash
ENZYME=${ENZYME-GATC}
```

这只是 shell 语义修正；实际酶/建库协议仍须由样本记录确定。`GATC` 不能泛指所有 Arima 产品。

### YaHS 的 MAPQ 过滤与 BAM 排序

scaffolding 示例 `samtools sort → markdup → index` 得到坐标排序 BAM，随后执行 `yahs -q 10`。当前 YaHS README NOTE 1 与 `link.c` 明确说明：**非 read-name 排序 BAM 会禁用 mapping quality 过滤**。因此不能认为该示例真的应用了 q10。

做法是保留坐标 BAM 用于索引/审阅，再创建名称排序副本给 YaHS；或者按正确的双端规则预过滤。不要对名称排序 BAM 再要求坐标索引：

```bash
# hic.coord.markdup.bam 已完成正确的 duplicate 处理
samtools sort -n -@ 8 -o hic.name.bam hic.coord.markdup.bam
yahs -q 10 -o scaffold contigs.fa hic.name.bam
```

依据：[YaHS 官方 README](https://github.com/c-zhou/yahs/blob/6c46061ea1665073068cccbed81c6707e3bd07bf/README.md)。原示例中 markdup 只标记、未 `-r` 删除；BAM 分支的重复标记处理与导出 BED 后的显式过滤也需分别核对，不能混用。

### 细菌示例没有完成污染清理

`workflows/genome-assembly-pipeline/examples/bacterial_assembly.sh` 把 medaka consensus 复制为 final，然后调用 FCS screen，且失败用 `|| echo` 继续；没有把 FCS action report 应用为 cleaned FASTA 再交 QC。故它是**包含可失败筛查的教学脚本**，不能按注释称 final 已去污染。生产实现必须检查 screen 成功、审阅/应用结果，并让后续评价指向真正的清洁版本。

## 2. 不应照字面推广的生物学判断

| 原技能中的表述/倾向 | 本项目采用的限定 |
|---|---|
| 组装为 GenomeScope 大小 1.5–2 倍就去 haplotigs | 先明确是单个 primary、单个 hap，还是两套 hap 合计；二倍体两套完整 hap 合计约 2 倍可正常。再结合拷贝数、覆盖、杂合、污染和真实重复诊断 |
| “只有 k-mer/trio QC 能看分型”或“Hi-C hap-mers” | 亲本特异 hap-mer 是一种分型评价证据；没有亲本不能凭 Hi-C 文件自动得到父母本特异 k-mer。其他独立分型证据/实验也可能用于评估，不能把唯一方法写死 |
| “没有 UL 两个工具都无法 T2T” | 这是过度绝对化；是否能闭合取决于物种、重复长度、reads 与目标难度。不能将人类难区经验变成所有物种的必要条件；加 UL 也不保证 T2T |
| polishing 必须某固定轮数；细菌 Polypolish 等经验可直接推广 | 根据平台/模型、倍性、原始错误和前后质量决定；细菌实验结论不自动适用于高杂合真核 |
| N50 大幅增加主要说明 N 增多 | 少量 N 连接已有长序列也可大幅提升 scaffold N50；应分别报告 contig/scaffold、gap/N 总量与结构证据，不能从 N50 比值倒推 N 比例 |
| 图上某种条带即可删假重复或断开 | 接触图信号受 repeats、多重比对、倍性和真实结构影响；结合覆盖、序列、图和其他证据再编辑，保留操作理由 |
| MIMAG 示例 high_quality = 完整性/污染/GUNC 联合筛选 | 源文后面也承认 HQ 还需 rRNA/tRNA 等条件；代码标签并没有落实全部条件，宜改名为 marker_qc_pass，再添加完整标准，不可直接发表为 HQ MAG |
| 固定 BUSCO、QV、覆盖度、FCS 内存值当硬阈值 | 记录方法、版本、谱系、数据库、数据深度与项目目标；参考条件适用时才用，例子中的人类/鸟类参数不能照搬到环节动物 |

这些是对范围、证据和逻辑的限制，不声称本轮重新完成各个领域论文的全面复核。FCS 提交要求等随时间变化的政策表述，本轮没有作为确定规则采纳；实际提交时按 NCBI 当前说明核对。

## 3. 验证结果如何解释

全库结构校验通过与以上问题并不矛盾：安装器没有执行软件例子，也没有检查其生物学结论。专项审计脚本记录 shell 语法、空环境变量行为和两套固定源码的差异，见 [audit.py](../tests/bioskills_audit/audit.py) 与 [专项结果](../tests/bioskills_audit/content_checks.json)。这些不是 Hi-C 生物数据测试；本轮未运行 bioSkills 示例的实际组装。

## 追加：GenomeScope的lambda与纯合峰不是同一口径

bioSkills `genome-assembly/genome-profiling/SKILL.md` 第87行将lambda/kmercov说成纯合峰位置，不能直接用于当前GenomeScope2二倍体模型。固定GenomeScope源码 `R/nls_peak.R` 和 `R/report_results.R` 显示其lambda/kcov为单条同源拷贝的k-mer覆盖参数，二倍体典型杂合峰约λ、纯合峰约2λ；总碱基D/G还须考虑倍性、read长度、错误与过滤。不要把纯合峰直接作为 `-l` 初值，也不要把λ直接当HiFi总覆盖。默认优先让模型估计，失配时先核查峰身份和倍性。详见[27](27_测序数据预判组装难度与二代补充策略.md)。本项为源码模型口径核查，尚无本地R拟合验证。
