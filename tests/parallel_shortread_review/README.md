# 短读分支并行学习证据

日期2026-11-02。见[55笔记](../../notes/55_短读与混合流程深读补充.md)。

`python3 tests/parallel_shortread_review/check_compound_failure.py`会在独立临时目录生成极小假FASTA，比较全部类别存在/缺失secondary两例的多段shell汇总行为，将时间、命令、退出码、stderr及输出hash写到`compound_failure_result.json`。临时数据随后清理。

这是自主编写的shell错误传播机制演示，未复制运行上游源码、未安装Platanus、没有生物测序数据，也不是对真实上游缺陷的运行复现。原始运行结果另保存在`compound_failure_result_original_20261102.json`，重跑不覆盖原记录。

本批阅读身份/范围及文件SHA256见`../../notes/sources/parallel_shortread_2026-11-02.json`。远程main的commit、完整源文件hash尚未取得，不能把笔记hash当上游源码hash。
