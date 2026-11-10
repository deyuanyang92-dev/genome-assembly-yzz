# 参考辅助、格式交接与Hi-C学习批次

日期：2026-11-02。本轮针对用户指出的漏项修订，所有产物保存在本地仓库，没有提交或推送。本文是批次入口，不替代[全历史任务审计](full_request_gap_audit_2026-11-02.md)。

## 本轮可查阅交付

| 问题 | 本地产物 | 证据范围 |
|---|---|---|
| 只有二代但有参考，能走哪些路线 | [59参考辅助方法体系](../59_参考辅助组装方法体系与工具选择.md)；[综述章节审查](reference_assembly_reviews_2026-11-02.md)；[早期引导与再组装审查](guided_assembly_audit_2026-11-02.md) | 方法、选定综述章节及官方接口；本批未运行这些参考工具 |
| SAM/原生HiFi BAM转FASTQ，hifiasm GFA转FASTA | [60格式交接](../60_组装格式转换与数据交接.md)；[合成实测](../../tests/format_conversion_2026-11-02/README.md) | samtools1.21七项检查；固定gfatools图段导出两项检查及noseq失败观察；pbtk仅文档核查 |
| 挂载器选择、Juicer等角色与HapHiC算法 | [61挂载选型](../61_HiC挂载选型与HapHiC机制.md)；[10种挂载器比较](hic_scaffolder_comparison_2026-11-02.md)；[HapHiC机制](haphic_mechanism_review_2026-11-02.md) | 文档、局部源码、维护状态；本批新增挂载运行0 |
| HapHiC论文怎样做实验、参数、评分 | [补充方法与命令复核](haphic_supplement_methods_review_2026-11-02.md)；[下载来源/哈希](haphic_2024/provenance.json) | 官方113页PDF已保存，实际审查选定方法与命令；未读全部图表，未复现实验 |
| Sanger人工校正培训 | [本轮图文审查](sanger_curation_training_review_2026-11-02.md)；原材料在sanger_training目录 | 两份官方PDF文本及12个选定图文页；未运行GUI或真实校正 |
| 微信视频是否已经学到 | [本次访问证据](wechat_revisit_2026-11-02.json)与[09说明](../09_视频与Skills学习.md) | 再访问仍为验证页；媒体、音轨、字幕均未取得 |

## 模型分工与检查

用户要求选择适合模型后，GPT-6 Astra独立核查HapHiC选定方法和命令；GPT-6.1 Terra修订旧笔记和目录检查；GPT-6.1 Sol补读Sanger培训；主agent实际执行转换、取得官方材料并整合。模型名称不替代来源或实测证据。

目录当前62篇编号笔记、32个专题、61行软件分层覆盖记录。新增samtools、gfatools、pbtk的版本/范围记录；29条自动诊断仍是设计记录，没有因为本轮出现失败例而宣称实现了诊断器。

`python3 scripts/knowledge_base.py check`检查目录、链接、指定来源哈希及元数据；它不检验生物学结论。参考辅助、Hi-C与格式转换的关键词已接入本地检索，以后先读取本地记录，变化的版本或证据缺口再定向核验。

全历史任务仍不能标为全部完成：未取得视频；bioSkills尚非全正文通读；多套完整流程未全部复现；真实目标数据及异个体Hi-C、去冗余、完整注释等生产验证未做。未来开发需求已有记录，不能写成程序已实现。
