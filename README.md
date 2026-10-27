# 全基因组组装流程学习库

> 位置：`/media/deyuan/18T_B/genome_assembly` · 建于 2026-10-26
> 用途：收集、学习、测试经典的全基因组 de novo 组装流程，为环节动物（Annelida）组装做准备。

## 1. 目录结构

```
genome_assembly/
├── README.md                          ← 本文件：总览、对比、学习路线、测试状态
├── pipelines/                         ← 各流程源码（固定版本，供阅读学习；不进 git，用 fetch_pipelines.sh 拉取）
│   ├── fetch_pipelines.sh             ← 按固定 commit 一键拉取下面 8 个仓库
│   ├── sanger-tol_genomeassembly/     1.0.1  (131f0ea)
│   ├── VGP_galaxy_iwc/                main@d9ec763（只检出 workflows/VGP-assembly-v2）
│   ├── nf-core_genomeassembler/       2.0.1  (c608622)
│   ├── cnag_CLAWS/                    v3.2   (b7af156)
│   ├── ebp-nor_GenomeAssembly/        main@d31bbee（仓库没有 tag）
│   ├── marbl_verkko/                  v2.3.2 (39e9fb2)
│   ├── aidenlab_juicer/               1.6    (f866383)；注意 main 分支已经是 Juicer 2
│   └── aidenlab_3d-dna/               201008 (cb63403)；注意 master 分支反而是更旧的 180922
├── notes/                             ← 中文学习笔记（每篇都有"本笔记依据"，标明读过哪些文件）
│   ├── 01_sanger-tol_genomeassembly.md   ★ 本机已测试
│   ├── 02_VGP_Galaxy.md
│   ├── 03_nf-core_genomeassembler.md
│   ├── 04_CNAG_CLAWS.md
│   ├── 05_EBP-Nor_GenomeAssembly.md
│   ├── 06_Verkko.md
│   ├── 07_Juicer_3D-DNA.md
│   └── 08_核心工具速查.md               ← 建议先读这篇
├── tests/
│   └── sanger-tol_genomeassembly_test/  ← run_test.sh、fetch_test_data.sh、compare_with_snapshot.py
│                                           results/（本机测试结果）、results_official_busco/（用官方 BUSCO 库复核）
├── containers/
│   ├── singularity/                   ← Singularity 镜像缓存（NXF_SINGULARITY_CACHEDIR），各流程共用
│   └── prefetch_singularity_images.sh ← 带续传和重试的镜像预下载脚本
└── databases/
    └── busco_downloads/lineages/eukaryota_odb12   ← 离线 BUSCO 谱系库
```

## 2. 本机运行环境

| 项目 | 情况 |
|---|---|
| 硬件 | 72 核 / 503 GB 内存；18T_B 盘可用 13 T |
| Nextflow | 用 conda 环境 **`nextflow`**（Nextflow 25.10.4 + OpenJDK 21）。系统自带的 `/usr/local/bin/nextflow` 是 19.10，配 Java 11，太旧，没有改动它 |
| 容器 | Singularity CE 4.3.1（推荐）；也有 Docker 29.1.3 |
| 网络 | 通过代理 `127.0.0.1:7890` 上网，**偶尔会断连**，见 §6 |

```bash
source /home/deyuan/miniforge3/etc/profile.d/conda.sh && conda activate nextflow
export NXF_SINGULARITY_CACHEDIR=/media/deyuan/18T_B/genome_assembly/containers/singularity
export NXF_OPTS='-Xms1g -Xmx4g'
```

## 3. 流程总览对比

