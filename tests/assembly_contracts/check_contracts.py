#!/usr/bin/env python3
"""Exercise scaffold invariants with valid and deliberately corrupted tiny fixtures.

This tests the existing strict lossless-scaffolding verifier, not a general AGP parser
or assembly algorithm. No external bioinformatics programs are invoked.
"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('learning_verifier', HERE.parent / 'learning_smoke/verify.py')
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)

CONTIGS = {'a': 'ACGTR', 'b': 'CCGTA'}
ROWS = [
    'chr1\t1\t5\t1\tW\ta\t1\t5\t+',
    'chr1\t6\t7\t2\tN\t2\tscaffold\tyes\tproximity_ligation',
    'chr1\t8\t12\t3\tW\tb\t1\t5\t-',
]
SCAFFOLDS = {'chr1': 'ACGTRNNTACGG'}


class ScaffoldContracts(unittest.TestCase):
    def check(self, rows=None, scaffolds=None):
        with tempfile.TemporaryDirectory(prefix='assembly-contract-') as tmp:
            path = Path(tmp) / 'assembly.agp'
            path.write_text('\n'.join(ROWS if rows is None else rows) + '\n')
            VERIFIER.check_agp(path, CONTIGS, SCAFFOLDS if scaffolds is None else scaffolds)

    def test_valid_reverse_and_gap(self):
        self.check()

    def test_valid_iupac_reverse_complement(self):
        self.check([
            'chr1\t1\t5\t1\tW\ta\t1\t5\t-',
            'chr2\t1\t5\t1\tW\tb\t1\t5\t+',
        ], {'chr1': 'YACGT', 'chr2': 'CCGTA'})

    def test_valid_split_component(self):
        self.check([
            'chr1\t1\t2\t1\tW\ta\t1\t2\t+',
            'chr1\t3\t5\t2\tW\ta\t3\t5\t+',
            'chr2\t1\t5\t1\tW\tb\t1\t5\t+',
        ], {'chr1': 'ACGTR', 'chr2': 'CCGTA'})

    def test_wrong_orientation(self):
        with self.assertRaisesRegex(RuntimeError, 'FASTA differs'):
            self.check(ROWS[:2] + [ROWS[2][:-1] + '+'])

    def test_object_coordinate_jump(self):
        with self.assertRaisesRegex(RuntimeError, 'object interval'):
            self.check(ROWS[:2] + [ROWS[2].replace('\t8\t12\t', '\t9\t13\t')])

    def test_part_number_jump(self):
        with self.assertRaisesRegex(RuntimeError, 'part number'):
            self.check(ROWS[:2] + [ROWS[2].replace('\t3\tW\t', '\t4\tW\t')])

    def test_gap_length_disagrees(self):
        with self.assertRaisesRegex(RuntimeError, 'gap length mismatch'):
            self.check([ROWS[0], ROWS[1].replace('\tN\t2\t', '\tN\t3\t'), ROWS[2]])

    def test_component_bounds(self):
        with self.assertRaisesRegex(RuntimeError, 'out of range'):
            self.check(ROWS[:2] + [ROWS[2].replace('\tb\t1\t5\t', '\tb\t2\t6\t')])

    def test_component_missing_even_if_fasta_matches(self):
        with self.assertRaisesRegex(RuntimeError, 'Missing input component'):
            self.check([ROWS[0]], {'chr1': 'ACGTR'})

    def test_component_base_lost_even_if_fasta_matches(self):
        with self.assertRaisesRegex(RuntimeError, 'Incomplete component'):
            self.check([
                'chr1\t1\t4\t1\tW\ta\t1\t4\t+',
                'chr2\t1\t5\t1\tW\tb\t1\t5\t+',
            ], {'chr1': 'ACGT', 'chr2': 'CCGTA'})

    def test_component_reused_even_if_fasta_matches(self):
        with self.assertRaisesRegex(RuntimeError, 'lost or reused'):
            self.check(ROWS + ['chr2\t1\t5\t1\tW\ta\t1\t5\t+'],
                       dict(SCAFFOLDS, chr2='ACGTR'))

    def test_scaffold_sequence_changed(self):
        with self.assertRaisesRegex(RuntimeError, 'FASTA differs'):
            self.check(scaffolds={'chr1': 'ACGTRNNTACGA'})

    def test_unknown_component(self):
        with self.assertRaisesRegex(RuntimeError, 'Unexpected AGP component'):
            self.check(ROWS[:2] + [ROWS[2].replace('\tb\t', '\tother\t')])

    def test_duplicate_fasta_identifier(self):
        with tempfile.TemporaryDirectory(prefix='assembly-contract-') as tmp:
            path = Path(tmp) / 'duplicate.fa'
            path.write_text('>a first\nACGT\n>a second\nTGCA\n')
            with self.assertRaisesRegex(RuntimeError, 'Duplicate FASTA identifier'):
                VERIFIER.read_fasta(path)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ScaffoldContracts))
    report = {
        'recorded': '2026-11-01', 'tests_run': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors),
        'passed': result.wasSuccessful(),
        'scope': 'Strict W-component AGP lossless-scaffolding invariants; synthetic fixtures only.',
        'limits': [
            'Not a full AGP 2.1 validator.',
            'Intentional filtering, polishing and gap filling require an explicit change ledger instead of full input preservation.',
            'No real Hi-C phasing, scaffolding accuracy or manual curation tested.',
        ],
    }
    (HERE / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
