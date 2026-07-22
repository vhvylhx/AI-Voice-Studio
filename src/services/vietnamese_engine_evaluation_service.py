from __future__ import annotations

from models.vietnamese_engine_evaluation import (
    EVIDENCE_CLAIMED,
    EVIDENCE_NOT_VERIFIED,
    EVIDENCE_UNSUPPORTED,
    LICENSE_BLOCKED,
    LICENSE_PASS,
    LICENSE_UNVERIFIED,
    SCORE_CLAIMED_ONLY,
    SCORE_MANUAL_REVIEW_REQUIRED,
    SCORE_NOT_TESTED,
    CandidateScore,
    DownloadPlan,
    EngineEvaluationRecord,
    LicenseAudit,
    LowResourceSafetyProfile,
)


class VietnameseEngineEvaluationService:

    def low_resource_profile(
        self,
    ):

        return LowResourceSafetyProfile().to_dict()

    def candidates(
        self,
    ):

        return [
            self.vieneu_record(),
            self.f5_vietnamese_record(),
            self.vixtts_record(),
        ]

    def summary(
        self,
    ):

        items = [
            item.to_dict()
            for item in self.candidates()
        ]

        return {
            "status": "STATIC_AUDIT_COMPLETE",
            "selection_result": self.recommendation(),
            "items": items,
            "low_resource_profile": self.low_resource_profile(),
            "canary": self.local_canary_plan(),
            "readiness_effect": {
                "vietnamese_engine_binding": "BLOCKED_PENDING_ENGINE_SELECTION",
                "generate_readiness_unlocked": False,
                "voice_binding_changed": False,
            },
        }

    def recommendation(
        self,
    ):

        records = self.candidates()

        vieneu = next(
            item
            for item in records
            if item.engine_id == "vieneu_tts"
        )

        if not vieneu.blockers:

            return "VIENEU_PRIMARY_CANDIDATE"

        return "NO_PRODUCTION_CANDIDATE_VERIFIED"

    def local_canary_plan(
        self,
    ):

        return {
            "status": "SKIPPED",
            "reason": "model_not_confirmed_locally_and_no_download_permission",
            "max_processes_per_engine": 1,
            "batch_size": 1,
            "parallel": False,
            "output_root": "diagnostics/evaluation",
            "production_write": False,
            "voice_binding_changed": False,
            "readiness_unlocked": False,
        }

    def download_plans(
        self,
    ):

        return {
            "items": [
                record.download_plan
                for record in self.candidates()
            ]
        }

    def scorecard_criteria(
        self,
        claimed=False,
    ):

        status = (
            SCORE_CLAIMED_ONLY
            if claimed
            else SCORE_NOT_TESTED
        )

        subjective = {
            "voice_similarity",
            "vietnamese_pronunciation",
            "tone_marks",
            "proper_names",
            "naturalness",
            "long_sentence_stability",
            "repetition_hallucination",
            "storytelling_style",
        }

        criteria = [
            "voice_similarity",
            "vietnamese_pronunciation",
            "tone_marks",
            "proper_names",
            "naturalness",
            "long_sentence_stability",
            "repetition_hallucination",
            "storytelling_style",
            "cpu_speed",
            "p1000_speed",
            "ram_vram",
            "windows_integration",
            "fine_tuning_private_dataset",
            "license",
            "maintenance_api_stability",
        ]

        result = []

        for criterion in criteria:

            item_status = status

            if criterion in subjective:

                item_status = SCORE_MANUAL_REVIEW_REQUIRED

            result.append(
                CandidateScore(
                    criterion=criterion,
                    status=item_status,
                    notes="Chưa nghe audio local trong AVS-014.21.",
                ).to_dict()
            )

        return result

    def vieneu_record(
        self,
    ):

        license_audit = LicenseAudit(
            source_code_license="Apache-2.0",
            model_checkpoint_license="Apache-2.0 for v2/v3 public package per model card; 0.3B experimental packages may be CC BY-NC 4.0 depending on chosen checkpoint",
            dataset_restrictions="Must verify selected checkpoint card before download/use.",
            commercial_use="allowed_for_apache_packages_only",
            attribution_required=True,
            redistribution_restriction="Keep upstream/package notices for Apache packages; do not redistribute NC checkpoints commercially.",
            status=LICENSE_PASS,
            notes=[
                "Production selection must lock a specific model repo/revision before download.",
            ],
            evidence_urls=[
                "https://github.com/pnnbao97/VieNeu-TTS",
                "https://docs.vieneu.io/docs/sdk/standard-mode/",
                "https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo",
            ],
        )

        download_plan = DownloadPlan(
            engine_id="vieneu_tts",
            model_id="pnnbao-ump/VieNeu-TTS-v3-Turbo or locked CPU/ONNX package",
            source="Hugging Face / VieNeu official package",
            revision="REQUIRED_BEFORE_DOWNLOAD",
            expected_files=[
                "model weights",
                "codec/checkpoint files",
                "config/tokenizer metadata",
            ],
            expected_size="UNKNOWN_UNTIL_LOCKED",
            checksum="REQUIRED_IF_AVAILABLE",
            license="Apache-2.0 package preferred",
            target_cache="cache/engines/vieneu_tts/<revision>/",
            disk_free_required="expected_size + 2GB safety margin",
            resumable=True,
            ready_to_download=False,
            blockers=[
                "revision_not_locked",
                "expected_size_not_verified_locally",
                "user_permission_required",
            ],
        ).to_dict()

        return EngineEvaluationRecord(
            engine_id="vieneu_tts",
            display_name="VieNeu-TTS",
            upstream_repository="https://github.com/pnnbao97/VieNeu-TTS",
            version_commit_tag="STATIC_AUDIT_2026-07-18",
            source_license="Apache-2.0",
            model_checkpoint_license=license_audit.model_checkpoint_license,
            windows_compatibility={
                "status": EVIDENCE_CLAIMED,
                "notes": "README/docs show Windows install path and CPU/ONNX mode.",
            },
            python_version={
                "status": EVIDENCE_NOT_VERIFIED,
                "notes": "Separate runtime should be validated before integration.",
            },
            cuda_requirements={
                "status": EVIDENCE_CLAIMED,
                "notes": "GPU mode requires modern CUDA; CPU/ONNX path is preferred for P1000 safety.",
            },
            cpu_inference={
                "status": EVIDENCE_CLAIMED,
                "notes": "ONNX/GGUF CPU path is documented.",
            },
            gpu_inference={
                "status": EVIDENCE_CLAIMED,
                "notes": "GPU path exists, but AVS should not load with GPT-SoVITS concurrently.",
            },
            minimum_observed_ram={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            minimum_observed_vram={
                "status": EVIDENCE_NOT_VERIFIED,
                "notes": "Prefer CPU mode until measured locally.",
            },
            model_size={
                "status": EVIDENCE_CLAIMED,
                "notes": "Packages range from small quantized to larger PyTorch checkpoints.",
            },
            sample_rate={
                "status": EVIDENCE_CLAIMED,
                "value": "24kHz for v2, 48kHz for v3 Turbo per upstream docs.",
            },
            voice_cloning_support={
                "status": EVIDENCE_CLAIMED,
                "value": True,
            },
            reference_audio_requirements={
                "status": EVIDENCE_CLAIMED,
                "notes": "3-8 seconds for v3 Turbo; v2 docs mention 3-5 seconds.",
            },
            reference_text_requirements={
                "status": EVIDENCE_CLAIMED,
                "notes": "Turbo path can clone without reference text; Standard may need reference text.",
            },
            vietnamese_pronunciation={
                "status": EVIDENCE_CLAIMED,
            },
            long_form_support={
                "status": EVIDENCE_CLAIMED,
            },
            style_emotion_support={
                "status": EVIDENCE_CLAIMED,
            },
            streaming_support={
                "status": EVIDENCE_CLAIMED,
            },
            fine_tuning_support={
                "status": EVIDENCE_CLAIMED,
                "notes": "Custom models/LoRA path exists; production fine-tune not part of this sprint.",
            },
            offline_support={
                "status": EVIDENCE_CLAIMED,
            },
            api_cli_library_integration={
                "status": EVIDENCE_CLAIMED,
                "notes": "Python SDK and web UI documented.",
            },
            maintenance_state={
                "status": EVIDENCE_CLAIMED,
                "notes": "Active upstream/docs as of static audit.",
            },
            known_limitations=[
                "Needs locked model package, license and disk plan before download.",
                "Local quality not measured yet.",
            ],
            blockers=[],
            recommendation="Primary candidate for next controlled local canary.",
            license_audit=license_audit.to_dict(),
            download_plan=download_plan,
            scorecard=self.scorecard_criteria(
                claimed=True
            ),
            evidence_urls=license_audit.evidence_urls,
        )

    def f5_vietnamese_record(
        self,
    ):

        license_audit = LicenseAudit(
            source_code_license="MIT for upstream SWivid/F5-TTS",
            model_checkpoint_license="CC-BY-NC-SA-4.0 / CC-BY-NC-4.0 for common Vietnamese checkpoints found in static audit",
            dataset_restrictions="Vietnamese fine-tunes cite ViVoice/VLSP datasets; commercial terms must be reviewed per checkpoint.",
            commercial_use="blocked_for_nc_checkpoints",
            attribution_required=True,
            redistribution_restriction="Non-commercial/share-alike restrictions for audited Vietnamese checkpoints.",
            status=LICENSE_BLOCKED,
            blockers=[
                "model_checkpoint_non_commercial",
            ],
            notes=[
                "Source license does not replace model/checkpoint license.",
            ],
            evidence_urls=[
                "https://github.com/SWivid/F5-TTS",
                "https://huggingface.co/hynt/F5-TTS-Vietnamese-ViVoice/blob/main/README.md",
                "https://huggingface.co/toandev/F5-TTS-Vietnamese/tree/main",
            ],
        )

        download_plan = DownloadPlan(
            engine_id="f5_tts_vietnamese",
            model_id="hynt/F5-TTS-Vietnamese-ViVoice or toandev/F5-TTS-Vietnamese",
            source="Hugging Face Vietnamese fine-tuned checkpoints",
            revision="REQUIRED_BEFORE_DOWNLOAD",
            expected_files=[
                "model_last.pt or model_latest.safetensors",
                "config.json",
                "vocab.txt",
            ],
            expected_size="1.35GB-6.74GB depending checkpoint",
            checksum="REQUIRED_IF_AVAILABLE",
            license=license_audit.model_checkpoint_license,
            target_cache="models/vietnamese/f5_tts/<revision>/",
            disk_free_required="expected_size + 2GB safety margin",
            resumable=True,
            ready_to_download=False,
            blockers=[
                "model_checkpoint_non_commercial",
                "user_permission_required",
            ],
        ).to_dict()

        return EngineEvaluationRecord(
            engine_id="f5_tts_vietnamese",
            display_name="F5-TTS Vietnamese",
            upstream_repository="https://github.com/SWivid/F5-TTS",
            version_commit_tag="STATIC_AUDIT_2026-07-18",
            source_license=license_audit.source_code_license,
            model_checkpoint_license=license_audit.model_checkpoint_license,
            windows_compatibility={
                "status": EVIDENCE_CLAIMED,
                "notes": "Python CLI path exists; local Windows/P1000 not verified.",
            },
            python_version={
                "status": EVIDENCE_CLAIMED,
                "notes": "Official project documents Python >=3.10 style environment.",
            },
            cuda_requirements={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            cpu_inference={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            gpu_inference={
                "status": EVIDENCE_CLAIMED,
            },
            minimum_observed_ram={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            minimum_observed_vram={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            model_size={
                "status": EVIDENCE_CLAIMED,
                "value": download_plan["expected_size"],
            },
            sample_rate={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            voice_cloning_support={
                "status": EVIDENCE_CLAIMED,
                "value": True,
            },
            reference_audio_requirements={
                "status": EVIDENCE_CLAIMED,
                "notes": "CLI uses ref_audio.",
            },
            reference_text_requirements={
                "status": EVIDENCE_CLAIMED,
                "notes": "CLI uses ref_text.",
            },
            vietnamese_pronunciation={
                "status": EVIDENCE_CLAIMED,
            },
            long_form_support={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            style_emotion_support={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            streaming_support={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            fine_tuning_support={
                "status": EVIDENCE_CLAIMED,
            },
            offline_support={
                "status": EVIDENCE_CLAIMED,
            },
            api_cli_library_integration={
                "status": EVIDENCE_CLAIMED,
                "notes": "CLI inference contract is documented by model cards.",
            },
            maintenance_state={
                "status": EVIDENCE_CLAIMED,
            },
            known_limitations=[
                "Vietnamese checkpoints audited are non-commercial.",
                "Large checkpoint sizes are risky for blind download.",
            ],
            blockers=license_audit.blockers,
            recommendation="Good technical comparison candidate; not production default while checkpoint license is non-commercial.",
            license_audit=license_audit.to_dict(),
            download_plan=download_plan,
            scorecard=self.scorecard_criteria(
                claimed=True
            ),
            evidence_urls=license_audit.evidence_urls,
        )

    def vixtts_record(
        self,
    ):

        license_audit = LicenseAudit(
            source_code_license="XTTS/Transformers integration, upstream-specific",
            model_checkpoint_license="coqui-public-model-license",
            dataset_restrictions="Must review Coqui public model terms before redistribution/commercial use.",
            commercial_use="license_review_required",
            attribution_required=True,
            redistribution_restriction="Coqui public model license terms apply.",
            status=LICENSE_UNVERIFIED,
            blockers=[
                "production_default_disallowed_by_sprint",
                "license_requires_review",
            ],
            evidence_urls=[
                "https://huggingface.co/capleaf/viXTTS/tree/main",
            ],
        )

        download_plan = DownloadPlan(
            engine_id="vixtts",
            model_id="capleaf/viXTTS",
            source="Hugging Face",
            revision="REQUIRED_BEFORE_DOWNLOAD",
            expected_files=[
                "model.pth",
                "config.json",
                "vocab.json",
                "LICENSE.txt",
            ],
            expected_size="1.88GB",
            checksum="REQUIRED_IF_AVAILABLE",
            license=license_audit.model_checkpoint_license,
            target_cache="models/vietnamese/vixtts/<revision>/",
            disk_free_required="expected_size + 2GB safety margin",
            resumable=True,
            ready_to_download=False,
            blockers=[
                "production_default_disallowed_by_sprint",
                "license_requires_review",
                "user_permission_required",
            ],
        ).to_dict()

        return EngineEvaluationRecord(
            engine_id="vixtts",
            display_name="viXTTS",
            upstream_repository="https://huggingface.co/capleaf/viXTTS",
            version_commit_tag="STATIC_AUDIT_2026-07-18",
            source_license=license_audit.source_code_license,
            model_checkpoint_license=license_audit.model_checkpoint_license,
            windows_compatibility={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            python_version={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            cuda_requirements={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            cpu_inference={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            gpu_inference={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            minimum_observed_ram={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            minimum_observed_vram={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            model_size={
                "status": EVIDENCE_CLAIMED,
                "value": "1.88GB",
            },
            sample_rate={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            voice_cloning_support={
                "status": EVIDENCE_CLAIMED,
            },
            reference_audio_requirements={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            reference_text_requirements={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            vietnamese_pronunciation={
                "status": EVIDENCE_CLAIMED,
            },
            long_form_support={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            style_emotion_support={
                "status": EVIDENCE_UNSUPPORTED,
            },
            streaming_support={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            fine_tuning_support={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            offline_support={
                "status": EVIDENCE_CLAIMED,
            },
            api_cli_library_integration={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            maintenance_state={
                "status": EVIDENCE_NOT_VERIFIED,
            },
            known_limitations=[
                "Sprint requires viXTTS only as comparison, not production default.",
                "License needs deeper review before commercial production use.",
            ],
            blockers=license_audit.blockers,
            recommendation="Comparison-only candidate.",
            license_audit=license_audit.to_dict(),
            download_plan=download_plan,
            scorecard=self.scorecard_criteria(
                claimed=False
            ),
            evidence_urls=license_audit.evidence_urls,
        )
