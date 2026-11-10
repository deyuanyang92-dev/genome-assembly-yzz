#!/usr/bin/env python3
"""Validate structural consistency of the official July 2026 Capitella bundle."""
import collections, gzip, hashlib, json, pathlib, re, subprocess, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "public_reference_capitella_2026-07"
OUT = ROOT / "capitella_reference_validation.json"

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

files={p.name:{"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(DATA.iterdir()) if p.is_file()}
assembly=next(p for p in DATA.glob('*.fasta.gz') if '.prot.' not in p.name)
seqs={}; seq=None
with gzip.open(assembly,'rt') as f:
    for line in f:
        if line.startswith('>'):
            seq=line[1:].strip().split()[0]; seqs[seq]=0
        else:
            seqs[seq]+=len(line.strip())
gff=next(DATA.glob('*.gff3.gz'))
features=collections.Counter(); ids=set(); parents=[]; missing_seq=set(); bad_bounds=[]; duplicate_ids=[]
with gzip.open(gff,'rt') as f:
    for line in f:
        if not line.strip() or line.startswith('#'): continue
        a=line.rstrip('\n').split('\t')
        if len(a)!=9: continue
        s,_,typ,start,end,_,_,_,attrs=a
        features[typ]+=1
        start=int(start); end=int(end)
        if s not in seqs: missing_seq.add(s)
        elif start<1 or end>seqs[s] or start>end: bad_bounds.append([s,typ,start,end,seqs[s]])
        m=re.search(r'(?:^|;)ID=([^;]+)',attrs)
        if m:
            if m.group(1) in ids: duplicate_ids.append(m.group(1))
            ids.add(m.group(1))
        m=re.search(r'(?:^|;)Parent=([^;]+)',attrs)
        if m: parents.extend(m.group(1).split(','))
proteins=next(DATA.glob('*.prot.fasta.gz'))
protein_count=0; protein_ids=[]
with gzip.open(proteins,'rt') as f:
    for line in f:
        if line.startswith('>'):
            protein_count+=1; protein_ids.append(line[1:].split()[0])
bed=next(DATA.glob('*.bed.gz')); bed_rows=0; bed_missing=set(); bed_bad=[]
with gzip.open(bed,'rt') as f:
    for line in f:
        if not line.strip() or line.startswith('#'): continue
        a=line.rstrip('\n').split('\t')
        if len(a)<3: continue
        bed_rows+=1; s=a[0]; start,end=int(a[1]),int(a[2])
        if s not in seqs: bed_missing.add(s)
        elif start<0 or end>seqs[s] or start>=end: bed_bad.append([s,start,end,seqs[s]])
result={"checked_at_local":time.strftime('%Y-%m-%dT%H:%M:%S%z'),"source":"NHGRI Capitella downloads, official files reported Last-Modified 2026-07-12; downloads page updated 2026-07-17","files":files,
"assembly":{"records":len(seqs),"total_bp":sum(seqs.values()),"lengths":seqs},
"gff3":{"feature_counts":dict(features),"unique_IDs":len(ids),"Parent_values":len(parents),"dangling_Parents":sum(x not in ids for x in parents),"unknown_seqids":sorted(missing_seq),"invalid_bounds_count":len(bad_bounds),"duplicate_ID_count":len(duplicate_ids),"examples_invalid_bounds":bad_bounds[:10]},
"protein_fasta":{"records":protein_count,"first_headers":protein_ids[:5]},
"repeat_bed":{"rows":bed_rows,"unknown_seqids":sorted(bed_missing),"invalid_bounds_count":len(bed_bad),"examples_invalid_bounds":bed_bad[:10]},
"interpretation":"Structural checks only. They do not establish biological completeness or independent annotation accuracy."}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(OUT)
print(json.dumps({"assembly":{"records":len(seqs),"total_bp":sum(seqs.values()),"largest_10":sorted(seqs.items(),key=lambda x:x[1],reverse=True)[:10]},
"gff3":{k:result['gff3'][k] for k in ('feature_counts','unique_IDs','Parent_values','dangling_Parents','unknown_seqids','invalid_bounds_count','duplicate_ID_count')},
"protein_fasta":{"records":protein_count},"repeat_bed":{"rows":bed_rows,"unknown_seqids":len(bed_missing),"invalid_bounds_count":len(bed_bad)}},ensure_ascii=False,indent=2))
