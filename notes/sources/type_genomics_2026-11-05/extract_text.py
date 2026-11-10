#!/usr/bin/env python3
"""Extract the abstract and scientific body through Outlook from retained JATS XML.

Letsch et al. (2025), DOI10.1093/sysbio/syaf040, CC BY4.0.
This changes the reading representation only; original XML is retained unchanged.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

base = Path(__file__).resolve().parent
article = ET.parse(base / 'article.xml').getroot()
lines = [
    'Source: Letsch et al. (2025), DOI10.1093/sysbio/syaf040; CC BY4.0.',
    'Derived text: abstract, introduction, scientific sections through Outlook.',
    'Original XML retained; citations/typography may be normalized by extraction.',
    '',
    'Abstract',
]
abstract = article.find('.//article-meta/abstract')
assert abstract is not None
lines.extend(''.join(p.itertext()) for p in abstract.findall('.//p'))
for element in article.find('body'):
    if element.tag == 'sec' and element.get('id') not in {'sec1', 'sec2', 'sec3', 'sec4'}:
        continue
    for child in element.iter():
        if child.tag in {'title', 'p'}:
            lines.extend(['', ''.join(child.itertext())])
(base / 'article_body.txt').write_text('\n'.join(lines) + '\n')