| 流程 | 框架 | 主要输入 | 组装器 | 分型 | 去冗余 | 挂载 | 去污染 | 细胞器 | 人工校正材料 | 在本机好不好跑 |
|---|---|---|---|---|---|---|---|---|---|---|
| **sanger-tol/genomeassembly** 1.0.1 | Nextflow | HiFi/ONT + Hi-C（CRAM）± trio、UL、10X | hifiasm | pri/alt、Hi-C、trio | purge_dups（可选） | YaHS | ✗（另用 ascc、blobtoolkit） | MitoHiFi、oatk | Pretext、`.hic`、`.mcool` | ★★★ 已容器化，**本机已测试** |
| **VGP**（Galaxy IWC） | Galaxy | HiFi ± Hi-C、trio、Bionano | hifiasm | pri/alt、Hi-C、trio | purge_dups（VGP6/6b） | YaHS（VGP8）；Bionano（VGP7） | ✓ FCS（VGP9） | MitoHiFi（VGP0） | ✓ 带轨道的 PretextMap + 校正后处理 | ★★ 公共 Galaxy 网页直接用；本地部署很重 |
| **nf-core/genomeassembler** 2.0.1 | Nextflow | ONT/HiFi ± Hi-C、短读长、参考基因组 | hifiasm、Flye（可用 RagTag patch 合并） | ✗（只适合单倍体或近交系） | ✗ | YaHS（要设 `scaffold_hic: true`）、LINKS、LongStitch、RagTag | ✗ | ✗ | ✗ | ★★★ 已容器化 |
| **CNAG CLAWS** v3.2 | Snakemake 6/7 | ONT/HiFi + Illumina、10X、Hi-C | Flye 和 hifiasm 并行（± NextDenovo） | Hi-C（hifiasm） | purge_dups | YaHS（chromap 比对） | ✗（可选 Kraken2） | ✗ | ✓ Pretext + 轨道 + TPF | ★ 强依赖 CNAG 集群环境 |
| **EBP-Nor** GenomeAssembly | Snakemake 7 | HiFi/ONT ± Hi-C | hifiasm | Hi-C（要设 `haploid: False`） | ✗ | YaHS（先按单倍型 k-mer 过滤 Hi-C） | ✓ FCS-adaptor + FCS-GX | oatk | ✓ rapid-curation 轨道 | ★ Sigma2 集群路径写死；要手动装好几个软件 |
| **Verkko** v2.3.2 | Snakemake 7（sh 启动脚本） | HiFi（必须）+ ONT UL（强烈推荐）± Hi-C、Pore-C、trio | 自带：MBG 图 + GraphAligner + Canu utgcns 共识 | trio、Hi-C、Pore-C（统一用 rukki），**不输出 pri/alt** | 不需要 | 内置（Hi-C/Pore-C 模式） | `--screen` 移出 mito、rDNA 等 | 移出 mito 并尝试环化 | 不生成 `.hic`；可手工编辑图路径后用 `--paths` 重跑共识 | ★★ conda 可装；必须用 Snakemake 7；资源需求大 |
| **Juicer 1.6 + 3D-DNA** 201008 | Bash/awk/Java | 已有的草图 contig + Hi-C FASTQ | **不做组装**，只做挂载 | 主流程不分型 | 仅 diploid 模式有 merge | 3D-DNA（迭代纠错 + debris 切除） | ✗ | ✗ | ✓ `.hic` + `.assembly` → JBAT 人工校正 | ★★ 不用安装；3D-DNA 的 Java 固定占 48 GB；一定要用 tag 版本 |

### 横向对比：同一步骤，各流程怎么做

| 环节 | sanger-tol | VGP | nf-core | CLAWS | EBP-Nor |
|---|---|---|---|---|---|
| k-mer 与基因组调查 | FastK + GenomeScope2 | Meryl + GenomeScope2 | jellyfish + GenomeScope **1.0** 脚本 | meryl + GenomeScope2 + Smudgeplot | FastK + GenomeScope2（ploidy 1/2/4）+ Smudgeplot |
| purge_dups 阈值 | `-m 1.5c -u 6c`（c = 1n 覆盖度） | transition = 1.5×kcov，upper = 4.5×kcov | 无 | calcuts 自动 | 无 |
| Hi-C 比对 | bwa-mem2 或 minimap2，CRAM 分块并行，samtools markdup | bwa-mem2 `-5SP`，markdup **删除重复**，MAPQ ≥ 10 | bwa-mem2 `-5SP`，Picard **只标记**重复，**不按 MAPQ 过滤** | chromap，去 PCR 重复，mq0 和 mq10 两套 | bwa `-5SPM`，samtools markdup |
| QC | asmstats、gfastats、BUSCO、MerquryFK | gfastats、Compleasm、Merqury | QUAST、BUSCO、Merqury | gfastats、BUSCO、Merqury、tidk，汇总成一张表 | BUSCO、gfastats |

> 这张表就是最好的学习材料：同样是"HiFi + Hi-C → 染色体级"，各团队在阈值、去重、MAPQ 过滤上的取舍都不一样。每一格的出处见对应笔记。

## 4. 怎么选（结合环节动物）

| 你的情况 | 建议 |
|---|---|
| HiFi + Hi-C（主流的参考基因组方案） | 主力用 **sanger-tol/genomeassembly**（本机已能跑）。参照 **VGP** 的设计补上去污染（FCS-GX）和人工校正步骤 |
| 只有 ONT（± Hi-C） | **nf-core/genomeassembler**（Flye 或 `hifiasm --ont`）。它不做去冗余，要自己补 purge_dups；挂载记得设 `scaffold_hic: true` |
| 目标是 T2T | **Verkko**（见笔记 06） |
| Hi-C 挂载后人工校正 | PretextView（ToL、VGP 的做法），或 Juicer + 3D-DNA + Juicebox（DNA Zoo 的做法，见笔记 07） |
| 只有 Illumina 短读长 | 现成流程都不适合；做系统发育可以用短读长组装器拿 BUSCO 基因（见笔记 08 §0） |

**环节动物的几个参数（已核实）**：
- **BUSCO 谱系**：odb12 里没有单独的 Annelida 谱系，最接近的是 **`lophotrochozoa_odb12`**。odb10 只能用 `metazoa_odb10`（EBP-Nor 的代码写死了 `_odb10` 后缀；VGP 用的 Compleasm 是 odb10 库）。
- **线粒体遗传密码**：**表 5（Invertebrate Mitochondrial）**，NCBI Taxonomy 中 Annelida 的 taxid 是 6340。
- **端粒序列**：VGP、EBP-Nor 默认是 `TTAGGG`。环节动物是否也是这个序列**尚未核实**，建议先用 `tidk explore` 在自己的数据上确认。

