from __future__ import annotations

from models.language_capability import (
    ENGINE_GPT_SOVITS,
    ENGINE_VIETNAMESE,
    LANGUAGE_CATALOG_VERSION,
    LanguageDefinition,
)


class LanguageCatalogService:

    def __init__(self):

        self._languages = [
            LanguageDefinition(
                code="vi",
                display_name_vi="Tiếng Việt",
                display_name_en="Vietnamese",
                primary=True,
                default_engine_id=ENGINE_VIETNAMESE,
                aliases=[
                    "vn",
                    "vie",
                    "vietnamese",
                ],
            ),
            LanguageDefinition(
                code="zh",
                display_name_vi="Tiếng Trung",
                display_name_en="Chinese",
                default_engine_id=ENGINE_GPT_SOVITS,
                gpt_sovits_language="all_zh",
                aliases=[
                    "cn",
                    "zh-cn",
                    "zh_hans",
                    "chinese",
                ],
            ),
            LanguageDefinition(
                code="en",
                display_name_vi="Tiếng Anh",
                display_name_en="English",
                default_engine_id=ENGINE_GPT_SOVITS,
                gpt_sovits_language="en",
                aliases=[
                    "eng",
                    "english",
                ],
            ),
            LanguageDefinition(
                code="ja",
                display_name_vi="Tiếng Nhật",
                display_name_en="Japanese",
                default_engine_id=ENGINE_GPT_SOVITS,
                gpt_sovits_language="all_ja",
                aliases=[
                    "jp",
                    "jpn",
                    "japanese",
                ],
            ),
            LanguageDefinition(
                code="ko",
                display_name_vi="Tiếng Hàn",
                display_name_en="Korean",
                default_engine_id=ENGINE_GPT_SOVITS,
                gpt_sovits_language="all_ko",
                aliases=[
                    "kr",
                    "kor",
                    "korean",
                ],
            ),
            LanguageDefinition(
                code="yue",
                display_name_vi="Tiếng Quảng Đông",
                display_name_en="Cantonese",
                default_engine_id=ENGINE_GPT_SOVITS,
                gpt_sovits_language="all_yue",
                aliases=[
                    "cantonese",
                    "zh-yue",
                ],
            ),
        ]

        self._alias_map = {}

        for language in self._languages:

            self._alias_map[language.code] = language.code

            for alias in language.aliases:

                self._alias_map[alias.lower()] = language.code

    def list_languages(self):

        return [
            item.to_dict()
            for item in self._languages
        ]

    def catalog(self):

        return {
            "catalog_version": LANGUAGE_CATALOG_VERSION,
            "languages": self.list_languages(),
            "primary_language": "vi",
            "gpt_sovits_languages": self.gpt_sovits_mapping(),
            "default_enabled_languages": [
                "vi",
            ],
        }

    def supported_codes(self):

        return [
            item.code
            for item in self._languages
        ]

    def normalize(
        self,
        language_code,
    ):

        code = str(
            language_code or ""
        ).strip().lower().replace(
            "_",
            "-",
        )

        if not code:

            return "vi"

        return self._alias_map.get(
            code,
            code,
        )

    def normalize_many(
        self,
        language_codes,
    ):

        result = []

        for item in language_codes or []:

            code = self.normalize(
                item
            )

            if code in self.supported_codes() and code not in result:

                result.append(
                    code
                )

        return result

    def definition(
        self,
        language_code,
    ):

        code = self.normalize(
            language_code
        )

        for item in self._languages:

            if item.code == code:

                return item

        return None

    def gpt_sovits_mapping(
        self,
    ):

        return {
            item.code: item.gpt_sovits_language
            for item in self._languages
            if item.gpt_sovits_language
        }

    def default_engine_for(
        self,
        language_code,
    ):

        definition = self.definition(
            language_code
        )

        return definition.default_engine_id if definition else ""
