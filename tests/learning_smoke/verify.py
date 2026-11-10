"""Validate real smoke outputs and probe the upstream benchmark metric semantics."""
import collections
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / 'results'
DATA = HERE / 'test_data'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_fasta(path):
    sequences = {}
    name = None
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as handle:
        for line in handle:
            if line.startswith('>'):
                name = line[1:].split()[0]
                require(name not in sequences, f'Duplicate FASTA identifier: {name}')
                sequences[name] = []
            elif line.strip():
                require(name is not None, f'FASTA sequence before header: {path}')
                sequences[name].append(line.strip().upper())
    return {key: ''.join(value) for key, value in sequences.items()}


def check_agp(path, contigs, scaffolds):
    pieces = collections.defaultdict(list)
    intervals = collections.defaultdict(list)
    next_position = collections.defaultdict(lambda: 1)
    next_part = collections.defaultdict(lambda: 1)
    complement = str.maketrans('ACGTRYMKBDHVN', 'TGCAYRKMVHDBN')
    with path.open() as handle:
        for line in handle:
            if not line.strip() or line.startswith('#'):
                continue
            fields = line.rstrip().split('\t')
            require(len(fields) == 9, 'AGP must have 9 columns')
            obj, start, end, part, kind, component, first, last, direction = fields
            start, end, part = int(start), int(end), int(part)
            require(start == next_position[obj] and end >= start, f'AGP object interval: {obj}')
            require(part == next_part[obj], f'AGP part number: {obj}')
            next_position[obj], next_part[obj] = end + 1, part + 1
            if kind in {'N', 'U'}:
                require(int(component) == end - start + 1, 'AGP gap length mismatch')
                seq = 'N' * int(component)
            else:
                require(kind == 'W' and component in contigs, 'Unexpected AGP component')
                first, last = int(first), int(last)
                require(1 <= first <= last <= len(contigs[component]), 'AGP component out of range')
                require(direction in {'+', '-'}, 'Unknown AGP orientation')
                seq = contigs[component][first - 1:last]
                if direction == '-':
                    seq = seq.translate(complement)[::-1]
                intervals[component].append((first, last))
            require(len(seq) == end - start + 1, 'AGP span mismatch')
            pieces[obj].append(seq)
    require({key: ''.join(value) for key, value in pieces.items()} == scaffolds,
            'FASTA differs from independent AGP reconstruction')
    require(set(intervals) == set(contigs), 'Missing input component')
    for name, ranges in intervals.items():
        position = 1
        for start, end in sorted(ranges):
            require(start == position, f'Component lost or reused: {name}')
            position = end + 1
        require(position == len(contigs[name]) + 1, f'Incomplete component: {name}')


def main():
    checksums = {}
    for line in (HERE / 'fixture_checksums.sha256').read_text().splitlines():
        digest, name = line.split()
        actual = hashlib.sha256((DATA / name).read_bytes()).hexdigest()
        require(actual == digest, f'Fixture changed: {name}')
        checksums[name] = actual
    contigs = read_fasta(DATA / 'LYZE01.contigs.fasta.gz')
    scaffolds = read_fasta(OUT / 'yahs_scaffolds_final.fa')
    require(scaffolds == read_fasta(OUT / 'yahs_rebuilt.fa'), 'agp_to_fasta roundtrip differs')
    check_agp(OUT / 'yahs_scaffolds_final.agp', contigs, scaffolds)
    require(scaffolds == read_fasta(OUT / 'yahs.JBAT.FINAL.fa'), 'Unedited JBAT roundtrip differs')
    graph_stats = {}
    for path in sorted(OUT.glob('hifiasm*ctg.gfa')):
        seqs = [line.split('\t')[2] for line in path.read_text().splitlines() if line.startswith('S\t')]
        require(seqs and '*' not in seqs, f'Missing GFA segments: {path}')
        graph_stats[path.name] = {'segments': len(seqs), 'bases': sum(map(len, seqs))}
    require('hifiasm.bp.p_ctg.gfa' in graph_stats, 'Missing primary assembly')

    bench = OUT / 'benchmark'
    bench.mkdir(exist_ok=True)
    reference = bench / 'reference.agp'
    reference.write_text('chr1\t1\t100\t1\tW\ta\t1\t100\t+\n'
                         'chr1\t101\t200\t2\tW\tb\t1\t100\t+\n'
                         'chr2\t1\t100\t1\tW\tc\t1\t100\t+\n'
                         'chr2\t101\t200\t2\tW\td\t1\t100\t+\n')
    flipped = bench / 'flipped.agp'
    flipped.write_text(reference.read_text().replace('b\t1\t100\t+', 'b\t1\t100\t-'))
    source = REPO / 'pipelines/Noble-Lab_hic_scaffolder_benchmarks/main'
    scores = {}
    # Upstream imports matplotlib indirectly; use a writable temporary cache.
    with tempfile.TemporaryDirectory(prefix='hic-mpl-') as cache:
        env = dict(os.environ, MPLCONFIGDIR=cache)
        for path in (reference, flipped):
            result = subprocess.run([sys.executable, str(source / 'distance/edit_distance.py'),
                                     '-r', str(reference), '-a', str(path), '-o', str(bench)],
                                    capture_output=True, text=True, check=True, env=env)
            (bench / (path.stem + '.log')).write_text(result.stdout + result.stderr)
            scores[path.stem] = json.loads(path.with_suffix('.json').read_text())
    require(scores['reference'] == {'grouping': 1, 'order': 1, 'orientation': 1,
                                    'accuracy': 1, 'edit_distance': 0}, 'Self score unexpected')
    require(scores['flipped'] == {'grouping': 1, 'order': 1, 'orientation': 0.5,
                                  'accuracy': 0.75, 'edit_distance': 1}, 'Flip score unexpected')
    tiny = bench / 'tiny.fa'
    tiny.write_text('>x\n' + 'A' * 1000 + '\n')
    flagstat = bench / 'flagstat.json'
    flagstat.write_text(json.dumps({'QC-passed reads': {'read1': 10, 'mapped': 20}}))
    result = subprocess.run([sys.executable, str(source / 'alignment/sample_rate.py'),
                             '-i', str(tiny), '-a', str(flagstat), '-c', '50'],
                            capture_output=True, text=True, check=True)
    sentinel = result.stdout.strip()
    require(sentinel == '0.000000000000', 'Upstream sentinel behavior changed: re-audit wrapper')
    report = {'validated': True, 'python': platform.python_version(),
              'fixtures_sha256': checksums, 'hifiasm': graph_stats,
              'yahs': {'input_contigs': len(contigs), 'input_bases': sum(map(len, contigs.values())),
                       'output_scaffolds': len(scaffolds), 'output_bases': sum(map(len, scaffolds.values())),
                       'agp_coordinates_and_complete_component_coverage': True,
                       'agp_to_fasta_roundtrip': True, 'unedited_jbat_roundtrip': True},
              'benchmark': scores, 'upstream_insufficient_coverage_stdout': sentinel,
              'limits': ['No full paper benchmark', 'No Java hic generation or manual curation',
                         'No Hi-C hifiasm test', 'Video not acquired']}
    (HERE / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
