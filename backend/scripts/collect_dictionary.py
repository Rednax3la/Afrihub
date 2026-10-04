"""Fetch allowlisted licensed JSONL downloads; never connects to MongoDB.

Repeat runs reuse completed downloads and regenerate deduplicated normalized
output deterministically. Incomplete downloads are retried, never imported.
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.robotparser
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.dictionary_data import normalize_wiktionary

ROOT = Path(__file__).resolve().parents[2]
USER_AGENT = 'VernaculearnLexicon/1.0 (+https://vernaculearn.africa)'


def collect(inventory, output, session=None):
    session = session or requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    output.mkdir(parents=True, exist_ok=True)
    robots = session.get('https://kaikki.org/robots.txt', timeout=30)
    robots.raise_for_status()
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(robots.text.splitlines())
    report = {}
    for source in inventory:
        lang = source['language_id']
        report[lang] = {'entries': 0, 'status': source['status']}
        if source['status'] != 'approved_text_download':
            continue
        url = source['download_url']
        if not url.startswith('https://kaikki.org/dictionary/') or not parser.can_fetch(USER_AGENT, url):
            raise ValueError('Download is outside allowlist or blocked by robots.txt')
        raw = output / (lang + '.raw.jsonl')
        try:
            if not raw.exists():
                time.sleep(max(2, parser.crawl_delay(USER_AGENT) or 0))
                with session.get(url, timeout=(10, 60), stream=True) as response:
                    if response.status_code == 429:
                        report[lang].update(status='rate_limited', retry_after=response.headers.get('Retry-After', 'provider guidance required'))
                        (output / 'coverage.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
                        print('Provider rate limit reached; stopping all downloads. Resume only after Retry-After.', flush=True)
                        return report
                    response.raise_for_status()
                    size = 0
                    partial = raw.with_suffix('.partial')
                    with partial.open('wb') as target:
                        for chunk in response.iter_content(65536):
                            size += len(chunk)
                            if size > 150_000_000:
                                raise ValueError('Download exceeds 150 MB safety bound')
                            target.write(chunk)
                    partial.replace(raw)
                    raw.with_suffix('.metadata.json').write_text(json.dumps({'download_url': url,
                        'sha256': hashlib.sha256(raw.read_bytes()).hexdigest()}), encoding='utf-8')
            checksum = hashlib.sha256(raw.read_bytes()).hexdigest()
            metadata = json.loads(raw.with_suffix('.metadata.json').read_text(encoding='utf-8'))
            if metadata['download_url'] != url or metadata['sha256'] != checksum:
                raise ValueError('Cached source URL/checksum mismatch; inspect cache before reuse')
            seen = set()
            normalized = output / (lang + '.jsonl')
            with raw.open(encoding='utf-8') as data, normalized.with_suffix('.partial').open('w', encoding='utf-8') as target:
                for line in data:
                    for entry in normalize_wiktionary(json.loads(line), source, checksum):
                        if entry['_id'] not in seen:
                            target.write(json.dumps(entry, ensure_ascii=False) + '\n')
                            seen.add(entry['_id'])
            normalized.with_suffix('.partial').replace(normalized)
            report[lang] = {'entries': len(seen), 'status': 'acquired_unreviewed', 'sha256': checksum,
                            'download_url': url, 'raw_bytes': raw.stat().st_size}
        except (requests.RequestException, ValueError) as error:
            report[lang]['status'] = 'acquisition_blocked'
            report[lang]['reason'] = type(error).__name__
        print(f"{lang}: {report[lang]['entries']} entries ({report[lang]['status']})", flush=True)
        (output / 'coverage.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (output / 'coverage.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, default=ROOT / 'data/dictionary')
    args = cli.parse_args()
    collect(json.loads((ROOT / 'content/dictionary/sources.json').read_text(encoding='utf-8')), args.output)
