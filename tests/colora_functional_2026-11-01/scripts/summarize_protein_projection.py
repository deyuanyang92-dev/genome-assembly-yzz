#!/usr/bin/env python3
"""Export protein alignment evidence; records are not de novo gene counts."""
import argparse
import csv
import gzip
import json
from collections import Counter
from pathlib import Path
from validate_assemblies import fasta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gff", type=Path)
    parser.add_argument("genome", type=Path)
    parser.add_argument("proteins", type=Path)
    parser.add_argument("output_prefix", type=Path)
    args = parser.parse_args()
    genome = fasta(args.genome)
    proteins = {}
    with gzip.open(args.proteins, "rt") as handle:
        for line in handle:
            if line.startswith(">"):
                current = line[1:].split()[0]
                proteins[current] = 0
            else:
                proteins[current] += len(line.strip())
    transcripts = {}
    cds_counts = Counter()
    parents = []
    with args.gff.open() as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.rstrip().split("\t")
            assert len(fields) == 9
            name, _, kind, start, end, _, strand, phase, attributes = fields
            assert name in genome and 1 <= int(start) <= int(end) <= len(genome[name])
            attrs = dict(a.split("=", 1) for a in attributes.split(";") if "=" in a)
            if kind == "mRNA":
                protein, qstart, qend = attrs["Target"].split()
                assert protein in proteins
                assert 1 <= int(qstart) <= int(qend) <= proteins[protein]
                key = attrs["ID"]
                assert key not in transcripts
                transcripts[key] = dict(alignment_id=key, contig=name, start=int(start),
                                        end=int(end), strand=strand, protein=protein,
                                        protein_length=proteins[protein],
                                        query_coverage=(int(qend)-int(qstart)+1)/proteins[protein],
                                        identity=float(attrs.get("Identity", "nan")),
                                        rank=int(attrs.get("Rank", 0)))
            elif kind == "CDS":
                assert phase in {"0", "1", "2"}
                cds_counts[attrs["Parent"]] += 1
                parents.append(attrs["Parent"])
    assert transcripts and all(p in transcripts for p in parents)
    rows = list(transcripts.values())
    for row in rows:
        row["CDS_segments"] = cds_counts[row["alignment_id"]]
    strong = [r for r in rows if r["query_coverage"] >= .9 and r["identity"] >= .9]
    with args.output_prefix.with_suffix(".tsv").open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    report = dict(input_reference_proteins=len(proteins), alignment_records=len(rows),
                  distinct_proteins_aligned=len({r["protein"] for r in rows}),
                  records_query_coverage_ge90_identity_ge90=len(strong),
                  distinct_proteins_query_coverage_ge90_identity_ge90=len({r["protein"] for r in strong}),
                  CDS_segments=sum(cds_counts.values()), coordinates_and_parent_links="passed",
                  by_contig=dict(Counter(r["contig"] for r in rows)),
                  interpretation="Reference-protein evidence projection. Multiple hits can represent "
                  "alleles, paralogs, or fragmented matches; no final gene count, complete "
                  "gene catalog, annotation accuracy, or true gene absence claimed.")
    args.output_prefix.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
