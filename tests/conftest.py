from pathlib import Path
import sys


APP_PATH = Path(__file__).resolve().parents[1] / "app"

if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))
