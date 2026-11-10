#!/usr/bin/env python3
"""Verify archived provenance/outputs without invoking any assembler."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[1]
def read(p):return json.loads(p.read_text())
def check(path,want):
 actual=hashlib.sha256(path.read_bytes()).hexdigest()
 if actual!=want:raise ValueError('Checksum mismatch: '+str(path))
n=0
for rel,item in read(B/'input_archive_manifest.json').items():check(B/rel,item['sha256']);n+=1
records=[]
for name in ['execution_manifest.json','anchor_control_manifest.json']:
 doc=read(B/name);records+=doc['records']
 for label,files in doc['artifacts'].items():
  for name,item in files.items():check(B/'outputs'/label/name,item['sha256']);n+=1
records.append(read(B/'logs/invalid_nonascii_output.json'))
for item in records:check(B/item['log'],item['log_sha256']);n+=1
for item in read(R/'notes/sources/shortread_hybrid_review_2026-11-02.json')['local_source_snapshots']:check(R/item['path'],item['sha256']);n+=1
out=dict(passed=True,checked_sha256=n,successful_assembly_runs=sum(r['returncode']==0 and r['label']!='version' for r in records),negative_cli_cases=sum(r['returncode']!=0 for r in records),validation_scope='saved provenance integrity, not independent biological QC')
(B/'saved_evidence_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
