"""Synthetic interface checks of the pinned upstream get_seqs; not biological validation."""
from pathlib import Path
import json, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[2]
EXE=ROOT/'pipelines/dfguan_purge_dups/bin/get_seqs'
def total(p):
 return sum(len(x.strip()) for x in p.read_text().splitlines() if not x.startswith('>')) if p.exists() else 0
cases=[('internal_ends_only',['-e'],'ctg\t20000\t30000\tOVLP\n',50000),('internal_general',[],'ctg\t20000\t30000\tOVLP\n',40023),('terminal_ends_only',['-e'],'ctg\t0\t10000\tOVLP\n',40000),('whole_haplotig_ends_only',['-e'],'ctg\t0\t50000\tHAPLOTIG\n',0),('whole_junk_ends_only',['-e'],'ctg\t0\t50000\tJUNK\n',0),('whole_highcov_default',['-e'],'ctg\t0\t50000\tHIGHCOV\n',0),('whole_highcov_keep',['-e','-c'],'ctg\t0\t50000\tHIGHCOV\n',50000)]
results=[]
with tempfile.TemporaryDirectory(prefix='purging-interface-') as tmp:
 for name,opts,bed,expect in cases:
  d=Path(tmp)/name;d.mkdir();(d/'input.fa').write_text('>ctg\n'+'ACGT'*12500+'\n');(d/'dups.bed').write_text(bed)
  cmd=[str(EXE),*opts,'-p','out','dups.bed','input.fa'];run=subprocess.run(cmd,cwd=d,text=True,capture_output=True)
  primary=total(d/'out.purged.fa');moved=total(d/'out.hap.fa')
  inserted_ns=sum(x.upper().count('N') for x in (d/'out.purged.fa').read_text().splitlines() if not x.startswith('>'))
  results.append({'case':name,'options':opts,'returncode':run.returncode,'primary_bases':primary,'moved_bases':moved,'inserted_primary_ns':inserted_ns,'expected_primary_bases':expect,'passed':run.returncode==0 and primary==expect and primary+moved-inserted_ns==50000,'stderr':run.stderr})
report={'biological_validation':False,'scope':'7 synthetic extraction cases; not purge_dups classification or full pipeline','results':results}
p=Path(__file__).with_name('get_seqs_results.json');p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert all(x['passed'] for x in results)
