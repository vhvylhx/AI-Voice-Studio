import hashlib
import json
from pathlib import Path

from models.generate_pipeline_foundation import (
    GenerateArtifactRecord,
    GenerateManifestRecord,
    GeneratePlanRecord,
    GenerateRegistryEntry,
    GenerateRequestRecord,
    GenerateSessionRecord,
    now_iso,
)


class GenerateRepository:

    def __init__(
        self,
        root=None,
    ):

        self.root = Path(
            root or Path("workspace") / "generate"
        )

    def ensure_root(
        self,
    ):

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.sessions_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    @property
    def sessions_root(
        self,
    ):

        return self.root / "sessions"

    @property
    def registry_file(
        self,
    ):

        return self.root / "registry.json"

    def session_dir(
        self,
        session_id,
    ):

        return self.sessions_root / session_id

    def atomic_write_json(
        self,
        path,
        data,
    ):

        path = Path(
            path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = path.with_suffix(
            path.suffix + ".tmp"
        )

        temp.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temp.replace(
            path
        )

        return path

    def checksum(
        self,
        data,
    ):

        return hashlib.sha256(
            json.dumps(
                data,
                ensure_ascii=False,
                sort_keys=True,
                separators=(
                    ",",
                    ":",
                ),
            ).encode(
                "utf-8"
            )
        ).hexdigest()

    def read_json(
        self,
        path,
        default=None,
    ):

        path = Path(
            path
        )

        if not path.exists():

            return default

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def save_request(
        self,
        session_id,
        record,
    ):

        return self.atomic_write_json(
            self.session_dir(
                session_id
            )
            / "request.json",
            record.to_dict(),
        )

    def load_request(
        self,
        session_id,
    ):

        data = self.read_json(
            self.session_dir(
                session_id
            )
            / "request.json",
            {},
        )

        return GenerateRequestRecord.from_dict(
            data
        ) if data else None

    def save_session(
        self,
        record,
    ):

        return self.atomic_write_json(
            self.session_dir(
                record.session_id
            )
            / "session.json",
            record.to_dict(),
        )

    def load_session(
        self,
        session_id,
    ):

        data = self.read_json(
            self.session_dir(
                session_id
            )
            / "session.json",
            {},
        )

        return GenerateSessionRecord.from_dict(
            data
        ) if data else None

    def save_plan(
        self,
        plan,
    ):

        existing = self.load_plan(
            plan.session_id
        )

        if (
            existing
            and existing.frozen
            and existing.immutable_checksum_sha256
        ):

            incoming = self.checksum(
                plan.immutable_payload()
            )

            if incoming != existing.immutable_checksum_sha256:

                raise ValueError(
                    "generate_plan_frozen_mutation"
                )

            plan.immutable_checksum_sha256 = (
                existing.immutable_checksum_sha256
            )

        path = self.atomic_write_json(
            self.session_dir(
                plan.session_id
            )
            / "plan.json",
            plan.to_dict(),
        )

        reopened = self.load_plan(
            plan.session_id
        )

        if reopened and plan.plan_checksum_sha256:

            if (
                reopened.plan_checksum_sha256
                != plan.plan_checksum_sha256
            ):

                raise ValueError(
                    "generate_plan_checksum_readback_failed"
                )

        return path

    def load_plan(
        self,
        session_id,
    ):

        data = self.read_json(
            self.session_dir(
                session_id
            )
            / "plan.json",
            {},
        )

        return GeneratePlanRecord.from_dict(
            data
        ) if data else None

    def save_manifest(
        self,
        manifest,
    ):

        return self.atomic_write_json(
            self.session_dir(
                manifest.session_id
            )
            / "manifest.json",
            manifest.to_dict(),
        )

    def load_manifest(
        self,
        session_id,
    ):

        data = self.read_json(
            self.session_dir(
                session_id
            )
            / "manifest.json",
            {},
        )

        return GenerateManifestRecord.from_dict(
            data
        ) if data else None

    def save_artifacts(
        self,
        session_id,
        artifacts,
    ):

        return self.atomic_write_json(
            self.session_dir(
                session_id
            )
            / "artifacts.json",
            {
                "updated_at": now_iso(),
                "items": [
                    GenerateArtifactRecord.from_dict(
                        item
                    ).to_dict()
                    for item in artifacts
                ],
            },
        )

    def load_artifacts(
        self,
        session_id,
    ):

        data = self.read_json(
            self.session_dir(
                session_id
            )
            / "artifacts.json",
            {
                "items": [],
            },
        )

        if data.get(
            "items",
            None,
        ) is None:

            manifest = self.load_manifest(
                session_id
            )

            return list(
                manifest.artifact_records
                if manifest
                else []
            )

        return [
            GenerateArtifactRecord.from_dict(
                item
            )
            for item in data.get(
                "items",
                []
            )
        ]

    def upsert_artifact(
        self,
        artifact,
    ):

        artifact = GenerateArtifactRecord.from_dict(
            artifact
        )

        items = self.load_artifacts(
            artifact.session_id
        )

        replaced = False

        for index, item in enumerate(
            items
        ):

            if item.artifact_id == artifact.artifact_id:

                items[
                    index
                ] = artifact

                replaced = True

                break

        if not replaced:

            items.append(
                artifact
            )

        self.save_artifacts(
            artifact.session_id,
            items,
        )

        return artifact

    def load_registry(
        self,
    ):

        self.ensure_root()

        data = self.read_json(
            self.registry_file,
            {
                "items": [],
            },
        )

        return [
            GenerateRegistryEntry.from_dict(
                item
            )
            for item in data.get(
                "items",
                []
            )
        ]

    def save_registry(
        self,
        items,
    ):

        return self.atomic_write_json(
            self.registry_file,
            {
                "updated_at": now_iso(),
                "items": [
                    item.to_dict()
                    for item in items
                ],
            },
        )

    def upsert_registry(
        self,
        entry,
    ):

        items = self.load_registry()

        replaced = False

        for index, item in enumerate(
            items
        ):

            if item.session_id == entry.session_id:

                items[
                    index
                ] = entry

                replaced = True

                break

        if not replaced:

            items.append(
                entry
            )

        self.save_registry(
            items
        )

        return entry

    def list_sessions(
        self,
        project_id="",
    ):

        items = self.load_registry()

        if project_id:

            items = [
                item
                for item in items
                if item.project_id == project_id
            ]

        return sorted(
            items,
            key=lambda item: item.updated_at
            or item.created_at,
            reverse=True,
        )
