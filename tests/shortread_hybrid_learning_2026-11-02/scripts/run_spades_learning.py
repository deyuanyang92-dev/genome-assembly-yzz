#!/usr/bin/env python3
"""Run existing SPAdes 4.0.0 without changing its environment.

Official test is biological toy data. Repeat experiments use artificial error-free
reads; none of these runs validates SPAdes 4.3.0 or a large eukaryotic genome.
"""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,os,json,hashlib,gzip,shutil
BASE=Path(__file__).resolve().parents[1]
WORK=Path('/tmp/yzz-shortread-hybrid-20261102')
PREFIX=Path('/root/miniconda3/envs/mitoz3.6')
ARGV=[str(PREFIX/'bin/python'),str(PREFIX/'bin/spades.py')]
ENV=os.environ.copy();ENV['PYTHONDONTWRITEBYTECODE']='1'
ENV['PATH']=str(PREFIX/'bin')+os.pathsep+ENV.get('PATH','')

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_fasta(p):
 text=p.read_text();return ''.join(x.strip() for x in text.splitlines() if not x.startswith('>'))
def rc(s):return s.translate(str.maketrans('ACGT','TGCA'))[::-1]
def run(label,options,cwd,expected_success=True):
 cwd.mkdir(parents=True,exist_ok=True)
 log=BASE/'logs'/f'{label}.log'; record=dict(label=label,argv=ARGV+options,cwd=str(cwd),started_at=now(),expected_success=expected_success)
 with log.open('w') as f:
  proc=subprocess.run(record['argv'],cwd=cwd,env=ENV,stdout=f,stderr=subprocess.STDOUT)
 record.update(returncode=proc.returncode,finished_at=now(),log=str(log.relative_to(BASE)),log_sha256=sha(log))
 (BASE/'logs'/f'{label}.json').write_text(json.dumps(record,indent=2)+'\n')
 print(label,proc.returncode,flush=True)
 if (proc.returncode==0)!=expected_success:raise RuntimeError(f'Unexpected exit for {label}; see {log}')
 return record

def main():
 WORK.mkdir(exist_ok=True)
 # Refuse to reuse/overwrite a previous test namespace; explicit resume is separate.
 if (WORK/'official/spades_test').exists() or (WORK/'repeat_pe').exists():
  raise RuntimeError('Run namespace already contains outputs; inspect them rather than silently overwrite')
 records=[]
 records.append(run('version',['--version'],WORK))
 records.append(run('official_test',['--test','-t','2','-m','4'],WORK/'official'))
 g=read_fasta(BASE/'generated_inputs/G1.fa')
 inp=WORK/'inputs';inp.mkdir(exist_ok=True)
 for mate in (1,2):
  with gzip.open(inp/f'pe_R{mate}.fq.gz','wt') as f:
   for n,i in enumerate(range(0,len(g)-500+1,2)):
    seq=g[i:i+150] if mate==1 else rc(g[i+350:i+500])
    f.write(f'@fragment{n}/{mate}\n{seq}\n+\n'+('I'*len(seq))+'\n')
 with (inp/'long2300.fa').open('w') as f:
  for n,i in enumerate(range(0,len(g)-2300+1,25)):
   f.write(f'>synthetic_no_error_long_{n}\n{g[i:i+2300]}\n')
 common=['--only-assembler','-1',str(inp/'pe_R1.fq.gz'),'-2',str(inp/'pe_R2.fq.gz'),'-k','21,33,55','-t','2','-m','4']
 records.append(run('repeat_pe',common+['-o',str(WORK/'repeat_pe')],WORK))
 records.append(run('repeat_hybrid',common+['--nanopore',str(inp/'long2300.fa'),'-o',str(WORK/'repeat_hybrid')],WORK))
 records.append(run('invalid_isolate_careful',['--isolate','--careful',*common[1:],'-o',str(WORK/'invalid_flags')],WORK,False))
 records.append(run('invalid_continue_extra',['--continue','-o',str(WORK/'repeat_pe'),'-t','3'],WORK,False))
 artifacts={}
 for label,path in [('official',WORK/'official/spades_test'),('repeat_pe',WORK/'repeat_pe'),('repeat_hybrid',WORK/'repeat_hybrid')]:
  dest=BASE/'outputs'/label;dest.mkdir(parents=True,exist_ok=True)
  artifacts[label]={}
  for name in ['contigs.fasta','scaffolds.fasta','assembly_graph_with_scaffolds.gfa','params.txt','spades.log','input_dataset.yaml']:
   src=path/name
   if src.is_file():
    shutil.copy2(src,dest/name);artifacts[label][name]=dict(sha256=sha(src),bytes=src.stat().st_size)
 inputs_manifest={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in inp.glob('*')}
 manifest=dict(schema_version=1,run_version='SPAdes4.0.0 existing environment',review_version='SPAdes4.3.0 not executed',records=records,artifacts=artifacts,inputs=inputs_manifest,biological_toy_runs=1,synthetic_assembler_runs=2,negative_cli_checks=2,production_validation=0)
 (BASE/'execution_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
