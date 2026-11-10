# 全基因组持续学习与实操

用户授权的会话 Goal 已设为 active，具体目标见 [GOAL](GOAL.md)。当前接续既有全基因组学习库，避免把重新列出工具当作新增能力。

## 当前新增证据

- Snakemake 8.30.0 已安装在 `/tmp/yzz-learning-snakemake-env`，原学习库及原 Conda 环境未修改。
- Colora 固定提交 `d6569edaff8da51739688b246dda2dfb2da13d7a` 已复制到独立 `work/colora`。
- HiFi/ONT 原始二进制分片已合并为新文件，并完整读取 gzip、检查 FASTQ 四行结构及序列/质量长度。HiFi为8,078条、145,099,146 bp；ONT为15,534条、274,711,323 bp。
- 默认缓存写入只读目录导致的失败已保留日志；缓存改到 `/tmp` 后，原生 Snakemake dry-run 成功，任务总数24。
- fastp、hifiasm、双hap Arima/YaHS、KMC/GenomeScope、四套离线BUSCO、NanoPlot、Oatk、Bandage、gfastats均已实际执行。QUAST 5.3.0也已单独成功生成四个组装比较报告。Colora默认24项DAG目标均有有效输出，最后Snakemake `all` 返回0并确认请求结果齐备；QUAST因Unicode输出路径限制而在ASCII临时路径运行后放回，解释和失败恢复证据见[实测收尾](notes/06_完整Colora功能测试与软件账本.md)。
- 教程中的 BUSCO `2025-07-01` 文件404。官方 `file_versions.tsv` 当前列出 `saccharomycetaceae_odb12` 日期2026-05-22及MD5；已据此下载、匹配官方MD5并安全解包，不静默更换版本。
- OatkDB已下载，按官方测试选取v20230921的dikarya profiles，并记录上游提交。

## 版本与学习时间账本（2026-11-02更新）

新增[软件学习与版本账本](软件学习与版本账本.md)及机器可读TSV。每条记软件/源码版本、记录时间（Asia/Shanghai）、证据路径、真实操作或仅阅读状态、已覆盖范围，以及未来哪些条件下可以跳过重复熟悉。Conda软件的精确build/下载URL/SHA256保存在`environment_locks/manifest.json`与同目录explicit锁文件；原生编译工具另存二进制SHA256和上游commit。未确认的历史运行版本标明未知，绝不从当前版本反推旧版本。软件升级、工作流commit变化、数据类型/目标变化或发生新故障时只重学受影响部分。

仅在独立测试配置中关闭可选FCS-GX；不宣称已经完成污染筛查。官方测试不同菌株的Hi-C只能用于流程功能测试。有效HiFi覆盖率尚无本轮可靠G估计，生产50×标准状态为pending；不能把这个测试子集称作高质量多毛类核基因组。

新增结果：miniprot原生示例输出1个mRNA、17段CDS，坐标、Parent、16个相邻phase关系通过；回贴发现Colora输入覆盖集中于核染色体I、XI及线粒体。详见[实测与边界](notes/04_原生注释测试与覆盖偏倚.md)。[方法选择表](notes/02_补充方法选择与边界.md)、[原始论文记录](notes/03_原始论文阅读与版本更新.md)、[RAGNAROK源码核查](notes/01_RAGNAROK模块补充核查.md)同步留档。

阶段结果、完整命令和失败恢复见[实操记录](notes/05_实操阶段结果与恢复说明.md)及[Colora默认目标收尾](notes/06_完整Colora功能测试与软件账本.md)。环境显式锁定清单在`environment_locks/`，不修改全局或原生产环境。

## 学习与实测的区别

| 主题 | 已接续的依据 | 当前要补的能力 |
|---|---|---|
| 调查与测序 | 既有21、27、28、30、34笔记；新读段格式和碱基量检查 | 原生k-mer调查、有效核覆盖、倍性及样本一致性验证 |
| 组装与分型 | Colora附带HiFi/跨菌株Hi-C测试已完成 | 仍需目标物种数据及同个体独立证据；测试例仅验证代码流可运行 |
| 去冗余与污染 | 既有36–38笔记及固定源码 | 生物样本清理前后拷贝/独有序列损失对照；生产污染数据库尚未运行 |
| Hi-C与人工校正 | 既有31–35与24任务DAG | 比对/去重/挂载、AGP一致性、人工审阅后重评，不能只看N50 |
| 质量与完整性 | BUSCO 6.0.0离线四套输出、QUAST 5.3.0、NanoPlot 1.46.2完成 | BUSCO结果因测试输入仅约1.25 Mb且跨品系/稀疏，不能解释为软件故障或生物样本完整性；仍需可靠k-mer恢复/QV、gap/未定位证据 |
| 注释 | miniprot原生例、参考蛋白投射和Oatk附带profile功能测试已完成 | 仍需生产型重复/结构/ncRNA/功能及RNA证据流程，不能把简单回贴等同完整基因注释 |
| 比较基因组 | 既有44研究入口 | 先审计基因组及注释资产，再做同源/核心基因；不能只比较基因数 |
| genome skimming | 作为低深度独立应用范围 | 不能以细胞器/高拷贝基因回收成功代替核基因组组装验证 |

既有资料“学习过”的结论不是本轮对全部上游实现的新审计。新结果均附命令和日志，未完成项保持未完成。

## 恢复执行

1. 以上Colora同版本/同命令软件入门与安装可按[账本](软件学习与版本账本.md)跳过。
2. 继续盘点用户目标物种/项目资产、样本身份与有效HiFi覆盖，按既有≥50×门槛评估。
3. 继续生产适用的污染/去冗余对照、结构与重复注释/RNA证据、多维QC和比较基因组。上述未完成项不能由酵母测试代替。

来源：[Colora官方源码](https://github.com/LiaOb21/colora)、[Colora原始论文](https://doi.org/10.1093/bioinformatics/btaf175)、[Merqury官方源码](https://github.com/marbl/merqury)、[Merqury原始论文](https://doi.org/10.1186/s13059-020-02134-9)、[BUSCO官方版本索引](https://busco-data.ezlab.org/v5/data/file_versions.tsv)。
