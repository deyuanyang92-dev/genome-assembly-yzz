#!/usr/bin/env python3
"""把本机测试结果与官方 nf-test 快照（tests/default.nf.test.snap）比对：
1) 输出路径清单（忽略规则同 tests/default.nf.test）；2) 稳定文件的 md5（忽略规则同 tests/.nftignore）。
用法：python3 -I compare_with_snapshot.py <pipeline_dir> <results_dir>
"""
import gzip, hashlib, json, re, sys
from pathlib import Path

pipe, results = Path(sys.argv[1]), Path(sys.argv[2])
snap = json.loads((pipe / "tests/default.nf.test.snap").read_text())
content = next(iter(snap.values()))["content"]
exp_tasks, exp_paths, exp_md5 = content[0], content[2], content[3]


def glob_to_regex(pat):
    """Java PathMatcher 风格的 glob：{a,b}、**（可跨目录）、*（不跨目录）、?"""
    out, i = "", 0
    while i < len(pat):
        c = pat[i]
        if pat.startswith("**", i):
            out += ".*"; i += 2; continue
        if c == "*": out += "[^/]*"
        elif c == "?": out += "[^/]"
        elif c == "{":
            j = pat.index("}", i)
            out += "(?:" + "|".join(re.escape(x) for x in pat[i + 1:j].split(",")) + ")"
            i = j
        else: out += re.escape(c)
        i += 1
    return re.compile("^" + out + "$")


def matcher(patterns):
    regs = [glob_to_regex(p) for p in patterns]
    return lambda rel: any(r.match(rel) for r in regs)


# 1) 路径清单
ignore_names = matcher(["pipeline_info/*.{html,json,txt}", "**/mito/**/**"])
actual_paths = sorted(str(p.relative_to(results)) for p in results.rglob("*") if not ignore_names(str(p.relative_to(results))))
missing = sorted(set(exp_paths) - set(actual_paths))
extra = sorted(set(actual_paths) - set(exp_paths))
print(f"[路径] 快照 {len(exp_paths)} 条，实际 {len(actual_paths)} 条；缺少 {len(missing)}，多出 {len(extra)}")
for m in missing[:30]: print("  缺少:", m)
for e in extra[:30]: print("  多出:", e)

# 2) 稳定文件 md5
nftignore = [l.strip() for l in (pipe / "tests/.nftignore").read_text().splitlines() if l.strip() and not l.startswith("#")]
ignore_content = matcher(nftignore)


def md5s(path):
    raw = hashlib.md5(path.read_bytes()).hexdigest()
    if path.suffix == ".gz":
        try: return {raw, hashlib.md5(gzip.decompress(path.read_bytes())).hexdigest()}
        except OSError: pass
    return {raw}


actual_files = [p for p in results.rglob("*") if p.is_file() and not ignore_content(str(p.relative_to(results)))]
exp_by_name = {}
for entry in exp_md5:
    name, h = entry.rsplit(":md5,", 1)
    exp_by_name.setdefault(name, set()).add(h)
ok, bad, absent = 0, [], []
act_names = {}
for p in actual_files: act_names.setdefault(p.name, []).append(p)
for name, hashes in exp_by_name.items():
    if name not in act_names: absent.append(name); continue
    got = set().union(*(md5s(p) for p in act_names[name]))
    if hashes & got: ok += 1
    else: bad.append(name)
print(f"[md5] 快照中有 md5 的文件名 {len(exp_by_name)} 个：一致 {ok}，不一致 {len(bad)}，缺失 {len(absent)}")
for b in bad[:30]: print("  不一致:", b)
for a in absent[:30]: print("  缺失:", a)
print(f"[任务] 快照中成功任务数 {exp_tasks}（实际数请看 pipeline_info/execution_trace）")
