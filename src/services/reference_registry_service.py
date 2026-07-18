import json
import shutil
from datetime import datetime
from pathlib import Path

from models.reference_registry import ReferenceRegistry
from models.reference_registry import ReferenceRegistryEntry


class ReferenceRegistryService:

    REGISTRY_FILE = "reference_registry.json"

    def __init__(
        self,
        vault_root="workspace/reference_vault",
    ):

        self.vault_root = Path(
            vault_root
        )

        self.registry_dir = self.vault_root / "registry"

        self.registry_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    @property
    def registry_file(
        self,
    ):

        return self.registry_dir / self.REGISTRY_FILE

    def load(
        self,
    ):

        file = self.registry_file

        if not file.exists():

            return ReferenceRegistry()

        try:

            data = json.loads(
                file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            self.backup_corrupt(
                file
            )

            return ReferenceRegistry()

        return ReferenceRegistry.from_dict(
            data
        )

    def save(
        self,
        registry,
    ):

        registry.updated_at = datetime.now().isoformat()

        self.atomic_write_json(
            self.registry_file,
            registry.to_dict(),
        )

        return registry

    def upsert(
        self,
        asset,
    ):

        registry = self.load()

        entry = ReferenceRegistryEntry.from_asset(
            asset
        )

        entries = [
            item
            for item in registry.entries
            if item.asset_id != entry.asset_id
        ]

        entries.append(
            entry
        )

        registry.entries = sorted(
            entries,
            key=lambda item: item.asset_id,
        )

        self.save(
            registry
        )

        return entry

    def get(
        self,
        asset_id,
    ):

        for entry in self.load().entries:

            if entry.asset_id == asset_id:

                return entry

        return None

    def find_by_checksum(
        self,
        checksum,
        asset_type="",
        extension="",
    ):

        checksum = str(
            checksum or ""
        )

        extension = str(
            extension or ""
        ).lower()

        for entry in self.load().entries:

            if entry.checksum != checksum:

                continue

            if asset_type and entry.asset_type != asset_type:

                continue

            if extension and not str(
                entry.managed_relative_path
            ).lower().endswith(
                extension
            ):

                continue

            return entry

        return None

    def backup_corrupt(
        self,
        file,
    ):

        file = Path(
            file
        )

        if not file.exists():

            return None

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        target = file.with_suffix(
            file.suffix + f".corrupt.{timestamp}.bak"
        )

        shutil.copy2(
            file,
            target,
        )

        return target

    def atomic_write_json(
        self,
        file,
        data,
    ):

        file = Path(
            file
        )

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = file.with_suffix(
            file.suffix + ".tmp"
        )

        with open(
            temp,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                data,
                handle,
                indent=4,
                ensure_ascii=False,
            )

            handle.flush()

        temp.replace(
            file
        )
