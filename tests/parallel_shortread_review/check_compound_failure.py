#!/usr/bin/env python3
"""Own synthetic fixture for shell finalizer semantics, NOT Platanus execution.

Motivated by selected phase.cpp finalization structure. No upstream source is
copied, compiled, or run. Inputs are fake FASTAs, not biological sequencing data.
"""
from pathlib import Path
import tempfile,subprocess,json,hashlib,shlex
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
q=shlex.quote
cases=[]
with tempfile.TemporaryDirectory(prefix='yzz-phase-finalizer-') as temp:
 for absent in [None,'secondary']:
  d=Path(temp)/('complete' if absent is None else 'missing_secondary');d.mkdir()
  categories=['primary','secondary','other','fork1','fork2','nested']
  for i,name in enumerate(categories):
   if name!=absent:(d/(name+'.fa')).write_text('>'+name+'\n'+'ACGT'*(i+1)+'\n')
  # Earlier missing input fails, but the final successful command determines rc.
  groups=[('all.fa',categories),('hetero.fa',['fork1','fork2','nested']),('consensus.fa',['primary','fork1','other'])]
  command='; '.join('cat '+' '.join(q(n+'.fa') for n in names)+' > '+q(out) for out,names in groups)
  cp=subprocess.run(['/bin/sh','-c',command],cwd=d,text=True,capture_output=True)
  result=dict(case=d.name,argv=['/bin/sh','-c',command],returncode=cp.returncode,stderr=cp.stderr,expected_input_missing=absent,all_fasta_headers=(d/'all.fa').read_text().count('>'),output_sha256={out:hashlib.sha256((d/out).read_bytes()).hexdigest() for out,_ in groups})
  cases.append(result)
assert cases[0]['returncode']==0 and cases[0]['all_fasta_headers']==6
assert cases[1]['returncode']==0 and cases[1]['stderr'] and cases[1]['all_fasta_headers']==5
report=dict(checked_at=datetime.now(timezone.utc).isoformat(),scope='synthetic shell mechanism demonstration; not upstream bug reproduction',cases=cases,passed=True,upstream_assembler_runs=0,biological_runs=0)
(BASE/'compound_failure_result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
