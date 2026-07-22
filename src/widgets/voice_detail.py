from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class VoiceDetail(QWidget):

    language_selection_changed = Signal(
        list,
        bool,
    )

    def __init__(self):

        super().__init__()

        self._loading_languages = False

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name = QLabel("-")
        self.engine = QLabel("-")
        self.language = QLabel("-")
        self.enabled_languages = QLabel("-")
        self.language_readiness = QLabel("-")
        self.status = QLabel("-")
        self.model = QLabel("-")
        self.dataset = QLabel("-")
        self.preview = QLabel("-")

        form.addRow(
            "Voice",
            self.name,
        )

        form.addRow(
            "Engine",
            self.engine,
        )

        form.addRow(
            "Language",
            self.language,
        )

        form.addRow(
            "Ngôn ngữ bật",
            self.enabled_languages,
        )

        form.addRow(
            "Readiness ngôn ngữ",
            self.language_readiness,
        )

        form.addRow(
            "Model",
            self.model,
        )

        form.addRow(
            "Dataset",
            self.dataset,
        )

        form.addRow(
            "Preview",
            self.preview,
        )

        form.addRow(
            "Status",
            self.status,
        )

        layout.addLayout(
            form
        )

        language_box = QGroupBox(
            "Ngôn ngữ được phép đọc"
        )

        language_layout = QVBoxLayout(
            language_box
        )

        self.all_languages_checkbox = QCheckBox(
            "Tất cả"
        )

        self.all_languages_checkbox.setToolTip(
            "Cho phép Voice đọc tất cả ngôn ngữ đã cấu hình. "
            "Tùy chọn này không tự dịch nội dung."
        )

        language_layout.addWidget(
            self.all_languages_checkbox
        )

        self.language_definitions = [
            (
                "vi",
                "Tiếng Việt",
            ),
            (
                "zh",
                "Tiếng Trung",
            ),
            (
                "en",
                "Tiếng Anh",
            ),
            (
                "ja",
                "Tiếng Nhật",
            ),
            (
                "ko",
                "Tiếng Hàn",
            ),
            (
                "yue",
                "Tiếng Quảng Đông",
            ),
        ]

        self.language_checkboxes = {}
        self.language_status_labels = {}

        for code, label in self.language_definitions:

            row = QHBoxLayout()

            checkbox = QCheckBox(
                label
            )

            status = QLabel(
                "Đã tắt"
            )

            status.setAlignment(
                Qt.AlignRight | Qt.AlignVCenter
            )

            row.addWidget(
                checkbox
            )

            row.addStretch(
                1
            )

            row.addWidget(
                status
            )

            language_layout.addLayout(
                row
            )

            self.language_checkboxes[
                code
            ] = checkbox

            self.language_status_labels[
                code
            ] = status

            checkbox.stateChanged.connect(
                self.on_language_checkbox_changed
            )

        self.all_languages_checkbox.stateChanged.connect(
            self.on_all_languages_changed
        )

        layout.addWidget(
            language_box
        )

    def clear(self):

        self.name.setText("-")
        self.engine.setText("-")
        self.language.setText("-")
        self.enabled_languages.setText("-")
        self.language_readiness.setText("-")
        self.model.setText("-")
        self.dataset.setText("-")
        self.preview.setText("-")
        self.status.setText("-")

        self._loading_languages = True

        self.all_languages_checkbox.setChecked(
            False
        )

        for code, checkbox in self.language_checkboxes.items():

            checkbox.setChecked(
                False
            )

            self.language_status_labels[
                code
            ].setText(
                "Đã tắt"
            )

        self._loading_languages = False

    def load(
        self,
        voice,
        language_capabilities=None,
    ):

        self.name.setText(
            voice.display_name
        )

        self.engine.setText(
            voice.config.engine or "-"
        )

        self.language.setText(
            voice.config.language
        )

        self.enabled_languages.setText(
            ", ".join(
                getattr(
                    voice.config,
                    "enabled_languages",
                    [
                        voice.config.language,
                    ],
                )
            )
        )

        self.language_readiness.setText(
            getattr(
                voice.config,
                "language_selection_mode",
                "selected",
            )
        )

        self.load_language_selection(
            voice,
            language_capabilities,
        )

        self.model.setText(
            voice.config.model or "-"
        )

        if hasattr(
            voice,
            "dataset_dir",
        ):

            self.dataset.setText(
                voice.dataset_dir.name
            )

        else:

            self.dataset.setText("-")

        self.preview.setText(
            "Có"
            if voice.preview.exists()
            else "Chưa có"
        )

        self.status.setText(
            voice.config.training_status
        )

    def load_language_selection(
        self,
        voice,
        language_capabilities=None,
    ):

        enabled = set(
            getattr(
                voice.config,
                "enabled_languages",
                [
                    "vi",
                ],
            )
            or [
                "vi",
            ]
        )

        all_codes = [
            code
            for code, _label in self.language_definitions
        ]

        self._loading_languages = True

        for code in all_codes:

            self.language_checkboxes[
                code
            ].setChecked(
                code in enabled
            )

            self.language_status_labels[
                code
            ].setText(
                self.status_text_for_language(
                    code,
                    enabled,
                    language_capabilities,
                )
            )

        self.all_languages_checkbox.setChecked(
            all(
                code in enabled
                for code in all_codes
            )
        )

        self._loading_languages = False

    def checked_language_codes(self):

        return [
            code
            for code, _label in self.language_definitions
            if self.language_checkboxes[
                code
            ].isChecked()
        ]

    def on_all_languages_changed(
        self,
        state,
    ):

        if self._loading_languages:

            return

        if not state:

            return

        self._loading_languages = True

        for checkbox in self.language_checkboxes.values():

            checkbox.setChecked(
                True
            )

        self._loading_languages = False

        self.language_selection_changed.emit(
            self.checked_language_codes(),
            True,
        )

    def on_language_checkbox_changed(
        self,
        _state,
    ):

        if self._loading_languages:

            return

        selected = self.checked_language_codes()

        if not selected:

            sender = self.sender()

            if sender is not None:

                self._loading_languages = True

                sender.setChecked(
                    True
                )

                self._loading_languages = False

            return

        all_selected = len(
            selected
        ) == len(
            self.language_definitions
        )

        self._loading_languages = True

        self.all_languages_checkbox.setChecked(
            all_selected
        )

        self._loading_languages = False

        self.language_selection_changed.emit(
            selected,
            all_selected,
        )

    def status_text_for_language(
        self,
        code,
        enabled,
        language_capabilities,
    ):

        if code not in enabled:

            return "Đã tắt"

        route = {}

        for item in (
            language_capabilities or {}
        ).get(
            "languages",
            [],
        ):

            if item.get(
                "code"
            ) == code:

                route = item.get(
                    "route",
                    {},
                )

                break

        status = route.get(
            "status",
            "",
        )

        reason = route.get(
            "reason",
            "",
        )

        blockers = set(
            route.get(
                "blockers",
                [],
            )
        )

        if status == "READY":

            return "Sẵn sàng"

        if any(
            "missing" in blocker or "invalid" in blocker
            for blocker in blockers
        ):

            return "Thiếu model"

        if status == "UNVERIFIED" or reason == "LANGUAGE_INFERENCE_UNVERIFIED":

            return "Chưa kiểm chứng"

        if (
            reason
            in {
                "VI_REQUIRES_VIETNAMESE_ENGINE",
                "ENGINE_ADAPTER_UNAVAILABLE",
            }
            or "engine_adapter_unavailable" in blockers
        ):

            return "Không hỗ trợ"

        return "Chưa cấu hình"
