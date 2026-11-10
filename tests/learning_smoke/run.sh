#!/usr/bin/env bash
# Public fixtures only. No production data; no downloads or user data deletion.
set -euo pipefail
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$repo_dir"
test_dir=tests/learning_smoke
data_dir="$test_dir/test_data"
out_dir="$test_dir/results"
mkdir -p "$out_dir"
(cd "$data_dir" && sha256sum -c ../fixture_checksums.sha256)
python3 - <<'PY'
import json, subprocess
from pathlib import Path
for item in json.loads(Path('notes/sources/source_manifest.json').read_text())['repositories']:
    if item['directory'] not in {'lh3_hifiasm', 'c-zhou_yahs', 'Noble-Lab_hic_scaffolder_benchmarks'}:
        continue
    path = Path('pipelines') / item['directory']
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != item['commit']:
        raise SystemExit(f'Source revision mismatch: {path}: {actual}')
PY
make -C pipelines/lh3_hifiasm -j4 >"$out_dir/build_hifiasm.log" 2>&1
make -C pipelines/c-zhou_yahs -j4 >"$out_dir/build_yahs.log" 2>&1
# -i avoids accepting stale graph caches when repeating the smoke run.
pipelines/lh3_hifiasm/hifiasm -i -f0 -t4 -o "$out_dir/hifiasm" \
  "$data_dir/hic-study-chr11-2M.fa.gz" >"$out_dir/hifiasm.log" 2>&1
pipelines/c-zhou_yahs/yahs -o "$out_dir/yahs" \
  "$data_dir/LYZE01.contigs.fasta.gz" "$data_dir/LYZE01.hic.bed.gz" >"$out_dir/yahs.log" 2>&1
pipelines/c-zhou_yahs/agp_to_fasta "$out_dir/yahs_scaffolds_final.agp" \
  "$data_dir/LYZE01.contigs.fasta.gz" -o "$out_dir/yahs_rebuilt.fa" >"$out_dir/agp_to_fasta.log" 2>&1
pipelines/c-zhou_yahs/juicer pre -a -o "$out_dir/yahs.JBAT" "$out_dir/yahs.bin" \
  "$out_dir/yahs_scaffolds_final.agp" "$data_dir/LYZE01.contigs.fasta.gz.fai" >"$out_dir/juicer_pre.log" 2>&1
pipelines/c-zhou_yahs/juicer post -o "$out_dir/yahs.JBAT" "$out_dir/yahs.JBAT.assembly" \
  "$out_dir/yahs.JBAT.liftover.agp" "$data_dir/LYZE01.contigs.fasta.gz" >"$out_dir/juicer_post.log" 2>&1
python3 "$test_dir/verify.py"
