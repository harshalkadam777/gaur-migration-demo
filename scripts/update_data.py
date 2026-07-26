
name: Weekly Data Update

on:
  schedule:
    - cron: "0 3 * * 1"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          fi

      - name: Verify repository structure
        run: |
          pwd
          find . -maxdepth 3 -type f | sort
          test -f scripts/update_data.py

      - name: Run weekly pipeline
        env:
          PYTHONUNBUFFERED: "1"
        run: |
          python scripts/update_data.py

      - name: Commit generated updates
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          if [ -n "$(git status --porcelain)" ]; then
            git add -A
            git commit -m "chore: weekly data refresh"
            git pull --rebase origin main
            git push origin HEAD:main
          else
            echo "No changes generated."
          fi
