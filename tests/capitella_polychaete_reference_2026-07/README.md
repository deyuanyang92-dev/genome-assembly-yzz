# Capitella July 2026 reference test

This is a dated, reproducible test of the official NHGRI Capitella teleta bundle, downloaded 2026-11-02. Official landing pages: https://research.nhgri.nih.gov/capitella/downloads.html and https://research.nhgri.nih.gov/capitella/about.html. The site reported its update on 2026-07-17; file server Last-Modified was 2026-07-12.

## What is here

- `public_reference_capitella_2026-07/`: five original compressed genome, GFF3, protein, repeat BED and functional XLSX files.
- `capitella_reference_validation.json`: file SHA256/size plus assembly, GFF3, protein and BED structural checks.
- `capitella_functional_xlsx_validation.json`: workbook IDs, embedded protein sequence and Panther row checks against the current GFF3/proteome.
- `capitella_miniprot_summary.json`, `capitella_miniprot.log`, `capitella_miniprot_alignment.gff.gz`: same-release protein mapping summary and output.
- `08_Capitella最新多毛类参考基因组实操.md`: Chinese findings, caveats and recommended database handling.
- `scripts/validate_capitella_reference.py`, `scripts/validate_capitella_functional_xlsx.py`: reproducible validation scripts.
- `software_learning_ledger.tsv`: versions/times/evidence and what can be skipped on an exact rerun.

## Key observations

The genome is 277,327,828 bp in 452 records; the ten largest are named chrom_1 through chrom_10 and contain 92.84% of assembled bases. GFF3 coordinates and IDs, protein/transcript counts and repeat BED bounds passed structural checks. Miniprot 0.18-r281 aligned at least one model for 34,665/34,669 same-release proteins; this is internal consistency evidence, not independent assembly completeness.

The Trinotate sheet has all 34,669 transcript IDs matching GFF3, but 131 embedded peptide sequences differ from the supplied current protein FASTA. NHGRI says the new release lifted protein-coding annotations from the previous assembly while preserving gene IDs, and the previous release is no longer hosted; that could explain the peptide discrepancies but does not prove their cause. Panther is sparse and multirow: 13 transcript IDs are absent from current GFF3, and 4,360 current transcript IDs have no Panther row. Preserve source/version and quarantine mismatches when building a database; do not treat missing Panther rows as negative functional evidence. See https://research.nhgri.nih.gov/capitella/about.html.

## Reproduce

Run `python3 scripts/validate_capitella_reference.py` and `python3 scripts/validate_capitella_functional_xlsx.py` from this directory. The second script used Python 3.13.11 and openpyxl 3.1.5. The miniprot command was `miniprot -t 4 --gff genome.mpi proteins.fa` with miniprot 0.18-r281; decompressed FASTAs and index were temporary and are not included.

Paper: Davies et al. 2026, https://academic.oup.com/gbe/article/18/3/evag041/8495731. The paper’s assembly metrics refer to its study release; do not assume they are the July 2026 download release’s independent QC results.
