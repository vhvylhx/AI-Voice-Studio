from core.app_context import AppContext


class GenerateService:

    def generate(self, job):

        engine = AppContext.engine_manager.current()

        if engine is None:

            raise RuntimeError(
                "Chưa chọn Engine."
            )

        return engine.generate(
            text_file=job.text_file,
            output_file=job.output_file,
            voice=job.voice,
        )