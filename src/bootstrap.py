import json
import subprocess
import sys
from pathlib import Path

from services.bootstrap_service import BootstrapService


def safe_print(
    text,
):

    try:

        print(
            text
        )

    except UnicodeEncodeError:

        encoding = getattr(
            sys.stdout,
            "encoding",
            None,
        ) or "utf-8"

        data = str(
            text
        ).encode(
            encoding,
            errors="replace",
        )

        sys.stdout.buffer.write(
            data + b"\n"
        )


def run(
    launch_main=True,
):

    service = BootstrapService()

    target = service.startup_target()

    if target[
        "target"
    ] == "main_application":

        if launch_main:

            return subprocess.call(
                [
                    sys.executable,
                    str(
                        Path(
                            __file__
                        ).with_name(
                            "main.py"
                        )
                    ),
                ]
            )

        return target

    safe_print(
        "AI Voice Studio cần thiết lập môi trường trước khi mở giao diện chính."
    )

    for issue in target[
        "status"
    ].get(
        "issues",
        [],
    ):

        safe_print(
            f"- {issue.get('message_vi', issue.get('component', ''))}"
        )

        for line in issue.get(
            "remediation",
            [],
        ):

            safe_print(
                f"  * {line}"
            )

    if not launch_main:

        return target

    return 1


if __name__ == "__main__":

    result = run(
        launch_main=False
    )

    if isinstance(
        result,
        dict,
    ):

        safe_print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False,
            )
        )
