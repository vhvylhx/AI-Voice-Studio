from pathlib import Path
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile
import re

from services.text_matching_service import TextMatchingService


class DatasetService:

    AUDIO_EXTENSIONS = (
        ".mp3",
    )

    TEXT_EXTENSIONS = (
        ".txt",
        ".docx",
    )

    DEFAULT_OPTIONS = {
        "remove_ads": False,
        "remove_chapter_title": False,
        "remove_intro": False,
        "remove_outro": False,
    }

    def __init__(self):

        self.workspace = None

        self.matching = TextMatchingService()

        self.last_total_text = 0

        self.last_total_audio = 0

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

            root = output_dir / "_source"

            self.extract_zip(
                source,
                root,
            )

        else:

            root = source

        return self.scan(
            root,
            output_dir=output_dir,
            options=options,
        )

    def repair(
        self,
        dataset_result,
        output_dir,
        config=None,
    ):

        from services.dataset_repair_service import DatasetRepairService

        return DatasetRepairService().repair(
            dataset_result,
            output_dir,
            config=config,
        )

    def review(
        self,
        dataset_result=None,
        repair_report=None,
        output_dir=None,
        config=None,
    ):

        from services.dataset_review_service import DatasetReviewService

        return DatasetReviewService().create_review(
            dataset_result=dataset_result,
            repair_report=repair_report,
            output_dir=output_dir,
            config=config,
        )

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

        self.last_total_text = len(
            text_files
        )

        self.last_total_audio = len(
            audio_files
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

            errors.extend(
                record["errors"]
            )

        audio_records = []

        for audio_file in audio_files:

            record = self.read_audio_record(
                audio_file,
                folder,
            )

            audio_records.append(
                record
            )

            errors.extend(
                record["errors"]
            )

        valid_text_records = self.remove_duplicates(
            [
                record
                for record in text_records
                if not record["errors"]
            ],
            "text",
            errors,
        )

        valid_audio_records = self.remove_duplicates(
            [
                record
                for record in audio_records
                if not record["errors"]
            ],
            "audio",
            errors,
        )

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
                        "Không tìm thấy audio cho text.",
                        "Kiểm tra tên file hoặc bổ sung MP3 cùng số chương.",
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
                    "Không tìm thấy text cho audio.",
                    "Kiểm tra tên file hoặc bổ sung TXT/DOCX cùng số chương.",
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

            Path(
                output_dir
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

            self.write_outputs(
                output_dir,
                result,
            )

        return result

    def scan_folders(
        self,
        audio_folder,
        text_folder,
        output_dir=None,
        options=None,
    ):

        audio_folder = Path(
            audio_folder
        )

        text_folder = Path(
            text_folder
        )

        options = self.normalize_options(
            options
        )

        text_files = self.collect_files(
            text_folder,
            self.TEXT_EXTENSIONS,
        )

        audio_files = self.collect_files(
            audio_folder,
            self.AUDIO_EXTENSIONS,
        )

        self.last_total_text = len(
            text_files
        )

        self.last_total_audio = len(
            audio_files
        )

        errors = []

        items = []

        used_audio = set()

        text_records = []

        for text_file in text_files:

            record = self.read_text_record(
                text_file,
                text_folder,
                options,
            )

            text_records.append(
                record
            )

            errors.extend(
                record["errors"]
            )

        audio_records = []

        for audio_file in audio_files:

            record = self.read_audio_record(
                audio_file,
                audio_folder,
            )

            audio_records.append(
                record
            )

            errors.extend(
                record["errors"]
            )

        valid_text_records = self.remove_duplicates(
            [
                record
                for record in text_records
                if not record["errors"]
            ],
            "text",
            errors,
        )

        valid_audio_records = self.remove_duplicates(
            [
                record
                for record in audio_records
                if not record["errors"]
            ],
            "audio",
            errors,
        )

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
                        "Khong tim thay audio cho text.",
                        "Kiem tra ten file hoac bo sung MP3 cung so chuong.",
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
                    "Khong tim thay text cho audio.",
                    "Kiem tra ten file hoac bo sung TXT/DOCX cung so chuong.",
                )
            )

        result = self.create_result(
            {
                "audio_folder": audio_folder,
                "text_folder": text_folder,
            },
            output_dir,
            options,
            items,
            errors,
        )

        if output_dir is not None:

            Path(
                output_dir
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

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

        if self.is_test_file(
            file
        ):

            errors.append(
                self.error(
                    file,
                    "test_version",
                    "File text có dấu hiệu test, không ghép tự động.",
                    "Đổi tên nếu đây là dữ liệu thật; nếu là test thì giữ ngoài dataset train.",
                )
            )

        if self.match_info(
            file
        )["chapter"] is None:

            errors.append(
                self.error(
                    file,
                    "invalid_filename",
                    "Không lấy được số chương từ tên file text.",
                    "Đổi tên file để chứa số chương, ví dụ 171.txt hoặc Chương 171.txt.",
                )
            )

        if self.is_empty_file(
            file
        ):

            errors.append(
                self.error(
                    file,
                    "empty_file",
                    "File text rỗng.",
                    "Kiểm tra nội dung file text.",
                )
            )

            return self.text_record(
                file,
                root,
                content,
                raw_content,
                errors,
            )

        try:

            raw_content = self.read_text(
                file
            )

        except Exception as e:

            errors.append(
                self.error(
                    file,
                    "broken_file",
                    f"Không đọc được file text: {e}",
                    "Kiểm tra file có hỏng hoặc sai định dạng không.",
                )
            )

            return self.text_record(
                file,
                root,
                content,
                raw_content,
                errors,
            )

        content = self.clean_text(
            raw_content,
            options,
        )

        if not content.strip():

            errors.append(
                self.error(
                    file,
                    "empty_content",
                    "Nội dung text rỗng.",
                    "Kiểm tra nội dung sau khi đọc TXT/DOCX.",
                )
            )

        if self.matching.filename_content_mismatch(
            file,
            content,
        ):

            errors.append(
                self.error(
                    file,
                    "filename_content_mismatch",
                    "Số chương trong tên file không khớp nội dung text.",
                    "Kiểm tra lại tên file và nội dung chương; không tự ghép sang chương khác.",
                )
            )

        return self.text_record(
            file,
            root,
            content,
            raw_content,
            errors,
        )

    def text_record(
        self,
        file,
        root,
        content,
        raw_content,
        errors,
    ):

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

        if self.is_test_file(
            file
        ):

            errors.append(
                self.error(
                    file,
                    "test_version",
                    "File audio có dấu hiệu test, không ghép tự động.",
                    "Đổi tên nếu đây là dữ liệu thật; nếu là test thì giữ ngoài dataset train.",
                )
            )

        if self.match_info(
            file
        )["chapter"] is None:

            errors.append(
                self.error(
                    file,
                    "invalid_filename",
                    "Không lấy được số chương từ tên file audio.",
                    "Đổi tên file để chứa số chương, ví dụ 171.mp3.",
                )
            )

        if self.is_empty_file(
            file
        ):

            errors.append(
                self.error(
                    file,
                    "empty_file",
                    "File audio rỗng.",
                    "Kiểm tra lại file MP3.",
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
                    f"Không đọc được file audio: {e}",
                    "Kiểm tra file có hỏng hoặc quyền đọc file.",
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

    def remove_duplicates(
        self,
        records,
        kind,
        errors,
    ):

        result = []

        seen = {}

        for record in records:

            key = self.matching.duplicate_key(
                record["file"],
                kind,
            )

            if key in seen:

                errors.append(
                    self.error(
                        record["file"],
                        "duplicate",
                        f"File {kind} trùng khóa ghép với file khác.",
                        "Giữ lại một file đúng, đổi tên hoặc đưa file trùng ra khỏi dataset.",
                    )
                )

                continue

            seen[key] = record

            result.append(
                record
            )

        return result

    def match_audio(
        self,
        text_file,
        audio_records,
    ):

        return self.matching.match_audio(
            text_file,
            audio_records,
        )

    def match_key(
        self,
        file,
    ):

        return self.matching.match_key(
            file
        )

    def match_info(
        self,
        file,
    ):

        return self.matching.chapter_info(
            file
        )

    def audio_match_sort_key(
        self,
        audio_record,
    ):

        return self.matching.audio_sort_key(
            audio_record
        )

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
            "match_rule": audio_record.get(
                "match_rule",
                "",
            ),
            "match_key": audio_record.get(
                "match_key",
                "",
            ),
            "audio_part": audio_record.get(
                "audio_part",
                None,
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

        health = self.create_health(
            items,
            errors,
        )

        summary = {
            "valid_pairs": len(
                items
            ),
            "error_count": len(
                errors
            ),
            "health": health,
        }

        manifest = {
            "schema_version": 2,
            "options": options,
            "summary": summary,
            "health": health,
            "items": self.serialize_items(
                items
            ),
        }

        report = {
            "schema_version": 2,
            "summary": summary,
            "health": health,
            "errors": errors,
            "manifest": "manifest.json",
            "metadata": "metadata.list",
        }

        if isinstance(
            root,
            dict,
        ):

            manifest["source_roots"] = {
                key: str(
                    Path(
                        value
                    )
                )
                for key, value in root.items()
            }

        else:

            manifest["source_root"] = str(
                Path(root)
            )

        if output_dir is not None:

            manifest["output_dir"] = str(
                Path(output_dir)
            )

        return {
            "items": items,
            "errors": errors,
            "summary": summary,
            "health": health,
            "manifest": manifest,
            "report": report,
        }

    def create_health(
        self,
        items,
        errors,
    ):

        counts = {
            "total_mp3": self.last_total_audio,
            "total_text": self.last_total_text,
            "matched": len(
                items
            ),
            "unmatched": 0,
            "filename_content_mismatch": 0,
            "duplicate": 0,
            "missing_audio": 0,
            "missing_text": 0,
            "invalid_filename": 0,
            "test_version": 0,
            "empty_file": 0,
            "empty_content": 0,
            "broken_file": 0,
            "usable_percent": 0.0,
            "blocking_errors": 0,
        }

        for error in errors:

            code = error.get(
                "code",
                "",
            )

            if code in counts:

                counts[code] += 1

        counts["unmatched"] = (
            counts["missing_audio"]
            + counts["missing_text"]
        )

        counts["blocking_errors"] = sum(
            1
            for error in errors
            if error.get(
                "code"
            )
            in (
                "missing_audio",
                "missing_text",
                "test_version",
                "invalid_filename",
                "filename_content_mismatch",
                "duplicate",
                "empty_file",
                "empty_content",
                "broken_file",
            )
        )

        if counts["total_mp3"]:

            counts["usable_percent"] = round(
                counts["matched"]
                / counts["total_mp3"]
                * 100,
                2,
            )

        return counts

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
                    "match_rule": item.get(
                        "match_rule",
                        "",
                    ),
                    "match_key": item.get(
                        "match_key",
                        "",
                    ),
                    "audio_part": item.get(
                        "audio_part",
                        None,
                    ),
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

        (output_dir / "metadata.list").write_text(
            "\n".join(
                metadata
            ),
            encoding="utf-8",
        )

        if result["errors"]:

            (output_dir / "errors.log").write_text(
                "\n".join(
                    f"{error['file']} | {error['code']} | {error['message']} | {error.get('suggestion', '')}"
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
        suggestion="",
    ):

        return {
            "file": str(
                file
            ),
            "code": code,
            "message": message,
            "reason": message,
            "suggestion": suggestion,
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

    def is_test_file(
        self,
        file,
    ):

        return self.matching.is_test_file(
            file
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
