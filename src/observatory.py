"""Konkan Gaur Observatory: auditable, dependency-free collection and publishing."""
from __future__ import annotations
import argparse
import csv
import json
import shutil
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def request_json(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'KonkanGaurObservatory/2.0', 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def inaturalist(config):
    """Full date-window scan; fail rather than silently truncate a capped result."""
    base = 'https://api.inaturalist.org/v1/'
    taxa = request_json(base + 'taxa?' + urllib.parse.urlencode({'q': 'Bos gaurus', 'rank': 'species'}))
    matches = [t for t in taxa['results'] if t['name'] == 'Bos gaurus']
    if len(matches) != 1:
        raise ValueError('Could not uniquely resolve Bos gaurus')
    params = dict(config['bounds'], taxon_id=matches[0]['id'], d1=config['start_date'],
                  d2=date.today().isoformat(), per_page=200, order_by='id', order='asc', page=1)
    rows = []
    while True:
        payload = request_json(base + 'observations?' + urllib.parse.urlencode(params))
        if payload['total_results'] > config['max_records']:
            raise ValueError('Source exceeds max_records; narrow date/area before retrying')
        batch = payload['results']
        for item in batch:
            observed = item.get('observed_on')
            if not observed:
                continue
            # Keep only public metadata; no observer identity, photos, or exact coordinates.
            rows.append({'id': 'inat:' + str(item['id']), 'source': 'iNaturalist',
                         'url': 'https://www.inaturalist.org/observations/' + str(item['id']),
                         'observed_on': observed, 'reported_at': item.get('created_at'),
                         'source_quality': item.get('quality_grade'),
                         'source_license': item.get('license_code'),
                         'location_obscured': bool(item.get('obscured') or item.get('geoprivacy')),
                         'species': 'Bos gaurus'})
        if len(rows) >= payload['total_results'] or len(batch) < 200:
            return rows
        params['page'] += 1
        time.sleep(1)


def collect(root=ROOT, fetch=inaturalist):
    config = read(root / 'config/sources.json', {})
    prior = read(root / 'data/status.json', {})
    candidates = {r['id']: r for r in read(root / 'data/candidates.json', [])}
    sources, failed, enabled = [], False, 0
    for name, settings in config.items():
        if not settings.get('enabled'):
            sources.append({'source': name, 'state': 'disabled'})
            continue
        enabled += 1
        try:
            if name != 'inaturalist':
                raise ValueError('Unknown collector: ' + name)
            rows = fetch(settings)
            before = set(candidates)
            for row in rows:
                first_seen = candidates.get(row['id'], {}).get('first_seen', now())
                candidates[row['id']] = dict(row, first_seen=first_seen)
            sources.append({'source': name, 'state': 'ok', 'fetched': len(rows),
                            'new': len(set(candidates) - before), 'checked_at': now()})
        except Exception as exc:
            failed = True
            sources.append({'source': name, 'state': 'failed', 'error': str(exc)[:300], 'checked_at': now()})
    state = 'failed' if failed else ('ok' if enabled else 'not_configured')
    status = {'state': state, 'attempted_at': now(), 'sources': sources,
              'last_success_at': now() if state == 'ok' else prior.get('last_success_at'),
              'candidate_count': len(candidates)}
    write(root / 'data/candidates.json', sorted(candidates.values(), key=lambda r: r['id']))
    write(root / 'data/status.json', status)
    return 1 if failed else 0


def verified_events(root=ROOT):
    """CSV is the explicit review boundary; never promote API quality to approval."""
    with (root / 'data/reviews.csv').open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    events, seen = [], set()
    for row in rows:
        if row['decision'] not in {'verified', 'rejected', 'duplicate', 'pending'}:
            raise ValueError('Invalid review decision')
        if not row['record_id'] or row['record_id'] in seen:
            raise ValueError('Missing or repeated record_id')
        seen.add(row['record_id'])
        if row['decision'] != 'verified':
            continue
        for field in ['event_id', 'observed_on', 'district', 'locality', 'source_url', 'reviewed_by', 'reviewed_on']:
            if not row[field].strip():
                raise ValueError(f'{row["record_id"]}: missing {field}')
        for field in ['observed_on', 'reviewed_on']:
            if date.fromisoformat(row[field]) > date.today():
                raise ValueError('Future date in ' + row['record_id'])
        url = urllib.parse.urlparse(row['source_url'])
        if url.scheme not in {'http', 'https'} or not url.netloc:
            raise ValueError('Source must have a valid HTTP(S) URL')
        event = {k: row[k] for k in ['event_id', 'observed_on', 'district', 'locality']}
        event['source_url'] = row['source_url']
        event['count'] = int(row['count']) if row['count'] else None
        if event['count'] is not None and event['count'] < 1:
            raise ValueError('Animal count must be positive or blank')
        existing = next((e for e in events if e['event_id'] == event['event_id']), None)
        if existing:
            for field in ['observed_on', 'district', 'locality', 'count']:
                if event[field] != existing[field]:
                    raise ValueError('Conflicting reports for event ' + event['event_id'])
            if event['source_url'] not in existing['sources']:
                existing['sources'].append(event['source_url'])
        else:
            event['sources'] = [event.pop('source_url')]
            events.append(event)
    return sorted(events, key=lambda e: e['observed_on'], reverse=True)


def weekly(events, today=None):
    today = today or date.today()
    monday = today - timedelta(days=today.weekday())
    result = []
    for offset in range(25, -1, -1):
        start = monday - timedelta(weeks=offset)
        end = start + timedelta(days=7)
        count = sum(start <= date.fromisoformat(e['observed_on']) < end for e in events)
        result.append({'week': start.isoformat(), 'verified_events': count,
                       'coverage': 'unknown', 'partial': offset == 0})
    return result


def build(root=ROOT):
    events = verified_events(root)
    out = root / 'site'
    out.mkdir(exist_ok=True)
    for file in (root / 'web').iterdir():
        if file.is_file():
            shutil.copy2(file, out / file.name)
    status = read(root / 'data/status.json', {'state': 'never_run'})
    # Public status does not expose raw error messages or unreviewed records.
    public_status = {k: status.get(k) for k in ['state', 'attempted_at', 'last_success_at', 'candidate_count']}
    public_status['sources'] = [{k: s.get(k) for k in ['source', 'state', 'new', 'fetched']} for s in status.get('sources', [])]
    payload = {'built_at': now(), 'status': public_status, 'events': events, 'weekly': weekly(events),
               'annual': [{'year': year, 'verified_events': sum(e['observed_on'].startswith(str(year)) for e in events)} for year in range(date.today().year - 5, date.today().year + 1)],
               'interpretation': 'Verified reported sightings; not population counts or proven migration. Coverage is unknown.'}
    write(out / 'data.json', payload)
    (out / '.nojekyll').touch()
    # Export CSV with spreadsheet formula-injection protection.
    def safe(value):
        text = str(value) if value is not None else ''
        return "'" + text if text.startswith(('=', '+', '-', '@', '\t', '\r')) else text
    with (out / 'sightings.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['event_id', 'observed_on', 'district', 'locality', 'count', 'sources'])
        for event in events:
            writer.writerow([safe(event[k]) for k in ['event_id', 'observed_on', 'district', 'locality', 'count']] + [' | '.join(event['sources'])])
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['collect', 'build', 'validate'])
    args = parser.parse_args()
    if args.command == 'collect':
        return collect()
    if args.command == 'build':
        build()
    else:
        verified_events()
    return 0


if __name__ == '__main__':
    sys.exit(main())
