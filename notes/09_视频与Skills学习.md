# 视频访问证据与 Skills 学习

记录日期：2026-11-01。原始链接：https://mp.weixin.qq.com/s/QGKqelwis4CpgCpC5Ldekg?scene=1 。

2026-11-02再次通过curl访问，传输成功但取得18,172字节的“环境异常，完成验证后即可继续访问”页面，仍未取得音视频或字幕。新访问记录见[本轮证据](sources/wechat_revisit_2026-11-02.json)。这次失败不能归因为整个终端网络不可用：同轮官方GitHub PDF和Springer补充材料已下载成功；受阻的是该微信入口及其访问条件。

## 实际取得的内容

通过 Windows PowerShell `Invoke-WebRequest -OutFile` 取得实际公众号页面；Linux 请求此前只取得验证页。页面提供标题“使用Hi-C Skills进行拟南芥染色体构建”，视频号导入标记、1920×1080、771 秒（12 分 51 秒），视频标识 `wxv_4677590747829714948`。已下载并查看封面图片。封面上的覆盖率/挂载率是示意图中的文字，未取得实验定义，不能作为实验结果引用。

随后使用独立临时配置的 Windows Chrome headless 加载页面、保存渲染后 DOM。页面实际提示“请在微信客户端打开”，没有得到可下载的 video src。网页的 `__mpVideoTransInfo` 为空。检查页面加载的官方 `common_share_video` JavaScript：视频号路径通过微信 JSAPI `handleVideoAction/getFinderPlayInfo`，或带上下文的 Finder 播放组件取得媒体信息；组件会检查微信环境。此证据解释了为什么取得文章 HTML 仍不能等同于取得视频。

**当前尚未获得音视频，也没有逐帧观看、转写或核实视频演示命令。** 不推断视频用了哪一个 GitHub skills 仓库，不编造时间轴。原始 HTML、DOM 与封面保存在 `sources/wechat/`（本地保留、忽略提交）；仅作访问取证，其中可能含短期播放参数。

## GitHub 视频工具的适用边界

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)：已下载源码并尝试对此链接提取；本次请求失败，且源码中未找到针对该公众号视频号嵌入页的专用提取器。不能把支持普通腾讯视频等同于支持此链接。
- [wechat-video-subtitle](https://github.com/jianminggan/wechat-video-subtitle)、[WechatVideoDL](https://github.com/topgptus/WechatVideoDL)：阅读项目介绍，相关路径依赖视频号分享链接、浏览器及腾讯元宝登录等前提。本次没有可用的登录会话或本地媒体，没有完成下载/转写；未将这些项目直接安装为可信生产依赖。
- ASR/字幕工具可以处理已取得的音视频，但下载、微信内播放会话、语音识别是三个不同问题。下一步有效输入是视频原文件，或能在当前环境解析的原始视频分享链接；若由用户提供文件，可转写并结合关键帧核对代码、参数和结果，之后再补时间轴。

## 独立补充学习：如何将 Hi-C 工作流写成 skills

已阅读 [GPTomics/bioSkills 的 scaffolding SKILL.md](https://github.com/GPTomics/bioSkills/blob/main/genome-assembly/scaffolding/SKILL.md)，并与本地 YaHS/HapHiC 官方源码交叉核对。这是补充来源，**未确认它就是视频采用的 skill**。本次未安装外部 skill；外部说明中的命令需要经过版本和数据条件核实后才可执行。

Skill 是可重复使用的任务说明和检查约定；真正计算仍由组装器、比对工具和脚本完成。有效的 Hi-C skill 应包含：

1. 输入契约：样本对应关系、FASTA/Hi-C 文件、建库酶、倍性、染色体数的证据、primary 或 phased 输出目标。
2. 运行前检查：完整 FASTQ 配对、FASTA 标识唯一、BAM 的参考序列字典匹配当前 FASTA；明确 queryname/coordinate 排序要求，避免把旧组装的 BAM 用于新组装。
3. 命令与版本：源码 SHA/容器 digest、CPU/内存、完整参数、日志路径和退出码；未知染色体数不能由代理随意猜。
4. 阶段产物：原始 contig、过滤后的 links、AGP、scaffold FASTA、contact map、人工修改记录；阶段之间用显式路径交接。
5. 验收：AGP 坐标和方向、序列保留、结构异常、k-mer 完整性/QV、BUSCO、污染、分相一致性；不能只看 N50 或图片颜色。
6. 异常分支：低有效接触、重复序列、多倍体等位误连、异常断裂、自动分组与核型不符，均应有可解释的诊断与重跑条件。

可采用“先检查数据 → 选择模型与工具 → 生成可审阅命令 → 小样本验证 → 正式运行 → 结构质控和人工校正”的顺序。拟南芥示例能演示操作，但不能自动决定环节动物的倍性、杂合度、酶切模式或染色体数。后续实际运行需要样本数据与核型信息；本次任务只做源码学习和公开示例验证。
