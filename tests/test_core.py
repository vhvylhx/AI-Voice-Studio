import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import App

print(App.config.all())

App.logger.info("AI Voice Studio started.")