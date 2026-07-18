import json
import time
import urllib.request


BASE_URL = "http://127.0.0.1:8765"
TOKEN = "<PASTE_TOKEN_HERE>"


def request(
    method,
    path,
    data=None,
):

    body = None

    headers = {
        "Authorization": f"Bearer {TOKEN}",
    }

    if data is not None:

        body = json.dumps(
            data,
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        headers[
            "Content-Type"
        ] = "application/json"

    req = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers=headers,
        method=method,
    )

    with urllib.request.urlopen(
        req
    ) as response:

        return json.loads(
            response.read().decode(
                "utf-8"
            )
        )


def main():

    health = urllib.request.urlopen(
        BASE_URL + "/api/v1/health"
    )

    print(
        "health",
        health.read().decode(
            "utf-8"
        ),
    )

    catalog = request(
        "GET",
        "/api/v1/voice-catalog",
    )

    print(
        "catalog voices",
        len(
            catalog.get(
                "voices",
                [],
            )
        ),
    )

    job = request(
        "POST",
        "/api/v1/generation/jobs",
        {
            "voice_id": "0001",
            "variant_id": "default",
            "text": "Nội dung cần lồng tiếng.",
            "language": "vi",
            "output_format": "wav",
            "sample_rate": 32000,
            "speed": 1.0,
            "request_id": "video-app-demo-001",
        },
    )

    print(
        "job",
        job,
    )

    job_id = job[
        "job_id"
    ]

    while True:

        status = request(
            "GET",
            f"/api/v1/generation/jobs/{job_id}",
        )

        print(
            status[
                "status"
            ],
            status.get(
                "message_vi",
                "",
            ),
        )

        if status[
            "status"
        ] in (
            "completed",
            "failed",
            "cancelled",
        ):

            break

        time.sleep(
            1
        )

    result = request(
        "GET",
        f"/api/v1/generation/jobs/{job_id}/result",
    )

    print(
        "result",
        result,
    )


if __name__ == "__main__":

    main()
