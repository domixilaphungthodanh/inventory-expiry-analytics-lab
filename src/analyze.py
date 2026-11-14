import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if __name__ == "__main__":
    from run_inventory import prepare_environment, run
    run([prepare_environment(), "-m", "inventory_lab.analyze", *sys.argv[1:]])

