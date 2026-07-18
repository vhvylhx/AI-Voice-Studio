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

    @staticmethod
    def job_progress(payload):

        bus.emit(
            Events.JOB_PROGRESS,
            payload
        )

    @staticmethod
    def job_added(payload):

        bus.emit(
            Events.JOB_ADDED,
            payload
        )

        bus.emit(
            Events.QUEUE_CHANGED,
            payload
        )

    @staticmethod
    def job_updated(payload):

        bus.emit(
            Events.JOB_UPDATED,
            payload
        )

        bus.emit(
            Events.QUEUE_CHANGED,
            payload
        )

    @staticmethod
    def job_log(payload):

        bus.emit(
            Events.JOB_LOG,
            payload
        )

    @staticmethod
    def active_job_changed(payload):

        bus.emit(
            Events.ACTIVE_JOB_CHANGED,
            payload
        )

    @staticmethod
    def log_message(payload):

        bus.emit(
            Events.LOG_MESSAGE,
            payload
        )
