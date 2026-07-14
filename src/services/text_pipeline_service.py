from pathlib import Path

from services.dictionary_service import (
    DictionaryService,
)

from services.pronunciation_service import (
    PronunciationService,
)


class TextPipelineService:

    def __init__(self):

        self.dictionary = (
            DictionaryService()
        )

        self.pronunciation = (
            PronunciationService()
        )

    #
    # Main
    #

    def process(
        self,
        text,
        source_file=None,
    ):

        report = []

        #
        # Dictionary
        #

        text = self.apply_dictionary(
            text,
            report,
        )

        #
        # Pronunciation
        #

        text = self.apply_pronunciation(
            text,
            report,
        )

        return (
            text,
            report,
        )

    #
    # Dictionary
    #

    def apply_dictionary(
        self,
        text,
        report,
    ):

        new_text = (
            self.dictionary.replace_exact(
                text
            )
        )

        if new_text != text:

            report.append(
                "Dictionary"
            )

        return new_text


## ===== KẾT THÚC PART 1 =====
    #
    # Pronunciation
    #

    def apply_pronunciation(
        self,
        text,
        report,
    ):

        new_text = (
            self.pronunciation.process(
                text
            )
        )

        if new_text != text:

            report.append(
                "Pronunciation"
            )

        return new_text

    #
    # Cache
    #

    def save_tts(
        self,
        source_file,
        text,
    ):

        source = Path(source_file)

        cache_dir = (
            source.parent
            / ".tts_cache"
        )

        cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        tts_file = (
            cache_dir
            / f"{source.stem}.tts"
        )

        tts_file.write_text(
            text,
            encoding="utf-8",
        )

        return tts_file

    #
    # Full
    #

    def prepare(
        self,
        source_file,
        text,
    ):

        text, report = self.process(
            text=text,
            source_file=source_file,
        )

        tts_file = self.save_tts(
            source_file,
            text,
        )

        return (
            tts_file,
            report,
        )


## ===== KẾT THÚC FILE =====