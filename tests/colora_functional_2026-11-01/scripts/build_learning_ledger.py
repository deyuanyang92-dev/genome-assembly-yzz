#!/usr/bin/env python3
"""Build a dated, evidence-linked software learning ledger from recorded runs."""
import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")

def main():
    manifest = json.loads((ROOT / "environment_locks/manifest.json").read_text())
    envmap = {}
    for env in manifest["environments"]:
        for p in env["packages"]:
            envmap.setdefault(p["name"], set()).add(p["version"])
    rows = []
    def add(name, version, evidence, status, scope, skip):
        rows.append({"software": name, "version": version, "recorded_at": NOW,
                     "evidence": evidence, "learning_status": status,
                     "scope_learned": scope, "safe_to_skip_next_time": skip})

    add("Snakemake", "8.30.0", "snakemake_environment.txt; logs/colora_dryrun.log; logs/colora_all_*.json",
        "installed_and_workflow_run", "Colora DAG, isolated conda envs, rerun-incomplete and staged targets on this Linux test copy",
        "Skip basic setup for this exact version/config; recheck CLI changes or changed Colora commit.")
    actual = {"hifiasm": "0.25.0-r726", "fastp": "1.3.1", "minimap2": "2.31-r1302",
              "miniprot": "0.18-r281", "bwa": "0.7.19-r1273", "picard": "2.26.11",
              "yahs": "1.2.2"}
    scopes = {
      "hifiasm": ("logs/colora_assembly_run.log; assembly_validation.json", "HiFi assembly and GFA/FASTA correspondence on the provided test subset"),
      "fastp": ("fastp_summary.json; logs/colora_scaffolding_*.log", "Hi-C read filtering and read-count interpretation in the Colora test"),
      "minimap2": ("native_tool_versions.json; logs/hifi_to_reference.log; logs/hap1_to_reference.log", "read/assembly mapping to the chosen S288C chromosomes and coverage-bias audit"),
      "miniprot": ("native_tool_versions.json; miniprot_native_validation.json; hap1_nuclear_protein_evidence.json", "native example validation and reference-protein projection; not a full annotation"),
      "bwa": ("logs/colora_scaffolding_20261101T092616Z.log", "Arima Hi-C alignment stage in test workflow"),
      "picard": ("logs/colora_scaffolding_20261101T092616Z.log", "duplicate marking stage; not a biological duplicate-rate conclusion"),
      "yahs": ("logs/colora_scaffolding_20261101T092616Z.log; scaffold_validation.json", "Hi-C scaffolding and AGP-to-FASTA validation")}
    for name, ver in actual.items():
        ev, scope = scopes[name]
        add(name, ver, ev, "executed_and_reviewed", scope,
            "Skip this exact command/version walkthrough; recheck on new data, assembly mode, reference, or version.")
    # Conda packages with recorded versions; successful runs are marked when logs/results prove use.
    run_proof = {"busco": "work/colora/results/busco/*/short_summary.specific*.txt", "kmc": "work/colora/results/genomescope/summary.txt",
                 "genomescope2": "work/colora/results/genomescope/summary.txt", "oatk": "work/colora/results/oatk/oatk.asm.mito.ctg.fasta",
                 "quast": "work/colora/results/quast/report.tsv (ran separately at ASCII output path due QUAST Unicode-path restriction)", "nanoplot": "work/colora/results/nanoplot/NanoPlot-report.html",
                 "bandage": "work/colora/results/bandage/mito.jpg", "gfastats": "work/colora/results/gfastats/mito.stats"}
    for name in ("busco", "kmc", "genomescope2", "oatk", "quast", "nanoplot", "bandage", "gfastats"):
        versions = ",".join(sorted(envmap.get(name, []))) or "see environment_locks/manifest.json"
        proof = run_proof[name]
        status = "executed_successfully; all-target DAG exit 0" if name != "quast" else "executed_successfully_separately; all-target DAG exit 0 after output staged"
        add(name, versions, proof, status,
            "Version pinned by explicit conda package URL/build; scope/status will be finalized from the all-target log.",
            "Skip installation/tutorial repetition for this exact build only; inspect all-target result and rerun on changed inputs/version.")
    reviewed = [
      ("Colora", "commit d6569edaff8da51739688b246dda2dfb2da13d7a", "upstream source, workflow rules, and paper; work/colora; notes/03_原始论文阅读与版本更新.md", "source_reviewed_and_functional_test_in_progress", "Only this pinned workflow revision and its tested config; re-audit when commit/config changes."),
      ("RAGNAROK", "source commit recorded in ragnarok_source_review.json", "ragnarok_source_review.json; notes/01_RAGNAROK模块补充核查.md", "static_source_review", "Skip exact modules already inspected; do not treat as end-to-end execution."),
      ("RepeatMasker", "official docs checked 2026-11-01; runtime version not installed", "notes/02_补充方法选择与边界.md", "documentation_review_only", "Skip docs already logged; actual install/run and version remain unlearned."),
      ("OrthoFinder", "2.5.x documentation/paper review; runtime version not installed", "notes/02_补充方法选择与边界.md", "documentation_review_only", "Skip conceptual overview; still need pinned runtime and real input test."),
      ("IQ-TREE", "3.x official tutorial review; runtime version not installed", "notes/02_补充方法选择与边界.md", "documentation_review_only", "Skip conceptual overview; still need pinned runtime and real input test."),
      ("BRAKER", "BRAKER4 documentation review; runtime version not installed", "notes/02_补充方法选择与边界.md", "documentation_review_only", "Skip deprecated-version warning already recorded; need installation and example run."),
      ("Merqury", "paper/docs reviewed; runtime version not installed", "notes/02_补充方法选择与边界.md", "documentation_review_only", "Skip conceptual overview; need k-mer truth set and a real QV/completeness test."),
    ]
    for name, version, ev, status, skip in reviewed:
        add(name, version, ev, status, "Only the named reading/source-audit scope; no claim of full mastery or production validation.", skip)

    out = ROOT / "software_learning_ledger.tsv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(rows)
    md = ["# 软件学习与版本账本", "", f"账本生成时间：{NOW}（Asia/Shanghai）", "",
          "版本以本地运行日志、`native_tool_versions.json` 和 Conda 显式锁清单为证；状态分清源码/文档阅读、真实执行和待验收。‘可跳过’只针对记录的版本、配置与输入范围。版本变化、参数改变、换数据或软件升级时重新核对。", "",
          "详细机器可读记录见 [`software_learning_ledger.tsv`](software_learning_ledger.tsv)。", "",
          "| 软件 | 记录版本 | 状态 | 学习边界/下次可跳过范围 |", "|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['software']} | {r['version']} | {r['learning_status']} | {r['safe_to_skip_next_time']} |")
    (ROOT / "软件学习与版本账本.md").write_text("\n".join(md)+"\n", encoding="utf-8")
    print(f"Wrote {len(rows)} software records at {NOW}")

if __name__ == "__main__":
    main()
