import re


class CleanupService:

    CHINESE_RE = re.compile(
        r"[\u3400-\u9FFF]"
    )

    BRACKET_RE = re.compile(
        r"[\(\[\{（【][^)\]】}]*[\u3400-\u9FFF][^)\]】}]*[\)\]\}）】]"
    )

    def clean(
        self,
        text,
    ):

        report = []

        #
        # (蛰)
        #

        text = self.remove_chinese_brackets(
            text,
            report,
        )

        #
        # Ký tự Trung còn sót
        #

        text = self.remove_chinese(
            text,
            report,
        )

        #
        # Khoảng trắng
        #

        text = self.normalize_space(
            text,
        )

        return (
            text,
            report,
        )

    #
    # (蛰)
    #

    def remove_chinese_brackets(
        self,
        text,
        report,
    ):

        found = self.BRACKET_RE.findall(
            text
        )

        if found:

            report.extend(found)

        return self.BRACKET_RE.sub(
            "",
            text,
        )


## ===== KẾT THÚC PART 1 =====
    #
    # Trung còn sót
    #

    def remove_chinese(
        self,
        text,
        report,
    ):

        found = list(

            dict.fromkeys(

                self.CHINESE_RE.findall(
                    text
                )

            )

        )

        if found:

            report.extend(found)

        return self.CHINESE_RE.sub(
            "",
            text,
        )

    #
    # Space
    #

    def normalize_space(
        self,
        text,
    ):

        lines = []

        for line in text.splitlines():

            line = re.sub(
                r"[ \t]+",
                " ",
                line,
            ).strip()

            lines.append(
                line
            )

        return "\n".join(
            lines
        )


## ===== KẾT THÚC FILE =====