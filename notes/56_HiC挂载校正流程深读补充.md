# Hi-C挂载与人工校正：坐标恢复源码及实测补充

**同日后续更新**：文末PDF访问失败保留其早期批次含义；现在已下载两份官方PDF，读完抽取文本并查看12个关键图文页。新增[培训审查及版本边界](sources/sanger_curation_training_review_2026-11-02.md)，仍未运行PretextView GUI或真实人工校正。

2026-11-02。多agent分工之一，承接[35指南](35_EBP与Sanger_HiC挂载及人工校正指南.md)、[52接口](52_Juicer_BUSCO_Flye接口源码与排错补充.md)。本批新增：真实执行有编辑的YaHS post转换、FAI输出分支和重复/遗漏案例；静态追踪Pretext回写及3D-DNA后处理。没有执行GUI人工审图、Hi-C比对或新生物样本挂载，不增加完整工作流数量。

## 版本与本批阅读边界

- 本地YaHS commit `6c46061ea1665073068cccbed81c6707e3bd07bf`，`juicer post --version`为1.2.2；完整阅读本次相关`juicer.c::assembly_to_agp/main_post`和`assembly_annotation`，并检查`sdict.c`的FASTA写出分支。新运行4次post转换，非4次组装。
- 本地3D-DNA commit `cb63403c329dd45d0fdc4851746b5a8587528132`（201008）；补读post-review finalize/seal调用关系和edit-fasta脚本，不改变07已记录的版本身份，没有运行3D-DNA。
- 在线agp-tpf-utils当前main的pyproject标1.4.1、Python≥3.11；新读`pretext_to_asm.py`入口/参数、`build_assembly.py`重映射与缺失恢复、`assembly_stats.py`统计/警告。**main的完整commit未解析，不是已冻结发布版，也没有安装执行此包。** 远端页面可能有缓存，不能用1.4.1字符串替代内容哈希或锁定依赖。

版本、源码SHA256、命令与来源见[来源账本](sources/parallel_hic_2026-11-02.json)、[实测目录](../tests/parallel_hic_review/README.md)。

## YaHS到JBAT回写的实际数据模型

`juicer pre -a`生成的assembly定义编号、片段长度，liftover.agp将这些片段映射至原contig区间。`assembly_to_agp`读取`:::fragment`标识，以同一原片段累计长度恢复切分起点；排列行中整数的绝对值选片段，正负号表示方向。AGP使用1-based闭区间，C内部使用0-based偏移，写出时显式加1。

