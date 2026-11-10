#!/usr/bin/env python3
"""A reproducible information-limit experiment, NOT a genome assembler benchmark.

Enumerate every error-free fragment in two different 8-kb linear genomes.
Short fragments cannot bridge three identical 2-kb repeat copies; long ones can.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random

OUT = Path(__file__).resolve().parents[1]
RNG = random.Random(20261102)

def dna(n):
    return ''.join(RNG.choices('ACGT', k=n))

def revcomp(s):
    return s.translate(str.maketrans('ACGT', 'TGCA'))[::-1]

def fragments(s, length):
    return Counter(s[i:i+length] for i in range(len(s)-length+1))

def pairs(s, read_length, insert):
    return Counter((s[i:i+read_length], revcomp(s[i+insert-read_length:i+insert]))
                   for i in range(len(s)-insert+1))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    a, b, c, d = (dna(500) for _ in range(4))
    repeat = dna(2000)
    g1 = a + repeat + b + repeat + c + repeat + d
    g2 = a + repeat + c + repeat + b + repeat + d
    inputs = OUT / 'generated_inputs'
    inputs.mkdir(exist_ok=True)
    for label, g in [('G1',g1), ('G2',g2)]:
        (inputs / (label+'.fa')).write_text('>'+label+'\n'+g+'\n')
    short = {str(n): fragments(g1,n) == fragments(g2,n) for n in (31,150,500)}
    pe1, pe2 = pairs(g1,150,500), pairs(g2,150,500)
    long1, long2 = fragments(g1,2300), fragments(g2,2300)
    # Same read identities at 1, 10 or 100 copies remain indistinguishable.
    duplication = {str(f): Counter({k:v*f for k,v in pe1.items()}) ==
                           Counter({k:v*f for k,v in pe2.items()}) for f in (1,10,100)}
    checks = dict(genomes_are_different=g1 != g2,
                  genome_lengths_equal=len(g1)==len(g2)==8000,
                  short_fragment_spectra_equal=all(short.values()),
                  pe150_insert500_multisets_equal=pe1==pe2,
                  deeper_identical_sampling_remains_ambiguous=all(duplication.values()),
                  long2300_multisets_are_distinguishable=long1!=long2)
    result = dict(schema_version=1,checked_at=datetime.now(timezone.utc).isoformat(),
                  kind='synthetic_information_limit_experiment_not_upstream_assembler_execution',
                  seed=20261102,reference_structures=['A-R-B-R-C-R-D','A-R-C-R-B-R-D'],
                  unique_block_bp=500,identical_repeat_bp=2000,genome_bp=len(g1),
                  single_fragment_equality=short,pe_read_bp=150,pe_insert_bp=500,
                  pe_fragment_count_per_genome=sum(pe1.values()),
                  ideal_pe_mean_base_coverage=sum(pe1.values())*300/len(g1),
                  duplication_factor_equality=duplication,long_read_bp=2300,
                  unique_long_fragment_multiset_difference=sum((long1-long2).values()),
                  checks=checks,passed=all(checks.values()),
                  input_hashes={p.name:sha(p) for p in inputs.glob('*.fa')},
                  limitations=['No sequencing errors, ploidy, GC bias or random sampling',
                               'Exhaustive fragments are a controlled mathematical construction, not raw biological data',
                               'Does not prove that any particular assembler resolves the long-read case',
                               'A real repeat with informative internal differences may be resolvable without spanning it'])
    (OUT/'repeat_information_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
