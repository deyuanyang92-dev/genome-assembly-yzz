#!/usr/bin/env bash
# sanger-tol/genomeassembly 1.0.1 官方 test profile 测试
# 测试数据：二星瓢虫 Adalia bipunctata (icAdaBipu1) 抽样的 HiFi + Hi-C + 10X
# 用法：先 bash fetch_test_data.sh（下载输入到本地），再 bash run_test.sh（中断后重跑会自动 -resume 续跑）
# 说明：输入改用本地副本（*.local.yaml，与官方只差路径），避免经代理在线校验远程文件时偶发 TLS 失败；
#       镜像预先用 containers/prefetch_singularity_images.sh 下好；BUSCO 用本地的 eukaryota_odb12（与官方测试同一个谱系，离线模式）
#       save_fastk_databases / save_genomescope2_outputs 与官方 nf-test（tests/default.nf.test）一致，便于和快照逐文件比对
set -euo pipefail

source /home/deyuan/miniforge3/etc/profile.d/conda.sh
conda activate nextflow   # Nextflow 25.10.4 + OpenJDK 21

BASE=/media/deyuan/18T_B/genome_assembly
export NXF_SINGULARITY_CACHEDIR=$BASE/containers/singularity   # 镜像缓存放 18T 盘，后续流程共用
export NXF_OPTS='-Xms1g -Xmx4g'                                # 限制 Nextflow 主进程内存

cd "$(dirname "$0")"
nextflow run $BASE/pipelines/sanger-tol_genomeassembly \
    -profile test,singularity \
    --genomic_data icAdaBipu1_genomic.local.yaml \
    --assembly_specs default_spec.local.yaml \
    --busco_lineage_directory $BASE/databases/busco_downloads \
    --save_fastk_databases true --save_genomescope2_outputs true \
    --outdir results \
    -resume
