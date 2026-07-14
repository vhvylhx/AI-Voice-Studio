from events import bus, Events


class AppEvents:

    @staticmethod
    def project_changed(project):

        print("EVENT Project")

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

        print("EVENT Voice")

        bus.emit(
            Events.VOICE_CHANGED,
            voice
        )

    @staticmethod
    def engine_changed(engine):

        print("EVENT Engine", engine)

        bus.emit(
            Events.ENGINE_CHANGED,
            engine
        )