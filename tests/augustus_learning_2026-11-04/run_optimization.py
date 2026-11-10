#!/usr/bin/env python3
"""Bounded optimization demonstration: ONE meta parameter, two folds, one round."""
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from run_learning import digest

src, root = map(lambda x:Path(x).resolve(),sys.argv[1:])
out=root/'optimization'
out.mkdir()
config=root/'execution/config'
model=config/'species/yzz_fly_included'
shutil.copytree(model,out/'model_before')
metapars=out/'one_parameter.cfg'
metapars.write_text('/Constant/dss_end "2" "3"\n')
env=os.environ.copy()
env['AUGUSTUS_CONFIG_PATH']=str(config)
env['PATH']=str(src/'bin')+':'+str(src/'scripts')+':'+env['PATH']
commands=[]
def run(name,cmd):
    start=datetime.datetime.now().astimezone().isoformat()
    t0=time.monotonic()
    with (out/(name+'.out')).open('w') as stdout,(out/(name+'.err')).open('w') as stderr:
        p=subprocess.run(['/usr/bin/time','-f','%e\t%M','-o',str(out/(name+'.time.tsv')),*map(str,cmd)],
                         env=env,cwd=out,stdout=stdout,stderr=stderr,timeout=900)
    commands.append({'name':name,'command':list(map(str,cmd)),'started_at':start,
                     'elapsed_seconds':round(time.monotonic()-t0,3),'exit_code':p.returncode})
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    print(name,p.returncode,flush=True)
    assert p.returncode==0
run('optimize',['perl',src/'scripts/optimize_augustus.pl','--species=yzz_fly_included',
                '--metapars='+str(metapars),'--rounds=1','--kfold=2','--cpus=1','--pstep=2',
                root/'execution/inputs/genes.gb.train'])
run('retrain',[src/'bin/etraining','--species=yzz_fly_included','--stopCodonExcludedFromCDS=false',
               root/'execution/inputs/genes.gb.train'])
run('holdout',[src/'bin/augustus','--species=yzz_fly_included','--stopCodonExcludedFromCDS=false',
               '--UTR=off','--softmasking=0','--sample=0',root/'execution/inputs/genes.gb.test'])
shutil.copytree(model,out/'model_after')
metrics={}
for level in ['nucleotide','exon','gene']:
    line=next(s for s in (out/'holdout.out').read_text().splitlines() if s.startswith(level+' level'))
    values=[x.strip() for x in line.split('|')]
    metrics[level]={'sensitivity':float(values[-3]),'specificity_label_precision':float(values[-2])}
parameter_values={}
for stage in ['before','after']:
    cfg=(out/('model_'+stage)/'yzz_fly_included_parameters.cfg').read_text()
    parameter_values[stage]=int(re.search(r'^/Constant/dss_end\s+(\d+)',cfg,re.M)[1])
assert not (out/'retrain.err').read_text().strip()
(out/'validation.json').write_text(json.dumps({'optimization':'one meta parameter; 2-fold; 1 round; not full default optimization',
    'metapars_sha256':digest(metapars),'heldout_file_used_for_optimization':False,
    'retrained_on_all_392_training_loci':True,'parameter_values':parameter_values,
    'holdout_metrics':metrics,'target_species_validation':False},indent=2)+'\n')
