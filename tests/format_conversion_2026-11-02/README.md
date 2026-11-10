# 格式交接实测（2026-11-02）

本批仅是合成SAM/BAM的samtools1.21接口实测，不是真实HiFi样本，不运行CCS或hifiasm，不验证生物学准确度。

执行 `python3 tests/format_conversion_2026-11-02/verify_conversion.py`，实际二进制路径、命令、stderr、输入输出SHA256及7项检查见results.json。

验证：单端类别0未丢失，附加比对不重复导出；反向记录导出恢复原方向及质量顺序；rq/np标签按请求进入头注释；hard-clipped碱基不能恢复；缺失QUAL仍输出占位质量；SAM stdout与BAM压缩文件解压内容一致。

重要观察：最初按在线手册默认-v1推测缺失质量输出为ASCII34，实测此构建输出`BBBBB`（Phred33），最初失败记录保存在initial_observation.json。另试显式-v1/-v2/-v10，该例仍输出BBBBB。当前只记录这个构建/人工输入的现象，未确认根因或上游bug，不推广所有版本。最终检查将该结果明确标为观察到的占位质量，**没有把它解释成真实测量或修复了原数据**。因此实际流程应在导出前检查缺QUAL并拒绝将占位值用于HiFi质量判断。

合成read名字不代表真实PacBio分子；SAM头SO属性也不能替代真实记录排序检查。首次下载的未完成PDF不属于本实验数据。

## GFA导出接口实验

另外从上游克隆并编译gfatools提交`39c54d5dfe4678d4cfb75b37bd27d4fb21f4de72`，执行`verify_gfatools.py`。源码归档在`gfatools/source_39c54d5.tar.gz`，完整命令、输出、返回码、源码与二进制哈希见`gfatools/results.json`。归档解压后可用`make`重建；脚本中的SOURCE路径需要指向该构建目录。

- 含2个S、1条L、1条P路径的人工GFA导出2条原S序列；没有导出P路径拼接序列。2项内容断言通过。
- `S empty * LN:i:6`的单段无序列GFA在本构建执行gfa2fa返回`-11`（SIGSEGV），stdout/stderr为空。该例不属于成功转换。源码`main.c`的普通导出分支直接将`s->seq`传给`print_seq`，后者调用`strlen`而未在这里检查无序列；这是局部静态线索，没有用调试器确认栈或验证其他版本。
- 上游源码内版本字符串本身含`dirty`：`gfa.h: 0.5-r292-dirty`、`gfatools: 0.5-r296-dirty`。构建后`git status --short`只显示未跟踪二进制`gfatools`，不能据字符串推断本次修改了受跟踪源码。

因此生产转换必须前检S行有实际序列，失败保留原GFA和日志；不能因工具退出失败而改用awk输出`*`伪装成功。本实验不验证真实hifiasm组装、rGFA stable sequence导出或图路径重建。
