from pathlib import Path
import json
import re

from services.audio_service import AudioService
from services.dataset_service import DatasetService


class DatasetSegmentationService:

    def __init__(self):

        self.audio = AudioService()

        self.dataset = DatasetService()

    def prepare(
        self,
        source,
        dataset_dir,
        output_dir,
        options=None,
    ):

        dataset = self.dataset.prepare(
            source,
            dataset_dir,
            options=options,
        )

        return self.segment(
            dataset,
            output_dir,
        )

    def segment(
        self,
        dataset,
        output_dir,
    ):

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        items = dataset.get(
            "items",
            [],
        )

        groups = self.group_by_text(
            items
        )

        valid = []

        suspicious = []

        for text_path, group in groups.items():

            group = self.sort_audio_group(
                group
            )

            text = group[0].get(
                "content",
                "",
            )

            text_units = self.split_text_units(
                text
            )

            if len(group) == 1:

                self.add_segment(
                    valid,
                    suspicious,
                    group[0],
                    text,
                    "single_audio_text",
                )

                continue

            if len(text_units) == len(group):

                for index, item in enumerate(
                    group
                ):

                    self.add_segment(
                        valid,
                        suspicious,
                        item,
                        text_units[index],
                        "ordered_audio_paragraph",
                    )

                continue

            suspicious.append(
                {
                    "status": "suspicious",
                    "code": "manual_alignment_required",
                    "message": (
                        "Một text ghép với nhiều audio nhưng số đoạn text "
                        "không khớp chắc chắn với số audio."
                    ),
                    "text": str(
                        text_path
                    ),
                    "audio": [
                        str(
                            item["audio"]
                        )
                        for item in group
                    ],
                    "audio_count": len(
                        group
                    ),
                    "text_unit_count": len(
                        text_units
                    ),
                    "text_length": len(
                        text
                    ),
                }
            )

        missing_text = self.filter_dataset_errors(
            dataset,
            "missing_text",
        )

        missing_audio = self.filter_dataset_errors(
            dataset,
            "missing_audio",
        )

        report = self.create_report(
            valid,
            suspicious,
            missing_text,
            missing_audio,
            dataset,
        )

        manifest = self.create_manifest(
            valid,
            suspicious,
            report,
        )

        self.write_outputs(
            output_dir,
            manifest,
            report,
            valid,
        )

        return {
            "valid": valid,
            "suspicious": suspicious,
            "missing_text": missing_text,
            "missing_audio": missing_audio,
            "manifest": manifest,
            "report": report,
        }

    def add_segment(
        self,
        valid,
        suspicious,
        item,
        text,
        reason,
    ):

        audio_file = Path(
            item["audio"]
        )

        try:

            audio_info = self.audio.probe(
                audio_file
            )

        except Exception as e:

            suspicious.append(
                {
                    "status": "suspicious",
                    "code": "broken_audio",
                    "message": f"Không đọc được audio bằng ffprobe: {e}",
                    "audio": str(
                        audio_file
                    ),
                    "text": item.get(
                        "text_path",
                        "",
                    ),
                }
            )

            return

        if not text.strip():

            suspicious.append(
                {
                    "status": "suspicious",
                    "code": "empty_segment_text",
                    "message": "Đoạn text rỗng.",
                    "audio": str(
                        audio_file
                    ),
                    "text": item.get(
                        "text_path",
                        "",
                    ),
                    "audio_info": audio_info,
                }
            )

            return

        valid.append(
            {
                "id": f"{len(valid) + 1:06d}",
                "status": "valid",
                "reason": reason,
                "audio": str(
                    audio_file
                ),
                "text": item.get(
                    "text_path",
                    "",
                ),
                "content": text,
                "duration": audio_info["duration"],
                "sample_rate": audio_info["sample_rate"],
                "channels": audio_info["channels"],
                "channel_layout": audio_info["channel_layout"],
                "codec": audio_info["codec"],
            }
        )

    def group_by_text(
        self,
        items,
    ):

        groups = {}

        for item in items:

            key = Path(
                item["text"]
            )

            if key not in groups:

                groups[key] = []

            groups[key].append(
                item
            )

        return groups

    def sort_audio_group(
        self,
        group,
    ):

        return sorted(
            group,
            key=lambda item: self.audio_sort_key(
                item["audio"]
            ),
        )

    def audio_sort_key(
        self,
        file,
    ):

        stem = Path(file).stem.lower()

        parts = re.findall(
            r"\d+|\D+",
            stem,
        )

        key = []

        for part in parts:

            if part.isdigit():

                key.append(
                    (
                        0,
                        int(part),
                    )
                )

            else:

                key.append(
                    (
                        1,
                        part.strip(),
                    )
                )

        return key

    def split_text_units(
        self,
        text,
    ):

        units = []

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(
                r"\n\s*\n",
                text,
            )
            if paragraph.strip()
        ]

        if len(paragraphs) > 1:

            return paragraphs

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if len(lines) > 1:

            units.extend(
                lines
            )

        return units

    def filter_dataset_errors(
        self,
        dataset,
        code,
    ):

        return [
            error
            for error in dataset.get(
                "errors",
                [],
            )
            if error.get(
                "code"
            ) == code
        ]

    def create_report(
        self,
        valid,
        suspicious,
        missing_text,
        missing_audio,
        dataset,
    ):

        return {
            "schema_version": 1,
            "summary": {
                "valid_segments": len(
                    valid
                ),
                "suspicious_segments": len(
                    suspicious
                ),
                "missing_text": len(
                    missing_text
                ),
                "missing_audio": len(
                    missing_audio
                ),
                "dataset_errors": len(
                    dataset.get(
                        "errors",
                        [],
                    )
                ),
            },
            "valid": self.strip_content(
                valid
            ),
            "suspicious": suspicious,
            "missing_text": missing_text,
            "missing_audio": missing_audio,
        }

    def create_manifest(
        self,
        valid,
        suspicious,
        report,
    ):

        return {
            "schema_version": 1,
            "summary": report["summary"],
            "segments": [
                {
                    "id": item["id"],
                    "audio": item["audio"],
                    "text": item["text"],
                    "duration": item["duration"],
                    "sample_rate": item["sample_rate"],
                    "channels": item["channels"],
                    "text_length": len(
                        item["content"]
                    ),
                    "reason": item["reason"],
                }
                for item in valid
            ],
            "suspicious": suspicious,
        }

    def strip_content(
        self,
        valid,
    ):

        return [
            {
                key: value
                for key, value in item.items()
                if key != "content"
            }
            for item in valid
        ]

    def write_outputs(
        self,
        output_dir,
        manifest,
        report,
        valid,
    ):

        self.write_json(
            output_dir / "segmentation_manifest.json",
            manifest,
        )

        self.write_json(
            output_dir / "segmentation_report.json",
            report,
        )

        metadata = []

        for segment in valid:

            metadata.append(
                f"{segment['audio']}|{segment['content']}"
            )

        (
            output_dir
            / "segmentation_metadata.list"
        ).write_text(
            "\n".join(
                metadata
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
