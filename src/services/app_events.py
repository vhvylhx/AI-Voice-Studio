from events import bus, Events


class AppEvents:

    @staticmethod
    def project_changed(project):

        bus.emit(
            Events.PROJECT_CHANGED,
            project
        )

        bus.emit(
            Events.WORKSPACE_CHANGED,
            project
        )

    @staticmethod
    def voice_changed(voice):

        bus.emit(
            Events.VOICE_CHANGED,
            voice
        )

    @staticmethod
    def engine_changed(engine):

        bus.emit(
            Events.ENGINE_CHANGED,
            engine
        )