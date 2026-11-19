import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.synthetic import write_data

if __name__ == "__main__":
    print(write_data("data/generated/platform_data.json"))
