# RAGNAROK：实际RNA与整合模块核查

本轮新增下载源码到 `/tmp/yzz-learning-ragnarok`，固定提交及文件哈希见 `../ragnarok_source_review.json`。这是静态核查，未运行该注释流程，不计作注释成功。接续原学习库43的未完成项，补读main.nf的245–410行、stringtie、minimap2、miniprot及mikado2模块和配置相关参数。

## 输入分支与模块事实

1. main.nf将短RNA送入STAR，PacBio与ONT RNA分别送入不同的minimap2模块。PacBio模块为 `-ax splice:hq -uf`，ONT模块为 `-ax splice -uf -k14`。这些是转录本比对参数，不能用于基因组DNA回贴。
2. STRINGTIE_MIX使用 `--mix`，先短RNA BAM、后长RNA BAM；与官方StringTie手册要求的顺序一致。但正确顺序不等于对应数据已经验证，仍需审核排序、链方向和参考版本。
3. 单独长RNA分支调用通用STRINGTIE，与短RNA共享同一命令，源码未传 `-L`。官方手册把 `-L` 定义为长读段模式，并会更改单外显子覆盖和locus间隔参数。故该分支存在需要原生示例核验的模式配置风险；尚无实测证明其输出精度受损，不能把静态发现升级为准确率结论。
4. MINIPROT进行蛋白到基因组比对、输出GFF。其额外gff3输入仅用于index basename和依赖关系，不能把这一模块说成独立从头基因预测器。
5. Mikado配置接收模型清单、FASTA、评分和同源蛋白；prepare后以ORF和同源比对serialise，再pick模型。它是带评分/证据的选择，不是各预测器多数表决，多个共用RNA或AUGUSTUS的结果不能算独立票。
6. 配置的Helixer默认模型URL为land_plant，max_intron为10,000，skip_qc/skip_trim为true。这些默认值不能直接作为环节动物设置。STRINGTIE模块默认24CPU/150GB，超过当前机器可用于此任务的资源，需要本地profile覆盖；不能把仅下载源码当作可直接运行。

## 对后续实现的要求

以RNA平台和输入处理状态驱动原生命令；单长读与短长混合分别验收，核对StringTie版本。对默认植物模型和缺少适用动物模型的情形显式报错或要求选择，避免无声运行。资源参数通过profile配置，不修改现有上游副本。模型集要保留来源、所用证据及FASTA哈希，整合前检查坐标、ID和重复。

下一步应固定容器版本，取得小型RNA/参考注释例子，对照预期junction与转录本结构，验证单长读和混合分支，再决定是否作为多毛类后端。本轮未实施这些生物测试。

依据：[作者源码](https://github.com/ryandkuster/ragnarok)、[StringTie官方手册](https://ccb.jhu.edu/software/stringtie/index.shtml?t=manual)。上述风险是本轮依据源码与手册作出的判断，非作者报告的性能结论。
