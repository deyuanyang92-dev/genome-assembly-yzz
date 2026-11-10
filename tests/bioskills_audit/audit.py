#!/usr/bin/env python3
"""Inspect pinned templates without installing skills or running bioinformatics tools."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BIO = ROOT / 'pipelines/GPTomics_bioSkills'


def read(path):
    return path.read_text(encoding='utf-8')


def bash_value(expression):
    # Expressions below are fixed literals, never shell text obtained from a repository.
    return subprocess.check_output(
        ['bash', '-c', 'ENZYME=""; printf "%s" ' + expression], text=True
    )


def main():
    selected = [
        BIO / 'genome-assembly/hifi-assembly/examples/hifi_assembly_workflow.sh',
        BIO / 'genome-assembly/scaffolding/examples/yahs_scaffolding.sh',
        BIO / 'workflows/genome-assembly-pipeline/examples/bacterial_assembly.sh',
    ]
    syntax = []
    for path in selected:
        result = subprocess.run(['bash', '-n', str(path)], capture_output=True, text=True)
        syntax.append({'path': str(path.relative_to(ROOT)), 'exit_code': result.returncode,
                       'stderr': result.stderr})
    hifi = read(selected[0])
    scaffold = read(selected[1])
    manual = read(ROOT / 'pipelines/lh3_hifiasm/hifiasm.1')
    yahs = read(ROOT / 'pipelines/c-zhou_yahs/README.md')
    hic_branch = hifi.split('elif [ -n "${HIC_R1}" ]', 1)[1].split('\nelse', 1)[0]
    observed = {
        'hic_example_uses_bp_prefix': 'PREFIX="${SAMPLE}.bp"' in hic_branch,
        'pinned_hifiasm_manual_has_hic_hap1': '.hic.hap1.p_ctg.gfa' in manual,
        'omnic_empty_enzyme_with_colon_default': bash_value('"${ENZYME:-GATC}"'),
        'omnic_empty_enzyme_with_unset_only_default': bash_value('"${ENZYME-GATC}"'),
        'scaffolding_example_has_colon_default': 'ENZYME=${ENZYME:-GATC}' in scaffold,
        'scaffolding_example_indexes_bam_given_to_yahs': 'samtools index "${OUT}_hic.bam"' in scaffold,
        'yahs_readme_says_non_name_sort_suppresses_mapq':
            'mapping quality filtering is suppressed' in yahs,
        'bacterial_example_allows_screen_failure':
            '|| echo "FCS-GX needs' in read(selected[2]),
    }
    catalog = json.loads(read(ROOT / 'notes/sources/bioskills_catalog.json'))
    result = {
        'recorded': '2026-11-01',
        'bioskills_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=BIO, text=True).strip(),
        'scope': 'Static source comparisons, Bash syntax and fixed parameter-expansion experiment only; no biological pipeline run.',
        'catalog_counts': {'skills': catalog['skill_count'], 'categories': catalog['category_count']},
        'example_shell_syntax': syntax,
        'observed_template_issues': observed,
    }
    expected = [all(x['exit_code'] == 0 for x in syntax),
                catalog['skill_count'] == 561, catalog['category_count'] == 63,
                observed['hic_example_uses_bp_prefix'],
                observed['pinned_hifiasm_manual_has_hic_hap1'],
                observed['omnic_empty_enzyme_with_colon_default'] == 'GATC',
                observed['omnic_empty_enzyme_with_unset_only_default'] == '',
                observed['scaffolding_example_has_colon_default'],
                observed['scaffolding_example_indexes_bam_given_to_yahs'],
                observed['yahs_readme_says_non_name_sort_suppresses_mapq'],
                observed['bacterial_example_allows_screen_failure']]
    result['expected_observations_confirmed'] = all(expected)
    (Path(__file__).parent / 'content_checks.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if all(expected) else 1


if __name__ == '__main__':
    raise SystemExit(main())
