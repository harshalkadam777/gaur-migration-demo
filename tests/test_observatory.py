import csv
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import observatory as app
HEADER='record_id,event_id,decision,observed_on,district,locality,count,source_url,reviewed_by,reviewed_on'.split(',')
class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        for folder in ['data','config','web']:(self.root/folder).mkdir()
        app.write(self.root/'config/sources.json',{'inaturalist':{'enabled':True}});self.reviews([])
    def reviews(self,rows):
        with (self.root/'data/reviews.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=HEADER);w.writeheader();w.writerows(rows)
    def row(self,**changes):
        row=dict(zip(HEADER,['r1','e1','verified','2026-01-01','Sindhudurg','Kudal','3','https://example.org/evidence','reviewer','2026-01-02']));row.update(changes);return row
    def test_repeat_collection_is_idempotent(self):
        fetch=lambda _:[{'id':'inat:1','observed_on':'2026-01-01'}]
        app.collect(self.root,fetch);app.collect(self.root,fetch)
        self.assertEqual(len(app.read(self.root/'data/candidates.json',[])),1)
        self.assertEqual(app.read(self.root/'data/status.json',{})['sources'][0]['new'],0)
    def test_failure_preserves_records_and_last_success(self):
        app.collect(self.root,lambda _:[{'id':'inat:1'}]);before=app.read(self.root/'data/status.json',{})['last_success_at']
        def fail(_):raise TimeoutError('source unavailable')
        self.assertEqual(app.collect(self.root,fail),1)
        self.assertEqual(app.read(self.root/'data/status.json',{})['last_success_at'],before)
        self.assertEqual(len(app.read(self.root/'data/candidates.json',[])),1)
    def test_no_enabled_sources_is_not_success(self):
        app.write(self.root/'config/sources.json',{});app.collect(self.root)
        self.assertEqual(app.read(self.root/'data/status.json',{})['state'],'not_configured')
    def test_candidates_never_become_verified_automatically(self):
        app.collect(self.root,lambda _:[{'id':'inat:1','source_quality':'research'}])
        self.assertEqual(app.build(self.root)['events'],[])
    def test_duplicate_reports_count_as_one_event(self):
        self.reviews([self.row(),self.row(record_id='r2',source_url='https://example.org/other')]);events=app.verified_events(self.root)
        self.assertEqual(len(events),1);self.assertEqual(len(events[0]['sources']),2)
    def test_conflicting_event_reports_fail(self):
        self.reviews([self.row(),self.row(record_id='r2',count='5')])
        with self.assertRaises(ValueError):app.verified_events(self.root)
    def test_missing_evidence_fails(self):
        self.reviews([self.row(source_url='')])
        with self.assertRaises(ValueError):app.verified_events(self.root)
    def test_unsafe_evidence_url_fails(self):
        self.reviews([self.row(source_url='javascript:alert(1)')])
        with self.assertRaises(ValueError):app.verified_events(self.root)
    def test_future_observation_fails(self):
        self.reviews([self.row(observed_on='2999-01-01')])
        with self.assertRaises(ValueError):app.verified_events(self.root)
    def test_pending_and_rejected_are_not_published(self):
        self.reviews([self.row(decision='pending'),self.row(record_id='r2',decision='rejected')]);self.assertEqual(app.verified_events(self.root),[])
    def test_week_boundary_and_partial_week(self):
        weeks=app.weekly([{'observed_on':'2026-09-13'},{'observed_on':'2026-09-14'}],date(2026,9,17))
        self.assertEqual(len(weeks),26);self.assertEqual(weeks[-2]['verified_events'],1);self.assertEqual(weeks[-1]['verified_events'],1)
        self.assertTrue(weeks[-1]['partial']);self.assertTrue(all(w['coverage']=='unknown' for w in weeks))
    def test_csv_formula_protection(self):
        self.reviews([self.row(locality='=1+1')]);app.build(self.root)
        self.assertIn("'=1+1",(self.root/'site/sightings.csv').read_text())
    def test_source_taxon_resolution_and_pagination(self):
        settings={'bounds':{},'start_date':'2020-01-01','max_records':5000}
        page=[{'id':i,'observed_on':'2026-01-01'} for i in range(200)]
        replies=[{'results':[{'id':123,'name':'Bos gaurus'}]},{'total_results':201,'results':page},{'total_results':201,'results':[{'id':201,'observed_on':'2026-01-02'}]}]
        with patch.object(app,'request_json',side_effect=replies) as req,patch.object(app.time,'sleep'):rows=app.inaturalist(settings)
        self.assertEqual(len(rows),201);self.assertIn('page=2',req.call_args.args[0]);self.assertNotIn('latitude',rows[0])
    def test_large_source_fails_instead_of_silent_truncation(self):
        replies=[{'results':[{'id':123,'name':'Bos gaurus'}]},{'total_results':6000,'results':[]}]
        with patch.object(app,'request_json',side_effect=replies),self.assertRaises(ValueError):
            app.inaturalist({'bounds':{},'start_date':'2020-01-01','max_records':5000})
if __name__=='__main__':unittest.main()
