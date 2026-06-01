"""pytest root config.

Adds the repo root to sys.path so tests can do `from pipeline.filter import ...`
without the package being installed. The data repo intentionally has no
setup.py / pyproject.toml — the pipeline scripts are run directly, not
imported by external consumers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
