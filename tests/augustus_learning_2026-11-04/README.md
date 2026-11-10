# AUGUSTUS系统学习与官方组件实测

日期：2026-11-04，Asia/Shanghai。固定官方v3.5.0，commit `99e04771a7dc2feac4a62a60e88fd2f790c7bb3a`。系统笔记见[63](../../notes/63_AUGUSTUS原理训练证据与局部注释实测.md)。本批新增AUGUSTUS/BamTools两个固定源码clone，不改变旧批次26仓库统计的时间范围，不增加完整注释流程或目标物种生产验收数。

## 已实际执行

| 内容 | 输入与结果 | 证据 |
|---|---|---|
| 核心构建 | 官方源码编译augustus、etraining；禁用CGP和压缩FASTA读取，未改算法源码 | `build_initial.txt`、`build_retry.txt`、`provenance.json` |
| 无证据/有证据预测 | 官方人类两短序列，各2个模型16段CDS，但加入hints后边界/翻译改变 | `execution/runs/abinitio.*`、`hints.*` |
| UTR | 显式启用UTR并输出特征；2段five_prime_utr、1段three_prime_utr | `followup/utr_explicit.*` |
| 区间、截取、反向互补 | HS04636:501–8953；回填后结构与链一致 | `execution/validation.json` |
| 独立结构检查 | Parent、序列边界、CDS phase、提取翻译；保留不完整末端状态 | `run_learning.py`、`execution/validation.json` |
| GenBank预测评估 | 官方hsackI10位点 | `execution/runs/genbank_evaluation.*` |
| 错误输入 | 不存在的species、end小于start均按预期返回1 | `execution/commands.json` |
| 物种模型训练 | 官方果蝇392训练位点、100测试位点；包含stop约定，训练stderr为空 | `followup/etraining_included.*`、`followup/validation.json` |
| 有限元参数优化 | 一个参数`/Constant/dss_end`、2折、1轮；重训并在原100位点评估 | `optimization/commands.json`、`optimization/validation.json` |
| BAM→hints | 官方小BAM生成6条intron hints，与上游预期逐字节一致 | `followup/actual.intron.gff`、`expected.intron.gff` |
| RNA局部预测 | 上述BAM中一条chr2R hint，转换到40kb窗口后实际预测 | `followup/rna_window.*`、`rna_local_prediction.*` |
| PSL→hints | 官方现成EST PSL用blat2hints转换；BLAT本体未执行 | `followup/est.hints.gff`、`source_review.json` |

`execution/commands.json`记录初始实验；**修正后的训练和UTR以`followup/validation.json`为准**。`optimization/`只覆盖一参数小试，不是默认全部元参数优化。`software_learning_ledger.tsv`为复用入口；命令中绝对路径是本次运行环境，不是可直接复制到任意机器的部署路径。

有限优化结果：原值4的内部交叉验证目标0.6550，候选2/3分别为0.6251/0.6545，因此保留4；重训后的100位点整基因Sn/精确率仍为0.47/0.301，没有提升。优化本次用时约357秒、峰值RSS约54MiB，只代表这个一参数官方例子。该值来自`/usr/bin/time`，Python封装层另记自身观测耗时，两者保留原值。

## 两个值得保留的失败例

1. 旧教程使用`stopCodonExcludedFromCDS=true`，而本版附带果蝇训练/测试CDS均已包含终止密码子。初始`etraining`虽然退出0，却在stderr报大量末端错误，整基因匹配为0。独立核查392个训练CDS和100个测试CDS的终止密码子后改为false，基础训练整基因Sn=0.47、预测精确率=0.301。预装fly在相同正确约定下为0.59/0.373。两者训练史和同源独立性未审计，不视为独立公平benchmark。
2. 初始UTR命令重复给`--UTR=off`、`--UTR=on`，本版前者生效。后续使用唯一的`--UTR=on --print_utr=on`才是正确UTR实验。生成命令应避免重复参数。源码`properties.cc`相关优先级已查。

构建时首次直接执行src目标，链接完成后因缺bin目录复制失败；创建bin并复制已链接程序后继续。辅助Python首先用严格GenBank解析器审计简化LOCUS头失败，改为提取LOCUS ID；原始输入未改。后续统计UTR时大小写断言失败，修正汇总即可，未重复生物命令。这些不算上游软件缺陷，原始日志保留。

## 复现

需要Linux/WSL、C++编译器、make、Perl、Python与Biopython，BAM转换另需BamTools（本批固定v2.5.3，commit `7e5c183cdf37a6ab216402b26c07296807416472`）。所有安装/配置在临时目录或本实验目录，未写全局模型。

```bash
git clone --depth 1 --branch v3.5.0 https://github.com/Gaius-Augustus/Augustus.git /tmp/augustus-reproduce
cd /tmp/augustus-reproduce
mkdir -p bin
make -C src -j4 augustus etraining COMPGENEPRED=false ZIPINPUT=false
```

在知识库根目录运行，输出使用新的空目录。`run_learning.py`保留初次错误约定的反例，`run_followup.py`运行修正和证据转换，`run_optimization.py`运行有限优化：

```bash
python3 tests/augustus_learning_2026-11-04/run_learning.py \
  --source /tmp/augustus-reproduce --output /tmp/augustus-reproduction/execution
# 先按provenance.json构建BamTools及bam2hints，再继续：
python3 tests/augustus_learning_2026-11-04/run_followup.py \
  /tmp/augustus-reproduce /tmp/augustus-reproduction
python3 tests/augustus_learning_2026-11-04/run_optimization.py \
  /tmp/augustus-reproduce /tmp/augustus-reproduction
```

训练使用独立可写config，保存优化前后模型，输入train/test保持不变。脚本拒绝覆盖既有运行；`run_followup.py --summarize-only`仅核对既有命令并重建汇总，修正UTR统计时使用此模式。

## 归档与局限

- `selected_official_sources.tar.gz`保存所查官方文件、许可和所用PSL；不是完整仓库。`source_review.json`记录逐文件哈希、阅读范围和论文阅读层级。
- `runtime_binaries.tar.gz`及`provenance.json`保存程序和身份；二进制可用性仍依赖兼容运行库，不宣称跨机器即用。`artifact_manifest.json`用于复核归档内容未变。
- 时间与峰值RSS来自每次`.time.tsv`（秒、KB），汇总见`runtime_summary.tsv`。小例规模不代表全基因组或任意笔记本的性能。
- 名字不交集只验证位点分区，不证明同源簇独立；预装fly模型训练史未溯源。测试输出的specificity列在此是精确率TP/(TP+FP)。
- 没有目标多毛类训练/盲测，没有完整默认优化、PPX/CGP/CRF、真实RNA处理全链、完整注释流程、TBtools/GSAman界面操作或生产验证。
