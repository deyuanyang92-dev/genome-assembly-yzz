# Hi-C挂载选型与HapHiC机制

2026-11-03增补：[Hi-C订购量与有效深度生产判断](sources/hic_depth_production_review_2026-11-03.md)复核新取得的HapHiC Supplementary Data 1 Sheets 3/14，并区分benchmark mapped/2密度、过滤后深度及原始订购量。挂载率接近100%仍可能有严重排序/方向错误；不能将论文最低可运行量或EBP总量基线直接作为目标样本订单。

核查日期2026-11-02。复用notes11、12、31、35、45、56及software_coverage_matrix；本轮定向补读官方README／文档，并追加HapHiC官方补充材料选定方法与命令核查（第9节），不是所有挂载软件全覆盖，也没有新增Hi-C挂载运行。原有YaHS辅助格式转换不是挂载实测，不能用来宣称算法精度验证。表中的优势为机制适配或作者所述能力，不是本项目验证排名。

## 1. 主要挂载器

| 软件 | 输入/依赖与是否需要参考 | 适合考察的场景 | 机制优势 | 局限与选型提醒 | 版本/维护与证据 |
|---|---|---|---|---|---|
| YaHS | 初装FASTA/索引＋同阶段Hi-C比对；BAM/BED等按版本接口准备；无参考要求 | 一般单套、collapsed组装；每套已分相hap独立挂载须另处理跨hap比对 | 多尺度接触/挂载图、迭代连接和纠错；无需预设染色体数；AGP/JBAT交接成熟 | 不是专门的多倍体等位链接分离器；低覆盖/重复可能产生假断点；数据不足不能靠纠错解决 | 本地1.2.2，SHA `6c46061ea1665073068cccbed81c6707e3bd07bf`；部分源码已读，新增运行0。见[12使用说明](12_组装与HiC挂载使用说明.md)及[56坐标恢复](56_HiC挂载校正流程深读补充.md) |
| 3D-DNA | 初装FASTA＋Juicer风格去重联系文件；Java/Bash/Gawk等；diploid相关模块还依赖LastZ；无需参考 | 常规染色体挂载，配合Juicebox人工校正；历史项目复现 | 迭代挂载与断错，后续polish/split/seal/merge及post-review衔接 | 自动切断和merge影响输入序列表示；diploid模式不等于高倍体分相；分辨率和真实核结构可能影响判断 | 本地固定201008 SHA `cb63403c329dd45d0fdc4851746b5a8587528132`；README还含180419/180922字样，不以标题代替可执行版本。部分后处理静态阅读，未运行 |
| SALSA2 | 初装FASTA、FAI、**按read name排序的BED**、真实酶切位点或DNASE；可选匹配GFA；无参考要求 | 长读初装后挂载；希望将组装图与Hi-C共同使用的对照路线 | 组装图能约束Hi-C连接；可记录输入切断点和每轮AGP | 没有专门保证等位/多倍体区分；旧Python/NetworkX依赖需隔离；不能把坐标排序BED直接送入 | 官方marbl/SALSA README当前描述改进版及old_salsa分支，要求Python2.7、NetworkX<1.2等；本轮未锁发布版或commit，未安装运行 |
| HapHiC | 初装FASTA＋符合排序/过滤要求的Hi-C BAM或适配pairs＋分组目标；可选匹配hifiasm GFA；不需参考 | phased二倍/多倍体，collapsed二倍体与异源多倍体也可考察 | 等位感知接触过滤、MCL分组、reassign及组内排序；能利用hifiasm分相信息 | 分组目标必须匹配输入套数/倍性；无法凭工具消除switch/collapse或跨个体相位问题；常规pipeline和quick_view目标不同 | 本地1.0.7 SHA `74f1cb27d7753ce061ee673c0d62fdd44187060e`，release指df0f5ac；同版本号后续变化需按SHA锁定；部分代码/issue已读，未完整运行 |
| ALLHiC | 目标初装/注释＋Hi-C；经典allele-aware流程需近缘二倍体染色体参考与注释构建allele table，再prune/partition/rescue/optimize | 经典自源多倍体、历史甘蔗研究复现 | 去等位链接并处理collapsed序列引起的混连，按组优化排序方向 | 依赖allele表质量及预设分组；不能说“不需要参考”的经典同一模式；不应无条件作为新项目首选 | **官方README明确不再维护，推荐C-Phasing/HapHiC**；仓库可见allhic.v0.9.8但本轮未确认执行版/SHA；Wiki方法已读，未运行 |
| pin_hic | 初装FASTA/FAI＋Hi-C BAM；C编译/zlib；无参考要求 | 一般Hi-C挂载的另一机制对照 | N-best邻居、双向选择和局部最优连接；迭代断错；SAT记录挂载路径 | 不应因某benchmark高倍体得分就称其等位感知；SAT与AGP/JBAT互转需验坐标；官方示例shell含占位/变量，不能照抄即生产运行 | 官方README部分阅读，源码/版本未锁；不以Bioconda版本代替上游已审版本，未运行 |
| GreenHill | 初装及Hi-C；支持不同haplotype-aware/pseudo/mixed输入；可结合PE/MP/长读，长读涉及minimap2；无参考要求 | 希望结合contig结构与reads进行染色体挂载、二倍体haplotype重建 | 对应haplotig合为consensus→scaffold→再phasing；适配多种初装形态 | 输入表示和对应haplotig关系必须核实；不是任意多倍体通用保证；不要把论文旧Platanus配置直接换成当前版本 | 官方README给出v1.1.0结果，不能据此确认当前执行版；2023方法论文，选定段落/README已读，未运行 |
| LACHESIS | 草图FASTA＋过滤Hi-C BAM、配置/聚类目标；参考可选作评价，不是算法硬要求 | 理解历史聚类→排序→定向框架及老项目复现 | 经典染色体尺度挂载方法，原论文含短读初装应用 | 相似等位序列/复杂倍性不是其专用设计；旧编译和samtools接口增加适配成本 | 官方明确停止积极开发；手册要求samtools0.1.19或更早；本轮未锁版本/SHA，未运行 |
| **C-Phasing** | 初装FASTA＋Pore-C/HiFi-C(CiFi)长读联系，或Hi-C/Omni-C配对reads／对应联系文件；无近缘参考要求；非普通ONT任意等价替代联系文库 | 重点候选：复杂多倍体分相挂载，也支持二倍体和单套挂载 | 专门利用长读联系提高同源区定位能力；可设两轮同源分组、等位处理及collapsed rescue | 必须按文库选mapper/模式；同源短读歧义是其出发点但不代表全部消除；输入表示、倍性及分组数仍需核实 | 官方release页本次Latest为**v0.3.2**，短SHA `6b01004`；本轮README、v0.3.1用法、release元数据已读，未做v0.3.2源码/CLI一致性审核或安装运行 |
| EndHiC | 初装长度表＋HiC-Pro bin BED、raw/normalized矩阵等；无参考要求 | 端部有充分信号的高连续contig；较碎输入官方也提供迭代模式 | 用contig端区联系降低整条contig接触混杂；比较多端区/阈值结果 | 端区大小/bin分辨率与contig长度有关；不能把固定高连续例的效果推给极碎短读初装；未确证多倍体等位处理能力 | 官方README/输入部分已读，未锁版本/SHA、未运行；不能写成“只支持长contig、碎片输入绝对不能运行” |

