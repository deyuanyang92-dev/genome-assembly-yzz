#!/usr/bin/env python3
"""Cross-check archived branch deliverables; never invoke biological programs."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parent;R=B.parents[1]
def read(p):return json.loads(p.read_text())
def check(p,sha):
 if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:raise ValueError('Hash mismatch: '+str(p))
doc=read(B/'manifest.json');n=0
for item in doc['files']:check(R/item['path'],item['sha256']);n+=1
# Also verify identities recorded before integration, rather than only newly assigned hashes.
for branch in doc['branches']:
 ledger=read(R/branch['source'])
 for key in ['local_artifacts','local_sources','files']:
  for item in ledger.get(key,[]):
   if isinstance(item,dict) and 'path' in item and 'sha256' in item:check(R/item['path'],item['sha256']);n+=1
hic=read(R/'tests/parallel_hic_review/execution_manifest.json')
assert len(hic['records'])==4 and all(r['returncode']==0 for r in hic['records'])
for r in hic['records']:check(R/'tests/parallel_hic_review'/r['log'],r['log_sha256']);n+=1
rna=read(R/'tests/parallel_annotation_review/execution.json')
assert len(rna['records'])==2 and all(r['returncode']==0 for r in rna['records'])
assert rna['records'][0]['alignments'][0]['cigar']=='800M2000N800M'
assert rna['records'][1]['alignments'][0]['cigar']=='800M2000D800M'
sem=read(R/'tests/parallel_standards_review/acceptance_semantics_results.json')
assert len(sem['cases'])==16 and all(c['passed'] for c in sem['cases'])
shell=read(R/'tests/parallel_shortread_review/compound_failure_result.json')
assert len(shell['cases'])==2 and shell['cases'][1]['returncode']==0 and shell['cases'][1]['all_fasta_headers']==5
out=dict(passed=True,checked_sha256=n,branch_evidence_files=len(doc['files']),research_agents=3,scope='archive integrity and recorded toy outcomes; not independent biological QC',runtime_counts=doc['runtime_counts'])
(B/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
