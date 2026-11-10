#!/usr/bin/env python3
"""Check assembly FASTA/GFA consistency and report sequence statistics."""
import argparse
import hashlib
import json
from pathlib import Path


def fasta(path):
    seqs = {}
    current = None
    with path.open() as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                current = line[1:].split()[0]
                if current in seqs:
                    raise ValueError(f"Duplicate FASTA ID: {current}")
                seqs[current] = []
            else:
                if current is None:
                    raise ValueError("Sequence before FASTA header")
                if set(line.upper()) - set("ACGTNRYKMSWBDHV"):
                    raise ValueError("Unexpected nucleotide character")
                seqs[current].append(line.upper())
    result = {k: "".join(v) for k, v in seqs.items()}
    if not result or any(not s for s in result.values()):
        raise ValueError("Empty assembly or sequence")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    work = args.base / "work/colora"
    report = {}
    for hap in ["hap1", "hap2"]:
        fa = work / f"results/assemblies/asm_{hap}.fa"
        gfa = work / f"results/hifiasm/asm.{hap}.gfa"
        seqs = fasta(fa)
        graph = {}
        with gfa.open() as handle:
            for line in handle:
                fields = line.rstrip().split("\t")
                if fields[0] == "S":
                    if fields[1] in graph or fields[2] == "*":
                        raise ValueError("Duplicate/missing graph sequence")
                    graph[fields[1]] = fields[2].upper()
        if graph != seqs:
            raise ValueError(f"FASTA/GFA mismatch: {hap}")
        sizes = sorted(map(len, seqs.values()), reverse=True)
        total = sum(sizes)
        cumulative = 0
        for count, size in enumerate(sizes, 1):
            cumulative += size
            if cumulative >= total / 2:
                n50, l50 = size, count
                break
        report[hap] = dict(sequences=len(seqs), total_bp=total, longest_bp=sizes[0],
                           N50=n50, L50=l50, N_bp=sum(s.count("N") for s in seqs.values()),
                           fasta_sha256=hashlib.sha256(fa.read_bytes()).hexdigest(),
                           gfa_sha256=hashlib.sha256(gfa.read_bytes()).hexdigest(),
                           gfa_fasta_consistent=True)
    result = dict(assemblies=report, scope="Sequence consistency and contiguity only. "
                  "No complete-genome, structural correctness, or phasing accuracy claim.")
    target = args.base / "assembly_validation.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
