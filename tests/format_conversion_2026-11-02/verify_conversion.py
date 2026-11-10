"""Synthetic interface evidence, not a HiFi sample or assembly benchmark."""
from pathlib import Path
import subprocess, json, gzip, hashlib
base = Path(__file__).resolve().parent
samtools = Path('/root/miniconda3/envs/mitoz3.6/bin/samtools')
rows = [
 ['read_u',4,'*',0,0,'*','*',0,0,'ACGTA','IIIII','rq:f:0.999','np:i:8'],
 ['read_reverse',16,'chr1',1,60,'5M','*',0,0,'GACTT','EDCBA'],
 ['read_reverse',2048,'chr1',30,60,'5M','*',0,0,'GACTT','EDCBA'],
 ['read_hardclip',0,'chr1',10,60,'2H5M','*',0,0,'ACGTA','FFFFF'],
 ['read_missingqual',4,'*',0,0,'*','*',0,0,'ACGTA','*']]
sam = base/'synthetic.sam'
sam.write_text('@HD\tVN:1.6\tSO:queryname\n@SQ\tSN:chr1\tLN:100\n'+'\n'.join('\t'.join(map(str,r)) for r in rows)+'\n')
commands = []
def run(args):
 r=subprocess.run(args,capture_output=True)
 commands.append(dict(argv=list(map(str,args)),returncode=r.returncode,stderr=r.stderr.decode()))
 if r.returncode: raise RuntimeError(r.stderr.decode())
 return r.stdout
version=run([str(samtools),'--version']).decode().splitlines()[0]
fastq=run([str(samtools),'fastq','-n','-T','rq,np',str(sam)])
(base/'synthetic.fastq').write_bytes(fastq)
lines=fastq.decode().splitlines()
records={lines[i][1:].split()[0]:(lines[i],lines[i+1],lines[i+3]) for i in range(0,len(lines),4)}
checks={
 'secondary_supplementary_not_exported_twice': len(records)==4 and len(lines)==16,
 'reverse_complement_restored': records['read_reverse'][1]=='AAGTC',
 'reverse_quality_restored': records['read_reverse'][2]=='ABCDE',
 'requested_tags_in_header': 'rq:f:' in records['read_u'][0] and 'np:i:8' in records['read_u'][0],
 'hard_clipped_bases_not_reconstructed': len(records['read_hardclip'][1])==5,
 'observed_missing_quality_placeholder_not_original': records['read_missingqual'][2]=='B'*5,
}
# Test BAM input and samtools own .gz output on this installed version.
run([str(samtools),'view','-b','-o',str(base/'synthetic.bam'),str(sam)])
run([str(samtools),'fastq','-n','-T','rq,np','-0',str(base/'synthetic.fastq.gz'),str(base/'synthetic.bam')])
checks['bam_to_gz_content_matches_sam_stdout']=gzip.open(base/'synthetic.fastq.gz','rb').read()==fastq
result={'scope':'samtools 1.21 synthetic SAM/BAM export only; no actual HiFi, no CCS, no bam2fastq/gfatools/hifiasm execution',
 'version':version,'binary':str(samtools),'commands':commands,'checks':checks,'passed':all(checks.values())}
result['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [sam,base/'synthetic.bam',base/'synthetic.fastq',base/'synthetic.fastq.gz']}
(base/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':version,'checks':checks,'passed':result['passed']},indent=2))
raise SystemExit(0 if result['passed'] else 1)
