#!/usr/bin/env python3
"""Exact checks on known toy truth; not a real-genome QC replacement."""
from pathlib import Path
import gzip, json, hashlib, shutil, importlib.util
B=Path(__file__).resolve().parents[1]
W=Path('/tmp/yzz-shortread-hybrid-20261102')
P=Path('/root/miniconda3/envs/mitoz3.6')
def fasta(p):
    op=gzip.open if p.suffix=='.gz' else open
    out=[]
    with op(p,'rt') as f:
        for line in f:
            if line.startswith('>'):out.append('')
            else:out[-1]+=line.strip()
    return out
def rc(s):return s.translate(str.maketrans('ACGT','TGCA'))[::-1]
def nx(ls,den):
    acc=0
    for n in ls:
        acc+=n
        if acc>=den/2:return n
    return None
def assess(label,truth):
    seqs=fasta(B/'outputs'/label/'contigs.fasta');ls=sorted(map(len,seqs),reverse=True)
    matches=[]
    for s in seqs:
        candidates=[(strand,truth.find(t)) for strand,t in [('+',s),('-',rc(s))]]
        matches.append([{'strand':a,'start_0based':b,'end_exclusive':b+len(s)} for a,b in candidates if b>=0])
    return dict(contig_lengths=ls,total_bp=sum(ls),truth_bp=len(truth),N50=nx(ls,sum(ls)),NG50=nx(ls,len(truth)),auN=sum(n*n for n in ls)/sum(ls),auNG=sum(n*n for n in ls)/len(truth),exact_truth_substring_matches=matches)
result={}
truth=fasta(P/'share/spades/test_dataset/reference_1K.fa.gz')[0]
result['official']=assess('official',truth)
for label in ['repeat_pe','repeat_hybrid']:result[label]=assess(label,fasta(B/'generated_inputs/G1.fa')[0])
for label in ['anchor3000_pe','anchor3000_hybrid']:result[label]=assess(label,fasta(B/'generated_inputs/anchor3000_truth.fa')[0])
# Cross-check formulas using the actual installed QUAST source, not a mirrored test.
q=Path('/tmp/yzz-learning-colora-envs/0eff1dd08048feedc658ebba6bc8c0c4_/lib/python3.11/site-packages/quast_libs/N50.py')
spec=importlib.util.spec_from_file_location('quast_n50',q);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result['metric_source_check']={'source':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'lengths':[1000,500],'auN':module.au_metric([1000,500]),'auNG_G2000':module.au_metric([1000,500],2000)}
assert result['official']['exact_truth_substring_matches'][0]
assert result['anchor3000_hybrid']['exact_truth_substring_matches'][0]
assert result['repeat_pe']['NG50'] is None
(B/'output_assessment.json').write_text(json.dumps(result,indent=2)+'\n')
archive={}
for name,src in [('repeat8000',W/'inputs'),('anchor18000',W/'anchor3000_inputs'),('official',P/'share/spades/test_dataset')]:
    dst=B/'inputs'/name;dst.mkdir(parents=True,exist_ok=True)
    for f in src.iterdir():
        if f.is_file() and (name!='official' or f.name in ['ecoli_1K_1.fq.gz','ecoli_1K_2.fq.gz','reference_1K.fa.gz']):
            shutil.copy2(f,dst/f.name);archive[str((dst/f.name).relative_to(B))]={'source':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
(B/'input_archive_manifest.json').write_text(json.dumps(archive,indent=2)+'\n')
print(json.dumps(result,indent=2))
