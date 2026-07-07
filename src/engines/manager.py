class EngineManager:

    def __init__(self):
        self.engine = None

    def set_engine(self, engine):
        self.engine = engine

    def generate(self, text, output):
        if self.engine is None:
            raise RuntimeError("No engine selected")

        self.engine.generate(text, output)