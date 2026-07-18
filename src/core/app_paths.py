from pathlib import Path


class AppPaths:
    ROOT = Path(__file__).resolve().parent.parent.parent

    ASSETS = ROOT / "assets"
    CACHE = ROOT / "cache"
    ENGINES = ROOT / "engines"
    LOGS = ROOT / "logs"
    OUTPUT = ROOT / "output"
    PROJECTS = ROOT / "projects"
    SETTINGS = ROOT / "settings"
    STYLE_PROFILES = ROOT / "style_profiles"
    TESTS = ROOT / "tests"
    VOICES = ROOT / "voices"
    WORKSPACE = ROOT / "workspace"

    @classmethod
    def ensure(cls):
        folders = [
            cls.ASSETS,
            cls.CACHE,
            cls.ENGINES,
            cls.LOGS,
            cls.OUTPUT,
            cls.PROJECTS,
            cls.SETTINGS,
            cls.STYLE_PROFILES,
            cls.TESTS,
            cls.VOICES,
            cls.WORKSPACE,
        ]

        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
