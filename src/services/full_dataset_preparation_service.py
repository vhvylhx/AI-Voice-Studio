from pathlib import Path
import json
import time

from models.alignment_quality_config import AlignmentQualityConfig
from models.workflow_config import WorkflowConfig
from services.dataset_repair_service import DatasetRepairService
from services.dataset_review_service import DatasetReviewService
from services.dataset_service import DatasetService
from services.train_audio_prep_service import TrainAudioPrepService


class FullDatasetPreparationService:

    def __init__(self):

        self.dataset = DatasetService()

        self.repair = DatasetRepairService()

        self.review = DatasetReviewService()

        self.audio_prep = TrainAudioPrepService()

        self.progress = []

    def run(
        self,
        workflow_config,
        quality_config=None,
        run_alignment=True,
        limit=None,
        max_new_sources=None,
        progress_callback=None,
    ):

        workflow = WorkflowConfig.from_dict(
            workflow_config
        )

        quality = (
            quality_config
            if quality_config is not None
            else AlignmentQualityConfig()
        )

        output_dir = Path(
            workflow.resolved_output_folder()
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        audio_folder = self.resolve_audio_folder(
            workflow
        )

        text_folder = self.resolve_text_folder(
            workflow
        )

        started = time.time()

        self.progress = []

        self.emit_progress(
            "scan",
            "",
            0,
            1,
            started,
            "Dang quet dataset.",
            "info",
            progress_callback,
        )

        dataset_dir = output_dir / "dataset"

        dataset = self.dataset.scan_folders(
            audio_folder=audio_folder,
            text_folder=text_folder,
            output_dir=dataset_dir,
        )

        self.emit_progress(
            "health",
            "",
            1,
            5,
            started,
            "Da tao Dataset Health.",
            "info",
            progress_callback,
        )

        repair_dir = output_dir / "repair"

        repair_report = self.repair.repair(
            dataset,
            repair_dir,
        )

        self.emit_progress(
            "repair",
            "",
            2,
            5,
            started,
            "Da chay Dataset Repair.",
            "info",
            progress_callback,
        )

        review_dir = output_dir / "review"

        review_report = self.review.create_review(
            dataset_result=dataset,
            repair_report=repair_report,
            output_dir=review_dir,
        )

        if workflow.review_mode == "auto":

            review_report = self.review.auto_review(
                review_report
            )

            self.review.write_report(
                review_report,
                review_dir,
            )

        self.emit_progress(
            "review",
            "",
            3,
            5,
            started,
            "Da tao Dataset Review.",
            "info",
            progress_callback,
        )

        alignment = None

        if run_alignment:

            alignment = self.audio_prep.prepare_from_folders(
                audio_folder,
                text_folder,
                dataset_dir,
                output_dir / "segmentation",
                output_dir / "alignment",
                limit=limit,
                max_new_sources=max_new_sources,
                quality_config=quality,
                review_report=review_report,
                progress_callback=progress_callback,
            )

        self.emit_progress(
            "metadata_validation",
            "",
            5,
            5,
            started,
            "Hoan tat Dataset Preparation.",
            "success",
            progress_callback,
            valid=len(
                (alignment or {}).get(
                    "valid",
                    [],
                )
            ),
            suspicious=len(
                (alignment or {}).get(
                    "suspicious",
                    [],
                )
            ),
            errors=len(
                (alignment or {}).get(
                    "errors",
                    [],
                )
            ),
        )

        report = self.create_report(
            dataset,
            repair_report,
            review_report,
            alignment,
            output_dir,
            workflow,
            quality,
        )

        self.write_json(
            output_dir / "full_dataset_report.json",
            report,
        )

        return {
            "dataset": dataset,
            "repair": repair_report,
            "review": review_report,
            "alignment": alignment,
            "report": report,
            "progress": self.progress,
        }

    def create_report(
        self,
        dataset,
        repair_report,
        review_report,
        alignment,
        output_dir,
        workflow,
        quality,
    ):

        health = dataset.get(
            "health",
            {},
        )

        alignment_report = (
            alignment or {}
        ).get(
            "report",
            {},
        )

        summary = dict(
            health
        )

        alignment_summary = alignment_report.get(
            "summary",
            {},
        )

        summary.update(
            {
                "source_processed": len(
                    alignment_report.get(
                        "source_reports",
                        [],
                    )
                ),
                "source_skipped": len(
                    [
                        item
                        for item in alignment_report.get(
                            "source_reports",
                            [],
                        )
                        if item.get(
                            "skipped_entire_file"
                        )
                    ]
                ),
                "valid_clips": alignment_summary.get(
                    "valid_clips",
                    0,
                ),
                "suspicious_clips": alignment_summary.get(
                    "suspicious_clips",
                    0,
                ),
                "errors": alignment_summary.get(
                    "errors",
                    0,
                ),
                "total_valid_duration": alignment_summary.get(
                    "total_valid_duration",
                    0.0,
                ),
                "similarity_min": alignment_summary.get(
                    "similarity_min",
                    0.0,
                ),
                "similarity_avg": alignment_summary.get(
                    "similarity_avg",
                    0.0,
                ),
                "similarity_max": alignment_summary.get(
                    "similarity_max",
                    0.0,
                ),
                "metadata_list": alignment_summary.get(
                    "metadata_path",
                    "",
                ),
            }
        )

        return {
            "schema_version": 1,
            "workflow": workflow.to_dict(),
            "quality_config": quality.to_dict(),
            "output_dir": str(
                output_dir
            ),
            "summary": summary,
            "dataset_health": health,
            "repair_summary": {
                "repaired": len(
                    repair_report.get(
                        "repaired",
                        [],
                    )
                ),
                "skipped": len(
                    repair_report.get(
                        "skipped",
                        [],
                    )
                ),
                "final_usable_percent": repair_report.get(
                    "final_usable_percent",
                    0.0,
                ),
            },
            "review_summary": review_report.get(
                "summary",
                {},
            ),
            "metadata_validation": (
                alignment_report.get(
                    "metadata_validation",
                    {},
                )
                if alignment_report
                else {}
            ),
        }

    def emit_progress(
        self,
        stage,
        current_file,
        current_item,
        total_items,
        started,
        message,
        level,
        progress_callback=None,
        valid=0,
        suspicious=0,
        errors=0,
    ):

        elapsed = max(
            0.0,
            time.time() - started,
        )

        percent = (
            current_item / total_items * 100
            if total_items
            else 0
        )

        estimated = (
            elapsed / current_item * (total_items - current_item)
            if current_item and current_item < total_items
            else 0
        )

        payload = {
            "stage": stage,
            "current_file": current_file,
            "current_item": current_item,
            "total_items": total_items,
            "percent": percent,
            "elapsed_seconds": elapsed,
            "estimated_remaining_seconds": estimated,
            "valid": valid,
            "suspicious": suspicious,
            "errors": errors,
            "message": message,
            "level": level,
        }

        self.progress.append(
            payload
        )

        if progress_callback:

            progress_callback(
                payload
            )

        return payload

    def resolve_audio_folder(
        self,
        workflow,
    ):

        if workflow.source_mode == "same_folder":

            return (
                workflow.input_folder
                or workflow.audio_folder
                or workflow.text_folder
            )

        return workflow.audio_folder

    def resolve_text_folder(
        self,
        workflow,
    ):

        if workflow.source_mode == "same_folder":

            return (
                workflow.input_folder
                or workflow.text_folder
                or workflow.audio_folder
            )

        return workflow.text_folder

    def write_json(
        self,
        file,
        data,
    ):

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )
