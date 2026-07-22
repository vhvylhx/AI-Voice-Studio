import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(
    0,
    str(
        SRC
    ),
)

from services.vieneu_controlled_import_service import (  # noqa: E402
    VieneuControlledImportService,
)


class FakeAudioService:

    def __init__(
        self,
        metadata=None,
    ):

        self.metadata = metadata or {
            "duration": 6.5,
            "sample_rate": 32000,
            "channels": 1,
            "codec": "pcm_s16le",
        }

    def probe(
        self,
        audio,
    ):

        return dict(
            self.metadata
        )


def test_default_plan_uses_managed_cache_root(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    plan = service.build_plan(
        allow_download=True,
        allow_gpu_runtime=False,
        allow_cpu_torch_frontend=True,
    )

    assert "cache" in plan.target_root
    assert "vieneu_tts" in plan.target_root
    assert plan.selection[
        "model_repo"
    ] == "pnnbao-ump/VieNeu-TTS-v3-Turbo"
    assert plan.license_gate == "PASS"
    assert plan.revision_gate == "PASS"


def test_source_contract_supports_cpu_onnx_ref_audio_without_gpu(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    contract = service.source_contract()

    assert contract.cpu_onnx_ref_audio_supported
    assert not contract.gpu_required_for_ref_audio
    assert contract.torch_import_required_for_fresh_ref_audio
    assert contract.cpu_torch_frontend_required_for_fresh_reference_enrollment
    assert not contract.cuda_allowed
    assert not contract.strict_torch_free_fresh_ref_audio_supported
    assert (
        contract.decision
        == "CPU_ONNX_REF_AUDIO_SUPPORTED_WITH_CPU_TORCH_FRONTEND"
    )
    assert "cpu_onnx_ref_audio_requires_torchaudio_frontend_in_vieneu_3_2_3" not in contract.blockers


def test_cpu_onnx_reference_cloning_requires_explicit_cpu_frontend_permission(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    plan = service.build_plan(
        allow_download=True,
        allow_gpu_runtime=False,
    )

    assert not plan.ready_for_canary
    assert (
        "cpu_torch_frontend_permission_required"
        in plan.blockers
    )


def test_cpu_onnx_canary_does_not_require_gpu_when_torch_free_not_required(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    plan = service.build_plan(
        allow_download=True,
        allow_gpu_runtime=False,
        require_torch_free=False,
        allow_cpu_torch_frontend=True,
    )

    assert plan.low_resource_gate == "PASS"
    assert plan.ready_for_canary
    assert (
        "reference_cloning_requires_pytorch_gpu_per_current_sdk_docs"
        not in plan.blockers
    )
    assert (
        "cpu_torch_frontend_required_for_fresh_reference_enrollment"
        not in plan.blockers
    )


def test_cpu_onnx_canary_blocks_gpu_runtime(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    plan = service.build_plan(
        allow_download=True,
        allow_gpu_runtime=True,
        allow_cpu_torch_frontend=True,
    )

    assert not plan.ready_for_canary
    assert "gpu_runtime_not_allowed_for_vieneu_cpu_canary" in plan.blockers


def test_no_download_without_explicit_service_permission(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    plan = service.build_plan(
        allow_download=False,
        allow_gpu_runtime=False,
        allow_cpu_torch_frontend=True,
    )

    assert not plan.ready_to_download
    assert "download_permission_not_enabled_for_service_call" in plan.blockers


def test_reference_validation_accepts_voice_0001_candidate_shape(tmp_path):

    audio = tmp_path / "reference.wav"
    audio.write_bytes(
        b"not-real-audio-but-probed-by-fake"
    )

    service = VieneuControlledImportService(
        app_root=tmp_path,
        audio_service=FakeAudioService(),
    )

    reference = service.validate_reference(
        audio,
        "Tùy ý một pháp tướng phá diệt.",
    )

    assert reference.status == "valid"
    assert reference.duration == 6.5
    assert reference.sample_rate == 32000
    assert reference.requires_resample_copy


def test_reference_validation_blocks_missing_text(tmp_path):

    audio = tmp_path / "reference.wav"
    audio.write_bytes(
        b"not-real-audio-but-probed-by-fake"
    )

    service = VieneuControlledImportService(
        app_root=tmp_path,
        audio_service=FakeAudioService(),
    )

    reference = service.validate_reference(
        audio,
        "",
    )

    assert reference.status == "blocked"
    assert "reference_text_missing" in reference.blockers


def test_canary_report_does_not_unlock_readiness_when_blocked(tmp_path):

    audio = tmp_path / "reference.wav"
    audio.write_bytes(
        b"not-real-audio-but-probed-by-fake"
    )

    service = VieneuControlledImportService(
        app_root=tmp_path,
        audio_service=FakeAudioService(),
    )

    plan = service.build_plan(
        allow_download=True,
        allow_gpu_runtime=False,
    )
    reference = service.validate_reference(
        audio,
        "Tùy ý một pháp tướng phá diệt.",
    )
    report = service.prepare_canary_report(
        plan,
        reference,
        run_id="vieneu_canary_test",
    )

    assert report.status == "BLOCKED"
    assert report.readiness_effect[
        "generate_execution"
    ] == "BLOCKED"
    assert report.readiness_effect[
        "wav_output"
    ] == "BLOCKED"


def test_write_report_only_under_diagnostics_or_cache(tmp_path):

    audio = tmp_path / "reference.wav"
    audio.write_bytes(
        b"not-real-audio-but-probed-by-fake"
    )

    service = VieneuControlledImportService(
        app_root=tmp_path,
        audio_service=FakeAudioService(),
    )

    plan = service.build_plan(
        allow_download=True,
        allow_gpu_runtime=False,
    )
    reference = service.validate_reference(
        audio,
        "Tùy ý một pháp tướng phá diệt.",
    )
    report = service.prepare_canary_report(
        plan,
        reference,
        run_id="vieneu_canary_test",
    )

    path = service.write_report(
        report
    )

    assert path.exists()
    assert path.name == "vieneu_canary_report.json"


def test_install_plan_uses_cpu_only_torch_index(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    plan = service.build_plan(
        allow_download=True,
        allow_gpu_runtime=False,
        allow_cpu_torch_frontend=True,
    )

    flattened = " ".join(
        " ".join(
            command
        )
        for command in plan.install_commands
    )

    assert "download.pytorch.org/whl/cpu" in flattened
    assert "download.pytorch.org/whl/cu" not in flattened
    assert "onnxruntime-gpu" not in flattened
    assert "truststore==0.10.4" in flattened


def test_cpu_runtime_payload_blocks_cuda_provider(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    result = service.verify_cpu_only_runtime_payload(
        {
            "torch_cuda_available": False,
            "onnx_providers": [
                "CPUExecutionProvider",
                "CUDAExecutionProvider",
            ],
        }
    )

    assert result[
        "status"
    ] == "BLOCKED"
    assert "onnx_cuda_provider_available" in result[
        "blockers"
    ]


def test_cpu_runtime_payload_blocks_forbidden_gpu_package(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    result = service.verify_cpu_only_runtime_payload(
        {
            "torch_cuda_available": False,
            "onnx_providers": [
                "CPUExecutionProvider",
            ],
            "installed_packages": [
                "onnxruntime-gpu",
            ],
        }
    )

    assert result[
        "status"
    ] == "BLOCKED"
    assert "forbidden_gpu_package_installed" in result[
        "blockers"
    ]


def test_runtime_manifest_records_cpu_only_policy(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    plan = service.build_plan(
        allow_download=True,
        allow_gpu_runtime=False,
        allow_cpu_torch_frontend=True,
    )

    manifest = service.build_runtime_manifest(
        plan,
        {
            "python_version": "3.12.0",
            "onnxruntime_version": "1.23.2",
            "torch_version": "2.8.0+cpu",
            "torchaudio_version": "2.8.0+cpu",
            "torch_cuda_available": False,
            "onnx_providers": [
                "CPUExecutionProvider",
            ],
        },
    )

    assert manifest.status == "READY"
    assert manifest.cpu_only
    assert not manifest.cuda_expected
    assert manifest.fingerprint


def test_experimental_adapter_is_canary_only(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    capabilities = service.experimental_adapter_capabilities()

    assert capabilities[
        "scope"
    ] == "EXPERIMENTAL_CANARY_ONLY"
    assert not capabilities[
        "production_provider_registered"
    ]


def test_codec_contract_uses_single_moss_repo(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    codec = service.default_codec_selection()

    assert codec.repo_id == "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX"
    assert len(
        codec.required_files
    ) == 6
    assert "moss_audio_tokenizer_encode.onnx" in codec.required_files
    assert "moss_audio_tokenizer_decode_full.onnx" in codec.required_files


def test_codec_partial_download_is_not_ready(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    codec_root = tmp_path / "codec"
    codec_root.mkdir()
    (
        codec_root / "moss_audio_tokenizer_encode.onnx"
    ).write_bytes(
        b"partial"
    )

    result = service.verify_codec_completeness(
        codec_root
    )

    assert result[
        "status"
    ] == "BLOCKED"
    assert "codec_required_file_missing" in result[
        "blockers"
    ]


def test_codec_size_mismatch_is_not_ready(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    codec_root = tmp_path / "codec"
    codec_root.mkdir()

    for filename in service.CODEC_REQUIRED_FILES:

        (
            codec_root / filename
        ).write_bytes(
            b"x"
        )

    result = service.verify_codec_completeness(
        codec_root,
        expected_sizes={
            service.CODEC_REQUIRED_FILES[
                0
            ]: 2,
        },
    )

    assert result[
        "status"
    ] == "BLOCKED"
    assert "codec_size_mismatch" in result[
        "blockers"
    ]


def test_resource_profile_is_low_resource_cpu_only(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    profile = service.resource_safety_profile()

    assert profile.profile_id == "low_resource_safe_32gb"
    assert profile.inference_concurrency == 1
    assert profile.subprocess_concurrency == 1
    assert profile.batch_size == 1
    assert profile.cpu_threads == 2
    assert profile.process_priority == "BELOW_NORMAL"
    assert not profile.gpu_allowed


def test_resource_preflight_blocks_under_8gb(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    result = service.resource_preflight_decision(
        available_ram_gb=7.9
    )

    assert result[
        "status"
    ] == "BLOCKED"
    assert "available_ram_below_start_threshold" in result[
        "blockers"
    ]


def test_resource_phase_decisions(tmp_path):

    service = VieneuControlledImportService(
        app_root=tmp_path
    )

    assert service.can_start_next_canary_phase(
        8.0
    )[
        "decision"
    ] == "continue"
    assert service.can_start_next_canary_phase(
        7.0
    )[
        "decision"
    ] == "do_not_start_next_phase"
    assert service.can_start_next_canary_phase(
        5.0
    )[
        "decision"
    ] == "stop_at_safe_boundary"
    assert service.can_start_next_canary_phase(
        3.9
    )[
        "decision"
    ] == "cancel_and_cleanup"
