import json
import re
from pathlib import Path


class PronunciationService:

    def __init__(self):

        self.root = Path("dictionary")

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.file = self.root / "dictionary.json"

        self.words = self.load()

    #
    # Dictionary
    #

    def load(self):

        if not self.file.exists():

            data = {

                "AI": "ây ai",
                "API": "ây pi ai",
                "GPT": "gi pi tê",
                "TTS": "ti ti ét",
                "CPU": "xê pi iu",
                "GPU": "gi pi iu",
                "USB": "iu ét bê",

            }

            self.save(data)

            return data

        with open(

            self.file,

            "r",

            encoding="utf-8",

        ) as f:

            return json.load(f)

    def save(

        self,

        data=None,

    ):

        if data is None:

            data = self.words

        with open(

            self.file,

            "w",

            encoding="utf-8",

        ) as f:

            json.dump(

                data,

                f,

                indent=4,

                ensure_ascii=False,

            )

    #
    # CRUD
    #

    def all(self):

        return dict(

            sorted(

                self.words.items()

            )

        )

    def add(

        self,

        word,

        speak,

    ):

        self.words[word] = speak

        self.save()

    def remove(

        self,

        word,

    ):

        if word in self.words:

            del self.words[word]

            self.save()

    def update(

        self,

        word,

        speak,

    ):

        self.words[word] = speak

        self.save()

    #
    # Repeat
    #

    def split_repeat(

        self,

        text,

    ):

        #
        # hahaha
        # -> ha ha ha
        #

        def repl(match):

            value = match.group()

            if len(value) < 6:

                return value

            if value == value[0] * len(value):

                return value

            if value.startswith("ha"):

                return " ".join(

                    [

                        "ha"

                    ] * (

                        len(value) // 2

                    )

                )

            return value

        return re.sub(

            r"[A-Za-z]{6,}",

            repl,

            text,

        )

    #
    # Replace
    #

    def replace_dictionary(

        self,

        text,

    ):

        for word in sorted(

            self.words,

            key=len,

            reverse=True,

        ):

            text = re.sub(

                rf"\b{re.escape(word)}\b",

                self.words[word],

                text,

            )

        return text

    #
    # Roman
    #

    def replace_roman(

        self,

        text,

    ):

        #
        # TODO
        #
        # Sprint sau
        #

        return text

    #
    # Main
    #

    def process(

        self,

        text,

    ):

        text = self.split_repeat(

            text

        )

        text = self.replace_dictionary(

            text

        )

        text = self.replace_roman(

            text

        )

        return text