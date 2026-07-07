from engine.base_engine import BaseEngine


class EngineManager:

    def __init__(self):

        self._engines = {}

        self._current = None

    def register(self, engine: BaseEngine):

        info = engine.info()

        self._engines[info.id] = engine

        if self._current is None:
            self._current = info.id

    def unregister(self, engine_id):

        if engine_id in self._engines:

            del self._engines[engine_id]

            if self._current == engine_id:
                self._current = None

    def engines(self):

        return list(self._engines.values())

    def engine_ids(self):

        return list(self._engines.keys())

    def current(self):

        if self._current is None:
            return None

        return self._engines.get(self._current)

    def current_id(self):

        return self._current

    def select(self, engine_id):

        if engine_id not in self._engines:
            raise RuntimeError(f"Engine '{engine_id}' not found.")

        self._current = engine_id

    def generate(
        self,
        text_file,
        output_file,
        voice=None
    ):

        engine = self.current()

        if engine is None:
            raise RuntimeError("No engine selected.")

        if not engine.is_available():
            raise RuntimeError(
                "Current engine is unavailable."
            )

        return engine.generate(
            text_file=text_file,
            output_file=output_file,
            voice=voice,
        )