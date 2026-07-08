from core.app_context import AppContext


class EngineService:

    def all(self):

        return AppContext.engine_manager.engines()

    def current(self):

        return AppContext.engine_manager.current()

    def current_id(self):

        return AppContext.engine_manager.current_id()

    def select(self, engine_id):

        AppContext.engine_manager.select(
            engine_id
        )