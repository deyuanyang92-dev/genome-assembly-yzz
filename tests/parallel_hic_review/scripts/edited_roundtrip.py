#!/usr/bin/env python3
"""Exercise YaHS's real post-curation converter with known artificial edits."""
from pathlib import Path
import json,subprocess,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];R=B.parents[1];I=B/'inputs';O=B/'outputs';L=B/'logs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rc(s):return s.translate(str.maketrans('ACGT','TGCA'))[::-1]
def fa(path):
 d={};key=None
 for line in path.read_text().splitlines():
  if line.startswith('>'):key=line[1:].split()[0];d[key]=''
  elif key:d[key]+=line.strip()
 return d
seq={'A':'ACGTTAGCAATCCGATGCTA','B':'GGAATTCCTAGGCCAA','C':'TTGCAACGATTC'}
p=I/'original.fa';p.write_text(''.join(f'>{n}\n{s}\n' for n,s in seq.items()))
offset=0;index=[]
for n,s in seq.items():
 offset+=len(n)+2;index.append(f'{n}\t{len(s)}\t{offset}\t{len(s)}\t{len(s)+1}\n');offset+=len(s)+1
(I/'original.fa.fai').write_text(''.join(index))
(I/'liftover.agp').write_text(''.join(f'ctg{x:08d}.1\t1\t{len(s)}\t1\tW\t{n}\t1\t{len(s)}\t+\n' for x,(n,s) in enumerate(seq.items(),1)))
head='>ctg00000001.1:::fragment_1 1 8\n>ctg00000001.1:::fragment_2 2 12\n>ctg00000002.1 3 16\n>ctg00000003.1 4 12\n'
for name,body in [('edited','-2 3 1\n-4\n'),('duplicated','-2 3 1 1\n-4\n'),('omitted','-2 3\n-4\n')]: (I/(name+'.assembly')).write_text(head+body)
exe=R/'pipelines/c-zhou_yahs/juicer';records=[]
def run(label,asm,fasta):
 argv=[str(exe),'post','--gap-size','100','-o',str(O/label),str(I/asm),str(I/'liftover.agp'),str(I/fasta)]
 if (O/(label+'.FINAL.agp')).exists():raise RuntimeError('Refusing overwrite; use a fresh output namespace')
 start=datetime.now(timezone.utc).isoformat();p=subprocess.run(argv,capture_output=True,text=True)
 (L/(label+'.log')).write_text(p.stdout+p.stderr)
 rec=dict(label=label,argv=argv,started_at=start,finished_at=datetime.now(timezone.utc).isoformat(),returncode=p.returncode,log=str((L/(label+'.log')).relative_to(B)),log_sha256=sha(L/(label+'.log')))
 records.append(rec);assert p.returncode==0
run('edited','edited.assembly','original.fa')
run('index_only','edited.assembly','original.fa.fai')
run('duplicated','duplicated.assembly','original.fa')
run('omitted','omitted.assembly','original.fa')
expected={'scaffold_1':rc(seq['A'][8:20])+'N'*100+seq['B']+'N'*100+seq['A'][:8],'scaffold_2':rc(seq['C'])}
assert fa(O/'edited.FINAL.fa')==expected
assert (O/'index_only.FINAL.agp').read_text()==(O/'edited.FINAL.agp').read_text()
assert not (O/'index_only.FINAL.fa').exists()
# Interval accounting catches legal-format but scientifically unreviewed losses/copies.
def inventory(path):
 counts={n:[0]*len(s) for n,s in seq.items()}
 for l in path.read_text().splitlines():
  f=l.split('\t')
  if f[4]=='W':
   n=f[5];a,b=int(f[6])-1,int(f[7]);assert 0<=a<b<=len(seq[n])
   for j in range(a,b):counts[n][j]+=1
 return {'missing_source_bp':sum(c==0 for x in counts.values() for c in x),'overused_source_bp':sum(c>1 for x in counts.values() for c in x),'extra_source_copies_bp':sum(max(0,c-1) for x in counts.values() for c in x)}
account={n:inventory(O/(n+'.FINAL.agp')) for n in ['edited','duplicated','omitted']}
assert account['edited']=={'missing_source_bp':0,'overused_source_bp':0,'extra_source_copies_bp':0}
assert account['duplicated']['overused_source_bp']==8 and account['omitted']['missing_source_bp']==8
artifacts={str(p.relative_to(B)):dict(sha256=sha(p),bytes=p.stat().st_size) for folder in [I,O,L] for p in folder.iterdir() if p.is_file()}
out=dict(kind='artificial_conversion_fixture_not_hic_biological_validation',software='YaHS juicer 1.2.2',source_commit=subprocess.check_output(['git','-C',str(exe.parent),'rev-parse','HEAD'],text=True).strip(),binary_sha256=sha(exe),records=records,expected_lengths={n:len(s) for n,s in expected.items()},source_sequence_bp=sum(map(len,seq.values())),exact_sequence_assertion=True,index_only_produces_fasta=False,interval_accounting=account,artifacts=artifacts,limitations=['No .hic, Pretext or Juicebox GUI was used','No Hi-C alignment or biological scaffolding run','Duplicated/omitted fragments are accepted converter inputs, not established upstream bugs'])
(B/'execution_manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['exact_sequence_assertion','expected_lengths','interval_accounting','index_only_produces_fasta']},indent=2))
