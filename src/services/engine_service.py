from pathlib import Path
import json

from core.app_context import AppContext
from services.runtime_service import RuntimeService


class EngineService:

    CONFIG = Path("config/engines.json")

    DEFAULT_ENGINE = "gpt_sovits"

    SCHEMA_VERSION = 1

    def __init__(self):

        self.CONFIG.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.CONFIG.exists():

            self.save_config(
                self.default_config()
            )

        else:

            self.save_config(
                self.load_config()
            )

        self.apply_config()

    def default_config(self):

        return {
            "schema_version": self.SCHEMA_VERSION,
            "default_engine": self.DEFAULT_ENGINE,
            "engines": [],
        }

    def all(self):

        return AppContext.engine_manager.engines()

    def all_info(self):

        return [
            self.info(
                engine
            )
            for engine in self.all()
        ]

    def current(self):

        return AppContext.engine_manager.current()

    def info(
        self,
        engine=None,
    ):

        if engine is None:

            engine = self.current()

        if engine is None:

            return None

        info = engine.info()

        runtime = self.runtime_status()

        info.selected = (
            info.id == self.current_id()
        )

        info.available = engine.is_available()

        info.running = (
            runtime.engine_running
            if info.selected
            else False
        )

        info.python_version = runtime.python_version

        info.python_executable = runtime.python_executable

        info.ffmpeg_available = runtime.ffmpeg_available

        info.cuda_available = runtime.cuda_available

        info.cuda_version = runtime.cuda_version

        info.nvidia_available = runtime.nvidia_available

        info.gpu_name = runtime.gpu_name

        info.gpu_driver = runtime.gpu_driver

        info.runtime_status = runtime.to_dict()

        if not info.available:

            info.last_error = "Engine chưa sẵn sàng."

        return info

    def current_id(self):

        return AppContext.engine_manager.current_id()

    def default_id(self):

        config = self.load_config()

        for item in config["engines"]:

            if item.get("default"):

                return item["id"]

        return config.get(
            "default_engine",
            self.DEFAULT_ENGINE,
        )

    def select(
        self,
        engine_id,
    ):

        AppContext.engine_manager.select(
            engine_id
        )

        AppContext.runtime_service.refresh()

    def runtime_status(self):

        return RuntimeService().status()

    def load(self):

        return self.load_config()["engines"]

    def load_config(self):

        try:

            data = json.loads(
                self.CONFIG.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            data = self.default_config()

        if isinstance(
            data,
            list,
        ):

            data = {
                "schema_version": self.SCHEMA_VERSION,
                "default_engine": self.DEFAULT_ENGINE,
                "engines": data,
            }

        config = self.default_config()

        config.update(
            data
        )

        if not isinstance(
            config.get("engines"),
            list,
        ):

            config["engines"] = []

        return config

    def save(
        self,
        data,
    ):

        config = self.load_config()

        config["engines"] = data

        self.save_config(
            config
        )

    def save_config(
        self,
        config,
    ):

        normalized = self.default_config()

        normalized.update(
            config
        )

        self.CONFIG.write_text(
            json.dumps(
                normalized,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def add(
        self,
        engine_id,
        path,
    ):

        self.set_path(
            engine_id,
            path,
        )

    def set_path(
        self,
        engine_id,
        path,
    ):

        data = self.load()

        found = False

        for item in data:

            if item.get("id") == engine_id:

                item["path"] = str(path)

                item.update(
                    self.detect_engine(
                        engine_id,
                        path,
                    )
                )

                found = True

        if not found:

            item = {
                "id": engine_id,
                "path": str(path),
                "default": False,
            }

            item.update(
                self.detect_engine(
                    engine_id,
                    path,
                )
            )

            data.append(
                item
            )

        self.save(data)

        self.apply_config()

    def remove(
        self,
        engine_id,
    ):

        data = [
            item
            for item in self.load()
            if item["id"] != engine_id
        ]

        self.save(data)

        self.apply_config()

    def set_default(
        self,
        engine_id,
    ):

        data = self.load()

        for item in data:

            item["default"] = (
                item["id"] == engine_id
            )

        self.save(data)

        self.apply_config()

    def configure_gpt_sovits(
        self,
        path,
        make_default=True,
    ):

        self.set_path(
            "gpt_sovits",
            path,
        )

        if make_default:

            self.set_default(
                "gpt_sovits"
            )

        self.select(
            "gpt_sovits"
        )

        return self.info(
            AppContext.engine_manager.get(
                "gpt_sovits"
            )
        )

    def configured_path(
        self,
        engine_id,
    ):

        for item in self.load():

            if item.get("id") == engine_id:

                return item.get(
                    "path",
                    "",
                )

        return ""

    def apply_config(self):

        for item in self.load():

            engine = AppContext.engine_manager.get(
                item.get("id")
            )

            if engine is None:

                continue

            path = item.get(
                "path",
                "",
            )

            if (
                path
                and
                hasattr(
                    engine,
                    "set_path",
                )
            ):

                engine.set_path(
                    path
                )

    def detect_engine(
        self,
        engine_id,
        path,
    ):

        if engine_id == "gpt_sovits":

            return self.detect_gpt_sovits(
                path
            )

        return {
            "ready": False,
            "missing": [],
            "version": "",
        }

    def detect_gpt_sovits(
        self,
        path,
    ):

        root = Path(path)

        files = {
            "root": root,
            "python": root / "runtime" / "python.exe",
            "inference_cli": (
                root
                / "GPT_SoVITS"
                / "inference_cli.py"
            ),
            "webui": root / "webui.py",
        }

        missing = [
            name
            for name, file in files.items()
            if not file.exists()
        ]

        return {
            "ready": not missing,
            "missing": missing,
            "version": (
                "GPT-SoVITS v2 Pro"
                if files["root"].exists()
                else ""
            ),
        }
