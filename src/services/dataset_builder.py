from pathlib import Path
import shutil
import zipfile

from services.text_service import TextService
from services.log_service import LogService


class DatasetBuilder:

    def __init__(self):

        self.text = TextService()

        self.log = LogService()

    def build(
        self,
        source,
        output_dir,
    ):

        source = Path(source)

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        workspace = (
            output_dir
            / "_workspace"
        )

        if workspace.exists():

            shutil.rmtree(
                workspace
            )

        workspace.mkdir()

        #
        # Copy / Extract
        #

        if source.is_file():

            if source.suffix.lower() == ".zip":

                with zipfile.ZipFile(
                    source,
                    "r",
                ) as z:

                    z.extractall(
                        workspace
                    )

            else:

                shutil.copy2(
                    source,
                    workspace
                )

        else:

            for file in source.rglob("*"):

                if file.is_file():

                    shutil.copy2(
                        file,
                        workspace
                    )

        audio_files = []

        text_files = []

        for file in workspace.rglob("*"):

            if not file.is_file():

                continue

            suffix = file.suffix.lower()

            if suffix in (
                ".mp3",
                ".wav",
            ):

                audio_files.append(
                    file
                )

            elif suffix in (
                ".txt",
                ".docx",
            ):

                text_files.append(
                    file
                )

        dataset = []

        skipped = []

        errors = []

## ===== KẾT THÚC PART 1 =====
        #
        # Match chapter
        #

        for text_file in text_files:

            #
            # Bỏ file test
            #

            if self.text.is_test_file(
                text_file
            ):

                skipped.append(
                    f"TEST : {text_file.name}"
                )

                continue

            #
            # Đọc text
            #

            try:

                content = self.text.read(
                    text_file
                )

            except Exception as e:

                errors.append(
                    f"Không đọc được {text_file.name} : {e}"
                )

                continue

            content = self.text.normalize(
                content
            )

            #
            # Bỏ text còn tiếng Trung
            #

            if self.text.contains_chinese(
                content
            ):

                skipped.append(
                    f"Chinese : {text_file.name}"
                )

                continue

            #
            # Lấy số chương
            #

            chapter = self.text.extract_chapter_number(
                text_file
            )

            if chapter is None:

                errors.append(
                    f"Không xác định được chương : {text_file.name}"
                )

                continue

            #
            # Tìm tất cả audio của chương
            #

            audios = []

            for audio in audio_files:

                audio_chapter = self.text.extract_chapter_number(
                    audio
                )

                if audio_chapter == chapter:

                    audios.append(
                        audio
                    )

            if not audios:

                errors.append(
                    f"Thiếu audio : {text_file.name}"
                )

                continue

            audios = sorted(
                audios,
                key=lambda x: x.name.lower()
            )

            #
            # Chỉ ghép chương.
            # Chưa chia text.
            # Chưa cắt audio.
            #

            dataset.append(

                {
                    "chapter": chapter,

                    "text_file": text_file,

                    "text": content,

                    "audios": audios,
                }

            )

        #
        # Sort theo chương
        #

        dataset.sort(
            key=lambda x: x["chapter"]
        )

## ===== KẾT THÚC PART 2 =====
        #
        # Export dataset
        #

        metadata = []

        report = {

            "total": len(dataset),

            "skipped": skipped,

            "errors": errors,

            "items": []

        }

        for item in dataset:

            chapter = item["chapter"]

            text = item["text"]

            audios = item["audios"]

            for index, audio in enumerate(

                audios,

                start=1,

            ):

                #
                # TODO
                #
                # WhisperX
                #
                # transcript
                # = AlignmentService.align(
                #     audio,
                #     text,
                # )
                #
                # transcript.text
                # transcript.start
                # transcript.end
                #
                # Nếu không align được
                # -> bỏ sample
                #

                output_audio = (

                    output_dir
                    / f"{chapter:04d}_{index:03d}{audio.suffix}"

                )

                shutil.copy2(

                    audio,

                    output_audio,

                )

                metadata.append(

                    f"{output_audio.name}|{text}"

                )

                report["items"].append(

                    {

                        "chapter": chapter,

                        "audio": output_audio.name,

                        "text_length": len(text),

                    }

                )

        (
            output_dir
            / "metadata.list"
        ).write_text(

            "\n".join(metadata),

            encoding="utf-8",

        )

        import json

        with open(

            output_dir / "report.json",

            "w",

            encoding="utf-8",

        ) as f:

            json.dump(

                report,

                f,

                indent=4,

                ensure_ascii=False,

            )

        if errors:

            (

                output_dir
                / "errors.log"

            ).write_text(

                "\n".join(errors),

                encoding="utf-8",

            )

        if skipped:

            (

                output_dir
                / "skipped.log"

            ).write_text(

                "\n".join(skipped),

                encoding="utf-8",

            )

        shutil.rmtree(

            workspace,

            ignore_errors=True,

        )

        return report


## ===== KẾT THÚC FILE =====