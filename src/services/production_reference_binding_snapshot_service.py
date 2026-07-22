import hashlib
import json
from pathlib import Path

from services.production_reference_binding_service import (
    ProductionReferenceBindingError,
    ProductionReferenceBindingService,
)


class ProductionReferenceBindingSnapshotService:

    SNAPSHOT_FILE = "production_reference_binding.json"

    def __init__(
        self,
        root="workspace/production_reference_binding",
        binding_service=None,
    ):

        self.root = Path(
            root
        )

        self.binding_service = (
            binding_service
            or ProductionReferenceBindingService()
        )

    @property
    def snapshot_file(
        self,
    ):

        return self.root / self.SNAPSHOT_FILE

    def save_snapshot(
        self,
        reference_selection,
        generalization,
        production_readiness,
    ):

        binding = self.binding_service.bind_winner(
            reference_selection=reference_selection,
            generalization=generalization,
            production_readiness=production_readiness,
        )

        payload: dict[str, object] = {
            "reference_selection": dict(
                binding.reference_selection
            ),
            "generalization": dict(
                binding.generalization
            ),
            "production_readiness": dict(
                binding.production_readiness
            ),
        }

        payload["checksum_sha256"] = self.stable_checksum(
            payload
        )

        if self.snapshot_file.exists():

            existing = self.load_payload()

            if existing != payload:

                raise ProductionReferenceBindingError(
                    "SNAPSHOT_IMMUTABLE"
                )

            return binding

        self.atomic_write_json(
            self.snapshot_file,
            payload,
        )

        return binding

    def get_binding(
        self,
    ):

        payload = self.load_payload()

        expected_checksum = self.stable_checksum(
            {
                "reference_selection": payload.get(
                    "reference_selection"
                ),
                "generalization": payload.get(
                    "generalization"
                ),
                "production_readiness": payload.get(
                    "production_readiness"
                ),
            }
        )

        if payload.get(
            "checksum_sha256"
        ) != expected_checksum:

            raise ProductionReferenceBindingError(
                "SNAPSHOT_CHECKSUM_INVALID"
            )

        return self.binding_service.bind_winner(
            reference_selection=payload.get(
                "reference_selection"
            ),
            generalization=payload.get(
                "generalization"
            ),
            production_readiness=payload.get(
                "production_readiness"
            ),
        )

    def load_payload(
        self,
    ):

        if not self.snapshot_file.exists():

            raise ProductionReferenceBindingError(
                "SNAPSHOT_NOT_READY"
            )

        try:

            payload = json.loads(
                self.snapshot_file.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            json.JSONDecodeError,
        ) as error:

            raise ProductionReferenceBindingError(
                "SNAPSHOT_INVALID"
            ) from error

        if not isinstance(
            payload,
            dict,
        ):

            raise ProductionReferenceBindingError(
                "SNAPSHOT_INVALID"
            )

        return payload

    def stable_checksum(
        self,
        payload,
    ):

        data = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        )

        return hashlib.sha256(
            data.encode(
                "utf-8"
            )
        ).hexdigest()

    def atomic_write_json(
        self,
        path,
        payload,
    ):

        path = Path(
            path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_path = path.with_suffix(
            path.suffix + ".tmp"
        )

        try:

            with temp_path.open(
                "w",
                encoding="utf-8",
            ) as handle:

                json.dump(
                    payload,
                    handle,
                    ensure_ascii=False,
                    indent=4,
                )

                handle.flush()

            temp_path.replace(
                path
            )

        except OSError:

            if temp_path.exists():

                temp_path.unlink()

            raise