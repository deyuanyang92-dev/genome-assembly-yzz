#!/usr/bin/env python3
"""Run fixed AUGUSTUS official examples; archive commands, timing and evidence.

Requires Biopython and a compiled official v3.5.0 tree. Use a fresh output dir.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from Bio import SeqIO

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    src, out = args.source.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'commands.json').exists():
        raise SystemExit('Refusing to overwrite a previous run')
    inputs, runs = out / 'inputs', out / 'runs'
    inputs.mkdir(exist_ok=True)
    runs.mkdir(exist_ok=True)
    config = out / 'config'
    config.mkdir(exist_ok=True)
    for p in (src / 'config').iterdir():
        if p.name != 'species':
            if p.is_dir():
                shutil.copytree(p, config / p.name, dirs_exist_ok=True)
            else:
                shutil.copy2(p, config / p.name)
    (config / 'species').mkdir(exist_ok=True)
    for model in ['generic', 'human', 'fly']:
        shutil.copytree(src / 'config/species' / model, config / 'species' / model)
    originals = ['examples/example.fa', 'examples/HS04636.fa', 'examples/hints.gff',
                 'examples/hsackI10.gb', 'examples/chr2L/genes.gb.train',
                 'examples/chr2L/genes.gb.test']
    provenance = {}
    for rel in originals:
        target = inputs / Path(rel).name
        shutil.copy2(src / rel, target)
        provenance[target.name] = {'source_path': rel, 'sha256': digest(target)}
    env = os.environ.copy()
    env['AUGUSTUS_CONFIG_PATH'] = str(config)
    env['PATH'] = str(src / 'bin') + ':' + str(src / 'scripts') + ':' + env['PATH']
    commands = []

    def run(name, cmd, expect=0):
        start = datetime.datetime.now().astimezone().isoformat()
        t0 = time.monotonic()
        with (runs / (name + '.out')).open('w') as stdout, (runs / (name + '.err')).open('w') as stderr:
            result = subprocess.run(['/usr/bin/time', '-f', '%e\t%M', '-o',
                                     str(runs / (name + '.time.tsv')), *map(str, cmd)],
                                    stdout=stdout, stderr=stderr, env=env, cwd=out,
                                    timeout=600)
        entry = {'name': name, 'command': list(map(str, cmd)), 'started_at': start,
                 'elapsed_seconds': round(time.monotonic()-t0, 3), 'exit_code': result.returncode,
                 'expected_exit_code': expect, 'stdout_sha256': digest(runs / (name + '.out'))}
        commands.append(entry)
        (out / 'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
        print(name, result.returncode, entry['elapsed_seconds'], flush=True)
        assert result.returncode == expect, entry

    aug, etrain = src / 'bin/augustus', src / 'bin/etraining'
    base = [aug, '--species=human', '--gff3=on', '--UTR=off', '--softmasking=0',
            '--sample=0', '--codingseq=on', '--stopCodonExcludedFromCDS=false']
    run('version', [aug, '--version'])
    run('abinitio', [*base, inputs / 'example.fa'])
    run('hints', [*base, '--hintsfile='+str(inputs / 'hints.gff'),
                  '--extrinsicCfgFile='+str(config / 'extrinsic/extrinsic.MPE.cfg'), inputs / 'example.fa'])
    # Historical duplicate-option run: first --UTR=off wins in this version.
    # Corrected explicit UTR run is in run_followup.py.
    run('utr', [*base, '--UTR=on', inputs / 'example.fa'])
    seq = next(SeqIO.parse(inputs / 'HS04636.fa', 'fasta'))
    left, right = 501, len(seq)-500
    cropped = seq[left-1:right]
    cropped.id = cropped.name = 'HS04636_crop'
    cropped.description = ''
    SeqIO.write([cropped], inputs / 'crop.fa', 'fasta')
    run('range', [*base, '--predictionStart='+str(left), '--predictionEnd='+str(right), inputs / 'HS04636.fa'])
    run('crop', [*base, inputs / 'crop.fa'])
    rc = cropped.reverse_complement(id='HS04636_crop_rc', description='')
    SeqIO.write([rc], inputs / 'crop_rc.fa', 'fasta')
    run('crop_rc', [*base, inputs / 'crop_rc.fa'])
    run('invalid_species', [aug, '--species=yzz_missing_model_20261104', inputs / 'HS04636.fa'], expect=1)
    run('invalid_interval', [*base, '--predictionStart=9000', '--predictionEnd=100', inputs / 'HS04636.fa'], expect=1)
    run('genbank_evaluation', [*base, inputs / 'hsackI10.gb'])
    # Official fly train/test partition, not a newly sampled target-species dataset.
    # AUGUSTUS uses simplified GenBank, not strict INSDC. Only parse LOCUS IDs here.
    train = re.findall(r'^LOCUS\s+(\S+)', (inputs / 'genes.gb.train').read_text(), re.M)
    test = re.findall(r'^LOCUS\s+(\S+)', (inputs / 'genes.gb.test').read_text(), re.M)
    assert set(train).isdisjoint(test)
    run('new_species', ['perl', src / 'scripts/new_species.pl', '--species=yzz_fly_demo'])
    # Deliberate retention of the initial wrong-convention experiment. The old
    # tutorial uses excluded stop codons; these shipped files INCLUDE them.
    # Exit 0 here does not mean accepted training. See stderr and run_followup.py.
    run('etraining', [etrain, '--species=yzz_fly_demo', '--stopCodonExcludedFromCDS=true', inputs / 'genes.gb.train'])
    run('trained_holdout', [aug, '--species=yzz_fly_demo', '--stopCodonExcludedFromCDS=true',
                            '--UTR=off', '--softmasking=0', '--sample=0', inputs / 'genes.gb.test'])
    run('shipped_fly_holdout', [aug, '--species=fly', '--stopCodonExcludedFromCDS=true',
                                '--UTR=off', '--softmasking=0', '--sample=0', inputs / 'genes.gb.test'])

    def features(name):
        records = []
        for line in (runs / (name+'.out')).read_text().splitlines():
            if not line or line.startswith('#'):
                continue
            f = line.split('\t')
            if len(f) != 9:
                continue
            records.append((f[0], f[2], int(f[3]), int(f[4]), f[6], f[7],
                            dict(x.split('=', 1) for x in f[8].split(';') if '=' in x)))
        return records

    checks = {}
    genomes = {r.id: r.seq for r in SeqIO.parse(inputs/'example.fa', 'fasta')}
    reports = {}
    for name in ['abinitio', 'hints', 'utr']:
        rows = features(name)
        ids = {r[6]['ID'] for r in rows if 'ID' in r[6]}
        cds = collections.defaultdict(list)
        for sid, typ, a, b, strand, phase, attrs in rows:
            assert 1 <= a <= b <= len(genomes[sid])
            for parent in attrs.get('Parent', '').split(','):
                assert not parent or parent in ids
            if typ == 'CDS':
                cds[attrs['Parent']].append((sid, a, b, strand, int(phase)))
        translations = {}
        for parent, chunks in cds.items():
            chunks.sort(key=lambda x:x[1], reverse=chunks[0][3]=='-')
            pieces = []
            for i, (sid,a,b,strand,phase) in enumerate(chunks):
                dna = genomes[sid][a-1:b]
                pieces.append(dna if strand=='+' else dna.reverse_complement())
                if i:
                    prev = chunks[i-1]
                    assert phase == (3-((prev[2]-prev[1]+1-prev[4]) % 3)) % 3
            dna = sum(pieces[1:], pieces[0])
            protein = str(dna[chunks[0][4]:].translate())
            translations[parent] = {'length_bp': len(dna), 'length_aa_with_stop':len(protein),
                                    'internal_stops':protein[:-1].count('*'),
                                    'starts_M':protein.startswith('M'), 'ends_stop':protein.endswith('*')}
        reports[name] = {'features': dict(collections.Counter(r[1] for r in rows)), 'translations':translations}
    checks['structure_and_phase_valid'] = True
    def signature(name, transform=lambda a,b,s:(a,b,s)):
        return sorted((typ,*transform(a,b,strand),phase) for _,typ,a,b,strand,phase,_ in features(name))
    checks['range_equals_lifted_crop'] = signature('range') == signature('crop', lambda a,b,s:(a+left-1,b+left-1,s))
    checks['rc_coordinate_structure_equivalent'] = signature('crop') == signature('crop_rc', lambda a,b,s:(len(cropped)-b+1,len(cropped)-a+1,'-' if s=='+' else '+'))
    checks['hints_change_structure'] = signature('abinitio') != signature('hints')
    checks['train_test_locus_names_disjoint'] = True
    checks['crop'] = {'original_id':seq.id, 'start_1based':left, 'end_1based':right, 'length':len(cropped)}
    assert checks['range_equals_lifted_crop']
    assert checks['rc_coordinate_structure_equivalent']
    report = {'checks':checks, 'predictions':reports, 'training':{'train_loci':len(train), 'test_loci':len(test),
              'partition':'official examples/chr2L; no new homology-cluster leakage audit',
              'optimization_run':False, 'target_species':False,
              'accepted':False, 'reason':'wrong stop-codon convention; corrected in followup'}, 'input_provenance':provenance,
              'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip(),
              'binary_sha256':{'augustus':digest(aug),'etraining':digest(etrain)}}
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(checks,indent=2), flush=True)

if __name__ == '__main__':
    main()
