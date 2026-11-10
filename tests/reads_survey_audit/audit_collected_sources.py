"""Offline behavioral audit of the collected LRGE paper wrapper, using mocked tools.
Does not execute KMC, GenomeScope, or biological input. Only owned temporary paths.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'pipelines/mbhall88_lrge/paper/workflow/scripts/genomescope.py'
spec = importlib.util.spec_from_file_location('collected_gscope', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
results = []
for retain in (False, True):
    with tempfile.TemporaryDirectory(prefix='yzz-survey-audit-') as owned:
        base = Path(owned)
        output = base / 'wrapper_tmp'
        commands = []
        def fake_run(cmd, **kwargs):
            commands.append(cmd)
            if cmd[0] == 'genomescope2':
                Path(cmd[cmd.index('-o') + 1], 'summary.txt').write_text('mock result\n')
            return subprocess.CompletedProcess(cmd, 0, b'', b'')
        argv = [str(SOURCE), str(base/'sample.reads.fq'), '--tmp', str(output), '--log', str(base/'run.log')]
        if retain:
            argv.append('--no-cleanup')
        with patch.object(sys, 'argv', argv), patch.object(module.subprocess, 'run', fake_run):
            module.main()
        exists = (output / 'summary.txt').exists()
        assert exists == retain
        assert '-ci2' in commands[0] and '-cs255' in commands[0]
        assert commands[2][commands[2].index('-p')+1] == '1'
        results.append({'no_cleanup': retain, 'final_summary_retained': exists,
                        'upstream_default_ploidy': 1, 'upstream_default_counter_cap': 255})
report = {'date': '2026-11-01', 'kind': 'mocked_wrapper_behavior_only',
          'biological_runs': 0, 'cases_passed': len(results), 'cases': results,
          'finding': 'Default cleanup deletes GenomeScope final output placed in --tmp; --no-cleanup retains it.'}
(ROOT/'tests/reads_survey_audit/validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
