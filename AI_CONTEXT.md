# Shared AI context: genome assembly learning library

## Type genomics and specimen provenance (2026-11-05)

For type specimens, taxonomy-linked genomes and historical material, read [note64](notes/64_Type_Genomics模式标本基因组与分类溯源.md) and its [reading ledger](notes/sources/type_genomics_2026-11-05/review_ledger.json). Letsch et al. 2025 DOI10.1093/sysbio/syaf040 has scientific full-text, figures1–3 and supplementary table S1 reading evidence; selected ICZN provisions were checked. Historical type low-coverage data can support taxonomic linkage to separately vouchered fresh-reference genomes; keep specimen identities and name-bearing status separate. A topotypic specimen is not automatically a type; digital records do not automatically replace animal name-bearing specimens. The paper's10–20x examples do not lower this project's effective HiFi≥50x requirement for a chosen high-quality HiFi reference route. No extraction, sequencing, type designation or biological pipeline was performed. Current catalog:65 numbered notes,33 topics; historical counts retain their date scope.

## AUGUSTUS annotation learning (2026-11-04)

Read [note63](notes/63_AUGUSTUS原理训练证据与局部注释实测.md) and [component ledger](tests/augustus_learning_2026-11-04/README.md) for AUGUSTUS questions. Fixed v3.5.0 commit 99e04771a7dc2feac4a62a60e88fd2f790c7bb3a now has official example prediction, hints, writable-model training, bounded optimization, BAM-to-hints, local coordinate/strand and translation evidence. The initial excluded-stop convention caused training errors despite exit 0; the bundled fly CDS include stops and require false. This supersedes the earlier no-independent-AUGUSTUS-run scope, only for these examples. No target-polychaete model, full default optimization, TBtools/GSAman GUI or complete annotation workflow was validated.

## Colora paper and core assembly software manual/issues review (2026-11-10)

Read [note65](notes/65_核心组装软件说明书与Issues深读.md), [note66 status matrix](notes/66_全软件说明书与Issues阅读进度.md), the [core software ledger](notes/sources/software_manual_issue_review_2026-11-10.json), the [survey/QC/polishing ledger](notes/sources/software_manual_issue_review_2026-11-10_round2.json), the [repeat/annotation ledger](notes/sources/software_manual_issue_review_annotation_2026-11-10.json), and the [transcript/function annotation ledger](notes/sources/software_manual_issue_review_transcript_2026-11-10.json) before answering debugging or usage questions about these tools. This is a read-only targeted high-value issue review, not exhaustive review of every repository issue; no software was installed or run this round. The supplied 25-page Colora bioRxiv preprint is distinct from the 2025 published paper and the pinned source checkout; the existing Colora functional test remains separate prior evidence. Colora issue page has no visible issues, so inspect dependency issue trackers for component failures. Note66 distinguishes documentation read, issue index checked, issue body read, and pending software; do not overstate the coverage.

## QS019 production planning feature (2026-11-03)

The user requested a feature to guide real Hi-C procurement with HiFi alone. Read [QS019 specification](notes/62_HiC测序采购与挂载充分性规划_QS019.md): V1 first-order planning using assembly profiles, matched experiments and explicit retention scenarios; V2 actual QC updates; V3 depth and structural sufficiency. Input/report templates exist; the feature is not implemented or production validated. This adds one design record, not a new experimental execution.

After the user rejected the vague design, section 0 now records exact vendor-specific initial order rules (Phase sequencing pairs and fragmentation increment; Omni-C 30X starting guidance), archived with hashes. Treat these as protocol starting orders, distinct from experiment-supported effective targets and structural sufficiency. A raw starting order must not be divided by a putative 10% retention again. Do not generalize Phase's N50/contig-count increment to other protocols or multi-haplotype assemblies. Arima search snippets were found, but redirected original pages were insufficient to register a current executable rule.

## Hi-C procurement advice correction (2026-11-03)

Before recommending Hi-C sequencing amounts, read notes/sources/hic_depth_production_review_2026-11-03.md. Newly acquired HapHiC Supplementary Data 1 Sheets 3/14 show that near-100% anchoring can coexist with poor ordering/orientation at low effective depths. Use matched paper evidence and explicit raw-to-filtered pair definitions; do not turn EBP >50× into a sample-specific order or demand 50× filtered effective Hi-C. With HiFi only, assess assembly first and provide evidence-based budget scenarios; shallow QC refines the estimate rather than replacing a justified initial recommendation.

## 2026-11-03 reference scaffold component execution

RagTag v2.1.0 exact commit e993fb2787346345662c240967a3ec80bb2aac64 now has three synthetic scaffold executions: default gaps, inferred gaps, and an altered-reference layout disagreeing with artificial target truth. See tests/ragtag_scaffold_2026-11-03/README.md. Independent AGP reconstruction, component preservation and unplaced retention passed. This updates the older "reference tools unrun" scope only for RagTag scaffold; no raw-read assembly, correct/patch/merge, Hi-C or real sample validation was added.

## Reference-assisted assembly, conversion and Hi-C selection repair

Read notes59–61 before these questions: reference involvement during assembly vs post-assembly scaffolding; SAM/BAM HiFi export and hifiasm GFA selection; HapHiC and other Hi-C scaffolders. The independent initial assembly + RagTag route is valid reference-assisted assembly, but not the only route. Early reference-guided assembly is not compulsory whenever a reference exists. See notes/sources/full_request_gap_audit_2026-11-02.md for all historical request gaps. New samtools1.21 synthetic export evidence does not validate real HiFi or new biological assemblies. ALLHiC upstream says no longer maintained; HapHiC1.0.7 needs exact commit.