因此，.review.assembly、liftover.agp及原FASTA必须作为同一版本绑定。文件名相同不保证匹配；人工改动片段定义顺序、长度或编号，可能改变恢复坐标。不能只保存review文件而丢弃liftover与原FASTA。源码依据：[固定commit juicer.c](https://github.com/c-zhou/yahs/blob/6c46061ea1665073068cccbed81c6707e3bd07bf/juicer.c)。

**新验证的输出分支：** 第三参数接受`.fai`时，程序有长度字典，可以生成FINAL.agp，但不会生成FINAL.fa；输入原FASTA并给`-o`才会进入序列写出分支。退出0且缺FASTA未必是崩溃，应先核对实际输入和所请求输出。缺少`-o`也不能期待文件前缀产物。

## 有编辑的小例：不是此前未编辑回环的重复

人工构造A=20 bp、B=16 bp、C=12 bp，共48 bp，A在8 bp处切分。编辑后将A后12 bp倒向、连接B、再连接A前8 bp；C独立倒向。各连接用100个N占位。真值由原序列直接切片/反向互补定义，独立于AGP解析器计算。

| 实际命令案例 | 退出 | 核查 |
|---|---|---|
| 原FASTA＋切分/翻转/重排assembly | 0 | 236 bp和12 bp两条输出，与人工真值逐碱基一致；48 bp原序列每个坐标恰好使用一次 |
| 同一assembly＋FAI | 0 | AGP与上例相同，没有生成FASTA |
| 排列中重复使用A前8 bp | 0 | 转换器写出重复；独立区间清单发现8 bp源坐标被使用两次 |
| 排列中遗漏A前8 bp | 0 | 转换器写出缩短结果；独立清单发现8 bp原坐标未使用 |

[脚本](../tests/parallel_hic_review/scripts/edited_roundtrip.py)、[命令/日志/哈希/判定](../tests/parallel_hic_review/execution_manifest.json)。这些重复/遗漏是构造的输入，不是已证实的上游bug：转换工具不等同生物学守恒验证器，审阅中也可能有明确隔离序列的合法需求。

开发时需在primary、haplotigs、contaminants、unplaced等**全部输出及有理由的排除表**上核算源区间。总长度相同仍可能同时重复和遗漏；非N总量相同也不够，应检查原contig的每个区间、方向、使用次数与排除原因。输出236+12=248 bp中的200个N是占位，不是新恢复的200 bp序列。

## Pretext回写：新读到的具体保护及副作用

[pretext_to_asm.py](https://raw.githubusercontent.com/sanger-tol/agp-tpf-utils/main/src/tola/assembly/scripts/pretext_to_asm.py)入口检查Pretext AGP中的`bp_per_texel`；普通AGP不能只改后缀冒充Pretext导出。当前默认clobber=True，自动化应显式禁止覆盖或创建独立目录。输入索引可在原FASTA旁生成，故只读输入目录需要提前安排。入口可读取额外YAML资产，输出不一定是一份输入原样改序；需登记补入资产与分类。

[build_assembly.py](https://raw.githubusercontent.com/sanger-tol/agp-tpf-utils/main/src/tola/assembly/build_assembly.py)利用图谱分辨率确定端部误差处理，重映射后恢复图中未出现的输入片段；切割后检查片段衔接、重叠与长度守恒。默认最大长度2 Gbp会尝试在gap处分段，找不到可用gap可报错；因此输出比GUI中多条可能来自此规则，不能直接诊断成编辑丢失。恢复的未显示序列仍需审计其分类及原坐标。

[assembly_stats.py](https://raw.githubusercontent.com/sanger-tol/agp-tpf-utils/main/src/tola/assembly/assembly_stats.py)按源/输出连接集合计算joins和breaks，按输入片段长度作部分统计分母；跨hap挪动与新建连接的统计含义不同。源码注明某些SUPER_前缀再校正场景可能影响统计。常染色体数不一致等检查记录warning，不能把退出0解释为所有sanity checks通过。

本批只是这些模块的静态阅读，未验证标签冲突、精度恢复和超长分段的运行行为；不把源码中的保护说成已部署在本项目。

## AGP内部约定与提交标准必须区分

[NCBI AGP2.1](https://www.ncbi.nlm.nih.gov/genbank/genome_agp_specification/)规定坐标为1-based闭区间，未知长度U gap使用100 bp，gap长度应为正。Sanger的[agp-tpf-utils README](https://github.com/sanger-tol/agp-tpf-utils)说明其内部使用200 bp的U gap并带9列以外标签。这是明确的接口差异：内部可被某工具接受，不等于可直接提交GenBank。

不能无声将200改100：修改会影响下游全部对象坐标、FASTA和图谱。应保留内部版本，单独生成并验证提交版本，记录gap重编码和坐标变换；也不能因写成N就推断未知间隔长度已知。具体提交转换需与对应数据库规则和真实证据核实。本次fixture显式用100 bp，未运行NCBI完整官方验证器。

## 3D-DNA后处理：重投影图与重新比对的区别

本地post-review默认stage为finalize；seal会调用主流程的seal阶段，不能当作同一无变化导出动作。finalize从review拆出cprops/asm，重投影原mnd坐标生成最终图，再切原FASTA并进入finalize-output；中间图使用的是旧比对的转换结果，**不是对新FASTA重新mapping**。新边界和跨个体结构争议需另外考虑重新比对及独立长读证据。

本地edit-fasta脚本提示依赖cprops与FASTA兼容，不能期待它替代全输入一致性审计。输入FASTA顺序/ID/长度、MND参考字典、原cprops和review四者都应以manifest绑定。来源：[固定post-review](https://github.com/aidenlab/3d-dna/blob/cb63403c329dd45d0fdc4851746b5a8587528132/run-asm-pipeline-post-review.sh)。

## 同种非同个体Hi-C：可执行对照的设计记录

这是设计，尚无新跨个体实测。先固定目标A的初装S0、可用HiFi/ONT及源图，不用B个体Hi-C提前改变A的分相，避免无法分离挂载与分相作用。

1. 保留S0；用B文库按固定过滤/软件配置得到S_B；必要时增加不切原contig或其他候选参数作敏感性对照，不能凭预期染色体数挑最顺眼一版。
2. 每个新增连接/断点记录原A两侧区间与方向、B有效唯一分子、局部可比对性、覆盖/重复、A图分支和跨边界A长分子。B信号一致而A分子支持相反结构时，保留个体SV解释，不强行改为B核型。
3. 分开报告挂载比例与错接疑点；在相同源区间及分母上比较拷贝、独立k-mer、BUSCO、A长读支持和不确定区域。用B重新出图只是同源内部检查；即使把B reads分成训练/保留集，也不能解除“都来自B个体”的限制。
4. 无足够A证据且B图改善者标“B支持、A结构未确认”；重复区歧义、冲突者可保留unplaced或多个候选。不要用一个综合分数自动把“未知”判成“有利”。

最低待开发记录字段：event_id、input_manifest、A坐标、编辑类型、B分子与过滤、A支持/反对、替代解释、复核图、置信等级、是否保留。现成post工具复用；跨个体证据仲裁与全部输出区间核算仍需后续开发，不宣称自动功能已实现。

## 仍未完成

PretextView交互训练与截图、Sanger两个PDF逐图阅读、微信视频解析、agp-tpf-utils固定commit安装/测试、TreeVal/curationpretext匹配版test profile及真实A/B案例。此轮两份PDF分别遇cache miss/不支持octet-stream，来源账本保留失败；不计为已阅读图例。
