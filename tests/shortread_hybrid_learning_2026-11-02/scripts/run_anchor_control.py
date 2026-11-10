#!/usr/bin/env python3
"""Follow-up control: 3-kb unique blocks, same 2-kb repeat; 5-kb long reads.

Compares PE-only and hybrid within this new fixture. This does not isolate the
cause of the previous 500-bp-anchor failure, since fixture and long length change.
"""
from pathlib import Path
import importlib.util,random,gzip,json,shutil
P=Path(__file__).resolve().parent/'run_spades_learning.py'
spec=importlib.util.spec_from_file_location('learning_runner',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
w=m.WORK;out=m.BASE
if (w/'anchor3000_pe').exists():raise RuntimeError('preserve existing outputs; use a new namespace')
rng=random.Random(20261103)
def dna(n):return ''.join(rng.choices('ACGT',k=n))
a,b,c,d=[dna(3000) for _ in range(4)];repeat=dna(2000)
g=a+repeat+b+repeat+c+repeat+d
inp=w/'anchor3000_inputs';inp.mkdir(exist_ok=True)
(inp/'truth.fa').write_text('>synthetic_anchor3000_G1\n'+g+'\n')
for mate in (1,2):
 with gzip.open(inp/f'pe_R{mate}.fq.gz','wt') as f:
  for n,i in enumerate(range(0,len(g)-500+1,3)):
   seq=g[i:i+150] if mate==1 else m.rc(g[i+350:i+500])
   f.write(f'@fragment{n}/{mate}\n{seq}\n+\n'+('I'*150)+'\n')
with (inp/'long5000.fa').open('w') as f:
 for n,i in enumerate(range(0,len(g)-5000+1,50)):
  f.write(f'>synthetic_no_error_long{n}\n{g[i:i+5000]}\n')
common=['--only-assembler','-1',str(inp/'pe_R1.fq.gz'),'-2',str(inp/'pe_R2.fq.gz'),'-k','21,33,55','-t','2','-m','4']
records=[m.run('anchor3000_pe',common+['-o',str(w/'anchor3000_pe')],w),m.run('anchor3000_hybrid',common+['--nanopore',str(inp/'long5000.fa'),'-o',str(w/'anchor3000_hybrid')],w)]
artifacts={}
for label in ['anchor3000_pe','anchor3000_hybrid']:
 dest=out/'outputs'/label;dest.mkdir(parents=True,exist_ok=True);artifacts[label]={}
 for name in ['contigs.fasta','scaffolds.fasta','assembly_graph_with_scaffolds.gfa','params.txt','spades.log','input_dataset.yaml']:
  p=w/label/name
  if p.exists():shutil.copy2(p,dest/name);artifacts[label][name]=dict(sha256=m.sha(p),bytes=p.stat().st_size)
shutil.copy2(inp/'truth.fa',out/'generated_inputs/anchor3000_truth.fa')
manifest=dict(kind='synthetic_followup_not_biological_validation',genome_bp=len(g),unique_block_bp=3000,repeat_bp=2000,pe_read_bp=150,pe_insert_bp=500,pe_step=3,long_read_bp=5000,long_step=50,records=records,artifacts=artifacts,input_hashes={p.name:m.sha(p) for p in inp.glob('*')},limitations='Relative to the prior experiment both unique-block length and long-read length change; do not infer a unique root cause')
(out/'anchor_control_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
