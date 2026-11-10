# 用户授权的多agent学习批次：2026-11-02

3个学习agent并行，主agent负责第四分支、交叉检查和统一索引。本批是定向深读与轻量验证，不是整套知识库学习完毕。

| 分工 | 新增内容 | 本地交付 |
|---|---|---|
| shortread_deep | Platanus阶段/异常/产品源码，2019论文方法与分相评价语义 | [55](../../notes/55_短读与混合流程深读补充.md) |
| hic_deep | YaHS编辑后坐标恢复；Pretext/3D-DNA后处理源码与跨个体评估设计 | [56](../../notes/56_HiC挂载校正流程深读补充.md) |
| standards_deep | EBP措辞、HGSVC3方法和复现入口、固定版HMM-Flagger WDL接口 | [57](../../notes/57_质量标准与证据验收深读补充.md) |
| root | RAGNAROK输入互斥、StringTie混合合同、DNA/RNA比对语义及统一核查 | [58](../../notes/58_自动注释输入路由与剪接比对核查.md) |

## 实际执行与边界

- YaHS juicer post：4次人工输入转换。切分/翻转/重排结果与真值一致；FAI分支只产AGP；构造8 bp重复或遗漏能被独立区间审计发现。
- Minimap2 2.31-r1302：2次无错误人工RNA比对；splice:hq识别2000N，map-hifi得到2000D，均退出0。
- 独立shell机制：1个实验、2条件，说明前命令失败可被后命令成功掩盖；不是Platanus上游故障复现。
- 验收状态示例：1脚本、16个合成场景，检查阈值/未知/过期证据等语义；不是生产质量判定器。

新增真实生物组装、完整流程执行、上游clone与目标物种生产验收均为0。没有GUI操作、微信视频内容获取或完整论文补充材料复现。远端main没有完整commit时已标未固定；发布说明、源码风险与已复现行为分别记载。

## 复核与复用

`manifest.json`列出四分支来源账本、笔记、命令/日志/产物等49个文件的SHA256。执行`python3 tests/multi_agent_learning_2026-11-02/verify_batch.py`只检查已保存证据，不重跑组装。全库目录检查：`python3 scripts/knowledge_base.py check`。

可开发检查整理为[findings.tsv](findings.tsv)，全部仍是设计待办，没有添加自动修复功能。全库诊断JSON保持29条，不能把本表条目混作已实现诊断数量。已有上游26仓库和bioSkills25篇正文计数不变。

新增4篇已接入catalog、README和AI_CONTEXT；之后按问题优先读取本地笔记。新版本、新数据类型或缺失证据再定向查官方资料。
