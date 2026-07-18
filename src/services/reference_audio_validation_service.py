from pathlib import Path


class ReferenceAudioValidationService:

    AUDIO_EXTENSIONS = {
        ".mp3",
        ".wav",
        ".flac",
        ".m4a",
    }

    def __init__(
        self,
        audio_service=None,
    ):

        self.audio_service = audio_service

    def validate_file(
        self,
        audio_path,
        transcript="",
        transcript_required=False,
    ):

        messages = []

        if not str(
            audio_path or ""
        ).strip():

            messages.append(
                self.issue(
                    "missing",
                    "Chua chon audio tham chieu.",
                )
            )

            return self.result(
                "missing",
                messages,
            )

        file = Path(
            audio_path
        )

        if not file.exists():

            messages.append(
                self.issue(
                    "audio_missing",
                    "Audio tham chieu khong ton tai.",
                    str(
                        file
                    ),
                )
            )

        elif file.suffix.lower() not in self.AUDIO_EXTENSIONS:

            messages.append(
                self.issue(
                    "audio_extension_unsupported",
                    "Dinh dang audio tham chieu chua duoc ho tro.",
                    str(
                        file
                    ),
                )
            )

        if (
            transcript_required
            and not str(
                transcript or ""
            ).strip()
        ):

            messages.append(
                self.issue(
                    "reference_text_required",
                    "Engine yeu cau transcript cho audio tham chieu.",
                )
            )

        metadata = {}

        if (
            file.exists()
            and file.suffix.lower() in self.AUDIO_EXTENSIONS
            and self.audio_service is not None
        ):

            try:

                metadata = self.audio_service.probe(
                    file
                )

            except Exception as exc:

                messages.append(
                    self.issue(
                        "audio_probe_failed",
                        f"Khong doc duoc thong tin audio: {exc}",
                        str(
                            file
                        ),
                    )
                )

        state = "valid" if not messages else "invalid"

        return self.result(
            state,
            messages,
            metadata,
        )

    def validate_folder(
        self,
        folder,
    ):

        path = Path(
            folder or ""
        )

        messages = []

        if not str(
            folder or ""
        ).strip() or not path.exists():

            messages.append(
                self.issue(
                    "folder_missing",
                    "Thu muc audio tham chieu khong ton tai.",
                    str(
                        path
                    ),
                )
            )

            return self.result(
                "missing",
                messages,
            )

        audio_files = [
            item
            for item in path.rglob("*")
            if item.is_file()
            and item.suffix.lower() in self.AUDIO_EXTENSIONS
        ]

        if not audio_files:

            messages.append(
                self.issue(
                    "folder_empty",
                    "Thu muc khong co audio tham chieu hop le.",
                    str(
                        path
                    ),
                )
            )

        return self.result(
            "valid" if not messages else "invalid",
            messages,
            {
                "audio_count": len(
                    audio_files
                ),
            },
        )

    def issue(
        self,
        code,
        reason,
        path="",
    ):

        return {
            "code": code,
            "reason": reason,
            "path": path,
            "suggestion": "Chon lai file/folder tham chieu hop le.",
        }

    def result(
        self,
        state,
        messages,
        metadata=None,
    ):

        return {
            "state": state,
            "ok": state == "valid",
            "messages": messages,
            "metadata": metadata or {},
        }
