# Sanger Hi-C培训资料取回与选择性图文审阅

2026-11-02。承接[35指南](../35_EBP与Sanger_HiC挂载及人工校正指南.md)和[56坐标恢复](../56_HiC挂载校正流程深读补充.md)的PDF访问缺口。本轮**已经取得两份官方公开PDF，阅读全部抽取文本，并实际渲染查看12个关键页**；没有安装或打开PretextView、编辑培训图、运行TreeVal/curationpretext/pretext-to-asm，也没有完成逐图或视频培训。旧记录的下载失败不能继续作为本轮文件不可得的结论。

## 1. 来源、版本和实际阅读范围

原始入口是[Sanger curation-resources](https://github.com/sanger-tol/curation-resources)。下载发生于2026-11-02约14:01–14:02 UTC（22:01–22:02北京时间）；没有记录精确完成秒值。文件、抽取文本、README、API响应、关键页拼图和[机器账本](sanger_training/review_manifest.json)均保存在[sanger_training](sanger_training/)目录。

| 保存的官方文件 | 页数/大小 | 版本与阅读边界 |
|---|---|---|
| [PretextView-Tutorial.pdf](sanger_training/PretextView-Tutorial.pdf)，[官方raw](https://raw.githubusercontent.com/sanger-tol/curation-resources/main/PretextView-Tutorial.pdf) | 20页；5,035,563 bytes | 第2页明确为PretextView **0.2.5**编写；全部抽取文本已读，实际看图为PDF页12、16、18、20 |
| [Interpreting_HiC_Maps_guide.pdf](sanger_training/Interpreting_HiC_Maps_guide.pdf)，[官方raw](https://raw.githubusercontent.com/sanger-tol/curation-resources/main/Interpreting_HiC_Maps_guide.pdf) | 17页；2,104,384 bytes | 未找到明确软件版本/发布日期；全部抽取文本已读，实际看图为PDF页5、6、8、9、11、12、14、15 |
| [README.upstream.md](sanger_training/README.upstream.md)，[官方README](https://github.com/sanger-tol/curation-resources#suggested-workflow) | 8,176 bytes | 已读保存正文；将旧教程的回写路径与当前README所列路径区分 |

页码均按PDF从1开始的物理页计数。两PDF的creation/modification日期元数据为空，不能由下载日期推断教程是2026版。同期API取回的main提交为`d8763186ee0c5246520eb2643765b4705e449cc7`（提交日期2026-08-13）；随后又从该完整commit地址分别下载两PDF至`/tmp`，两次exit0且SHA256与保存的main版本逐一相同，故**两PDF已核对为该commit的对应内容**。README仅保存main版及其本地哈希，不冒称也完成逐文件commit验证。

| 文件 | SHA256 |
|---|---|
| PretextView-Tutorial.pdf | `c6c498b19b16fa2e954fb1e49ac486cb4df2a40bd860c4e1f7b75c1c8585da7f` |
| Interpreting_HiC_Maps_guide.pdf | `b73b045e7587716ba510a4edb98c6d7f8aa834b0d56dbbda35702795a0840904` |
| README.upstream.md | `63231be5807aa9cb6966f59ecbfd1def612542d7ad7c6a016995af6230fb98c6` |

## 2. 培训材料实际教的图谱判断

下表来自本轮实际渲染查看的图，不是只根据标题推断。拼图留存在[连接与重排](sanger_training/reviewed_figures/interpret_join_reorder.jpg)和[竞争解释](sanger_training/reviewed_figures/interpret_alternatives.jpg)。这些图例是人工提出候选事件的依据，没有给出可直接套用所有物种的定量阈值。

| Interpreting PDF页 | 实际图例与操作含义 | 在本项目必须保留的限制 |
|---|---|---|
| 5 | 四种角部高接触信号示范如何判断两个片段的连接端和方向；正确排列后强信号应接回主对角线 | 要比较两端及邻域；不能把任意较亮块直接当连接 |
| 6 | 两scaffold间有整体联系、却没有明显端部接触峰；教程认为可支持同染色体，但不足排序/定向 | 染色体归属与相邻连接是不同层次的决定；可保留Unloc |
| 8 | 原A/B/C排列在接点附近失去连续联系，旁侧有强信号；示意解为C+、B−、A+，恢复连续主对角线 | 这是具体教学图的解，不是所有类似纹理唯一解 |
| 9 | 三段顺序已对，中间段方向需反转；教程提示其他案例还会利用小片段辅助定位 | 要把“局部翻转”和“整体重排”分开记录 |
| 11 | 图中疑似hap重复同时有深度减半和gap附近转折 | 教程以单套代表组装为目标；本项目要交付两hap时，不能照图直接删除真实第二套hap |
| 12 | 串联重复区域深度升高、区域内部广泛接触、对外联系弱；许多小片段也与该区域相关 | 重复/多重比对能造成异常纹理，不应一律解释为倒位或错接 |
| 14 | 教材称“sister chromatids”间倒位；改变方向后仍会同时出现对角和离轴信号 | 仅作结构异质性教学案例，不据图确认细胞学机制；跨个体Hi-C尤其不能为了漂亮对角线抹去目标个体差异 |
| 15 | 无信号或低于背景的scaffold被列为候选污染；教程要求用BTK、BLAST等进一步确认 | “无Hi-C信号”本身不能自动删除序列，短片段/低可比对性也需排查 |

此外，文本第3页明确分辨率会隐藏大基因组中的错组装并限制小片段定向；第13页允许部分卫星重复保持未定位；第16页的性染色体半深度以异配性别样本为前提；第17页提到端粒/着丝粒之间也可有联系。后两项只完成文本阅读，未在本轮逐图检验，不能把跨染色体空间联系一律作为合并依据。

## 3. 从TreeVal准备证据到Pretext编辑，再回写序列

官方保存README把**TreeVal或curationpretext**列为curation分析数据的准备流程，并说明TreeVal可包含JBrowse2配套文件。本轮没有新增TreeVal完整参数/schema或运行证据；仍按35/56的边界理解其职责，不能说下载PDF就已验证该流程。

已核实的交接顺序如下；其中GUI按Tutorial 0.2.5说明，实施时应核对实际安装版本。关键页面见[编辑导出拼图](sanger_training/reviewed_figures/tutorial_edit_export.jpg)。

1. **固定原输入与证据。** 将与图一致的原FASTA、索引、Pretext图、覆盖/gap/重复等轨道绑定版本。Tutorial第9–10页文本说明bedGraph通过PretextGraph成为可显示轨道；它们是辅助证据，不会自动校正序列。
2. **用E编辑排列。** Tutorial第12页：选择、移动、反转、断开或连接图上的片段；中键/空格在选择前后含义不同。尤其`s`在E模式中是Snap开关，而在普通模式用于进入Scaffold Edit，快捷键必须连同模式记录。Snap限制把片段放入尚未切断的另一scaffold内部，不证明生物学连接正确。
3. **用M记录分类，再用S涂染色体。** Tutorial第14–16页与README一致：Haplotig、Unloc、性染色体及其他hap等标签会影响回写分类；Unloc应放在所属染色体端部并随染色体一起涂色。Tutorial第16–17页称未涂色序列作为singleton导出。不要为了得到预期染色体数给证据不足的小片段强行排序。
4. **保存状态、导出AGP，区分两者。** 第17–18页Generate AGP输出当前图中的排列描述，**不是直接得到完整精确FASTA**。第18页高亮说明坐标/长度受texel限制，小于一个texel的输入序列不一定导出。保存全部原FASTA可让后处理找回这些片段；若仅用图中AGP重拼可静默丢失它们。
5. **使用匹配版本的回写工具恢复原序列区间。** Interpreting第3页和Tutorial第14/16页仍引用历史`rapid_pretext2tpf`脚本；本轮保存README则明确用`agp-tpf-utils`的`pretext-to-asm`，输入**原FASTA和Pretext导出AGP**。不要把旧脚本名直接当当前生产命令。56已有源码阅读，不能因README承诺守恒便省略全部分类输出中的重复/遗漏核算。
6. **从校正FASTA重新制图并检查。** README要求产生新Pretext图复查；这句话没有单独规定或证明已重新比对reads。实施时分别登记“旧links坐标转换制图”和“reads对新FASTA重新mapping制图”，不能混为一个验证级别；真实跨个体结构争议还需要目标个体独立分子证据。

README给出的接口可整理为下列**未执行模板**，实施前仍须固定agp-tpf-utils commit并核验CLI：

```bash
pretext-to-asm --assembly original.fa --pretext edited.agp \
  --output curated.fa --no-clobber
```

Tutorial第19–20页还提示：保留原图副本，手动Save State补充自动状态保存；Load State要求先打开相应未编辑图，状态文件与图文件名绑定，且该旧教程明确说跨PretextView版本不保证兼容。正文说后缀`.savestate`，示例却写`.savestate_1`，因此必须保留实际导出文件/版本并现场验证，不能从教程示例臆造跨版本加载保证。状态文件、AGP、改动清单各自用途不同，都要归档。

## 4. 本轮证据及尚未完成

实际执行的是下载、`pdfinfo`、`pdftotext -layout`、PyMuPDF关键页渲染和`view_image`查看。Interpreting的文本抽取曾报两条`Badly formatted number`警告；所选页面成功渲染，不能据此把整份文档标为损坏，也不能保证所有图形都已检查。原始PDF是主要证据，TXT只作为检索辅助。

子agent默认代理curl一度exit7、直连重试exit6（[具体本轮日志](sanger_training/child_network_attempts.json)）；父agent在同轮用公开raw URL成功下载两PDFexit0。这里记录的是上下文不同的网络响应，不能延续旧的“本轮PDF未取得”状态。GitHub blob页面本身不等于取得PDF；本轮已用PDF页数、文件大小与哈希核对文件实体。

尚未完成：其余页面的逐图阅读、培训数据实际交互编辑与截图、导出/回写/重新制图实操、视频观看、TreeVal/curationpretext匹配版本test profile，以及真实样本结构验证。新增完整生物组装、GUI人工校正、生产验收数量均为0。本记录修补的是**公开培训PDF可得性与关键操作/图例阅读**缺口。
