import json
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from models.project_config import ProjectConfig
from models.project_model import ProjectModel
from services.project_backup_service import ProjectBackupService
from services.project_package_service import ProjectPackageService
from services.project_registry_service import ProjectRegistryService
from services.project_validation_service import ProjectValidationService


class ProjectService:

    def __init__(
        self,
    ):

        self.root = Path(
            "projects"
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.trash_root().mkdir(
            parents=True,
            exist_ok=True,
        )

        self.registry_service = ProjectRegistryService(
            self.root
        )

        self.validation_service = ProjectValidationService()

        self.backup_service = ProjectBackupService()

        self.package_service = ProjectPackageService()

    #
    # Create / Load / Save
    #

    def create(
        self,
        name: str,
        description="",
        open_after_create=False,
        current_project_service=None,
    ):

        display_name = self.validate_name(
            name
        )

        if self.display_name_exists(
            display_name
        ):

            raise ValueError(
                "Project đã tồn tại."
            )

        config = ProjectConfig()
        config.project_id = self.next_project_id()
        config.display_name = display_name
        config.description = str(
            description or ""
        )
        config.created_at = datetime.now().isoformat()
        config.updated_at = config.created_at
        config.status = "active"
        config.archive_state = "active"

        project_root = self.root / config.project_id

        if project_root.exists():

            raise ValueError(
                "Project ID đã tồn tại."
            )

        project_root.mkdir(
            parents=True,
            exist_ok=False,
        )

        config.project_root = str(
            project_root
        )
        config.workspace_root = str(
            project_root
        )

        self.ensure_folders(
            project_root,
            config,
        )

        self.save_config(
            project_root,
            config,
        )

        project = self.load(
            config.project_id
        )

        self.registry().upsert(
            project
        )

        if open_after_create:

            self.open_project(
                project.id,
                current_project_service=current_project_service,
            )

        return project

    def load(
        self,
        identifier: str,
        ensure_folders=True,
    ):

        project_root = self.resolve_project_folder(
            identifier
        )

        config_file = project_root / "project.json"

        with open(
            config_file,
            "r",
            encoding="utf-8",
        ) as handle:

            config = ProjectConfig.from_dict(
                json.load(
                    handle
                )
            )

        migrated = False

        if not config.project_id:

            config.project_id = self.next_project_id(
                exclude=project_root.name
            )

            migrated = True

        if not config.display_name:

            config.display_name = project_root.name

            migrated = True

        if config.schema_version < 2:

            config.schema_version = 2

            migrated = True

        if not config.project_root:

            config.project_root = str(
                project_root
            )

            migrated = True

        if not config.workspace_root:

            config.workspace_root = str(
                project_root
            )

            migrated = True

        if ensure_folders:

            self.ensure_folders(
                project_root,
                config,
            )

        if migrated:

            self.save_config(
                project_root,
                config,
            )

        return ProjectModel(
            name=project_root.name,
            path=project_root,
            input_dir=project_root / config.text_folder,
            output_dir=project_root / config.audio_folder,
            cache_dir=project_root / "cache",
            log_dir=project_root / "logs",
            config=config,
        )

    def save(
        self,
        project,
    ):

        self.save_config(
            project.path,
            project.config,
        )

        try:

            self.registry().upsert(
                self.load(
                    project.id
                    or project.name
                )
            )

        except Exception:

            pass

    def save_config(
        self,
        project,
        config,
    ):

        config.updated_at = datetime.now().isoformat()

        temp = Path(
            project
        ) / "project.tmp.json"

        temp.write_text(
            json.dumps(
                config.to_dict(),
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temp.replace(
            Path(
                project
            )
            / "project.json"
        )

    def ensure_folders(
        self,
        project,
        config,
    ):

        project = Path(
            project
        )

        for folder in [
            config.text_folder,
            config.audio_folder,
            config.export_folder,
            "cache",
            "logs",
        ]:

            (
                project / folder
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

    #
    # Project selection / registry
    #

    def open_project(
        self,
        identifier,
        current_project_service=None,
    ):

        project = self.load(
            identifier,
            ensure_folders=False,
        )

        project.config.last_opened_at = datetime.now().isoformat()

        self.save_config(
            project.path,
            project.config,
        )

        project = self.load(
            project.name
        )

        self.registry().mark_recent(
            project
        )

        if current_project_service is not None:

            current_project_service.set(
                project
            )

        return project

    def close_project(
        self,
        current_project_service=None,
    ):

        if current_project_service is not None:

            current_project_service.clear()

        registry = self.registry().load()
        registry.current_project_id = ""
        self.registry().save(
            registry
        )

        return True

    def switch_project(
        self,
        identifier,
        current_project_service=None,
    ):

        if current_project_service is not None:

            current_project_service.clear()

        return self.open_project(
            identifier,
            current_project_service=current_project_service,
        )

    def recent_projects(
        self,
    ):

        registry = self.registry().load()

        entries = {
            entry.project_id: entry
            for entry in registry.entries
        }

        return [
            entries[project_id]
            for project_id in registry.recent_project_ids
            if project_id in entries
        ]

    def registry(
        self,
    ):

        self.registry_service.root = self.root

        return self.registry_service

    #
    # List / Resolve
    #

    def list(
        self,
    ):

        projects = []

        if not self.root.exists():

            return projects

        for folder in self.root.iterdir():

            if folder.name in {
                ".trash",
            }:

                continue

            if (
                folder.is_dir()
                and (
                    folder / "project.json"
                ).exists()
            ):

                projects.append(
                    folder.name
                )

        return sorted(
            projects
        )

    def list_projects(
        self,
        include_archived=True,
    ):

        result = []

        for name in self.list():

            try:

                project = self.load(
                    name
                )

            except Exception:

                continue

            if (
                not include_archived
                and project.is_archived
            ):

                continue

            result.append(
                project
            )

        self.registry().sync_from_projects(
            result
        )

        return sorted(
            result,
            key=lambda project: (
                project.display_name.lower(),
                project.id,
            ),
        )

    def exists(
        self,
        name: str,
    ):

        try:

            self.resolve_project_folder(
                name
            )

            return True

        except FileNotFoundError:

            return False

    def resolve_project_folder(
        self,
        identifier,
    ):

        identifier = str(
            identifier or ""
        )

        direct = self.root / identifier

        if direct.exists():

            return direct

        normalized = self.normalize_display_name(
            identifier
        ).lower()

        if not self.root.exists():

            raise FileNotFoundError(
                direct
            )

        for folder in self.root.iterdir():

            if not folder.is_dir() or folder.name == ".trash":

                continue

            config_file = folder / "project.json"

            if not config_file.exists():

                continue

            try:

                data = json.loads(
                    config_file.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                continue

            if data.get(
                "project_id"
            ) == identifier:

                return folder

            display_name = data.get(
                "display_name",
                folder.name,
            )

            if self.normalize_display_name(
                display_name
            ).lower() == normalized:

                return folder

        raise FileNotFoundError(
            direct
        )

    #
    # Lifecycle
    #

    def rename(
        self,
        old_name: str,
        new_name: str,
    ):

        new_name = self.validate_name(
            new_name
        )

        project = self.load(
            old_name
        )

        if self.display_name_exists(
            new_name,
            exclude_project_id=project.id,
        ):

            raise ValueError(
                "Project đã tồn tại."
            )

        project.config.display_name = new_name

        self.save(
            project
        )

        return self.load(
            project.name
        )

    def duplicate(
        self,
        source_identifier,
        new_display_name,
        mode="config_only",
    ):

        source = self.load(
            source_identifier
        )

        duplicated = self.create(
            new_display_name
        )

        data = source.config.to_dict()
        data["project_id"] = duplicated.id
        data["display_name"] = self.validate_name(
            new_display_name
        )
        data["status"] = "active"
        data["archive_state"] = "active"
        data["source_project_id"] = source.id
        data["duplicated_from_project_id"] = source.id
        data["created_at"] = datetime.now().isoformat()
        data["updated_at"] = data["created_at"]
        data["last_opened_at"] = ""
        data["project_root"] = str(
            duplicated.path
        )
        data["workspace_root"] = str(
            duplicated.path
        )

        duplicated.config = ProjectConfig.from_dict(
            data
        )

        self.save(
            duplicated
        )

        if mode == "full_copy":

            self.copy_project_content(
                source.path,
                duplicated.path,
            )

        return self.load(
            duplicated.name
        )

    def archive(
        self,
        identifier,
    ):

        project = self.load(
            identifier,
            ensure_folders=False,
        )

        project.config.status = "archived"
        project.config.archive_state = "archived"

        self.save(
            project
        )

        return self.load(
            project.name
        )

    def restore_archive(
        self,
        identifier,
    ):

        project = self.load(
            identifier
        )

        project.config.status = "active"
        project.config.archive_state = "active"

        self.save(
            project
        )

        return self.load(
            project.name
        )

    #
    # Legacy trash helpers kept for compatibility, not wired as Project Manager delete.
    #

    def delete(
        self,
        name: str,
        current_project_service=None,
    ):

        return self.archive(
            name
        )

    def trash_root(
        self,
    ):

        return self.root / ".trash"

    def soft_delete(
        self,
        name: str,
    ):

        project = self.load(
            name
        )

        return {
            "schema_version": 1,
            "project_id": project.id,
            "project_name": project.display_name,
            "original_path": str(
                project.path
            ),
            "deleted_at": datetime.now().isoformat(),
            "archived": True,
        }

    def list_trash(
        self,
    ):

        return []

    def restore(
        self,
        trash_name,
        new_name=None,
    ):

        return self.restore_archive(
            trash_name
        )

    def delete_permanently(
        self,
        trash_name,
    ):

        raise RuntimeError(
            "Xóa vĩnh viễn Project bị khóa trong Sprint này."
        )

    def empty_trash(
        self,
    ):

        raise RuntimeError(
            "Dọn sạch thùng rác bị khóa trong Sprint này."
        )

    def read_trash_metadata(
        self,
        folder,
    ):

        raise FileNotFoundError(
            folder
        )

    #
    # Workflow memory
    #

    def save_dataset_workflow(
        self,
        project,
        workflow_config,
    ):

        config = project.config
        config.last_audio_folder = str(
            getattr(
                workflow_config,
                "audio_folder",
                "",
            )
        )
        config.last_text_folder = str(
            getattr(
                workflow_config,
                "text_folder",
                "",
            )
        )
        config.last_output_folder = str(
            getattr(
                workflow_config,
                "output_folder",
                "",
            )
        )
        config.last_source_mode = str(
            getattr(
                workflow_config,
                "source_mode",
                "same_folder",
            )
        )
        config.last_use_input_as_output = bool(
            getattr(
                workflow_config,
                "use_input_folder_as_output",
                True,
            )
        )
        config.last_voice_id = str(
            getattr(
                workflow_config,
                "selected_voice_id",
                "",
            )
        )
        config.last_runtime_profile_id = str(
            getattr(
                workflow_config,
                "runtime_profile_id",
                "",
            )
        )

        self.save(
            project
        )

        return project

    def save_generate_selection(
        self,
        project,
        selection_config,
    ):

        config = project.config
        config.last_generate_mode = str(
            getattr(
                selection_config,
                "mode",
                "standard",
            )
        )
        config.last_generate_voice_id = str(
            getattr(
                selection_config,
                "voice_id",
                "",
            )
        )
        config.last_generate_variant_id = str(
            getattr(
                selection_config,
                "selected_variant_id",
                "",
            )
        )
        config.last_generate_allow_all_variants = bool(
            getattr(
                selection_config,
                "allow_all_variants",
                False,
            )
        )
        config.last_generate_variant_ids = list(
            getattr(
                selection_config,
                "allowed_variant_ids",
                [],
            )
        )
        config.last_generate_allow_all_styles = bool(
            getattr(
                selection_config,
                "allow_all_styles",
                False,
            )
        )
        config.last_generate_style_ids = list(
            getattr(
                selection_config,
                "allowed_style_ids",
                [],
            )
        )

        speed = getattr(
            selection_config,
            "speed",
            None,
        )

        config.last_generate_speed = float(
            getattr(
                speed,
                "speed",
                1.0,
            )
        )
        config.last_generate_preset_id = str(
            getattr(
                selection_config,
                "preset_id",
                "",
            )
        )
        config.last_generate_reference_style_id = str(
            getattr(
                selection_config,
                "reference_style_id",
                "",
            )
        )
        config.last_generate_text_profile_id = str(
            getattr(
                selection_config,
                "text_profile_id",
                "",
            )
        )
        config.last_generate_input_path = str(
            getattr(
                selection_config,
                "input_path",
                "",
            )
        )
        config.last_generate_output_folder = str(
            getattr(
                selection_config,
                "output_folder",
                "",
            )
        )
        config.last_generate_output_name = str(
            getattr(
                selection_config,
                "output_name",
                "",
            )
        )
        config.last_generate_output_format = str(
            getattr(
                selection_config,
                "output_format",
                "wav",
            )
        )
        config.last_generate_mp3_bitrate_kbps = int(
            getattr(
                selection_config,
                "mp3_bitrate_kbps",
                192,
            )
        )

        self.save(
            project
        )

        return project

    def save_runtime_training_profile(
        self,
        project,
        training_profile,
    ):

        config = project.config
        config.training_profile_mode = str(
            getattr(
                training_profile,
                "mode",
                "auto",
            )
        )
        config.auto_detect_hardware = bool(
            getattr(
                training_profile,
                "auto_detect_hardware",
                True,
            )
        )
        config.training_runtime_profile_id = str(
            getattr(
                training_profile,
                "runtime_profile_id",
                "",
            )
        )
        config.training_compute_mode = str(
            getattr(
                training_profile,
                "compute_mode",
                "auto",
            )
        )
        config.training_batch_size = int(
            getattr(
                training_profile,
                "batch_size",
                1,
            )
        )
        config.training_num_workers = int(
            getattr(
                training_profile,
                "num_workers",
                0,
            )
        )
        config.training_vram_profile = str(
            getattr(
                training_profile,
                "vram_profile",
                "low_vram",
            )
        )
        config.training_gpt_epochs = int(
            getattr(
                training_profile,
                "gpt_epochs",
                20,
            )
        )
        config.training_sovits_epochs = int(
            getattr(
                training_profile,
                "sovits_epochs",
                50,
            )
        )
        config.training_save_interval = int(
            getattr(
                training_profile,
                "save_interval",
                1,
            )
        )
        config.training_pretrained_model_version = str(
            getattr(
                training_profile,
                "pretrained_model_version",
                "v2Pro",
            )
        )
        config.training_resume_policy = str(
            getattr(
                training_profile,
                "resume_policy",
                "manual",
            )
        )
        config.training_hardware_fingerprint = str(
            getattr(
                training_profile,
                "hardware",
                {},
            ).get(
                "fingerprint",
                "",
            )
        )

        if config.training_profile_mode == "custom":

            config.training_custom_config = (
                training_profile.to_dict()
                if hasattr(
                    training_profile,
                    "to_dict",
                )
                else {}
            )

        self.save(
            project
        )

        return project

    #
    # Export / Import / Backup / Validation
    #

    def export_project(
        self,
        identifier,
        package_file,
        mode="lightweight",
        reference_vault=None,
    ):

        return self.package_service.export_project(
            self.load(
                identifier
            ),
            package_file,
            mode=mode,
            reference_vault=reference_vault,
        )

    def import_project(
        self,
        package_file,
        import_as_new=True,
        reference_vault=None,
    ):

        result = self.package_service.import_project(
            package_file,
            self.root,
            import_as_new=import_as_new,
            reference_vault=reference_vault,
        )

        project = self.load(
            result[
                "project_id"
            ]
        )

        source_name = result[
            "manifest"
        ].get(
            "display_name",
            project.display_name,
        )

        project.config.project_id = result[
            "project_id"
        ]
        project.config.display_name = self.unique_display_name(
            f"{source_name} (Import)"
        )
        project.config.imported_from = {
            "package": str(
                package_file
            ),
            "source_project_id": result[
                "manifest"
            ].get(
                "project_id",
                "",
            ),
        }
        project.config.project_root = str(
            project.path
        )
        project.config.workspace_root = str(
            project.path
        )

        self.save(
            project
        )

        return self.load(
            project.name
        )

    def backup_project(
        self,
        identifier,
        reason="manual",
        mode="metadata",
        reference_vault=None,
    ):

        return self.backup_service.backup_project(
            self.load(
                identifier
            ),
            reason=reason,
            mode=mode,
            reference_vault=reference_vault,
        )

    def restore_backup(
        self,
        identifier,
        backup_path,
        reference_vault=None,
    ):

        project = self.load(
            identifier
        )

        result = self.backup_service.restore_project(
            project,
            backup_path,
            reference_vault=reference_vault,
        )

        self.registry().upsert(
            self.load(
                project.name
            )
        )

        return result

    def validate(
        self,
        identifier,
        reference_vault=None,
    ):

        project = self.load(
            identifier,
            ensure_folders=False,
        )

        result = self.validation_service.validate(
            project,
            reference_vault=reference_vault,
        )

        if reference_vault is not None:

            project.config.reference_summary = self.reference_summary(
                reference_vault
            )

        project.config.health_state = result[
            "state"
        ]
        project.config.validation_messages = result[
            "messages"
        ]

        self.save(
            project
        )

        return result

    def reference_summary(
        self,
        reference_vault,
    ):

        registry = reference_vault.registry_service.load()

        total = len(
            registry.entries
        )

        missing = 0
        corrupt = 0

        for entry in registry.entries:

            path = (
                reference_vault.vault_root
                / entry.managed_relative_path
            )

            if not path.exists():

                missing += 1

                continue

            try:

                if (
                    entry.checksum
                    and reference_vault.sha256(
                        path
                    )
                    != entry.checksum
                ):

                    corrupt += 1

            except Exception:

                corrupt += 1

        return {
            "total": total,
            "managed": total,
            "external_only": 0,
            "missing": missing,
            "corrupt": corrupt,
        }

    def repair(
        self,
        identifier,
    ):

        project = self.load(
            identifier
        )

        self.backup_project(
            project.name,
            reason="before_repair",
        )

        result = self.validation_service.repair(
            project
        )

        self.validate(
            project.name
        )

        return result

    #
    # Helpers
    #

    def validate_name(
        self,
        name,
    ):

        name = self.normalize_display_name(
            name
        )

        if not name:

            raise ValueError(
                "Tên Project không được rỗng."
            )

        if len(
            name
        ) > 120:

            raise ValueError(
                "Tên Project quá dài."
            )

        if any(
            unicodedata.category(
                char
            ).startswith(
                "C"
            )
            for char in name
        ):

            raise ValueError(
                "Tên Project chứa ký tự điều khiển."
            )

        if re.search(
            r'[<>:"/\\|?*]',
            name,
        ):

            raise ValueError(
                "Tên Project chứa ký tự không hợp lệ."
            )

        return name

    def normalize_display_name(
        self,
        name,
    ):

        return " ".join(
            str(
                name or ""
            ).strip().split()
        )

    def display_name_exists(
        self,
        display_name,
        exclude_project_id="",
    ):

        target = self.normalize_display_name(
            display_name
        ).lower()

        for project in self.list_projects(
            include_archived=True
        ):

            if project.id == exclude_project_id:

                continue

            if self.normalize_display_name(
                project.display_name
            ).lower() == target:

                return True

        return False

    def unique_display_name(
        self,
        display_name,
    ):

        base = self.validate_name(
            display_name
        )

        if not self.display_name_exists(
            base
        ):

            return base

        index = 2

        while True:

            candidate = f"{base} {index}"

            if not self.display_name_exists(
                candidate
            ):

                return candidate

            index += 1

    def next_project_id(
        self,
        exclude=None,
    ):

        used = set()

        for name in self.list():

            if name == exclude:

                continue

            file = self.root / name / "project.json"

            if not file.exists():

                continue

            try:

                data = json.loads(
                    file.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                continue

            project_id = data.get(
                "project_id",
                "",
            )

            if project_id:

                used.add(
                    project_id
                )

        index = 1

        while index <= 999999:

            project_id = f"project_{index:06d}"

            if project_id not in used:

                return project_id

            index += 1

        while True:

            project_id = f"project_{uuid4().hex[:12]}"

            if project_id not in used:

                return project_id

    def write_json(
        self,
        file,
        data,
    ):

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                data,
                handle,
                indent=4,
                ensure_ascii=False,
            )

    def _rename_path(
        self,
        old,
        new,
    ):

        Path(
            old
        ).rename(
            new
        )

    def copy_project_content(
        self,
        source_root,
        target_root,
    ):

        excluded = {
            "cache",
            "temp",
            "logs",
            "output",
            "backups",
        }

        source_root = Path(
            source_root
        )
        target_root = Path(
            target_root
        )

        for item in source_root.iterdir():

            if item.name in excluded:

                continue

            if item.name == "project.json":

                continue

            target = target_root / item.name

            if item.is_dir():

                if target.exists():

                    continue

                shutil.copytree(
                    item,
                    target,
                )

            elif item.is_file():

                shutil.copy2(
                    item,
                    target,
                )
