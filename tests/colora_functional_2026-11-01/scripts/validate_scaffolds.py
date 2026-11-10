#!/usr/bin/env python3
"""Reconstruct YaHS scaffolds independently from AGP and input contigs."""
import json
from collections import defaultdict
from pathlib import Path
from validate_assemblies import fasta
from summarize_reference_mapping import union_length


def main():
    base = Path(__file__).resolve().parents[1]
    work = base / "work/colora/results"
    output = {}
    complement = str.maketrans("ACGTNRYKMSWBDHV", "TGCANYRMKSWVHDB")
    for hap in ["hap1", "hap2"]:
        contigs = fasta(work / f"assemblies/asm_{hap}.fa")
        scaffolds = fasta(work / f"yahs_{hap}/asm_yahs_scaffolds_final.fa")
        rebuilt = defaultdict(list)
        offsets = defaultdict(int)
        parts = defaultdict(int)
        used = defaultdict(list)
        gaps = 0
        with (work / f"yahs_{hap}/asm_yahs_scaffolds_final.agp").open() as handle:
            for line in handle:
                if line.startswith("#") or not line.strip():
                    continue
                f = line.rstrip().split("\t")
                assert len(f) == 9
                name, start, end, part, kind = f[:5]
                start, end, part = int(start), int(end), int(part)
                assert start == offsets[name] + 1 and part == parts[name] + 1
                span = end-start+1
                if kind in {"N", "U"}:
                    assert span == int(f[5])
                    sequence = "N" * span
                    gaps += span
                else:
                    assert kind == "W", f"Unsupported AGP component type {kind}"
                    key, first, last, orientation = f[5:]
                    first, last = int(first), int(last)
                    assert key in contigs and 1 <= first <= last <= len(contigs[key])
                    assert span == last-first+1 and orientation in {"+", "-"}
                    sequence = contigs[key][first-1:last]
                    if orientation == "-":
                        sequence = sequence.translate(complement)[::-1]
                    used[key].append((first-1, last))
                rebuilt[name].append(sequence)
                offsets[name], parts[name] = end, part
        assert {k: "".join(v) for k, v in rebuilt.items()} == scaffolds
        missing = sum(len(s)-union_length(used[k]) for k, s in contigs.items())
        duplicated = sum(sum(e-s for s, e in spans)-union_length(spans) for spans in used.values())
        output[hap] = dict(input_contigs=len(contigs), output_scaffolds=len(scaffolds),
                           total_bp=sum(map(len, scaffolds.values())), gap_bp=gaps,
                           unrepresented_input_bp=missing, reused_input_bp=duplicated,
                           agp_reconstruction_exact=True,
                           sequences_unchanged_ignoring_names=sorted(contigs.values()) == sorted(scaffolds.values()))
    result = dict(haplotypes=output, scope="AGP bookkeeping and sequence reconstruction. "
                  "Not independent confirmation of chromosome-scale structural correctness.")
    (base / "scaffold_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
