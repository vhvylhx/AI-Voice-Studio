import sys
import zipfile
from datetime import datetime
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.project_service import ProjectService  # noqa: E402
import services.project_backup_service as project_backup_service  # noqa: E402
from services.reference_vault_service import ReferenceVaultService  # noqa: E402


class DeterministicDateTime:

    current = datetime(
        2026,
        7,
        22,
        10,
        0,
        0,
        1000,
    )

    @classmethod
    def now(
        cls,
    ):

        value = cls.current

        cls.current = value + timedelta(
            microseconds=1,
        )

        return value


def make_project_and_vault(tmp_path):

    service = ProjectService()
    service.root = tmp_path / "projects"
    service.root.mkdir()

    project = service.create(
        "Backup Ref"
    )

    source = tmp_path / "ref.txt"
    source.write_text(
        "text",
        encoding="utf-8",
    )

    vault = ReferenceVaultService(
        tmp_path / "vault"
    )

    asset = vault.import_file(
        source,
        "training_reference_text",
        source_project_id=project.id,
    )[
        "asset"
    ]

    return service, project, vault, asset


def test_metadata_backup_is_distinct_from_complete_backup(
    tmp_path,
    monkeypatch,
):

    DeterministicDateTime.current = datetime(
        2026,
        7,
        22,
        10,
        0,
        0,
        1000,
    )

    monkeypatch.setattr(
        project_backup_service,
        "datetime",
        DeterministicDateTime,
    )

    service, project, vault, asset = make_project_and_vault(
        tmp_path
    )

    metadata = service.backup_project(
        project.id,
        mode="metadata",
        reference_vault=vault,
    )

    complete = service.backup_project(
        project.id,
        mode="complete",
        reference_vault=vault,
    )

    assert not metadata["manifest"]["contains_media"]
    assert complete["manifest"]["contains_media"]
    assert (
        Path(
            complete["backup_path"]
        )
        / "reference_vault"
        / asset.managed_relative_path
    ).exists()


def test_standard_export_import_restores_managed_reference(tmp_path):

    service, project, vault, asset = make_project_and_vault(
        tmp_path
    )

    package = tmp_path / "project.avproject.zip"

    service.export_project(
        project.id,
        package,
        mode="standard",
        reference_vault=vault,
    )

    with zipfile.ZipFile(
        package,
        "r",
    ) as archive:

        names = set(
            archive.namelist()
        )

    assert "manifest.json" in names
    assert f"reference_vault/{asset.managed_relative_path}" in names

    imported_service = ProjectService()
    imported_service.root = tmp_path / "imported_projects"
    imported_service.root.mkdir()

    imported_vault = ReferenceVaultService(
        tmp_path / "imported_vault"
    )

    imported = imported_service.import_project(
        package,
        reference_vault=imported_vault,
    )

    assert imported.id != project.id
    assert (
        imported_vault.vault_root
        / asset.managed_relative_path
    ).exists()
