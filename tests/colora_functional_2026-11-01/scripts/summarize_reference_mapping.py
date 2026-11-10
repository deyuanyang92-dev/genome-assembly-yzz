#!/usr/bin/env python3
"""Summarize nucleotide PAF using one best mapping per query (not QV)."""
import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path


def union_length(intervals):
    total = 0
    end = -1
    for start, stop in sorted(intervals):
        total += max(0, stop - max(start, end))
        end = max(end, stop)
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paf", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("output_prefix", type=Path)
    parser.add_argument("--mapq", type=int, default=20)
    args = parser.parse_args()
    lengths = {}
    opener = gzip.open if args.reference.suffix == ".gz" else open
    with opener(args.reference, "rt") as handle:
        for line in handle:
            if line.startswith(">"):
                name = line[1:].split()[0]
                lengths[name] = 0
            else:
                lengths[name] += len(line.strip())
    best = {}
    with args.paf.open() as handle:
        for line in handle:
            f = line.rstrip().split("\t")
            assert len(f) >= 12, "Invalid nucleotide PAF"
            rank = (int(f[9]), int(f[11]), int(f[3]) - int(f[2]))
            if f[0] not in best or rank > best[f[0]][0]:
                best[f[0]] = (rank, f)
    intervals = defaultdict(list)
    counts = defaultdict(int)
    matches = defaultdict(int)
    query_bp = defaultdict(int)
    for _, f in best.values():
        if int(f[11]) < args.mapq:
            continue
        name = f[5]
        assert int(f[6]) == lengths[name]
        intervals[name].append((int(f[7]), int(f[8])))
        counts[name] += 1
        matches[name] += int(f[9])
        query_bp[name] += int(f[3]) - int(f[2])
    rows = []
    for name, length in lengths.items():
        covered = union_length(intervals[name])
        rows.append(dict(reference=name, length=length, best_queries=counts[name],
                         covered_bp=covered, covered_fraction=covered / length,
                         matching_bases=matches[name], aligned_query_bp=query_bp[name]))
    with args.output_prefix.with_suffix(".tsv").open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    report = dict(mapped_query_names=len(best), retained_queries=sum(counts.values()),
                  mapq_threshold=args.mapq, references=rows,
                  interpretation="One best mapping per query; intervals count spans, including gaps. "
                  "Cross-strain reference, not exact truth; no QV, phased accuracy, "
                  "or complete-genome claim. Unmapped queries require FASTQ counts.")
    args.output_prefix.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "references"}, indent=2))


if __name__ == "__main__":
    main()
