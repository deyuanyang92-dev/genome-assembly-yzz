#!/usr/bin/env python3
"""Search the local genome knowledge catalog, or validate its durable references.

No network, biological analysis, or automatic diagnosis is performed.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'config/knowledge_base_catalog.json'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def features(text):
    """Keep Latin tool names intact; add Chinese words and adjacent bigrams."""
    result = set(re.findall(r'[a-z0-9][a-z0-9_.+-]*', text.lower()))
    for word in re.findall(r'[\u4e00-\u9fff]+', text):
        result.add(word)
        result.update(word[i:i+2] for i in range(len(word)-1))
    return result


def search(catalog, query, limit):
    terms = features(query)
    if not terms:
        raise ValueError('查询不能为空，且须包含中文或字母/数字')
    results = []
    for topic in catalog['topics']:
        meta = ' '.join([topic['title'], topic.get('question', ''), *topic['keywords']]).lower()
        score = sum(8 for term in terms if term in meta)
        # Metadata ranks questions; body hits retrieve source notes as secondary evidence.
        hits = []
        for rel in topic['notes']:
            body = (ROOT / rel).read_text(encoding='utf-8')
            lines = [line.strip() for line in body.splitlines() if line.strip() and not line.startswith('#')]
            ranked = [(sum(1 for term in terms if term in line.lower()), line) for line in lines]
            n, snippet = max(ranked, default=(0, ''))
            if n:
                hits.append((n, rel, snippet))
        score += min(6, max((a[0] for a in hits), default=0))
        if score:
            results.append((score, topic, sorted(hits, key=lambda h: -h[0])))
    results.sort(key=lambda x: (-x[0], x[1]['id']))
    for score, topic, hits in results[:limit]:
        print(f"{topic['id']} {topic['title']} (相关度 {score})")
        print('  状态：' + topic['coverage'])
        for rel in topic['notes']:
            print('  ' + rel)
        if hits:
            print('  片段：' + hits[0][2][:230])
        print()
    if not results:
        print('未检索到专题。请换用工具名或较短中文关键词。')
    return 0


def check(catalog):
    errors, warnings = [], []
    def require(condition, message):
        if not condition:
            errors.append(message)
    topics = catalog['topics']
    require(len({t['id'] for t in topics}) == len(topics), '重复专题ID')
    for t in topics:
        for rel in t['notes']:
            require((ROOT / rel).is_file(), f"缺少专题文件：{rel}")
    docs = catalog['documents']
    require(len({d['path'] for d in docs}) == len(docs), '重复文档路径')
    for doc in docs:
        require((ROOT / doc['path']).is_file(), '缺少索引文档：' + doc['path'])
    actual_docs = {str(p.relative_to(ROOT)) for p in (ROOT / 'notes').glob('[0-9][0-9]_*.md')}
    require(actual_docs == {d['path'] for d in docs}, '笔记目录与索引不一致，需刷新catalog')
    for prefix in tuple(f'{n:02d}_' for n in range(50, 63)):
        matches = list((ROOT / 'notes').glob(prefix + '*.md'))
        require(len(matches) == 1, '新笔记数量异常：' + prefix)
        for path in matches:
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                target = unquote(target.split('#')[0].strip('<>'))
                if not target or re.match(r'[a-zA-Z]+:', target):
                    continue
                require((path.parent / target).exists(), f'链接不存在：{path.name} -> {target}')
    ledger = read_json(ROOT / 'notes/sources/core_tools_review_2026-11-02.json')
    for source in ledger['files']:
        p = ROOT / source['path']
        if not p.is_file() and source.get('availability', '').startswith('ignored'):
            warnings.append('上游忽略目录未恢复：' + source['path'])
            continue
        require(p.is_file(), '缺少来源快照：' + source['path'])
        if p.is_file():
            require(hashlib.sha256(p.read_bytes()).hexdigest() == source['sha256'], '来源校验和不符：' + source['path'])
    rules = read_json(ROOT / 'config/software_diagnostics_knowledge.json')['rules']
    require(len({a['id'] for a in rules}) == len(rules), '诊断规则ID重复')
    for a in rules:
        require(bool(a.get('version_scope')) and bool(a.get('source_urls')), '诊断缺少版本/来源：' + a['id'])
        require(a.get('auto_fix_enabled') is False, '知识记录意外启用自动修复：' + a['id'])
    with (ROOT / 'templates/software_coverage_matrix.tsv').open(newline='') as f:
        software = list(csv.DictReader(f, delimiter='\t'))
    require(len({a['tool'] for a in software}) == len(software), '软件覆盖表重名')
    for row in software:
        require((ROOT / row['entry_note']).is_file(), '软件专题入口丢失：' + row['tool'])
    cards = read_json(ROOT / 'config/assembly_decision_cards.json')['cards']
    require(len({a['id'] for a in cards}) == len(cards), '判断卡ID重复')
    for card in cards:
        require(card.get('automated_action') is False, '判断卡意外启用自动行动：' + card['id'])
        for rel in card['notes']:
            require((ROOT / rel).is_file(), '判断卡来源缺失：' + rel)
    evidence = ROOT / catalog['current_execution_summary']['evidence']
    require(evidence.is_file(), '流程执行证据缺失')
    if evidence.is_file():
        run = read_json(evidence)
        require(run.get('returncode', run.get('return_code')) == 0, '所引用执行记录未成功')
    return dict(checked_at=datetime.now(timezone.utc).isoformat(),
                validation_scope='catalog/references/hashes/metadata only; not biological validation',
                topics=len(topics), documents=len(docs), software_rows=len(software),
                decision_cards=len(cards),
                diagnostic_design_records=len(rules), source_hashes=len(ledger['files']),
                errors=errors, warnings=warnings, passed=not errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    s = subs.add_parser('search', help='检索本地专题和笔记片段')
    s.add_argument('query')
    s.add_argument('--limit', type=int, default=5)
    c = subs.add_parser('check', help='核对目录、链接、校验和和记录')
    c.add_argument('--output', type=Path)
    args = parser.parse_args()
    catalog = read_json(CATALOG)
    if args.command == 'search':
        if args.limit < 1:
            parser.error('--limit必须>=1')
        return search(catalog, args.query, args.limit)
    result = check(catalog)
    output = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(output, encoding='utf-8')
    print(output, end='')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
