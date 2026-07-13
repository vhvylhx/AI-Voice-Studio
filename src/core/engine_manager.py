from engines.base_engine import BaseEngine


class EngineManager:

    def __init__(self):

        self._engines = {}

        self._current = None

    #
    # Register
    #

    def register(
        self,
        engine: BaseEngine,
    ):

        info = engine.info()

        self._engines[
            info.id
        ] = engine

        if self._current is None:

            self._current = info.id

    def unregister(
        self,
        engine_id,
    ):

        if engine_id in self._engines:

            del self._engines[
                engine_id
            ]

            if self._current == engine_id:

                self._current = None

    #
    # Query
    #

    def engines(self):

        return list(
            self._engines.values()
        )

    def ids(self):

        return list(
            self._engines.keys()
        )

    def engine_ids(self):

        return self.ids()

    def current(self):

        if self._current is None:

            return None

        return self._engines.get(
            self._current
        )

    def current_id(self):

        return self._current

    def get(
        self,
        engine_id,
    ):

        return self._engines.get(
            engine_id
        )

    #
    # Select
    #

    def select(
        self,
        engine_id,
    ):

        if engine_id not in self._engines:

            raise RuntimeError(
                f"Engine '{engine_id}' không tồn tại."
            )

        self._current = engine_id

    #
    # Runtime
    #

    def start(self):

        engine = self.current()

        if (

            engine

            and

            hasattr(
                engine,
                "start",
            )

        ):

            return engine.start()

    def stop(self):

        engine = self.current()

        if engine:

            engine.stop()

    def is_running(self):

        engine = self.current()

        if (

            engine

            and

            hasattr(
                engine,
                "is_running",
            )

        ):

            return engine.is_running()

        return False

    #
    # Shortcut
    #

    def generate(
        self,
        **kwargs,
    ):

        engine = self.current()

        if engine is None:

            raise RuntimeError(
                "No engine selected."
            )

        if not engine.is_available():

            raise RuntimeError(
                "Current engine is unavailable."
            )

        return engine.generate(
            **kwargs
        )

    def train(
        self,
        voice,
        dataset,
    ):

        engine = self.current()

        if engine is None:

            raise RuntimeError(
                "No engine selected."
            )

        if not engine.is_available():

            raise RuntimeError(
                "Current engine is unavailable."
            )

        return engine.train(
            voice,
            dataset,
        )

    def validate_dataset(
        self,
        dataset,
    ):

        engine = self.current()

        if engine is None:

            raise RuntimeError(
                "No engine selected."
            )

        if not engine.is_available():

            raise RuntimeError(
                "Current engine is unavailable."
            )

        return engine.validate_dataset(
            dataset
        )

    def create_preview(
        self,
        voice,
        output_file,
    ):

        engine = self.current()

        if engine is None:

            raise RuntimeError(
                "No engine selected."
            )

        if not engine.is_available():

            raise RuntimeError(
                "Current engine is unavailable."
            )

        return engine.create_preview(
            voice,
            output_file,
        )


## ===== KẾT THÚC FILE =====
