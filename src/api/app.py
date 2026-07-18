from services.local_api_service import LocalApiService


def create_local_api_service(
    config=None,
    voice_catalog=None,
    job_service=None,
    readiness=None,
    style_profiles=None,
):

    return LocalApiService(
        config=config,
        voice_catalog=voice_catalog,
        job_service=job_service,
        readiness=readiness,
        style_profiles=style_profiles,
    )
