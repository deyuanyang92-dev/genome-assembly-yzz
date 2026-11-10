#!/usr/bin/env python3
"""Execute upstream RagTag on deterministic artificial contigs; audit AGP independently."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def rc(seq):
    return seq.translate(str.maketrans('ACGTN', 'TGCAN'))[::-1]


def fasta_write(path, records):
    path.write_text(''.join(f'>{name}\n{seq}\n' for name, seq in records.items()))


def fasta_read(path):
    records = {}
    for line in path.read_text().splitlines():
        if line.startswith('>'):
            name = line[1:].split()[0]
            records[name] = ''
        else:
            records[name] += line.strip()
    return records


def run(cmd, env, log):
    with log.open('w') as out:
        p = subprocess.run(cmd, env=env, stdout=out, stderr=subprocess.STDOUT)
    if p.returncode:
        raise RuntimeError(f'{cmd} exited {p.returncode}; see {log}')
    return {'argv': cmd, 'exit_code': p.returncode, 'log': str(log.relative_to(ROOT))}


def audit(folder, query):
    actual = fasta_read(folder / 'ragtag.scaffold.fasta')
    rebuilt, layout, gaps, uses, ends = {}, {}, [], Counter(), {}
    parts = Counter()
    for line in (folder / 'ragtag.scaffold.agp').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        f = line.split('\t')
        name, start, end, part, kind = f[:5]
        start, end, part = int(start), int(end), int(part)
        assert start == ends.get(name, 0) + 1
        assert part == parts[name] + 1
        ends[name], parts[name] = end, part
        if kind in ('N', 'U'):
            seq = 'N' * int(f[5])
            gaps.append(len(seq))
        else:
            cid, a, b, strand = f[5], int(f[6]), int(f[7]), f[8]
            assert (a, b) == (1, len(query[cid])), 'full component preservation'
            assert strand in ('+', '-')
            seq = query[cid] if strand == '+' else rc(query[cid])
            uses[cid] += 1
            layout.setdefault(name, []).append([cid, strand])
        assert len(seq) == end - start + 1
        rebuilt[name] = rebuilt.get(name, '') + seq
    assert rebuilt == actual, 'independent AGP reconstruction must equal upstream FASTA'
    assert uses == Counter({name: 1 for name in query}), 'each query once, including unplaced'
    non_n = sum(len(s) - s.count('N') for s in actual.values())
    assert non_n == sum(map(len, query.values()))
    assert any(v == [['novel', '+']] for v in layout.values())
    return {'layout': layout, 'gap_lengths': gaps, 'non_N_bases': non_n,
            'total_bases': sum(map(len, actual.values())),
            'independent_agp_reconstruction': True, 'each_component_once': True,
            'novel_sequence_retained': True}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ragtag', type=Path, required=True)
    p.add_argument('--minimap2', type=Path, required=True)
    p.add_argument('--python', type=Path, required=True)
    args = p.parse_args()
    env = dict(os.environ)
    env['PATH'] = os.pathsep.join([str(args.python.parent), str(args.ragtag),
                                   str(args.minimap2.parent), env.get('PATH', '')])
    rng = random.Random(20261103)
    blocks = {k: ''.join(rng.choices('ACGT', k=20000)) for k in ('A', 'B', 'C', 'novel')}
    query = {'ctg_C': blocks['C'], 'ctg_A': blocks['A'],
             'ctg_B_rc': rc(blocks['B']), 'novel': blocks['novel']}
    inputs = ROOT / 'inputs'
    inputs.mkdir(exist_ok=True)
    fasta_write(inputs / 'query.fa', query)
    fasta_write(inputs / 'ref_forward.fa', {'chr1': blocks['A'] + 'G' * 2000 + blocks['B'] + 'T' * 3000 + blocks['C']})
    fasta_write(inputs / 'ref_rearranged.fa', {'chr1': blocks['A'] + 'G' * 2000 + rc(blocks['C']) + 'T' * 3000 + blocks['B']})
    fasta_write(inputs / 'target_truth.fa', {'target': blocks['A'] + blocks['B'] + blocks['C'], 'novel': blocks['novel']})
    commands, cases = [], {}
    for name, reference, opts in [('forward', 'ref_forward.fa', []),
                                   ('inferred_gaps', 'ref_forward.fa', ['-r']),
                                   ('reference_bias', 'ref_rearranged.fa', [])]:
        folder = ROOT / name
        if folder.exists():
            raise RuntimeError(f'{folder} exists; choose a fresh result directory before rerun')
        cmd = [str(args.python), str(args.ragtag / 'ragtag.py'), 'scaffold',
               '-t', '1', '-u', '-o', str(folder), *opts,
               str(inputs / reference), str(inputs / 'query.fa')]
        commands.append(run(cmd, env, ROOT / f'{name}.log'))
        cases[name] = audit(folder, query)
    forward = [['ctg_A', '+'], ['ctg_B_rc', '-'], ['ctg_C', '+']]
    biased = [['ctg_A', '+'], ['ctg_C', '-'], ['ctg_B_rc', '-']]
    assert cases['forward']['layout']['chr1_RagTag'] == forward
    assert cases['inferred_gaps']['layout']['chr1_RagTag'] == forward
    assert cases['reference_bias']['layout']['chr1_RagTag'] == biased
    assert cases['forward']['gap_lengths'] == [100, 100]
    assert cases['inferred_gaps']['gap_lengths'] == [2000, 3000]
    assert cases['reference_bias']['gap_lengths'] == [100, 100]
    # The reference-bias case deliberately disagrees with the independently defined artificial truth.
    cases['reference_bias']['matches_artificial_target_order_and_orientation'] = False
    versions = {}
    for key, cmd in {'ragtag_commit': ['git', '-C', str(args.ragtag), 'rev-parse', 'HEAD'],
                     'minimap2_version': [str(args.minimap2), '--version'],
                     'python_dependencies': [str(args.python), '-c',
                         'import sys,pysam; print(sys.version); print("pysam",pysam.__version__)']}.items():
        versions[key] = subprocess.check_output(cmd, text=True).strip()
    hashes = {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
              for f in sorted(ROOT.rglob('*')) if f.is_file() and f.name != 'results.json'}
    result = {'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'evidence_level': 'synthetic_component_execution', 'seed': 20261103,
              'versions': versions, 'commands': commands, 'cases': cases,
              'sha256': hashes,
              'limitations': ['No raw-read assembly, real biological sample or Hi-C data.',
                              'Only scaffold executed; correct/patch/merge not executed.',
                              'Reference gap lengths are not observed target gap lengths.']}
    (ROOT / 'results.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(cases, indent=2))


if __name__ == '__main__':
    main()