C-Phasing版本化模式核查：v0.3.1用法中`-n 8:4`表示染色体基数8、四倍体的两轮分组，`-n 8`走单套一次分组并跳过alleles；不能将这两种参数视为相同输出。该页CiFi示例使用`--mm2-params "-x cifi"`，旧v0.2.9页面曾用map-hifi，说明不能跨版本照搬。Hi-C/Omni-C输入为`-hic1/-hic2`，Pore-C为`-pcd`或预处理联系表；普通长读WGS不能仅改后缀冒充这些联系数据。

各工具产出的染色体尺度连接通常不恢复gap的真实碱基或真实长度。Hi-C的空间接触不等同于固定插入片段距离；不能把Hi-C“50 reads/kb”直接解释为50×测序碱基深度。仅改变N50不是准确性改善的证据。

## 2. 预处理和人工校正不是挂载器的同义词

| 工具/流程 | 角色 | 对接限制 |
|---|---|---|
| Juicer | Hi-C reads比对、配对/重复处理与联系数据生成等上游流程 | 可向3D-DNA等供联系文件；不是把contigs自动排序成染色体的挂载器；不同Juicer CPU/集群版本需锁定 |
| YaHS自带`juicer pre/post` | JBAT格式交接、编辑结果回写 | 与Aidenlab Juicer为不同程序；pre后仍需JuicerTools生成.hic；post必须匹配输入FASTA和liftover AGP |
| JuicerTools | Java联系矩阵/.hic处理 | pre创建.hic不代表人工审核已完成；与GUI/坐标缩放兼容性须记录 |
| Juicebox/JBAT | .hic图与assembly编辑、人工检查/拆分/重排 | 编辑后需正确回写FASTA/AGP；GUI看见漂亮对角线不替代完整性/相位/长读支持检查 |
| PretextMap/PretextView | 联系图构建与交互审图/编辑 | 图坐标、原FASTA与编辑AGP必须一致；Pretext导出需匹配后处理工具；不是自动挂载器 |
| Sanger TreeVal/curationpretext、agp-tpf-utils | 组织辅助轨道、校正前后图与坐标回写 | 分别承担评估/图生成/回写；不是所有工具都做自动挂载。notes35/56标明未运行GUI及真实项目 |

