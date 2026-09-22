"""Compatibility entry point for the formerly broken weekly command."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from observatory import collect
if __name__ == '__main__':
    raise SystemExit(collect())
