"""Collect pinned Unicode CLDR orthography evidence; no application/database calls."""
import hashlib
import json
import time
from pathlib import Path
import xml.etree.ElementTree as ET
import requests

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'data/research-cache'


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    evidence = {}
    session = requests.Session()
    session.headers['User-Agent'] = 'VernaculearnContentResearch/1.0'
    for language in json.loads((ROOT / 'content/languages.json').read_text()):
        code = language['code']
        # Akan is broader than Twi; retain the gap rather than substitute.
        if code == 'tw':
            evidence[language['id']] = {'status': 'needs_Asante_Twi_source_and_tutor_review'}
            continue
        url = f'https://raw.githubusercontent.com/unicode-org/cldr/release-47/common/main/{code}.xml'
        path = CACHE / (code + '.xml')
        if not path.exists():
            time.sleep(1)
            response = session.get(url, timeout=30)
            if response.status_code != 200:
                evidence[language['id']] = {'status': 'source_unavailable', 'url': url}
                continue
            path.write_bytes(response.content)
        data = path.read_bytes()
        exemplars = ET.fromstring(data).find("./characters/exemplarCharacters")
        evidence[language['id']] = {'status': 'draft_evidence', 'url': url,
            'sha256': hashlib.sha256(data).hexdigest(),
            'exemplar_characters': exemplars.text if exemplars is not None else None,
            'limitation': 'CLDR locale exemplars are not a complete alphabet or a pronunciation authority.'}
    target = ROOT / 'content/foundations'
    target.mkdir(parents=True, exist_ok=True)
    (target / 'orthography_evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v['status'] for k,v in evidence.items()}))


if __name__ == '__main__':
    main()
