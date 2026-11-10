# Colora 官方测试目标收尾及账本规则

记录时间：2026-11-02（Asia/Shanghai）。源码基准：LiaOb21/colora `d6569edaff8da51739688b246dda2dfb2da13d7a`；Snakemake 8.30.0。完整命令、起止时间与退出码见 `logs/colora_*.json`，完整输出见同名 `.log`。

## 默认目标运行结果

官方默认目标包含24项；前面分阶段完成输入、调查、组装、Hi-C处理/YaHS、BUSCO。末尾目标完成NanoPlot、Oatk、Bandage和gfastats；官方 QUAST 规则先后发现两个独立问题：它的Conda YAML未限制解释器，首解 Python 3.14 与 QUAST 5.3.0 的 `distutils.version` 导入不兼容；约束隔离环境后，又因项目路径含中文而被 QUAST 拒绝。保留两次失败日志。第三次在 `/tmp/yzz-quast-output` ASCII路径直接运行同版本QUAST（输入仍是本测试装配，命令选项含 `--fragmented --large`），成功生成完整HTML/TSV/PDF报告；结果目录复制回独立测试副本。Colora 的 `quast.yaml` 已在测试副本约束 Python 3.11，以便新环境不再选择移除 `distutils` 的Python；上游仓库和原科研目录未改。`python scripts/run_colora.py all` 最终返回0，Snakemake报告所有请求结果已存在且最新。此处准确含义是：所有默认目标产物齐备且DAG验收通过；QUAST结果是隔离输出路径单独生成后放回，不声称其原始规则在中文路径内直接成功。

| 软件/阶段 | 结果 | 本例解释 |
|---|---|---|
| NanoPlot 1.46.2 | `NanoPlot-report.html`、图和`NanoStats.txt`生成；8,078条HiFi、145,099,146 bp，平均读长17,962.3 bp，N50 18,785 bp | 只描述随附酵母功能测试read子集；不替代测序仪原始产出核验或多毛类覆盖评估 |
| Oatk 1.0 | 命令成功；mito fasta/GFA生成，候选序列总长90,085 bp；注释文件保留 | 测试数据、参考profile和输出都提示功能测试用途；存在重复/低分命中，不能称为经验证的线粒体基因组 |
| Bandage 0.9.0 | 输出 `mito.jpg` 成功 | 图形可视化仅用于检查输出图，不证明环状性或结构真实性 |
| gfastats 1.3.11 | 输出统计成功，单条90,085 bp序列，GC 17.11%，无gap | 是文件统计，不是完整性/分类鉴定 |
| QUAST 5.3.0 | 四个核装配版本报告成功 | scaffold前后序列数、总长、N50一致：挂载没有新增连接；报告 `report.tsv` 是可追溯主表 |
| BUSCO 6.0.0 | hap1/hap2/scaffold hap1/hap2四次离线结果完成 | 各C=7.1%, S=5.6%, D=1.5%, F=0%, M=92.9%（n=3282）；测试组装约1.25 Mb且目标覆盖高度稀疏，低值不用于判软件或生物样本质量 |
| KMC 3.2.4 + GenomeScope2 2.0.1 | k=21/p=2产出曲线和summary | 模型2.155–2.193 Mb、fit 30.5–87.5%，但多峰/采样偏差明显；不得引用为可靠G |

四个BUSCO组装版本完全相同结果，符合“YaHS无新连接”的观察；它不是Hi-C挂载正确的独立证明。所有结果限定在 ColorA 附带的测试菌株/小子集。Hi-C与HiFi来源不同菌株，FCS-GX在功能测试配置关闭。因此无生产污染筛查、相位、真实核基因组大小、装配QV或多毛类性能结论。

## 学习账本的去重语义

`software_learning_ledger.tsv`为机器可查主账本，Markdown为速查视图。记录字段包括工具/源码版本、记录时间（Asia/Shanghai）、直接证据路径、学习/运行状态、覆盖范围和可跳过范围。原生程序记录commit和二进制SHA256；Conda程序记录完整build、包URL、MD5/SHA256及工作流YAML hash在`environment_locks/manifest.json`和`.explicit.txt`。不能确认的旧环境版本保留“未知”，不由新版本倒推。

去重规则：相同工具版本+相同输入类型+同一命令目的可跳过概念和初装复习；参数、工具/参考数据库版本、物种/数据类型、工作流commit变更，或实际运行遇到新错误时，只补学受影响接口并新增一条时间记录。文档阅读、源码静态核查、成功实跑是分开的状态。环境建好或DAG dry-run通过不记成功实跑。

下一轮不再重做以上同版本初级安装/参数导览。优先转到：生产多毛类样本资产清点与样本身份核对；有效HiFi覆盖估算及50×门槛；生产适用的污染/去冗余基准；结构/重复注释和RNA证据；独立验证的核组装QC及比较基因组。每个新软件按此账本追加版本、UTC+本地时间、输入来源、命令、日志、核验及适用范围。