## 3. 可执行的选型思路（设计规则，未做生产验证）

1. 先判定输入是单套代表组装、两套/多套phased混合、mixed-haplotype，还是严重collapsed。染色体数要按实际输入表示解释，不能机械填物种n。
2. 单套高连续初装可将YaHS作为优先调查候选；3D-DNA作为有完整Juicebox流程的另一分支，SALSA2适合考察GFA协同。不是宣称YaHS总优。
3. phased或多倍体重点比较HapHiC；涉及Pore-C/CiFi或复杂多倍体时增加C-Phasing。ALLHiC保留历史方法/复现路线，并记录停维护状态。
4. GreenHill用于其支持的haplotig表示与可用reads组合；EndHiC按端部信号、bin与contig尺度选择；pin_hic可作图算法分支对照。
5. 同种不同个体Hi-C按notes31设计同一初装基线/分支；关闭或独立评估自动切断，分别记录“挂载贡献”和“目标个体相位证据”。工具等位感知不能解决样本身份差异。
6. 所有路线保留未挂载序列、原/校正组件对应、每轮AGP及联系图；核查污染、分组/顺序/方向、异常断点、k-mer/BUSCO及phase指标。自动与人工修改逐条留依据。

## 4. 比较研究的边界

已读notes11的2026正式版benchmark筛选工具截止2020-09-15，只测LACHESIS/HiRise/3D-DNA/SALSA/ALLHiC，不含YaHS/HapHiC；不能由其发表年份推出覆盖2026新工具。参考切片和真实de novo输入不同，也不能混用ranking。该论文作者评分overall accuracy不是碱基QV。比较新工具时必须固定相同contig身份、预处理计数口径、文库、参数、版本、目标表示和人工编辑范围；不要以各论文自报结果拼出统一排行榜。

本次没有重跑任何scaffolder或复现完整benchmark。原有4次YaHS post人工序列编辑转换只证明限定格式/坐标行为，不能计为4次Hi-C挂载。

## 5. 原始来源与本轮阅读范围

