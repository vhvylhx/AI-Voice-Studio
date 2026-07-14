from pathlib import Path
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile


class DatasetService:

    AUDIO_EXTENSIONS = (
        ".mp3",
    )

    TEXT_EXTENSIONS = (
        ".txt",
        ".docx",
    )

    CHINESE_RE = re.compile(
        r"[\u3400-\u9fff]"
    )

    DEFAULT_OPTIONS = {
        "remove_ads": False,
        "remove_chapter_title": False,
        "remove_intro": False,
        "remove_outro": False,
    }

    def __init__(self):

        self.workspace = None

    def load(self):

        if self.workspace is None:

            from services.workspace_service import WorkspaceService

            self.workspace = WorkspaceService()

        return self.workspace.load()

    def prepare(
        self,
        source,
        output_dir,
        options=None,
    ):

        source = Path(source)

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        options = self.normalize_options(
            options
        )

        if source.is_file():

            if source.suffix.lower() != ".zip":

                raise Exception(
                    "Dataset phải là Folder hoặc ZIP."
                )

            root = (
                output_dir
                / "_source"
            )

            self.extract_zip(
                source,
                root,
            )

        else:

            root = source

        result = self.scan(
            root,
            output_dir=output_dir,
            options=options,
        )

        return result

    def extract_zip(
        self,
        zip_file,
        output_dir,
    ):

        output_dir = Path(output_dir)

        if output_dir.exists():

            shutil.rmtree(
                output_dir
            )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        root = output_dir.resolve()

        with zipfile.ZipFile(
            zip_file,
            "r",
        ) as archive:

            for member in archive.infolist():

                name = Path(member.filename)

                if name.is_absolute():

                    raise Exception(
                        f"ZIP không an toàn: {member.filename}"
                    )

                target = (
                    output_dir
                    / name
                ).resolve()

                try:

                    target.relative_to(
                        root
                    )

                except ValueError:

                    raise Exception(
                        f"ZIP không an toàn: {member.filename}"
                    )

                archive.extract(
                    member,
                    output_dir,
                )

    def scan(
        self,
        folder,
        output_dir=None,
        options=None,
    ):

        folder = Path(folder)

        options = self.normalize_options(
            options
        )

        text_files = self.collect_files(
            folder,
            self.TEXT_EXTENSIONS,
        )

        audio_files = self.collect_files(
            folder,
            self.AUDIO_EXTENSIONS,
        )

        errors = []

        items = []

        used_audio = set()

        text_records = []

        for text_file in text_files:

            record = self.read_text_record(
                text_file,
                folder,
                options,
            )

            text_records.append(
                record
            )

            if record["errors"]:

                errors.extend(
                    record["errors"]
                )

        valid_text_records = [
            record
            for record in text_records
            if not record["errors"]
        ]

        audio_records = []

        for audio_file in audio_files:

            record = self.read_audio_record(
                audio_file,
                folder,
            )

            audio_records.append(
                record
            )

            if record["errors"]:

                errors.extend(
                    record["errors"]
                )

        valid_audio_records = [
            record
            for record in audio_records
            if not record["errors"]
        ]

        for text_record in valid_text_records:

            matched_audio = self.match_audio(
                text_record["file"],
                valid_audio_records,
            )

            if not matched_audio:

                errors.append(
                    self.error(
                        text_record["file"],
                        "missing_audio",
                        "File text thiếu audio."
                    )
                )

                continue

            for audio_record in matched_audio:

                used_audio.add(
                    audio_record["file"]
                )

                items.append(
                    self.create_item(
                        len(items) + 1,
                        text_record,
                        audio_record,
                    )
                )

        for audio_record in valid_audio_records:

            if audio_record["file"] in used_audio:

                continue

            errors.append(
                self.error(
                    audio_record["file"],
                    "missing_text",
                    "File audio thiếu text."
                )
            )

        result = self.create_result(
            folder,
            output_dir,
            options,
            items,
            errors,
        )

        if output_dir is not None:

            self.write_outputs(
                output_dir,
                result,
            )

        return result

    def collect_files(
        self,
        folder,
        extensions,
    ):

        result = []

        if not folder.exists():

            return result

        for file in folder.rglob("*"):

            if not file.is_file():

                continue

            if file.suffix.lower() not in extensions:

                continue

            result.append(
                file
            )

        return sorted(
            result,
            key=lambda x: str(x).lower(),
        )

    def read_text_record(
        self,
        file,
        root,
        options,
    ):

        errors = []

        content = ""

        raw_content = ""

        if self.has_chinese(
            file.name
        ):

            errors.append(
                self.error(
                    file,
                    "chinese_filename",
                    "Tên file text còn ký tự Trung."
                )
            )

        if self.is_empty_file(
            file
        ):

            errors.append(
                self.error(
                    file,
                    "empty_file",
                    "File text rỗng."
                )
            )

            return {
                "file": file,
                "relative_path": self.relative_path(
                    file,
                    root,
                ),
                "content": content,
                "raw_content": raw_content,
                "errors": errors,
            }

        try:

            raw_content = self.read_text(
                file
            )

        except Exception as e:

            errors.append(
                self.error(
                    file,
                    "broken_file",
                    f"Không đọc được file text: {e}"
                )
            )

            return {
                "file": file,
                "relative_path": self.relative_path(
                    file,
                    root,
                ),
                "content": content,
                "raw_content": raw_content,
                "errors": errors,
            }

        content = self.clean_text(
            raw_content,
            options,
        )

        if not content.strip():

            errors.append(
                self.error(
                    file,
                    "empty_content",
                    "Nội dung text rỗng."
                )
            )

        if self.has_chinese(
            content
        ):

            errors.append(
                self.error(
                    file,
                    "chinese_content",
                    "Nội dung text còn ký tự Trung."
                )
            )

        return {
            "file": file,
            "relative_path": self.relative_path(
                file,
                root,
            ),
            "content": content,
            "raw_content": raw_content,
            "errors": errors,
        }

    def read_audio_record(
        self,
        file,
        root,
    ):

        errors = []

        if self.has_chinese(
            file.name
        ):

            errors.append(
                self.error(
                    file,
                    "chinese_filename",
                    "Tên file audio còn ký tự Trung."
                )
            )

        if self.is_empty_file(
            file
        ):

            errors.append(
                self.error(
                    file,
                    "empty_file",
                    "File audio rỗng."
                )
            )

        try:

            with file.open(
                "rb"
            ) as f:

                f.read(
                    1
                )

        except Exception as e:

            errors.append(
                self.error(
                    file,
                    "broken_file",
                    f"Không đọc được file audio: {e}"
                )
            )

        return {
            "file": file,
            "relative_path": self.relative_path(
                file,
                root,
            ),
            "errors": errors,
        }

    def read_text(
        self,
        file,
    ):

        suffix = file.suffix.lower()

        if suffix == ".txt":

            return file.read_text(
                encoding="utf-8-sig",
            )

        if suffix == ".docx":

            try:

                from docx import Document

                doc = Document(
                    file
                )

                return "\n".join(
                    paragraph.text
                    for paragraph in doc.paragraphs
                )

            except ImportError:

                return self.read_docx_without_dependency(
                    file
                )

        raise Exception(
            f"Không hỗ trợ định dạng: {suffix}"
        )

    def read_docx_without_dependency(
        self,
        file,
    ):

        namespace = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

        with zipfile.ZipFile(
            file,
            "r",
        ) as archive:

            xml = archive.read(
                "word/document.xml"
            )

        root = ET.fromstring(
            xml
        )

        paragraphs = []

        for paragraph in root.findall(
            ".//w:p",
            namespace,
        ):

            texts = []

            for node in paragraph.findall(
                ".//w:t",
                namespace,
            ):

                if node.text:

                    texts.append(
                        node.text
                    )

            paragraphs.append(
                "".join(
                    texts
                )
            )

        return "\n".join(
            paragraphs
        )

    def clean_text(
        self,
        text,
        options=None,
    ):

        options = self.normalize_options(
            options
        )

        lines = []

        for line in text.replace(
            "\r",
            "\n",
        ).splitlines():

            line = line.strip()

            if not line:

                lines.append(
                    ""
                )

                continue

            if (
                options["remove_chapter_title"]
                and self.is_chapter_title(line)
            ):

                continue

            if (
                options["remove_ads"]
                and self.is_ad_line(line)
            ):

                continue

            if (
                options["remove_intro"]
                and self.is_intro_line(line)
            ):

                continue

            if (
                options["remove_outro"]
                and self.is_outro_line(line)
            ):

                continue

            lines.append(
                line
            )

        return "\n".join(
            lines
        ).strip()

    def match_audio(
        self,
        text_file,
        audio_records,
    ):

        text_key = self.match_key(
            text_file
        )

        matched = []

        for audio_record in audio_records:

            audio_key = self.match_key(
                audio_record["file"]
            )

            if audio_key == text_key:

                matched.append(
                    audio_record
                )

                continue

            if audio_key.startswith(
                f"{text_key}_"
            ) or audio_key.startswith(
                f"{text_key}-"
            ) or audio_key.startswith(
                f"{text_key} "
            ):

                matched.append(
                    audio_record
                )

        return sorted(
            matched,
            key=lambda x: str(x["file"]).lower(),
        )

    def match_key(
        self,
        file,
    ):

        return Path(file).stem.strip().lower()

    def create_item(
        self,
        index,
        text_record,
        audio_record,
    ):

        content = text_record["content"]

        return {
            "id": f"{index:06d}",
            "audio": audio_record["file"],
            "text": text_record["file"],
            "content": content,
            "audio_path": str(audio_record["file"]),
            "text_path": str(text_record["file"]),
            "audio_relative_path": audio_record["relative_path"],
            "text_relative_path": text_record["relative_path"],
            "audio_sha256": self.sha256(
                audio_record["file"]
            ),
            "text_sha256": self.sha256(
                text_record["file"]
            ),
            "content_sha256": self.text_sha256(
                content
            ),
            "text_length": len(
                content
            ),
        }

    def create_result(
        self,
        root,
        output_dir,
        options,
        items,
        errors,
    ):

        summary = {
            "valid_pairs": len(
                items
            ),
            "error_count": len(
                errors
            ),
        }

        manifest = {
            "schema_version": 1,
            "source_root": str(
                Path(root)
            ),
            "options": options,
            "summary": summary,
            "items": self.serialize_items(
                items
            ),
        }

        report = {
            "schema_version": 1,
            "summary": summary,
            "errors": errors,
            "manifest": "manifest.json",
            "metadata": "metadata.list",
        }

        if output_dir is not None:

            manifest["output_dir"] = str(
                Path(output_dir)
            )

        return {
            "items": items,
            "errors": errors,
            "summary": summary,
            "manifest": manifest,
            "report": report,
        }

    def serialize_items(
        self,
        items,
    ):

        result = []

        for item in items:

            result.append(
                {
                    "id": item["id"],
                    "audio": item["audio_relative_path"],
                    "text": item["text_relative_path"],
                    "audio_sha256": item["audio_sha256"],
                    "text_sha256": item["text_sha256"],
                    "content_sha256": item["content_sha256"],
                    "text_length": item["text_length"],
                }
            )

        return result

    def write_outputs(
        self,
        output_dir,
        result,
    ):

        output_dir = Path(output_dir)

        self.write_json(
            output_dir / "manifest.json",
            result["manifest"],
        )

        self.write_json(
            output_dir / "report.json",
            result["report"],
        )

        metadata = []

        for item in result["items"]:

            metadata.append(
                f"{item['audio_path']}|{item['content']}"
            )

        (
            output_dir
            / "metadata.list"
        ).write_text(
            "\n".join(metadata),
            encoding="utf-8",
        )

        if result["errors"]:

            (
                output_dir
                / "errors.log"
            ).write_text(
                "\n".join(
                    f"{error['file']} | {error['code']} | {error['message']}"
                    for error in result["errors"]
                ),
                encoding="utf-8",
            )

    def write_json(
        self,
        file,
        data,
    ):

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )

    def normalize_options(
        self,
        options=None,
    ):

        result = dict(
            self.DEFAULT_OPTIONS
        )

        if options is None:

            return result

        if isinstance(
            options,
            dict,
        ):

            source = options

        else:

            source = {
                key: getattr(
                    options,
                    key,
                    False,
                )
                for key in result
            }

        for key in result:

            result[key] = bool(
                source.get(
                    key,
                    result[key],
                )
            )

        return result

    def error(
        self,
        file,
        code,
        message,
    ):

        return {
            "file": str(
                file
            ),
            "code": code,
            "message": message,
        }

    def relative_path(
        self,
        file,
        root,
    ):

        try:

            return str(
                Path(file).relative_to(
                    Path(root)
                )
            )

        except ValueError:

            return str(
                file
            )

    def sha256(
        self,
        file,
    ):

        h = hashlib.sha256()

        with Path(file).open(
            "rb"
        ) as f:

            for chunk in iter(
                lambda: f.read(1024 * 1024),
                b"",
            ):

                h.update(
                    chunk
                )

        return h.hexdigest()

    def text_sha256(
        self,
        text,
    ):

        return hashlib.sha256(
            text.encode(
                "utf-8"
            )
        ).hexdigest()

    def is_empty_file(
        self,
        file,
    ):

        try:

            return Path(file).stat().st_size == 0

        except OSError:

            return True

    def has_chinese(
        self,
        text,
    ):

        return bool(
            self.CHINESE_RE.search(
                text
            )
        )

    def is_chapter_title(
        self,
        line,
    ):

        return bool(
            re.match(
                r"^\s*(chương|chapter)\s+\d+",
                line,
                flags=re.I,
            )
        )

    def is_ad_line(
        self,
        line,
    ):

        return bool(
            re.search(
                r"(quảng cáo|advertisement|sponsor)",
                line,
                flags=re.I,
            )
        )

    def is_intro_line(
        self,
        line,
    ):

        return bool(
            re.search(
                r"^(intro|mở đầu)\b",
                line,
                flags=re.I,
            )
        )

    def is_outro_line(
        self,
        line,
    ):

        return bool(
            re.search(
                r"^(outro|kết thúc)\b",
                line,
                flags=re.I,
            )
        )
