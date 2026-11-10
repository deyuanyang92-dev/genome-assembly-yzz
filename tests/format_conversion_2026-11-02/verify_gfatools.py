"""Small interface experiment, not a biological assembly benchmark."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = Path('/tmp/genome_gfatools_conversion_review')
BINARY = SOURCE / 'gfatools'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    out = HERE / 'gfatools'
    out.mkdir(exist_ok=True)
    valid = out / 'segments_with_path.gfa'
    valid.write_text('H\tVN:Z:1.0\nS\ta\tAACCGG\nS\tb\tGGTTAA\nL\ta\t+\tb\t+\t2M\nP\tjoined\ta+,b+\t2M\n')
    missing = out / 'missing_sequence.gfa'
    missing.write_text('H\tVN:Z:1.0\nS\tempty\t*\tLN:i:6\n')
    commands = []
    for input_path, name in [(valid, 'segments'), (missing, 'missing')]:
        cmd = [str(BINARY), 'gfa2fa', str(input_path)]
        run = subprocess.run(cmd, capture_output=True, timeout=15)
        (out / (name + '.fa')).write_bytes(run.stdout)
        (out / (name + '.stderr')).write_bytes(run.stderr)
        commands.append(dict(argv=cmd, returncode=run.returncode,
                             stdout=run.stdout.decode(), stderr=run.stderr.decode()))
    expected = '>a\nAACCGG\n>b\nGGTTAA\n'
    checks = {'sequence_bearing_segments_preserved': commands[0]['returncode'] == 0 and commands[0]['stdout'] == expected,
              'path_not_assembled': '>joined' not in commands[0]['stdout']}
    version = subprocess.run([str(BINARY), 'version'], capture_output=True, text=True, check=True)
    commit = subprocess.run(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
    records = dict(scope='Synthetic GFA conversion only; no hifiasm or Hi-C run',
                   commit=commit.stdout.strip(), version=version.stdout.strip(),
                   commands=commands, checks=checks,
                   missing_sequence_observation='Inspect returncode/stdout/stderr; never infer biological sequence from success',
                   sha256={str(p.relative_to(HERE)): digest(p) for p in out.iterdir() if p.is_file()},
                   source_sha256={name: digest(SOURCE / name) for name in ['main.c', 'gfa-io.c', 'README.md']},
                   binary_sha256=digest(BINARY))
    (out / 'results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(records, ensure_ascii=False, indent=2))
    assert all(checks.values()), checks

if __name__ == '__main__':
    main()
