#!/usr/bin/env python3
"""Synthetic spliced RNA mapping check using existing minimap2; not annotation validation."""
from pathlib import Path
from datetime import datetime,timezone
import random,subprocess,json,hashlib,re
B=Path(__file__).resolve().parent
BIN=Path('/tmp/yzz-learning-colora-envs/0eff1dd08048feedc658ebba6bc8c0c4_/bin/minimap2')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=random.Random(20261102)
def dna(n):return ''.join(r.choice('ACGT') for _ in range(n))
a=dna(800);intron='GT'+dna(1996)+'AG';b=dna(800)
(B/'genome.fa').write_text('>toy_chr\n'+a+intron+b+'\n')
(B/'rna.fa').write_text('>synthetic_spliced_transcript\n'+a+b+'\n')
records=[]
for label,args in [('splice_hq',['-ax','splice:hq','-uf','--secondary=no']),('genomic_hifi',['-ax','map-hifi','--secondary=no'])]:
 out=B/(label+'.sam');err=B/(label+'.stderr');cmd=[str(BIN),*args,str(B/'genome.fa'),str(B/'rna.fa')]
 with out.open('w') as o,err.open('w') as e:proc=subprocess.run(cmd,stdout=o,stderr=e)
 if proc.returncode:raise RuntimeError(label)
 align=[]
 for line in out.read_text().splitlines():
  if line.startswith('@'):continue
  f=line.split('\t');align.append(dict(flag=int(f[1]),position_1based=int(f[3]),cigar=f[5],introns=[int(x) for x in re.findall(r'(\d+)N',f[5])],tags=f[11:]))
 records.append(dict(label=label,argv=cmd,returncode=proc.returncode,sam_sha256=sha(out),stderr_sha256=sha(err),alignments=align))
version=subprocess.run([str(BIN),'--version'],capture_output=True,text=True,check=True).stdout.strip()
assert records[0]['alignments'][0]['cigar']=='800M2000N800M'
doc=dict(timestamp=datetime.now(timezone.utc).isoformat(),runtime_version=version,binary_sha256=sha(BIN),input_hashes={n:sha(B/n) for n in ['genome.fa','rna.fa']},truth=dict(exon_bp=[800,800],intron_bp=2000,transcript_bp=1600),records=records,limitation='artificial error-free single transcript; no StringTie or RAGNAROK execution; mapping preset is not inferred from platform alone')
(B/'execution.json').write_text(json.dumps(doc,indent=2)+'\n')
print(json.dumps(doc,indent=2))
