import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from models.local_api_config import LocalApiConfig
from services.current_project_service import CurrentProjectService
from services.local_api_service import LocalApiService
from services.project_service import ProjectService


def reset_root(name):

    root = ROOT / "cache" / name

    if root.exists():

        shutil.rmtree(root)

    root.mkdir(
        parents=True,
    )

    return root


def build_project_service():

    root = reset_root(
        "test_project_manager_api"
    )

    service = ProjectService()
    service.root = root / "projects"
    service.root.mkdir(
        parents=True,
    )

    return service


def test_local_api_project_read_only_endpoints():

    service = build_project_service()

    CurrentProjectService.clear()

    project = service.create(
        "Dự án thử"
    )

    service.open_project(
        project.id,
        current_project_service=CurrentProjectService,
    )

    api = LocalApiService(
        config=LocalApiConfig(
            local_api_enabled=True,
            local_api_token="secret",
        ),
        project_service=service,
        current_project=CurrentProjectService,
    )

    listed = api.route(
        "GET",
        "/api/v1/projects",
        {},
    )

    assert listed["status_code"] == 200
    assert listed["body"]["items"][0]["project_id"] == project.id
    assert "root_path" not in listed["body"]["items"][0]

    current = api.route(
        "GET",
        "/api/v1/projects/current",
        {},
    )

    assert current["body"]["current_project"]["display_name"] == "Dự án thử"

    detail = api.route(
        "GET",
        f"/api/v1/projects/{project.id}",
        {},
    )

    assert detail["body"]["project_id"] == project.id

    health = api.route(
        "GET",
        f"/api/v1/projects/{project.id}/health",
        {},
    )

    assert health["body"]["state"] == "valid"

    workspace = api.route(
        "GET",
        "/api/v1/workspace",
        {},
    )

    assert workspace["body"]["current_project"]["project_id"] == project.id


test_local_api_project_read_only_endpoints()

print("PROJECT_MANAGER_TEST_OK")
