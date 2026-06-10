from pathlib import Path
import sys


APP_PATH = Path(__file__).resolve().parent / "app"

if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from dashboard import main


if __name__ == "__main__":
    main()
