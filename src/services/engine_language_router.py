VIETNAMESE_LANGUAGE = "vi"
VIETNAMESE_ENGINE_ID = "vieneu"
GPT_SOVITS_ENGINE_ID = "gpt_sovits"


class EngineLanguageRouter:

    def normalize_language(
        self,
        language,
    ):

        return str(
            language
            or ""
        ).strip().lower()

    def required_engine(
        self,
        language,
    ):

        if self.normalize_language(
            language
        ) == VIETNAMESE_LANGUAGE:

            return VIETNAMESE_ENGINE_ID

        return ""

    def resolve_engine(
        self,
        language,
        requested_engine_id="",
    ):

        required = self.required_engine(
            language
        )

        if required:

            return required

        return requested_engine_id

    def validate_binding(
        self,
        language,
        engine_id,
    ):

        required = self.required_engine(
            language
        )

        if required and engine_id != required:

            return [
                "vietnamese_requires_vieneu_tts"
            ]

        return []