## 5. 学习路线（建议顺序）

1. **`notes/08_核心工具速查.md`**：先弄清每一步解决什么问题、有哪些工具可选。
2. **`notes/01_sanger-tol_genomeassembly.md`**：对照本机测试结果（`tests/sanger-tol_genomeassembly_test/results/`），一个目录一个目录地看输出。
3. **`notes/02_VGP_Galaxy.md`**：同样的 HiFi + Hi-C 思路，用 Galaxy 实现，并补上了去污染和人工校正。重点对比 purge_dups 阈值和 Hi-C 去重方式的差别。
4. **`notes/03_nf-core_genomeassembler.md`**：ONT 路线，以及"一次运行比较多种策略"的设计。
5. **`notes/04、05`**：欧洲两个生产流程（Snakemake），看实际生产中怎么组织配置、去污染和校正前的准备。
6. **`notes/06_Verkko.md`**：T2T 组装。
7. **`notes/07_Juicer_3D-DNA.md`**：经典的 Hi-C 挂载和人工校正。

## 6. 测试状态与本机已知问题

| 流程 | 测试内容 | 状态 |
|---|---|---|
| sanger-tol/genomeassembly 1.0.1 | 官方 test profile（二星瓢虫 icAdaBipu1：pri/alt + Hi-C phased + oatk） | ✅ **通过**。与官方 nf-test 快照逐个比对：输出路径 526/526、md5 111/111、任务数 170、48 个进程的软件版本零差异（用官方同版本的 BUSCO 谱系库时）。详情和结果解读见笔记 01 §10 |
| 其余流程 | 只读学习，未运行 | — |

**本机已知问题与解决办法**：
1. **代理链路偶尔断连**（实测：Java 发起的 HTTPS 请求约 9% 遇到 `SSLHandshakeException`，curl 下载有时出现 `unexpected EOF`）。Nextflow 在这两处不会重试：
   - 校验远程输入文件时，会误报 "does not exist" → 先把输入下载到本地（`tests/.../fetch_test_data.sh`）。
   - 拉取 Singularity 镜像时，断一次整个流程就失败 → 先预下载镜像（`containers/prefetch_singularity_images.sh`，镜像列表用 `nextflow inspect` 生成）。
   - BUSCO 运行时自己下载谱系库 → 改用离线谱系库（`--busco_lineage_directory`）。
   - 根本的解决办法是改善代理的稳定性，这需要你来处理。
2. **sanger-tol 1.0.1 的 bug**：单独写 `assembler: mitohifi` 的方案会被静默跳过，见笔记 01 §7。dev 分支已修复。

## 7. 下一步

- 准备好自己的数据（HiFi/ONT/Hi-C）后，可以照笔记 01 §4.3 的模板写 `genomic_data.yaml` 和 `assembly_specs.yaml`。Hi-C 要先转成未比对的 CRAM。
- 如果想实际跑其他流程：nf-core/genomeassembler 有现成的 `-profile test`；VGP 可以直接在 usegalaxy.eu 上运行。

## 8. 关于这个 Git 仓库

本目录同步到 https://github.com/deyuanyang92-dev/genome-assembly-yzz （**公开仓库**）。

- **入库的**：笔记、README、各个脚本、测试配置，都是文本。
- **不入库的**：大文件、第三方源码、可以重新生成的内容，具体见 `.gitignore`。

换一台机器（或删掉本地数据后）按下面步骤还原：

```bash
git clone https://github.com/deyuanyang92-dev/genome-assembly-yzz.git genome_assembly && cd genome_assembly
bash pipelines/fetch_pipelines.sh            # 8 个流程源码，按固定 commit 拉取（已验证与本机版本逐文件一致）

# 复现 sanger-tol 测试（环境见 §2）：
bash tests/sanger-tol_genomeassembly_test/fetch_test_data.sh
bash containers/prefetch_singularity_images.sh tests/sanger-tol_genomeassembly_test/images.txt
mkdir -p databases/busco_downloads/lineages && (cd databases/busco_downloads/lineages \
  && curl -fLO --retry 10 --retry-all-errors https://busco-data.s3.amazonaws.com/lineages/eukaryota_odb12.2026-05-22.tar.gz \
  && echo "08fb6d94a1699643c257653b77e05af5  eukaryota_odb12.2026-05-22.tar.gz" | md5sum -c - \
  && tar -xzf eukaryota_odb12.2026-05-22.tar.gz && rm eukaryota_odb12.2026-05-22.tar.gz)
bash tests/sanger-tol_genomeassembly_test/run_test.sh
```

> 脚本里写的是本机的绝对路径（`/media/deyuan/18T_B/genome_assembly`、`/home/deyuan/miniforge3`）。换机器时，先改各脚本开头的路径变量。
