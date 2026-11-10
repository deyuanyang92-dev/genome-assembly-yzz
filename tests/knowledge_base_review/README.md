# 知识库结构核查（2026-11-02）

运行：`python3 scripts/knowledge_base.py check --output tests/knowledge_base_review/validation.json`。

核查专题和编号笔记、50–52新增笔记的本地链接、源码快照SHA256、软件/判断卡来源、诊断设计记录、引用的Colora退出状态。结果见validation.json；这不重新验证Colora全部产物，也不做生物学分析或证明知识结论正确。

检索冒烟核对：`BUSCO 缺失`的首项为KB19基因完整度；`二代 染色体`的首项为KB11参考辅助，次项KB03二代组装。检索分数仅为词匹配相关度，不是科学可信度。

本批新增生物分析运行0次，未提交或推送。
