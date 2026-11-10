#!/usr/bin/env bash
# 按固定版本（commit）拉取本学习库用到的各流程源码；源码本身不放进本仓库。
# 用法：bash pipelines/fetch_pipelines.sh [目标目录，默认为本脚本所在目录]
# 已存在的仓库校验提交后跳过；网络不稳时会自动重试 3 次。
set -euo pipefail
DEST=${1:-$(cd "$(dirname "$0")" && pwd)}
mkdir -p "$DEST"

clone_at() {  # 目录名 仓库URL 版本说明 commit [只检出的子目录]
    local dir=$DEST/$1 url=$2 ref=$3 sha=$4 sparse=${5:-}
    if [ -d "$dir/.git" ]; then
        local actual
        actual=$(git -C "$dir" rev-parse HEAD)
        if [ "$actual" != "$sha" ]; then
            echo "FAILED $1：已有提交 $actual 与清单 $sha 不同；保留现有目录" >&2
            return 1
        fi
        echo "skip (提交一致) $1"; return 0
    fi
    if [ -e "$dir" ] || [ -L "$dir" ]; then
        echo "FAILED $1：目标已存在且不是可核查的 Git 仓库；保留现有路径" >&2
        return 1
    fi
    git init -q "$dir"
    git -C "$dir" remote add origin "$url"
    if [ -n "$sparse" ]; then
        git -C "$dir" sparse-checkout init --cone
        git -C "$dir" sparse-checkout set "$sparse"
    fi
    # fetch 和 checkout 都要联网（--filter=blob:none 时 checkout 才下载文件内容），所以一起重试
    for attempt in 1 2 3; do
        if git -C "$dir" fetch -q --depth 1 --filter=blob:none origin "$sha" && git -C "$dir" checkout -q FETCH_HEAD; then
            echo "ok $1 @ $ref ($(git -C "$dir" rev-parse --short HEAD))"; return 0
        fi
        echo "retry $attempt: $1" >&2; sleep 5
    done
    echo "FAILED $1：已删除半成品目录，稍后重跑本脚本即可" >&2
    rm -rf "${dir:?}"; return 1
}


# 与 notes/sources/source_manifest.json 的 2026-11-01 快照一致。
clone_at GPTomics_bioSkills https://github.com/GPTomics/bioSkills.git snapshot-2026-11-01 d91ed3d563019e649dc854c56ccd62551359488a
clone_at LiaOb21_colora https://github.com/LiaOb21/colora.git snapshot-2026-11-01 d6569edaff8da51739688b246dda2dfb2da13d7a
clone_at Noble-Lab_hic_scaffolder_benchmarks https://github.com/Noble-Lab/hic_scaffolder_benchmarks.git snapshot-2026-11-01 c6d09ad3cfed358d8186af5c99f99d94918b7be1
clone_at VGP_galaxy_iwc https://github.com/galaxyproject/iwc.git snapshot-2026-11-01 8da21209171cc44fe6f10a6a99dd0227ed1c0c2e workflows/VGP-assembly-v2
clone_at aidenlab_3d-dna https://github.com/aidenlab/3d-dna.git snapshot-2026-11-01 cb63403c329dd45d0fdc4851746b5a8587528132
clone_at aidenlab_juicer https://github.com/aidenlab/juicer.git snapshot-2026-11-01 f866383d66f780d98de2c1267703b4d3473f6250
clone_at c-zhou_yahs https://github.com/c-zhou/yahs.git snapshot-2026-11-01 6c46061ea1665073068cccbed81c6707e3bd07bf
clone_at cnag_CLAWS https://github.com/cnag-aat/CLAWS.git snapshot-2026-11-01 b7af1567c1a7f7024f299e771571eb41d476f131
clone_at dfguan_purge_dups https://github.com/dfguan/purge_dups.git snapshot-2026-11-01 f14dae13b7f41559bafd058f7278e8f5ac2813da
clone_at ebp-nor_GenomeAssembly https://github.com/ebp-nor/GenomeAssembly.git snapshot-2026-11-01 d31bbeec1aeb772d4b4eb30e29138b5a610a95dc
clone_at lh3_hifiasm https://github.com/chhylp123/hifiasm.git snapshot-2026-11-01 ec9a8b222d149d25b7355e83765698640d59b189
clone_at marbl_merqury https://github.com/marbl/merqury.git snapshot-2026-11-01 88f37c0f4dbb073001d194bcc5d5989a0b0527df
clone_at marbl_verkko https://github.com/marbl/verkko.git snapshot-2026-11-01 39e9fb22816da30b22426ad1914034bc3a2d0cfa
clone_at nf-core_genomeassembler https://github.com/nf-core/genomeassembler.git snapshot-2026-11-01 c608622876dc627020e6627a5ea8cffd0d2e3f3d
clone_at sanger-tol_genomeassembly https://github.com/sanger-tol/genomeassembly.git snapshot-2026-11-01 131f0ea272bb2fce9869d57f684f20f645467e34
clone_at zengxiaofei_HapHiC https://github.com/zengxiaofei/HapHiC.git snapshot-2026-11-01 74f1cb27d7753ce061ee673c0d62fdd44187060e
clone_at moniquevdor_GaleolariaReferenceGenome https://github.com/moniquevdor/GaleolariaReferenceGenome.git snapshot-2026-11-01 01c252196c6a8ba7c8fd93376ded2bb266eb3e7e
clone_at panlab-bioinfo_GPhase https://github.com/panlab-bioinfo/GPhase.git snapshot-2026-11-01 a9221035274e7397fc05dc5be693270c2758528c
clone_at tbenavi1_genomescope2.0 https://github.com/tbenavi1/genomescope2.0.git snapshot-2026-11-01 8f25e3a25eaa691cdae474daf5cfe5416bfc60dc
clone_at KamilSJaron_smudgeplot https://github.com/KamilSJaron/smudgeplot.git snapshot-2026-11-01 8ff8cd9885f8edcdf938e51dcfe9b9631d8cd1d0
clone_at thegenemyers_FASTK https://github.com/thegenemyers/FASTK.git snapshot-2026-11-01 0e24fb45b71c4e14382ae1e1bc063bf66ea4e112
clone_at mbhall88_lrge https://github.com/mbhall88/lrge.git snapshot-2026-11-01 01669fe358e3c6aec7328d5e4c238bdeb0eb2397
clone_at shenwei356_seqkit https://github.com/shenwei356/seqkit.git snapshot-2026-11-01 30d7dfc25893809acce74459d5000afef027b8d0
clone_at refresh-bio_KMC https://github.com/refresh-bio/KMC.git snapshot-2026-11-01 751ef36a3c1ccc6dda664f529ad218dc51d76f55
clone_at wdecoster_NanoPlot https://github.com/wdecoster/NanoPlot.git snapshot-2026-11-01 71af721be406cdcfcb1b974fe1db8e96f9e93c9e
clone_at wdecoster_chopper https://github.com/wdecoster/chopper.git snapshot-2026-11-01 ed2b6941c1aee157b841528f9461fec66dd77984
