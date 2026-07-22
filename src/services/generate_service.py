from core.app_context import AppContext

from services.text_service import (
    TextService,
)

from services.text_pipeline_service import (
    TextPipelineService,
)

from services.cleanup_service import (
    CleanupService,
)

from services.history_service import (
    HistoryService,
)

from services.generate_pipeline_service import (
    GeneratePipelineService,
)
from services.engine_language_router import EngineLanguageRouter


class GenerateService:

    def __init__(self):

        self.text = TextService()

        self.pipeline = (
            TextPipelineService()
        )

        self.cleanup = (
            CleanupService()
        )

        self.history = (
            HistoryService()
        )

        self.pipeline_generate = (
            GeneratePipelineService(
                engine_manager=AppContext.engine_manager,
            )
        )
        self.engine_router = EngineLanguageRouter()

    def prepare_text(
        self,
        text_file,
    ):

        #
        # Read
        #

        text = self.text.read(
            text_file
        )

        text = self.text.normalize(
            text
        )

        #
        # Dictionary + Pronunciation
        #

        text, report = (
            self.pipeline.process(
                text=text,
                source_file=text_file,
            )
        )

        #
        # Cleanup
        #

        text, clean_report = (
            self.cleanup.clean(
                text
            )
        )

        report.extend(
            clean_report
        )

        #
        # Save History
        #

        self.history.save(
            text_file,
            report,
        )

        #
        # Save .tts
        #

        tts_file, _ = (
            self.pipeline.prepare(
                source_file=text_file,
                text=text,
            )
        )

        return tts_file

    def generate(
        self,
        job,
    ):

        engine_id = None

        if job.voice:

            config = job.voice.config

            engine_id = self.engine_router.resolve_engine(
                getattr(
                    config,
                    "language",
                    "",
                ),
                job.voice.config.engine
            )

        if engine_id:

            AppContext.engine_manager.select(
                engine_id
            )

        prepared = self.prepare_text(
            job.text_file
        )

        return AppContext.engine_manager.generate(

            text_file=prepared,

            output_file=job.output_file,

            voice=job.voice,

        )

    def generate_request(
        self,
        request,
        voice,
        project=None,
        adapter=None,
    ):

        return self.pipeline_generate.run(
            request=request,
            voice=voice,
            project=project,
            adapter=adapter,
        )
