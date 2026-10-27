#!/usr/bin/env bash
# 按固定版本（commit）拉取本学习库用到的各流程源码；源码本身不放进本仓库。
# 用法：bash pipelines/fetch_pipelines.sh [目标目录，默认为本脚本所在目录]
# 已存在的目录会跳过；网络不稳时会自动重试 3 次。
set -euo pipefail
DEST=${1:-$(cd "$(dirname "$0")" && pwd)}
mkdir -p "$DEST"

clone_at() {  # 目录名 仓库URL 版本说明 commit [只检出的子目录]
    local dir=$DEST/$1 url=$2 ref=$3 sha=$4 sparse=${5:-}
    if [ -d "$dir/.git" ]; then echo "skip (已存在) $1"; return 0; fi
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

clone_at sanger-tol_genomeassembly https://github.com/sanger-tol/genomeassembly.git 1.0.1  131f0ea272bb2fce9869d57f684f20f645467e34
clone_at VGP_galaxy_iwc            https://github.com/galaxyproject/iwc.git        main    d9ec763d035e8ae637c8a135db5da93eb8982ca1 workflows/VGP-assembly-v2
clone_at nf-core_genomeassembler   https://github.com/nf-core/genomeassembler.git  2.0.1   c608622876dc627020e6627a5ea8cffd0d2e3f3d
clone_at cnag_CLAWS                https://github.com/cnag-aat/CLAWS.git           v3.2    b7af1567c1a7f7024f299e771571eb41d476f131
clone_at ebp-nor_GenomeAssembly    https://github.com/ebp-nor/GenomeAssembly.git   main    d31bbeec1aeb772d4b4eb30e29138b5a610a95dc
clone_at marbl_verkko              https://github.com/marbl/verkko.git             v2.3.2  39e9fb22816da30b22426ad1914034bc3a2d0cfa
clone_at aidenlab_juicer           https://github.com/aidenlab/juicer.git          1.6     f866383d66f780d98de2c1267703b4d3473f6250
clone_at aidenlab_3d-dna           https://github.com/aidenlab/3d-dna.git          201008  cb63403c329dd45d0fdc4851746b5a8587528132
