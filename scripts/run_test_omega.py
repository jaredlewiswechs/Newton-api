import sys
import os
import json

# Ensure repo root is on sys.path so `core` package can be imported regardless
# of the current working directory used by the test runner.
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from core.schemas import Omega


def main():
    o = Omega(prompt='Write a short paragraph on gravity', word_count_min=100, word_count_max=200)
    print('Omega OK:', o.prompt[:40])
    print(json.dumps(o.dict(), default=str)[:200])


if __name__ == '__main__':
    main()
