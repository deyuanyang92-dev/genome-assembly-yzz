"""Prepare an isolated upstream workflow copy; never writes to the source study."""
from pathlib import Path
import json, shutil, hashlib, subprocess, gzip, time
import yaml

BASE = Path(__file__).resolve().parents[1]
SRC = Path('/mnt/p/yzz-全基因组工作流程/genome-assembly-yzz/pipelines/LiaOb21_colora')
OUT = BASE / 'work/colora'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (BASE/'logs').mkdir(exist_ok=True)
    for name in ['workflow', 'config', 'scripts']:
        target = OUT/name
        if not target.exists():
            shutil.copytree(SRC/name, target)
    provenance = []
    for kind in ['hifi', 'ont']:
        raw = SRC/f'test_data/raw_{kind}'
        parts = sorted(raw.glob('*a?.fastq.gz'))
        if not parts:
            raise RuntimeError(f'No split input found: {raw}')
        target = OUT/f'test_data/raw_{kind}'
        target.mkdir(parents=True, exist_ok=True)
        merged = target/parts[0].name.replace('aa.fastq.gz', '.fastq.gz')
        if not merged.exists():
            with merged.open('wb') as dest:
                for part in parts:
                    with part.open('rb') as src:
                        shutil.copyfileobj(src, dest, 4*1024*1024)
        count = bases = 0
        lengths = []
        # Reading the complete gzip stream also verifies concatenation and CRC.
        with gzip.open(merged, 'rt') as f:
            while True:
                header = f.readline()
                if not header:
                    break
                seq, plus, qual = f.readline().strip(), f.readline(), f.readline().strip()
                if not header.startswith('@') or not plus.startswith('+') or len(seq) != len(qual):
                    raise RuntimeError(f'Invalid FASTQ record {count+1}: {merged}')
                count += 1; bases += len(seq); lengths.append(len(seq))
        provenance.append(dict(kind=kind, source_parts=[dict(path=str(p), sha256=sha(p)) for p in parts], merged_path=str(merged.relative_to(BASE)), sha256=sha(merged), reads=count, bases=bases, min_length=min(lengths), max_length=max(lengths)))
    hic = OUT/'test_data/raw_hic'
    hic.mkdir(parents=True, exist_ok=True)
    for source in sorted((SRC/'test_data/raw_hic').glob('*.fastq.gz')):
        target = hic/source.name
        if not target.exists():
            # Explicit individual read-file links; no writable directory link.
            target.symlink_to(source)
        provenance.append(dict(kind='hic', source=str(source), sha256=sha(source), linked_read_only_by_policy=True))
    config = yaml.safe_load((SRC/'config/config_test.yaml').read_text())
    config['include_fcsgx'] = False
    config['busco']['optional_params']['--offline'] = True
    local_config = OUT/'config/local_test.yaml'
    if not local_config.exists():
        local_config.write_text(yaml.safe_dump(config, sort_keys=False))
    revision = subprocess.run(['git','-C',str(SRC),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
    manifest = dict(upstream='https://github.com/LiaOb21/colora', revision=revision, inputs=provenance, config_changes={'include_fcsgx':{'upstream':True,'local':False,'reason':'Optional contamination screen omitted from this functional test; no production decontamination claim.'}}, biological_scope='Different yeast strains for HiFi/ONT and Hi-C. Functional test only.', created_unix=time.time())
    manifest['config_changes']['busco.optional_params.--offline'] = dict(upstream=None, local=True, reason='Use official-checksum-verified local lineage without network update checks.')
    (BASE/'colora_input_manifest.json').write_text(json.dumps(manifest, indent=2))
    progress = BASE/'progress.json'
    if not progress.exists():
        progress.write_text(json.dumps(dict(goal_status='active', stages={'source_review':'in_progress','input_preparation':'complete','dag':'pending','assembly':'pending','scaffolding':'pending','quality_evaluation':'pending','annotation':'pending','comparison_genomics':'pending'}, complete_upstream_workflows_run=0),indent=2))
    print(json.dumps(manifest,indent=2))

if __name__ == '__main__':
    main()
