# Hi-C校正接口实测，2026-11-02

本目录保存4次YaHS `juicer post`实际调用，不是Hi-C挂载或GUI操作。固定源码commit `6c46061ea1665073068cccbed81c6707e3bd07bf`，运行输出1.2.2。

`inputs/`中人工A/B/C合计48 bp。A在8处分开，重排为反向A后段→B→A前段，C独立反向。指定每个连接100 N，人工期望两条长度236和12；逐碱基通过。FAI分支只写AGP；重复/遗漏8 bp案例均退出0，但独立源区间核算检测出变化。

- 构造及实际调用：`scripts/edited_roundtrip.py`。
- 原始命令、时间、退出码、输入/输出/日志SHA256与核查：`execution_manifest.json`。
- 脚本拒绝覆盖既有输出；要重新执行请修改到新的独立运行目录，不能清空旧证据掩盖变化。
- 只验证格式与坐标/序列转换，未运行Juicer比对、JuicerTools、PretextView、3D-DNA或真实样本校正。人工输入不具有Hi-C接触信息。

源码选读、版本身份与网络限制见`../../notes/sources/parallel_hic_2026-11-02.json`；解释见`../../notes/56_HiC挂载校正流程深读补充.md`。
