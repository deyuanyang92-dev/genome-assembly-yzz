#!/usr/bin/env python3
"""Record installed conda packages without changing an environment."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=Path, default=Path("/tmp/yzz-learning-colora-envs"))
    args = parser.parse_args()
    base = Path(__file__).resolve().parents[1]
    out = base / "environment_locks"
    out.mkdir(exist_ok=True)
    records = []
    for folder in sorted(args.prefix.glob("*_")):
        if not (folder / "conda-meta/history").is_file() or not Path(str(folder) + ".env_setup_done").exists():
            continue
        packages = []
        for item in sorted((folder / "conda-meta").glob("*.json")):
            meta = json.loads(item.read_text())
            packages.append({k: meta.get(k) for k in
                             ["name", "version", "build", "subdir", "channel", "url", "md5", "sha256"]})
        urls = [p["url"] for p in packages if p["url"]]
        (out / f"{folder.name}.explicit.txt").write_text("@EXPLICIT\n" + "\n".join(urls) + "\n")
        source_yaml = Path(str(folder) + ".yaml")
        if source_yaml.exists():
            (out / f"{folder.name}.yaml").write_text(source_yaml.read_text())
        records.append(dict(prefix=str(folder), packages=packages,
                            package_count=len(packages), explicit_url_count=len(urls),
                            note="Snapshot; successful installation alone is not a successful task."))
    result = dict(environments=records,
                  workflow_env_yamls={str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in (base / "work/colora/workflow/envs").glob("*.yaml")})
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Recorded {len(records)} environments in {out}")


if __name__ == "__main__":
    main()
