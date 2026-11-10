# RagTag参考挂载组件实测

日期：2026-11-03。证据：固定上游版本的三个人工数据挂载组件执行；没有真实样本、原始reads组装或Hi-C实测。本目录补上此前参考挂载候选只有文档记录的缺口。

源码：官方[v2.1.0](https://github.com/malonge/RagTag/tree/e993fb2787346345662c240967a3ec80bb2aac64)，完整commit `e993fb2787346345662c240967a3ec80bb2aac64`，源码归档保存在本目录。只调整临时源码的Python脚本执行权限，内容未修改。没有使用PyPI同名包，因此此前PyPI2.1.1与上游身份未解决的问题不影响本次固定Git构建，但该问题本身仍未解决。官方[scaffold说明](https://github.com/malonge/RagTag/wiki/scaffold)于本日复核。

复用已有minimap2 `2.31-r1302`（源码commit `3c28777e7e2dcc90f825de1b9f17a89cca7d4452`，运行时二进制哈希见provenance.json），以及Colora测试环境Python3.14.10 / pysam0.24.1。scaffold实际调用链不需导入intervaltree/networkx；未声称安装并验证完整RagTag所有子命令。先前另建Python3.13环境pip联网安装依赖失败，随后使用已有环境执行；失败不代表RagTag不兼容。

输入由固定随机种子20261103生成：A、B、C、novel四段各20kb，query次序C、A、反向B、novel。人工目标真值为A→B→C，novel独立；参考在各块间含目标没有的2000/3000bp片段。真值独立保存在inputs/target_truth.fa；本实验只验证块级布局，未模拟reads、重复、杂合或误差。

| 分支 | 实际块布局（相对于A/B/C原块） | gap | 非N量／总量 |
|---|---|---|---|
| forward默认 | A→B→C | 100、100 N | 80000／80200bp |
| inferred_gaps，`-r` | A→B→C | 2000、3000 N | 80000／85000bp |
| reference_bias，更换为重排参考 | A→反向C→B | 100、100 N | 80000／80200bp |

每个分支均独立解析AGP，检查对象坐标连续、part编号、完整组件区间、每个query恰好使用一次、未定位novel保留，并从query按AGP重建FASTA，与上游结果逐碱基一致。默认gap与推断gap分别检查；没有使用上游自身agp2fa作为独立验证器。

观察：改变参考使布局改变并违背人工目标真值；全组件保留和非N量不变仍不能证明结构正确。`-r`得到参考距离大小的N，不是恢复目标gap实际序列，也没有复制参考特有碱基。这是设计输入下的明确观察，不是实际物种的误拼率估计或软件性能排名。

命令、退出状态、版本、输入/运行产物哈希和判断见[results.json](results.json)。源码归档、实际执行文件及环境补充哈希见[provenance.json](provenance.json)。原始stdout/stderr在各分支.log及分支目录。

复现（将路径替换为对应本机安装位置；三个结果目录已存在时脚本拒绝覆盖，先复制脚本到新的空目录运行）：

```bash
python3 run_examples.py \
  --ragtag /tmp/yzz-ragtag-20261103 \
  --minimap2 /tmp/yzz-learning-minimap2/minimap2 \
  --python /tmp/yzz-learning-colora-envs/bed4089c7b03833ad636547f76d08913_/bin/python
```

仅scaffold三次；correct、patch、merge、真实二代初装到参考挂载全流程和目标个体生物学验收均未执行。此前26上游仓库/1套Colora功能配置等历史批次计数不因此改写；本批新增固定RagTag clone及源码归档，不增加完整流程复现数。
