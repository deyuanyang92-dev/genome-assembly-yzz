#!/usr/bin/env python3
"""Targeted corrections and BAM-to-hints component checks after the initial run."""
import collections
import datetime
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import warnings
from Bio import SeqIO
from run_learning import digest

src, root = map(lambda x:Path(x).resolve(),sys.argv[1:3])
summarize_only = '--summarize-only' in sys.argv
out = root/'followup'
out.mkdir(exist_ok=summarize_only)
config = root/'execution/config'
inputs = root/'execution/inputs'
env = os.environ.copy()
env['AUGUSTUS_CONFIG_PATH'] = str(config)
env['PATH'] = str(src/'bin')+':'+str(src/'scripts')+':'+env['PATH']
commands = json.loads((out/'commands.json').read_text()) if summarize_only else []
def run(name, cmd):
    if summarize_only:
        assert any(c['name']==name and c['exit_code']==0 and c['command']==list(map(str,cmd)) for c in commands)
        return
    t0=time.monotonic()
    with (out/(name+'.out')).open('w') as stdout, (out/(name+'.err')).open('w') as stderr:
        result=subprocess.run(['/usr/bin/time','-f','%e\t%M','-o',str(out/(name+'.time.tsv')),
                               *map(str,cmd)],cwd=out,env=env,stdout=stdout,stderr=stderr,timeout=600)
    commands.append({'name':name,'command':list(map(str,cmd)),
                     'ended_at':datetime.datetime.now().astimezone().isoformat(),
                     'elapsed_seconds':round(time.monotonic()-t0,3),'exit_code':result.returncode})
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    print(name,result.returncode,flush=True)
    assert result.returncode==0

aug=src/'bin/augustus'
run('utr_explicit',[aug,'--species=human','--UTR=on','--print_utr=on','--gff3=on',
                    '--sample=0','--softmasking=0',inputs/'example.fa'])
run('new_species',['perl',src/'scripts/new_species.pl','--species=yzz_fly_included'])
run('etraining_included',[src/'bin/etraining','--species=yzz_fly_included',
                          '--stopCodonExcludedFromCDS=false',inputs/'genes.gb.train'])
for name,model in [('trained_holdout_included','yzz_fly_included'),('shipped_fly_holdout_included','fly')]:
    run(name,[aug,'--species='+model,'--stopCodonExcludedFromCDS=false','--UTR=off',
              '--sample=0','--softmasking=0',inputs/'genes.gb.test'])
terminal_codons={}
for part in ['train','test']:
    text=(inputs/('genes.gb.'+part)).read_text()
    # Normalize LOCUS headers in memory solely to let Biopython extract CDS.
    # Original AUGUSTUS input bytes are untouched and retained with SHA256.
    text=re.sub(r'^LOCUS[^\n]*',lambda m:'LOCUS       DEMO            '+
                f"{int(re.search(r'(\d+) bp',m[0])[1]):>11} bp    DNA     linear   UNK 01-JAN-1980",text,flags=re.M)
    with warnings.catch_warnings(record=True) as parser_warnings:
        records=list(SeqIO.parse(io.StringIO(text),'genbank'))
    terminal_codons[part]=dict(collections.Counter(str(f.extract(r.seq)[-3:]).upper()
                              for r in records for f in r.features if f.type=='CDS'))

bamrel='tests/short/auxprogs/bam2hints/test_files/test.s.sorted.bam'
refrel='tests/short/auxprogs/bam2hints/expected_results/test.intron.gff'
shutil.copy2(src/bamrel,out/'test.s.sorted.bam')
shutil.copy2(src/refrel,out/'expected.intron.gff')
run('bam2hints',[src/'bin/bam2hints','--in='+str(out/'test.s.sorted.bam'),
                 '--out='+str(out/'actual.intron.gff')])
assert (out/'actual.intron.gff').read_bytes()==(out/'expected.intron.gff').read_bytes()
chr2r=next(SeqIO.parse(src/'docs/tutorial/data/chr2R.fa','fasta'))
left,right=11860001,11900000
crop=chr2r[left-1:right]
crop.id='chr2R_window'
crop.description=''
SeqIO.write([crop],out/'rna_window.fa','fasta')
local_hints=[]
for line in (out/'actual.intron.gff').read_text().splitlines():
    f=line.split('\t')
    if f[0]=='chr2R' and int(f[3])>=left and int(f[4])<=right:
        f[0]=crop.id
        f[3],f[4]=str(int(f[3])-left+1),str(int(f[4])-left+1)
        local_hints.append('\t'.join(f))
(out/'rna_window.hints.gff').write_text('\n'.join(local_hints)+'\n')
assert local_hints
run('rna_local_prediction',[aug,'--species=fly','--gff3=on','--UTR=off','--sample=0',
                            '--softmasking=0','--hintsfile='+str(out/'rna_window.hints.gff'),
                            '--extrinsicCfgFile='+str(config/'extrinsic/extrinsic.M.RM.E.W.cfg'),
                            out/'rna_window.fa'])
run('blat2hints',['perl',src/'scripts/blat2hints.pl','--nomult',
                  '--in='+str(src/'docs/tutorial/data/est.psl'),
                  '--out='+str(out/'est.hints.gff')])

metrics={}
for name in ['trained_holdout_included','shipped_fly_holdout_included']:
    text=(out/(name+'.out')).read_text()
    metrics[name]={}
    for level in ['nucleotide','exon','gene']:
        line=next(s for s in text.splitlines() if s.startswith(level+' level'))
        values=[x.strip() for x in line.split('|')]
        metrics[name][level]={'sensitivity':float(values[-3]),'specificity_label_precision':float(values[-2])}
    assert 'Terminal exon doesn' not in (out/'etraining_included.err').read_text()
feature_counts=collections.Counter(line.split('\t')[2] for line in (out/'utr_explicit.out').read_text().splitlines()
                                   if not line.startswith('#') and len(line.split('\t'))==9)
assert any('utr' in x.lower() for x in feature_counts)
report={'terminal_codons':terminal_codons,'metrics':metrics,'utr_features':dict(feature_counts),
        'bam2hints_expected_bytes_match':True,'bam_input_source':bamrel,'bam_sha256':digest(out/'test.s.sorted.bam'),
        'rna_local_hints':len(local_hints),'rna_window_original_coordinates':[left,right],
        'rna_genome_source':'docs/tutorial/data/chr2R.fa','rna_genome_sha256':digest(src/'docs/tutorial/data/chr2R.fa'),
        'est_psl_source':'docs/tutorial/data/est.psl','est_psl_sha256':digest(src/'docs/tutorial/data/est.psl'),
        'training_accepted':True,'optimization_run':False,'target_species_validation':False,
        'corrections':['initial excluded-stop training retained as negative example; included-stop convention matches these inputs',
                       'initial UTR run had duplicate switches; explicit unique-switch run tested here'],
        'limitations':['official holdout loci disjoint by name; homology and training-history independence not established',
                       'RNA BAM and local genome are bundled fly examples, not target-species data',
                       'BLAT itself not run; conversion uses provided PSL',
                       'BAM upstream RNA mapping/QC not reproduced']}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