- [YaHS](https://github.com/c-zhou/yahs)、[HapHiC固定源码](https://github.com/zengxiaofei/HapHiC/tree/74f1cb27d7753ce061ee673c0d62fdd44187060e)：已有notes12/45/56和源账本；本轮复用，不夸大新增源码阅读。
- [3D-DNA](https://github.com/aidenlab/3d-dna)：本轮README流程/依赖，固定本地后处理范围见notes56。
- [SALSA](https://github.com/marbl/SALSA)：README改进版与old_salsa说明、输入/排序/GFA/酶及依赖。原版SALSA与SALSA2须区分。
- [ALLHiC](https://github.com/tangerzhang/ALLHiC)、[Wiki](https://github.com/tangerzhang/ALLHiC/wiki)：停维护声明、准备数据/allele prune/partition/optimize。关联Go实现[allhic](https://github.com/tanghaibao/allhic)不等同于完整ALLHiC包。
- [pin_hic](https://github.com/dfguan/pin_hic)：README概要/输入/迭代/SAT；方法论文[2021](https://doi.org/10.1186/s12859-021-04453-5)只核对题目与方法摘要入口，没有全源码审计。
- [GreenHill](https://github.com/ShunOuchi/GreenHill)、[2023方法论文](https://doi.org/10.1186/s13059-023-03006-8)：README与三个阶段段落；作者benchmark不作为本项目通用优胜结论。
- [LACHESIS](https://github.com/shendurelab/LACHESIS)：停止开发与旧依赖提示、手册结构；经典论文见仓库DOI。
- [C-Phasing README](https://github.com/wangyibin/CPhasing/blob/main/README.md)、[release页](https://github.com/wangyibin/CPhasing/releases)、[v0.3.1用法](https://wangyibin.github.io/CPhasing/v0.3.1/basic_usage/)：输入、场景、分组模式、联系人读取/回写、release元数据。版本化用法与最新release分开登记，不生成未经核对的v0.3.2生产命令。
- [EndHiC](https://github.com/fanagislab/EndHiC)：README端部/迭代定位与HiC-Pro矩阵输入；本轮没有阅读全文验证其性能数字。

## 6. 具体待开发诊断项

新增设计候选，不代表现有29条自动诊断已实现：输入FASTA/BAM/GFA身份一致性；工具专属排序和配对；酶切库vsOmni-C；旧Python依赖预检；ALLHiC停维护提示及替代路由；C-Phasing版本化文档/可执行参数差异；SAT/AGP/assembly坐标互转；倍性与分组目标；Hi-C样本身份；每连接证据与修改历史；拆分后reads联系坐标重投影；未定位和短contig去向。


## 7. HapHiC的具体判断与接口（固定源码局部复核）

用户指定原文为Zeng等2024 Nature Plants 10:1184–1200，DOI [10.1038/s41477-024-01755-3](https://doi.org/10.1038/s41477-024-01755-3)。此前只有部分README/入口/build/issue核查，不得概括为论文、算法和所有场景均已掌握。本轮增加cluster选定函数阅读，详见[HapHiC机制与10项前检](sources/haphic_mechanism_review_2026-11-02.md)。

- 它解决的是已有contig/unitig在相似同源背景下的染色体归组、排序和定向；不是从WGS reads直接重建完整相位的组装器。
- 等位接触分布识别/链接过滤、GFA已知hap标签降权、MCL扫描inflation、reassign救回与合并、组内排序优化是不同环节，不能只说“适合多倍体”。GFA先验也可能继承初装switch错误。
- `nchrs`指输入assembly所表示的预期主染色体scaffold数；一套hap、两套合并、collapsed输入不一定填同一值。`--remove_allelic_links`的倍性参数与nchrs不同。
- 固定README默认`--correct_nrounds 0`，不能口头把“具备纠错功能”变成“默认已经纠错”。异个体Hi-C尤其不能无审查启用切断。
- BAM必须按工具真实配对/排序契约准备，不能复用浏览器coordinate BAM；FASTA、GFA、BAM必须来自同一阶段并有一致ID/长度。
- `scaffolds.agp`和`scaffolds.raw.agp`引用校正组件与原组件区间的方式不同，回写时不能互换。`haphic refsort`只调整整条scaffold展示顺序/整体方向，不是RagTag式contig参考挂载。

## 8. 与转换及整体路线衔接

[60格式转换](60_组装格式转换与数据交接.md)规定hifiasm GFA导FASTA、保留GFA深度/相位标签及避免noseq误导出。HapHiC可以接收匹配FASTA的noseq GFA作辅助，但noseq本身无法生成FASTA，这两句话不矛盾。

[59参考辅助路线](59_参考辅助组装方法体系与工具选择.md)与Hi-C路线可以是并行比较或有明确证据的整合；RagTag产生的参考连接与Hi-C目标接触支持要分列。所有交付都要保留未定位序列、修改历史、人工编辑前后图与真实数据范围。新工具表和机制解释属于阅读/源码证据，没有增加真实样本挂载次数。

## 9. HapHiC补充方法：评分真值、非默认配置与迁移边界

新增证据来自[113页官方补充材料的选定方法与命令审查](sources/haphic_supplement_methods_review_2026-11-02.md)，保存原PDF、提取文本及SHA256。实际读到的是Supplementary Methods 1–4（印刷页2–6），Software Commands 1.1–1.11、2.1–2.3、3.1、3.4–3.7、4.1–4.7（选定内容跨页7–23）；**没有读完113页**，也没有重跑论文benchmark。旧机制审查的摘要/README证据与本次补充方法证据分开保留。

### 9.1 评分要依赖什么真值

| 实验 | 真值与输入条件 | 可得结论与边界 |
|---|---|---|
| 模拟染色体归组 | 人工修订的苜蓿XinJiangDaYe四倍体32条染色体模板；contig记录来源/hap/坐标/错误类型 | 挂载率、contiguity、误分配各回答不同问题；嵌合/塌缩组件排除规则限制评价范围；模板修订不是无假设生物学真值 |
| 排序/定向 | 水稻、拟南芥、CHM13noY参考切片，**按真实来源先归组**，关闭纠错 | CCC和DERANGE比较的是正确分组条件下的顺序/方向，不能当全基因组端到端准确率；SALSA2/YaHS合并多scaffold评分，3D-DNA用`0.assembly` |
| 真实案例Hi-C不一致性 | 已发表染色体组装作为真值，与待评scaffold各切500 kb bins，按距离和组间频率比较 | discordant bin-pairs/links仍依赖已发表组装和Hi-C，不能仅用未知样本BAM求无参考绝对准确率；同一Hi-C既挂载又评分存在证据依赖 |
| 真实案例组件坐标 | 已发表组装断N后组件的来源、坐标、方向已知，重新打乱再挂载 | reciprocal-best匹配及长度加权LIS区分错归组/倒置/移位；已知坐标不能外推为新的de novo样本也有相同真值 |

论文contiguity公式衡量dominant来源染色体的已挂载序列有多集中，**公式本身不保证scaffold纯度**。即使A全部序列与B片段混在一条scaffold，A的比值也可能等于1；仍须看misassignment、挂载率、scaffold数及排除集合。高连续度模拟保留了模板中的N，因此其“contig N50”还不能直接当作无gap contig N50。

### 9.2 论文结果并非一套默认参数全部跑出

- 25 kb N50例用`--Nx 70 --min_link_density 0.00002 --min_links 1`。Nx70缩小按累计长度纳入初始聚类的集合以省资源，后两项放宽救回；不能解释成Nx70纳入更多短片段。
- 低有效Hi-C深度例逐档下调链接数和密度阈值；原文给定范围1×至0.02×是特定模拟和调参实验，不能推广为本项目最低可靠Hi-C量，更不能替代所选HiFi路线的≥50×要求。原文默认倍数与绝对阈值有算术不一致，审查文件已保留原数并标待核验。
- 模拟嵌合用`--correct_nrounds 2`，模拟switch用`--remove_allelic_links <nhaps>`；它们分别对应切断和等位链接处理，不能据switch实验推断工具修复了contig内全部相位错误。
- 低N50且有较多塌缩的甘蔗/苜蓿例调整Nx、density/rank-sum过滤和救回阈值；potato C88例使用链接归一化和集中接触处理，HG002.v1还因性染色体较高link density调整阈值。高接触密度不自动等同于塌缩。
- `--skip_allhic`用于评估省去ALLHiC优化后的整条pipeline效率，仍包含其他阶段；诊断性的`--skip_clustering --verbose`另用于过滤机制评估，均不能与默认完整生产流程混计。

这些是作者实验配置记录，不是为未知新样本自动推荐的参数。后续候选配置需固定同一初装、保存默认对照，比较连接支持/冲突和未挂载序列，而不只追求更高挂载率。

### 9.3 旧命令接口和异个体Hi-C限制

补充材料过滤命令为Python `filter_bam.py ... --NM 3`；固定本地README为编译程序`utils/filter_bam ... --nm 3`。大小写和入口不同，BWA/samblaster/samtools版本、BAM配对组织及过滤计数也须记录。论文HapHiC小节没有唯一commit，不能用当前1.0.7直接代表2024论文执行版本；旧材料还有脚本名不一致及疑似BAM转BED命令笔误，逐命令复现前需对应历史代码核验。

补充材料指出，把不同水稻亚种的基因组和Hi-C分别合并，会低估同一细胞核内真实同源背景联系；这说明模拟设计可人为降低难度，**并未证明把个体B的Hi-C挂到个体A的初装一定安全**。A/B的SV、等位序列、性染色体与相位仍可能不同。按[31异个体Hi-C评估](31_非同个体HiC贡献与干扰评估.md)固定A的初装，分别记录B贡献的候选连接与冲突，以A的长读/其他独立证据核查断点和相位；B的Hi-C不能充当A的相位真值。

仍未验证：论文历史commit与全部评分依赖、所有模拟表格/补充数据、评分器实际实现和数值复现、真实目标物种及同/异个体对照。以上新增均为文档与局部静态核查，HapHiC挂载运行仍为0。
