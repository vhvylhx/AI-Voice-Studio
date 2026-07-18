from pathlib import Path


class StyleProfileExtractionService:

    def __init__(
        self,
        repository=None,
    ):

        self.repository = repository

    def prepare_extraction(
        self,
        style_profile_id,
        capabilities=None,
    ):

        state = {
            "style_profile_id": style_profile_id,
            "status": "blocked",
            "message_vi": (
                "Engine trich xuat Voice DNA/Reading Style chua duoc cai dat trong sprint nay."
            ),
            "missing_components": [
                "prosody_analyzer",
            ],
            "requested_capabilities": capabilities or [],
        }

        self.write_state(
            style_profile_id,
            state,
        )

        return state

    def start_extraction(
        self,
        style_profile_id,
    ):

        return self.prepare_extraction(
            style_profile_id
        )

    def cancel_extraction(
        self,
        style_profile_id,
    ):

        state = self.get_extraction_state(
            style_profile_id
        )

        state["status"] = "cancelled"

        self.write_state(
            style_profile_id,
            state,
        )

        return state

    def resume_extraction(
        self,
        style_profile_id,
    ):

        return self.prepare_extraction(
            style_profile_id
        )

    def get_extraction_state(
        self,
        style_profile_id,
    ):

        if self.repository is None:

            return {
                "style_profile_id": style_profile_id,
                "status": "unknown",
            }

        file = (
            self.repository.profile_dir(
                style_profile_id
            )
            / "extraction_state.json"
        )

        if not file.exists():

            return {
                "style_profile_id": style_profile_id,
                "status": "pending",
            }

        import json

        return json.loads(
            file.read_text(
                encoding="utf-8"
            )
        )

    def build_report(
        self,
        style_profile_id,
    ):

        state = self.get_extraction_state(
            style_profile_id
        )

        return {
            "style_profile_id": style_profile_id,
            "status": state.get(
                "status",
                "pending",
            ),
            "completed": False,
            "message_vi": state.get(
                "message_vi",
                "Chua co bao cao trich xuat.",
            ),
        }

    def write_state(
        self,
        style_profile_id,
        state,
    ):

        if self.repository is None:

            return

        folder = self.repository.profile_dir(
            style_profile_id
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.repository.atomic_write_json(
            Path(
                folder
            )
            / "extraction_state.json",
            state,
        )

