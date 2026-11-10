#!/usr/bin/env python3
"""Run the isolated, pinned Colora example; never silently bypass a task lock."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["dry-run", "environments", "assembly", "scaffolding", "survey", "busco", "reports", "all"])
    parser.add_argument("--snakemake", default="/tmp/yzz-learning-snakemake-env/bin/snakemake")
    parser.add_argument("--conda-prefix", default="/tmp/yzz-learning-colora-envs")
    parser.add_argument("--cores", type=int, default=4)
    args = parser.parse_args()
    base = Path(__file__).resolve().parents[1]
    work = base / "work/colora"
    command = [args.snakemake, "--configfile", "config/local_test.yaml", "--snakefile",
               "workflow/Snakefile", "--cores", str(args.cores), "--resources", "mem_mb=48000",
               "--software-deployment-method", "conda", "--conda-frontend", "conda",
               "--conda-prefix", args.conda_prefix, "--printshellcmds", "--rerun-incomplete"]
    if args.stage == "dry-run":
        command.append("--dry-run")
    elif args.stage == "environments":
        command.append("--conda-create-envs-only")
    elif args.stage == "assembly":
        command.extend(["results/assemblies/asm_hap1.fa", "results/assemblies/asm_hap2.fa"])
    elif args.stage == "scaffolding":
        command.extend(["results/yahs_hap1/asm_yahs_scaffolds_final.fa",
                        "results/yahs_hap2/asm_yahs_scaffolds_final.fa"])
    elif args.stage == "survey":
        command.append("results/genomescope")
    elif args.stage == "busco":
        command.append("results/busco")
    elif args.stage == "reports":
        command.extend(["results/gfastats/mito.stats", "results/bandage/mito.jpg"])
    env = os.environ.copy()
    env.update(XDG_CACHE_HOME="/tmp/yzz-learning-cache",
               CONDA_PKGS_DIRS="/tmp/yzz-learning-conda-pkgs",
               QT_QPA_PLATFORM="offscreen")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = base / "logs" / f"colora_{args.stage}_{stamp}.log"
    record = dict(stage=args.stage, command=command, cwd=str(work), log=str(log),
                  started_utc=stamp, returncode=None,
                  runtime_settings={k: env[k] for k in
                                    ["XDG_CACHE_HOME", "CONDA_PKGS_DIRS", "QT_QPA_PLATFORM"]},
                  configuration="FCS-GX disabled for functional test; cross-strain Hi-C")
    manifest = log.with_suffix(".json")
    manifest.write_text(json.dumps(record, indent=2) + "\n")
    print(f"Running {args.stage}; log: {log}", flush=True)
    try:
        with log.open("w") as handle:
            result = subprocess.run(command, cwd=work, env=env, stdout=handle,
                                    stderr=subprocess.STDOUT)
        returncode = result.returncode
    except KeyboardInterrupt:
        returncode = 130
    record["returncode"] = returncode
    record["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest.write_text(json.dumps(record, indent=2) + "\n")
    print(f"Exit status {returncode}; inspect {log}")
    raise SystemExit(returncode)


if __name__ == "__main__":
    main()
