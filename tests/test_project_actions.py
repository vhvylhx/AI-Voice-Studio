import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from services.current_project_service import CurrentProjectService
from services.project_service import ProjectService


def make_service(name):

    root = ROOT / "cache" / name

    if root.exists():

        shutil.rmtree(root)

    root.mkdir(
        parents=True,
    )

    service = ProjectService()
    service.root = root
    service.trash_root().mkdir(
        parents=True,
        exist_ok=True,
    )

    return service


def test_project_create_uses_id_folder_and_display_name():

    service = make_service(
        "test_project_create_identity"
    )

    project = service.create(
        "Alpha"
    )

    assert project.id == "project_000001"
    assert project.name == "project_000001"
    assert project.display_name == "Alpha"
    assert project.path.name == project.id
    assert service.load(
        "Alpha"
    ).id == project.id


def test_legacy_project_load_gets_display_name_without_changing_id():

    service = make_service(
        "test_project_legacy_load"
    )

    legacy = service.root / "Legacy Name"
    legacy.mkdir()

    (legacy / "project.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project_id": "legacy-id",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    loaded = service.load(
        "Legacy Name"
    )

    assert loaded.id == "legacy-id"
    assert loaded.display_name == "Legacy Name"
    assert loaded.path.name == "Legacy Name"


def test_project_rename_changes_display_name_only():

    service = make_service(
        "test_project_display_rename"
    )

    project = service.create(
        "Alpha"
    )

    renamed = service.rename(
        project.id,
        "Beta",
    )

    assert renamed.id == project.id
    assert renamed.display_name == "Beta"
    assert renamed.path == project.path
    assert service.exists(
        "Beta"
    )
    assert not service.exists(
        "Alpha"
    )


def test_duplicate_invalid_name_archive_and_restore_archive():

    service = make_service(
        "test_project_lifecycle"
    )

    project = service.create(
        "Alpha"
    )

    duplicate = service.duplicate(
        project.id,
        "Alpha Copy",
    )

    assert duplicate.id != project.id
    assert duplicate.config.duplicated_from_project_id == project.id
    assert duplicate.display_name == "Alpha Copy"

    try:

        service.rename(
            duplicate.id,
            "Bad/Name",
        )

        assert False

    except ValueError:

        pass

    archived = service.archive(
        project.id
    )

    assert archived.is_archived

    restored = service.restore_archive(
        project.id
    )

    assert not restored.is_archived
    assert restored.id == project.id


def test_open_close_switch_recent_and_current_project():

    service = make_service(
        "test_project_open_switch"
    )

    CurrentProjectService.clear()

    a = service.create(
        "Alpha"
    )
    b = service.create(
        "Beta"
    )

    opened = service.open_project(
        a.id,
        current_project_service=CurrentProjectService,
    )

    assert CurrentProjectService.get().id == opened.id

    switched = service.switch_project(
        b.id,
        current_project_service=CurrentProjectService,
    )

    assert CurrentProjectService.get().id == switched.id

    recent = service.recent_projects()

    assert recent[0].project_id == b.id

    service.close_project(
        CurrentProjectService
    )

    assert not CurrentProjectService.has_project()


def test_backup_export_import_validation_and_repair():

    service = make_service(
        "test_project_backup_export"
    )

    project = service.create(
        "Alpha"
    )

    backup = service.backup_project(
        project.id
    )

    assert Path(
        backup["backup_path"]
    ).exists()

    package = service.root / "alpha.avproject.zip"

    exported = service.export_project(
        project.id,
        package,
    )

    assert Path(
        exported["package_file"]
    ).exists()

    imported = service.import_project(
        package
    )

    assert imported.id != project.id
    assert imported.config.imported_from["source_project_id"] == project.id

    validation = service.validate(
        project.id
    )

    assert validation["state"] == "valid"

    shutil.rmtree(
        project.cache_dir
    )

    warning = service.validate(
        project.id
    )

    assert warning["state"] == "warning"

    repair = service.repair(
        project.id
    )

    assert repair["safe"] is True
    assert project.cache_dir.exists()


test_project_create_uses_id_folder_and_display_name()
test_legacy_project_load_gets_display_name_without_changing_id()
test_project_rename_changes_display_name_only()
test_duplicate_invalid_name_archive_and_restore_archive()
test_open_close_switch_recent_and_current_project()
test_backup_export_import_validation_and_repair()

print("PROJECT_ACTIONS_TEST_OK")
