import os
import sys

# Make data-processing/ and ml/ importable from the top-level tests.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for folder in ("data-processing", "ml"):
    sys.path.insert(0, os.path.join(ROOT, folder))
