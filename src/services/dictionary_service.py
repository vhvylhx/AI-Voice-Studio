from pathlib import Path


class DictionaryService:

    def __init__(self):

        self.root = Path("dictionary")

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.dictionary_file = (
            self.root / "dictionary.txt"
        )

        self.pronunciation_file = (
            self.root / "pronunciation.txt"
        )

        self.ads_file = (
            self.root / "ads.txt"
        )

        self.ensure_files()

    #
    # Initialize
    #

    def ensure_files(self):

        if not self.dictionary_file.exists():

            self.dictionary_file.write_text(
                (
                    "# Dictionary\n"
                    "# đúng 100% mới thay\n"
                    "# trái=phải\n\n"
                    "nhất bộ phân=một bộ phận\n"
                ),
                encoding="utf-8",
            )

        if not self.pronunciation_file.exists():

            self.pronunciation_file.write_text(
                (
                    "# Pronunciation\n"
                    "# chỉ phục vụ đọc\n\n"
                    "AI=ây ai\n"
                    "API=ây pi ai\n"
                    "GPT=gi pi tê\n"
                    "CPU=xê pi iu\n"
                    "GPU=gi pi iu\n"
                    "USB=iu ét bê\n"
                ),
                encoding="utf-8",
            )

        if not self.ads_file.exists():

            self.ads_file.write_text(
                (
                    "# Advertisement\n"
                    "# nguyên cụm mới xóa\n\n"
                    "Nguồn truyện=\n"
                    "Đọc truyện tại=\n"
                    "Truyện được copy từ=\n"
                ),
                encoding="utf-8",
            )

    #
    # Load
    #

    def load_pairs(
        self,
        file,
    ):

        result = []

        if not file.exists():

            return result

        for line in file.read_text(
            encoding="utf-8",
        ).splitlines():

            line = line.strip()

            if not line:

                continue

            if line.startswith("#"):

                continue

            if "=" not in line:

                continue

            left, right = line.split(
                "=",
                1,
            )

            left = left.strip()

            right = right.strip()

            if not left:

                continue

            result.append(
                (
                    left,
                    right,
                )
            )

        result.sort(
            key=lambda x: len(x[0]),
            reverse=True,
        )

        return result

    #
    # Public
    #

    def dictionary(self):

        return self.load_pairs(
            self.dictionary_file
        )

    def pronunciation(self):

        return self.load_pairs(
            self.pronunciation_file
        )

    def advertisements(self):

        return self.load_pairs(
            self.ads_file
        )

    #
    # Apply
    #

    def replace_exact(
        self,
        text,
    ):

        for source, target in self.dictionary():

            text = self.replace_words(
                text,
                source,
                target,
            )

        return text

    def replace_pronunciation(
        self,
        text,
    ):

        for source, target in self.pronunciation():

            text = self.replace_words(
                text,
                source,
                target,
            )

        return text

    def remove_ads(
        self,
        text,
    ):

        for source, _ in self.advertisements():

            text = text.replace(
                source,
                "",
            )

        return text

    #
    # Match theo CỤM TỪ
    #

    def is_word_char(
        self,
        ch,
    ):

        if not ch:

            return False

        return (
            ch.isalnum()
            or ch == "_"
        )

    def replace_words(
        self,
        text,
        source,
        target,
    ):

        source_cf = (
            source.casefold()
        )

        lower = (
            text.casefold()
        )

        start = 0

        while True:

            pos = lower.find(
                source_cf,
                start,
            )

            if pos < 0:

                break

            left_ok = (
                pos == 0
                or not self.is_word_char(
                    text[
                        pos - 1
                    ]
                )
            )

            end = (
                pos
                + len(source)
            )

            right_ok = (
                end >= len(text)
                or not self.is_word_char(
                    text[end]
                )
            )

## ===== KẾT THÚC PART 1 =====
            if left_ok and right_ok:

                text = (

                    text[:pos]

                    + target

                    + text[end:]

                )

                lower = (
                    text.casefold()
                )

                start = (
                    pos
                    + len(target)
                )

            else:

                start = (
                    pos + 1
                )

        return text


## ===== KẾT THÚC FILE =====