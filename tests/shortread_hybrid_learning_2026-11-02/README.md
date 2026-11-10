# 二代/混合组装学习实测，2026-11-02

这是组件与机制实验，不是完整物种组装验收。专题见[53](../../notes/53_二代与混合组装方法源码及实测.md)和[54](../../notes/54_bioSkills短读专题复核与纠错.md)。

- 审查：SPAdes4.3.0发布、手册与局部参数源码。
- 运行：已有`/root/miniconda3/envs/mitoz3.6`中的SPAdes4.0.0，conda构建h6dccd9a_3；没有改变该环境，没有把旧版运行计为新版验证。
- 实际5次组装：官方1 kb小数据1次，完全人工、无错误reads四次；另有3次负例。真实目标物种生产验收0。
- 输入、输出、日志、参数与SHA256已保存。`inputs/official`来自此版本自带test_dataset；其余inputs由本目录脚本构造，不是生物测序数据。软件局部源码及包元数据仅用于固定证据，不是新的分发或整套源码审计。

## 记录

| 文件 | 用途 |
|---|---|
| execution_manifest.json | 版本命令、官方测试、8 kb的PE/混合组装及前两个负例；不包含后续控制组，不能单独据此统计整批 |
| anchor_control_manifest.json | 18 kb控制组的PE/混合组装 |
| logs/invalid_nonascii_output.json | 第三个负例：中文输出路径 |
| repeat_information_result.json | 观测不可区分的穷举机制实验 |
| output_assessment.json | 5次组装长度、N50/NG50、auN/auNG与精确真值片段核对 |
| input_archive_manifest.json | 所有已归档小例输入的原位置、SHA256及大小 |
| source_snapshots/ | 本地选定源文件、包元数据快照；引用时保留版权/许可信息 |
| software_learning_ledger.tsv | 阅读版本、运行版本、范围和运行计数 |

## 复核与重跑

可在库根目录执行`python3 tests/shortread_hybrid_learning_2026-11-02/scripts/verify_saved_evidence.py`，只检查归档证据及校验和，不启动新组装。

`repeat_information_experiment.py`构造并检查两种8 kb排列的短片段观测集合。`run_spades_learning.py`与`run_anchor_control.py`保存了构造规则和实际命令，使用本机已有环境及ASCII临时目录。执行脚本有既有结果保护，不能直接覆写重跑；其他机器需先配置对应版本、独立ASCII工作目录和明确的归档输入路径。历史日志中的/tmp路径是原执行位置，持久副本在inputs/。

`assess_outputs.py`的逐碱基检查允许反向互补；输出中的位置是首个精确匹配，重复片段可能有多个位置，不能据此推断唯一定位。该脚本的本机依赖含旧环境及QUAST源位置；跨机器可直接核查归档真值和输出，并须显式固定自己的指标实现。

## 结果与边界

8 kb的两种组装都只有3条contig、总3220 bp；加入2300 bp人工长片段未改善。18 kb控制组从5条变为1条17999 bp；反向互补后与真值[0,17999)完全一致，仍缺最后1 bp。前后两套构造同时改变唯一块及长读长度，不能确认第一次不改善的单一原因。

人工无错误输入不模拟真实ONT错误谱、杂合性或真实基因组规模；这些结果不能替代真实样本的独立质量评估。shell网络下载失败，4.3未安装；MaSuRCA/ABySS本批未运行。详细来源/访问范围见[来源账本](../../notes/sources/shortread_hybrid_review_2026-11-02.json)。
