# Repository audit and migration

Inspected `harshalkadam777/gaur-migration-demo` at `7e1c8deaa93455e834bd9ce4b225e7e2b003788e` (2026-07-27).

1. `scripts/update_data.py` contained GitHub Actions YAML instead of Python.
2. `blank.yml` and `weekly-update.yml` both scheduled weekly updates.
3. `weekly-update.yml` ended with malformed permissions under jobs.
4. Streamlit displayed hard-coded sample district counts and annual trends.
5. The README claimed datasets, reports and overlays absent from this checkout; its clone/run paths and repository link were inconsistent.

The rewrite is on a separate branch. The old implementation remains recoverable at the above commit. Historical source data needs recovery and verification; sample counts are not migrated into the evidence register.

Collection preserves source metadata and status even on failure. Only candidates.json and status.json are committed automatically. Pages publishes verified CSV records. The optional Streamlit entry point is retained with verified data only.

Offline tests do not establish source completeness, species identity, migration, or account permissions. Live collection and deployment must be checked separately. No production changes or successful remote runs should be claimed on the basis of local tests.