Canonical library: `/mnt/p/yzz-全基因组工作流程/genome-assembly-yzz` (`P:\yzz-全基因组工作流程\genome-assembly-yzz` on Windows).

Later on 2026-11-02, the HapHiC 113-page supplement and two Sanger curation PDFs were successfully acquired. Selected methods/commands and 12 Sanger figure pages were reviewed; earlier download failures are historical. See notes/sources/reference_hic_batch_2026-11-02.md. gfatools source was compiled and two synthetic inputs executed, including a no-sequence SIGSEGV observation; this is not a biological assembly or a HapHiC run. Software coverage now has 61 rows, with evidence levels retained.

Tool-specific entry points and documented loading limits are summarized in `AGENT_COMPATIBILITY.md`.

## Read this first

Start with `notes/50_全基因组知识库导航与覆盖账本.md` and `config/knowledge_base_catalog.json`. Local search: `python3 scripts/knowledge_base.py search "BUSCO 缺失"`. Consult `notes/51_组装原理与证据驱动判断手册.md` for mechanisms, and `notes/52_Juicer_BUSCO_Flye接口源码与排错补充.md` for the added version-specific source review. Colora has one saved functional test configuration (QUAST separately staged; FCS-GX disabled), not a validated target-species production assembly.

The task covers whole-genome assembly across data types and combinations, not only HiFi/ONT. Read `notes/49_全基因组组装任务范围与数据路由总纲.md` before selecting or designing a route. Short-read, hybrid, reference-assisted and mapping-based scaffolding branches are within the original scope. Coverage of existing notes is not proof that every branch has been studied or tested.

1. `CONTEXT.md` for the project’s current scientific constraints and evidence boundaries.
2. `notes/00_学习进度清单.md` for what has and has not been studied or run.
3. `notes/21_组装基础与质量判断.md` and `notes/23_EBP2026规范与本项目对标要求.md` for core assembly/QC requirements.
4. `notes/44_公开环节动物基因组核心基因与机器学习可行性.md` for comparative genomics and polychaete assets.
5. Use `README.md` to find the relevant topic note; read only the notes relevant to the task.

## Reuse without repeating

- Before installing, benchmarking, or explaining a tool, search the applicable `software_learning_ledger.tsv` files under `tests/` and check version, data, command and learned scope.
- A matching version and scope can skip its basic walkthrough. New data, a changed version, new parameters, or a production-scale task still needs targeted validation.
- Every claim must keep its evidence label: document/paper reviewed, source statically inspected, component executed, or end-to-end workflow run. Do not turn one into another.
- Before designing an assembly adapter or debugging a failure, read `notes/45_软件说明书Issues与源码诊断知识库.md`, `config/software_diagnostics_knowledge.json` and `notes/sources/software_debug_review_2026-11-02.json`. Match exact commit, dependency and symptom evidence; issue reports are not confirmed root causes. The 29 rules are design records, not an implemented or validated diagnoser. Do not infer OOM from segfault alone or silently purge, change biological parameters, or discard caches.
- Keep source, version, date/time, command/config, checksums, result and limitations with each new practical test.

## New short-read/hybrid component evidence

Read `notes/53_二代与混合组装方法源码及实测.md` and `notes/54_bioSkills短读专题复核与纠错.md`. SPAdes4.3.0 selected source/manual review differs from actual4.0.0 runtime: one official toy, four synthetic assemblies, three negative CLI cases. Data, commands, output hashes and exact truth comparisons are archived under `tests/shortread_hybrid_learning_2026-11-02/`. Synthetic17999bp result lacks one terminal base of18000bp truth; another hybrid case did not improve. No new target-species production validation or complete paper-pipeline reproduction.

## Parallel learning follow-up

The user explicitly authorized multi-agent learning. Read notes55–58 and `tests/multi_agent_learning_2026-11-02/README.md` for newly reviewed Platanus orchestration, Hi-C edited coordinate recovery, EBP/Flagger evidence semantics and RNA routing. New runtime evidence: YaHS post4 synthetic edit conversions, minimap2 RNA mapping2, one shell-mechanism demonstration and one16-case acceptance-semantics example. No new biological assembly, production acceptance, GUI session or complete paper-workflow reproduction. Static source risks stay unconfirmed until upstream execution reproduces them.

## Current reference test

`tests/capitella_polychaete_reference_2026-07/README.md` describes the latest practical Capitella teleta reference test. It is a public reference resource, not the user’s own Travisia sample. The genome/GFF/protein/repeat bundle passed structural checks; same-release protein remapping is internal consistency only. The functional workbook has 131 peptide sequence differences and 13 Panther IDs absent from the current GFF; preserve provenance and do not silently overwrite sequences.

## Scientific constraints to carry into software design

- For a HiFi-based route, the user requires effective HiFi coverage ≥50×, calculated as usable target-individual HiFi bases divided by one haploid nuclear genome size; say when unknown or below threshold. Short-read-only routes are already within the full task scope: do not reject these solely for lacking HiFi. Assess their coverage and evidence separately; do not substitute Illumina bases for a chosen HiFi route’s threshold. See `notes/48_二代数据与参考辅助染色体组装路线.md` before reference-assisted assembly design.
- Hi-C from a different individual is not target-individual phasing evidence. Evaluate its scaffolding contribution and contradictions separately.
- N50, BUSCO, mapping and same-source remapping are separate evidence types; none alone establishes a correct chromosome-level assembly.
- Keep genome skimming and high-coverage nuclear genome assembly as different use cases.

## When coding in another repository

The library is not automatically loaded just because it exists elsewhere on disk. Add a short project instruction in the software repository that points to this file and the relevant notes, or attach these files in the chosen AI tool. Avoid copying the entire library into each prompt.
