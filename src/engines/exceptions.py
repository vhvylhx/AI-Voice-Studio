class EngineError(Exception):
    pass


class EngineNotInstalled(EngineError):
    pass


class EngineBusy(EngineError):
    pass


class EngineCancelled(EngineError):
    pass