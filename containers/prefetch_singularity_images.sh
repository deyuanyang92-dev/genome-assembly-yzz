#!/usr/bin/env bash
# 预先把 Nextflow 流程要用的 Singularity 镜像下载到 NXF_SINGULARITY_CACHEDIR（断点续传 + 自动重试）
# 原因：本机代理链路偶发断连，Nextflow 自己拉镜像时不重试，断一次整个流程就失败。
# 文件名与 Nextflow 的缓存命名一致（去掉 https://，'/' 和 ':' 换成 '-'，加 .img），Nextflow 会直接复用。
#
# 用法：bash prefetch_singularity_images.sh <镜像列表.txt>
#   镜像列表可以用 nextflow inspect 生成，例如：
#   nextflow inspect <流程目录> -profile <...>,singularity <参数...> -format json \
#     | python3 -c "import json,sys; print('\n'.join(sorted({p['container'] for p in json.load(sys.stdin)['processes'] if p.get('container')})))" > images.txt
set -euo pipefail

LIST=$1
CACHE=${NXF_SINGULARITY_CACHEDIR:-/media/deyuan/18T_B/genome_assembly/containers/singularity}
mkdir -p "$CACHE"

fetch_one() {
    local uri=$1 cache=$2
    local name target
    name=$(echo "${uri#https://}" | sed 's#[/:]#-#g').img
    target=$cache/$name
    if [ -s "$target" ] && singularity sif list "$target" > /dev/null 2>&1; then
        echo "ok (cached) $name"; return 0
    fi
    for attempt in 1 2 3 4 5 6; do
        if [[ $uri == https://* ]]; then
            curl -fsSL --retry 10 --retry-all-errors --retry-delay 5 -C - -o "$target.part" "$uri" || true
        else
            rm -f "$target.part"
            singularity pull --name "$target.part" "docker://$uri" > /dev/null 2>&1 || true
        fi
        if [ -s "$target.part" ] && singularity sif list "$target.part" > /dev/null 2>&1; then
            mv "$target.part" "$target"; echo "ok $name ($(du -h "$target" | cut -f1))"; return 0
        fi
        [[ $uri == https://* ]] || rm -f "$target.part"   # docker 转换失败的半成品不能续传
        echo "retry $attempt: $name" >&2; sleep 10
    done
    echo "FAILED $uri" >&2; return 1
}
export -f fetch_one

grep -v '^\s*$' "$LIST" | xargs -P 4 -I{} bash -c 'fetch_one "$@"' _ {} "$CACHE"
echo "all images ready in $CACHE"
