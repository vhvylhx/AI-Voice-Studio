import json
from pathlib import Path


class ProjectValidationService:

    REQUIRED_FOLDERS = [
        "text",
        "audio",
        "export",
        "cache",
        "logs",
    ]

    def validate(
        self,
        project,
        registry_entry=None,
        reference_vault=None,
    ):

        messages = []

        root = Path(
            project.path
        )

        config_file = root / "project.json"

        if not root.exists():

            messages.append(
                self.issue(
                    "project_missing",
                    "missing",
                    str(
                        root
                    ),
                    "Project folder không tồn tại. Hãy Locate/Relink hoặc Restore từ backup.",
                )
            )

            return self.result(
                "missing",
                messages,
            )

        if not config_file.exists():

            messages.append(
                self.issue(
                    "project_json_missing",
                    "invalid",
                    str(
                        config_file
                    ),
                    "Không tìm thấy project.json. Có thể restore từ backup hoặc import lại Project.",
                )
            )

        else:

            try:

                json.loads(
                    config_file.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception as exc:

                messages.append(
                    self.issue(
                        "project_json_corrupt",
                        "invalid",
                        str(
                            config_file
                        ),
                        f"project.json lỗi JSON: {exc}",
                    )
                )

        if not project.id:

            messages.append(
                self.issue(
                    "project_id_missing",
                    "blocked",
                    str(
                        config_file
                    ),
                    "Project thiếu ID. Có thể repair bằng cách sinh ID nếu đây là Project legacy.",
                )
            )

        if registry_entry and registry_entry.project_id != project.id:

            messages.append(
                self.issue(
                    "project_id_registry_mismatch",
                    "blocked",
                    str(
                        config_file
                    ),
                    "Project ID không khớp registry. Không tự sửa nếu chưa xác nhận.",
                )
            )

        for folder in self.REQUIRED_FOLDERS:

            if not (
                root / folder
            ).exists():

                messages.append(
                    self.issue(
                        "required_folder_missing",
                        "warning",
                        str(
                            root / folder
                        ),
                        "Có thể repair an toàn bằng cách tạo lại folder thiếu.",
                    )
                )

        if reference_vault is not None:

            messages.extend(
                self.validate_reference_vault(
                    reference_vault
                )
            )

        state = "valid"

        if any(
            item["level"] in {
                "blocked",
                "invalid",
            }
            for item in messages
        ):

            state = "invalid"

        elif messages:

            state = "warning"

        return self.result(
            state,
            messages,
        )

    def validate_reference_vault(
        self,
        reference_vault,
    ):

        messages = []

        try:

            registry = reference_vault.registry_service.load()

        except Exception as exc:

            return [
                self.issue(
                    "reference_registry_corrupt",
                    "invalid",
                    str(
                        getattr(
                            reference_vault.registry_service,
                            "registry_file",
                            "",
                        )
                    ),
                    f"Reference Registry khong doc duoc: {exc}",
                )
            ]

        seen = set()

        for entry in registry.entries:

            if entry.asset_id in seen:

                messages.append(
                    self.issue(
                        "reference_asset_id_collision",
                        "blocked",
                        entry.asset_id,
                        "Asset ID bi trung trong Reference Registry.",
                    )
                )

                continue

            seen.add(
                entry.asset_id
            )

            path = (
                reference_vault.vault_root
                / entry.managed_relative_path
            )

            try:

                path.relative_to(
                    reference_vault.vault_root
                )

            except Exception:

                messages.append(
                    self.issue(
                        "reference_managed_path_traversal",
                        "blocked",
                        str(
                            path
                        ),
                        "Managed path vuot khoi Reference Vault.",
                    )
                )

                continue

            if not path.exists():

                messages.append(
                    self.issue(
                        "reference_asset_missing",
                        "missing",
                        str(
                            path
                        ),
                        "Managed reference asset khong ton tai.",
                    )
                )

                continue

            try:

                actual = reference_vault.sha256(
                    path
                )

            except Exception as exc:

                messages.append(
                    self.issue(
                        "reference_asset_unreadable",
                        "corrupt",
                        str(
                            path
                        ),
                        f"Khong doc duoc asset: {exc}",
                    )
                )

                continue

            if entry.checksum and actual != entry.checksum:

                messages.append(
                    self.issue(
                        "reference_checksum_mismatch",
                        "corrupt",
                        str(
                            path
                        ),
                        "Checksum reference khong khop registry.",
                    )
                )

        return messages

    def repair(
        self,
        project,
    ):

        root = Path(
            project.path
        )

        actions = []

        for folder in self.REQUIRED_FOLDERS:

            target = root / folder

            if not target.exists():

                target.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                actions.append(
                    {
                        "code": "created_missing_folder",
                        "path": str(
                            target
                        ),
                    }
                )

        return {
            "project_id": project.id,
            "actions": actions,
            "safe": True,
        }

    def issue(
        self,
        code,
        level,
        path,
        suggestion,
    ):

        return {
            "code": code,
            "level": level,
            "path": path,
            "suggestion": suggestion,
        }

    def result(
        self,
        state,
        messages,
    ):

        return {
            "state": state,
            "messages": messages,
            "blocking": any(
                item["level"] in {
                    "blocked",
                    "invalid",
                }
                for item in messages
            ),
        }
