#!/usr/bin/env bash
# 把 default test 用到的远程输入下载到本地，并生成指向本地文件的 YAML（数据和方案与官方完全一致，只换路径）
# 原因：本机经代理访问远程文件时偶发 TLS 握手失败（SSLHandshakeException），
#       nf-schema 校验文件存在性时会误报 "does not exist" 并终止流程。
set -euo pipefail
cd "$(dirname "$0")"
PIPE=/media/deyuan/18T_B/genome_assembly/pipelines/sanger-tol_genomeassembly/assets/small_tests
mkdir -p test_data

urls=$(grep -hoE "https://[^\" ]+" $PIPE/icAdaBipu1_genomic.yaml $PIPE/default_spec.yaml | sort -u)
fam=$(echo "$urls" | grep '\.fam$')
urls="$urls"$'\n'"$(for ext in h3f h3i h3m h3p; do echo "$fam.$ext"; done)"   # oatk 的 HMM 配套索引

for u in $urls; do
    out=test_data/$(basename "$u")
    expected=$(curl -sIL --retry 5 --retry-all-errors "$u" | tr -d '\r' | awk 'tolower($1)=="content-length:" {n=$2} END {print n}')
    if [ -s "$out" ] && [ "$(stat -c %s "$out")" = "$expected" ]; then echo "ok (cached) $out"; continue; fi
    curl -fsSL --retry 8 --retry-all-errors --retry-delay 3 -o "$out" "$u"
    actual=$(stat -c %s "$out")
    if [ -z "$expected" ]; then echo "WARN no Content-Length for $u, size $actual"
    elif [ "$actual" != "$expected" ]; then echo "SIZE MISMATCH $out: $actual != $expected"; exit 1; fi
    echo "ok $out ($actual bytes)"
done

for f in test_data/*.gz; do gzip -t "$f"; done
echo "gzip integrity ok"

D=$(pwd)/test_data
sed -E "s#https://[^\" ]+/#$D/#" $PIPE/icAdaBipu1_genomic.yaml > icAdaBipu1_genomic.local.yaml
sed -E "s#https://[^\" ]+/#$D/#" $PIPE/default_spec.yaml       > default_spec.local.yaml
echo "local YAMLs written"
