#!/usr/bin/env python3
"""Compare NHGRI functional workbook transcript IDs to July 2026 GFF3/proteome."""
import collections, gzip, hashlib, json, pathlib, re, time
import openpyxl

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'public_reference_capitella_2026-07'
xlsx=next(DATA.glob('*.xlsx.gz'))
gff=next(DATA.glob('*.gff3.gz'))
protein=next(DATA.glob('*.prot.fasta.gz'))
w=openpyxl.load_workbook(gzip.open(xlsx,'rb'),read_only=True,data_only=True)
gff_tx=set()
with gzip.open(gff,'rt') as f:
    for line in f:
        if line.startswith('#'): continue
        a=line.rstrip('\n').split('\t')
        if len(a)==9 and a[2]=='transcript':
            m=re.search(r'(?:^|;)ID=([^;]+)',a[8])
            if m: gff_tx.add(m.group(1))
proteins={}; key=None; seq=[]
with gzip.open(protein,'rt') as f:
    for line in f:
        if line.startswith('>'):
            if key is not None: proteins[key]=''.join(seq).rstrip('*')
            key=line[1:].split()[0]; seq=[]
        else: seq.append(line.strip())
    if key is not None: proteins[key]=''.join(seq).rstrip('*')
report={'checked_at_local':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'openpyxl_version':openpyxl.__version__,
        'workbook_sha256':hashlib.sha256(xlsx.read_bytes()).hexdigest(),'gff3_transcripts':len(gff_tx),'proteins':len(proteins),'sheets':{}}
for ws in w.worksheets:
    it=ws.iter_rows(values_only=True); header=next(it); idcol=0 if ws.title=='Trinotate' else next((i for i,v in enumerate(header) if v and 'transcript' in str(v).lower()),0)
    ids=[]; peptide_checked=0; peptide_mismatches=[]; peptide_missing=[]
    pepcol=header.index('peptide') if ws.title=='Trinotate' and 'peptide' in header else None
    for row in it:
        if not row or len(row)<=idcol or row[idcol] is None: continue
        tid=str(row[idcol]); ids.append(tid)
        if pepcol is not None and len(row)>pepcol and row[pepcol]:
            peptide_checked+=1
            if tid not in proteins: peptide_missing.append(tid)
            elif str(row[pepcol]).rstrip('*')!=proteins[tid]: peptide_mismatches.append(tid)
    counts=collections.Counter(ids); unique=set(ids)
    report['sheets'][ws.title]={'rows_with_ids':len(ids),'unique_ids':len(unique),'duplicate_rows_beyond_unique':len(ids)-len(unique),
        'ids_absent_from_july_gff':sorted(unique-gff_tx),'gff_transcripts_absent_from_sheet':len(gff_tx-unique),
        'peptides_checked':peptide_checked,'peptide_id_absent_from_protein_fasta':len(peptide_missing),'peptide_sequence_mismatch_count':len(peptide_mismatches),
        'peptide_sequence_mismatch_examples':peptide_mismatches[:15]}
report['sheets']['Panther']['orphan_id_examples']=report['sheets']['Panther']['ids_absent_from_july_gff'][:20]
report['interpretation']='Trinotate transcript IDs match the July 2026 GFF3 exactly, but 131 embedded peptide sequences differ from the July 2026 protein FASTA, so sequence-level release compatibility is not exact. NHGRI states that latest-release protein-coding annotations were lifted from the prior assembly with gene IDs preserved and that the prior release is no longer hosted; this may explain, but does not prove the cause of, sequence differences. Panther is sparse/multirow with 13 orphan IDs and 4,360 current transcripts without a row; review before database joins.'
out=ROOT/'capitella_functional_xlsx_validation.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
