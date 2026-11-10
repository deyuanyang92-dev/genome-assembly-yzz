#!/usr/bin/env python3
"""Small acceptance-semantics demonstration, not a production genome assessor.

Does not infer organism identity or execute BUSCO, Merqury, Flagger, or assembly.
Input numbers in scenarios are synthetic; status is per criterion, never a
single assembly-quality score. Fixed biological/profile choices remain external.
"""
import json, math, hashlib
from pathlib import Path
from datetime import datetime, timezone
B=Path(__file__).resolve().parent

def number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def metric(value, op, target, evidence_sha, assembly_sha, applicable=True, reason=None):
    if not applicable:
        return 'not_applicable' if reason else 'pending'
    if not evidence_sha or not assembly_sha or evidence_sha != assembly_sha:
        return 'pending'
    if not number(value) or not number(target):return 'pending'
    operations={'>':lambda a,b:a>b,'>=':lambda a,b:a>=b,'<':lambda a,b:a<b,'<=':lambda a,b:a<=b,'==':lambda a,b:a==b}
    if op not in operations:raise ValueError('Unrecognised comparison')
    return 'pass' if operations[op](value,target) else 'below_target'

def hifi_gate(route, usable_target_bases, g_min, g_max, identity, genome_definition):
    if route=='short_read_only':
        return dict(status='not_applicable',reason='HiFi-specific gate; assess short-read route separately')
    if route not in ['hifi','hifi_ont']:return dict(status='pending',reason='route unclassified')
    if identity!='same_target_individual' or genome_definition!='one_haploid_nuclear_set':
        return dict(status='pending',reason='identity or genome denominator unresolved')
    if not all(number(x) and x>0 for x in [usable_target_bases,g_min,g_max]) or g_min>g_max:
        return dict(status='pending',reason='invalid/missing effective bases or genome interval')
    lo=usable_target_bases/g_max;hi=usable_target_bases/g_min
    status='pass' if lo>=50 else 'below_target' if hi<50 else 'pending'
    return dict(status=status,coverage_min=lo,coverage_max=hi,threshold=50,operator='>=',authority='user_project_requirement')

def main():
    cases=[]
    def record(name,actual,want):
        got=actual['status'] if isinstance(actual,dict) else actual
        cases.append(dict(name=name,observed=actual,expected=want,passed=got==want))
    common=('hifi',50_000_000_000,900_000_000,1_000_000_000,'same_target_individual','one_haploid_nuclear_set')
    record('HiFi exactly50 conservative bound',hifi_gate(*common),'pass')
    record('G uncertainty straddles50',hifi_gate('hifi',45e9,800e6,1e9,*common[4:]),'pending')
    record('all plausible G below50',hifi_gate('hifi',39e9,800e6,1e9,*common[4:]),'below_target')
    record('unknown individual cannot pass',hifi_gate(*common[:4],'unknown',common[5]),'pending')
    record('short reads not rejected for missing HiFi',hifi_gate('short_read_only',None,None,None,'unknown','unknown'),'not_applicable')
    record('invalid interval',hifi_gate('hifi',50e9,1e9,800e6,*common[4:]),'pending')
    record('strict EBP kmer boundary90',metric(90,'>',90,'abc','abc'),'below_target')
    record('strict EBP T2T QV boundary60',metric(60,'>',60,'abc','abc'),'below_target')
    record('project QV50 inclusive',metric(50,'>=',50,'abc','abc'),'pass')
    record('stale final assembly hash',metric(99,'>=',98,'old','new'),'pending')
    record('unknown observed',metric(None,'>=',98,'abc','abc'),'pending')
    record('NaN observed',metric(float('nan'),'>=',98,'abc','abc'),'pending')
    record('absent evidence hash',metric(99,'>=',98,None,'abc'),'pending')
    record('not applicable without reason',metric(None,'>=',98,'abc','abc',False),'pending')
    record('not applicable with reason',metric(None,'>=',98,'abc','abc',False,'linear telomere criterion excluded by documented circular-chromosome biology'),'not_applicable')
    record('boolean is not metric',metric(True,'>=',0,'abc','abc'),'pending')
    out=dict(checked_at=datetime.now(timezone.utc).isoformat(),kind='synthetic_acceptance_semantics_only',biological_runs=0,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=cases,passed=all(c['passed'] for c in cases))
    (B/'acceptance_semantics_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(passed=out['passed'],cases=len(cases),biological_runs=0),ensure_ascii=False))
    if not out['passed']:raise SystemExit(1)
if __name__=='__main__':main()
