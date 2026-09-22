# Konkan Gaur Observatory

A GitHub-native register of **verified reported sightings** of Indian gaur (*Bos gaurus*) in Konkan. Python collects public source metadata; a reviewer approves evidence; GitHub Pages publishes the register and a 26-week chart. No fabricated sightings, automatic migration claims, or sample counts are published.

## What is implemented

- iNaturalist collector with retries, pagination, bounded historical query and stable source IDs.
- Persistent candidate metadata and collection status in versioned JSON.
- Explicit CSV review gate. Multiple reports can share one event ID.
- Static mobile-friendly dashboard, English/Marathi introductory labels, district filter, weekly chart, six-calendar-year summary, regional reference map and verified CSV export. The reference map is not a sighting map.
- Separate collection, validation and Pages workflows. Failed collection preserves saved data and last-success time.
- Optional Streamlit compatibility viewer.

**Not yet implemented:** social-media/news scraping, automatic anomaly alerts, field survey effort, environmental overlays, automated species verification, or proven migration trajectories. The old README claimed datasets and reports that are not present in the repository. Historical data must be recovered and checked before importing. An empty verified register is intentional.

## Local use (Python 3.12)

```bash
git clone https://github.com/harshalkadam777/gaur-migration-demo.git
cd gaur-migration-demo
python -m unittest discover -s tests -v
python src/observatory.py build
python -m http.server 8000 --directory site
```

Open http://localhost:8000. No pip install is needed for this workflow.
To fetch current source metadata, run `python scripts/update_data.py`, then rebuild. Internet access is required for collection, not tests or the dashboard build.

## Apply the supplied rewrite patch

In a clean checkout of the existing repository, save `gaur-observatory-rewrite.patch` beside the repository, then run:

```bash
git switch -c codex/gaur-observatory-rewrite
git am ../gaur-observatory-rewrite.patch
python -m unittest discover -s tests -v
git push -u origin codex/gaur-observatory-rewrite
```

Open a pull request for that branch and review it before merging. If the repository has changed since the audited commit, resolve patch conflicts before continuing; do not force-push. The ZIP contains the replacement source tree, but uploading its files over the old tree will not delete obsolete files: remove `.github/workflows/blank.yml` when using that method. The patch handles that deletion automatically.

## GitHub setup

1. Merge the reviewed rewrite branch into `main`.
2. Under **Settings → Pages**, select **GitHub Actions** as the build source.
3. Under **Settings → Actions → General**, allow the collection workflow to write repository contents. Organization policies or branch protection may prevent automated data commits; do not disable protections without considering the alternative below.
4. Run **Actions → Collect sightings → Run workflow** on the default branch.
5. **Publish observatory** runs after collection, even if a source fails, to display saved failure status. It also runs on pushes to `main`. The `workflow_run` trigger is needed because commits using `GITHUB_TOKEN` do not normally start another push workflow.
6. Review **Actions** and the deployment URL under **Settings → Pages**.

Collection is scheduled Mondays at 03:17 UTC (08:47 IST). Schedules are best-effort, may be delayed, and can be disabled after inactivity in public repositories. The dashboard flags a last successful collection older than nine days. A stopped schedule cannot notify by itself: enable GitHub failure notifications and check dashboard freshness. This is a research dashboard, not a real-time wildlife warning service.

If protected branches reject bot pushes, the run fails visibly and preserves a 30-day `collection-records` recovery artifact. Import those records through a reviewed PR, or design a dedicated data branch. No force pushes or protection bypasses are used.

## Review a sighting

Read `data/candidates.json`, follow the original source, verify species/date/location, and add or edit a row in `data/reviews.csv` through a pull request. A source's research-grade label does not constitute project approval. News or local reports can also be entered directly when there is a public evidence URL.

| Column | Meaning |
|---|---|
| record_id | Unique source report ID, e.g. `inat:12345`; not a real example sighting |
| event_id | Shared ID for reports of the same event |
| decision | `pending`, `verified`, `duplicate`, or `rejected` |
| observed_on | Actual sighting date, YYYY-MM-DD; do not substitute upload date |
| district / locality | Manually checked location; do not infer exact positions from obscured records |
| count | Positive number of animals reported, or blank when unknown |
| source_url | Public HTTP(S) evidence URL |
| reviewed_by / reviewed_on | Reviewer identifier and review date |

Use the repository sighting issue form for new community reports; reviewers transfer approved evidence into the CSV. Issues are public. A verified row requires all fields except count. Reports sharing an event ID must agree on date, district, locality and count; reconcile discrepancies explicitly. Pending/rejected/duplicate rows do not contribute to the public event count. Matching IDs prevents repeated imports, but **cross-source duplicate detection is a human review task**.

## Geographic and scientific limits

`config/sources.json` contains a broad retrieval rectangle covering Konkan and nearby areas. It is not a district boundary: review records before inclusion. The configured start date is a retrieval window, not proof of complete six-year coverage. Source coverage, reporting effort and detectability vary. Zero records does not mean zero gaur. Weekly bars count events, not individual animals; the current week is incomplete. Exact coordinates and personal observer details are not collected or published. Candidate metadata remains visible in a public repository.

The dashboard's collection time describes the configured source scan, not complete surveillance of Konkan. Existing candidates are retained if upstream records disappear; reviewers should remove approval for withdrawn/invalid evidence. Do not copy unlicensed photographs or article text into the repository.

## Layout

- `src/observatory.py` — collector, validation and static build
- `scripts/update_data.py` — compatible weekly entry point
- `data/` — source candidates, review decisions, collection status
- `web/` — static dashboard assets
- `tests/` — offline correctness and failure-recovery tests
- `.github/workflows/` — collection, validation and Pages deployment
- `docs/REWRITE_AUDIT.md` — findings from the previous implementation

The primary deployment does not require cloud servers, API secrets, a database subscription or a continuously running Python process. GitHub plan limits and third-party data terms still apply.
