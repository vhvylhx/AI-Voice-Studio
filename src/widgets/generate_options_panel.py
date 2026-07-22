from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.generate_config import (
    GENERATE_MODE_AI_STYLE,
    GENERATE_MODE_STANDARD,
    GenerateAudioProfile,
    GenerateRequest,
    GenerateSelectionConfig,
    SpeedProfile,
)


class GenerateOptionsPanel(QWidget):

    def __init__(self):

        super().__init__()

        root = QVBoxLayout(self)

        source_box = QGroupBox(
            "Nguồn văn bản"
        )

        source_layout = QVBoxLayout(
            source_box
        )

        self.direct_text = QTextEdit()

        self.direct_text.setPlaceholderText(
            "Dán văn bản cần tạo audio..."
        )

        source_layout.addWidget(
            self.direct_text
        )

        file_row = QHBoxLayout()

        self.input_path = QLineEdit()

        self.input_path.setPlaceholderText(
            "TXT/DOCX..."
        )

        self.choose_txt_button = QPushButton(
            "Chọn TXT"
        )

        self.choose_docx_button = QPushButton(
            "Chọn DOCX"
        )

        file_row.addWidget(
            self.input_path
        )

        file_row.addWidget(
            self.choose_txt_button
        )

        file_row.addWidget(
            self.choose_docx_button
        )

        source_layout.addLayout(
            file_row
        )

        root.addWidget(
            source_box
        )

        options_box = QGroupBox(
            "Cấu hình Generate"
        )

        form = QFormLayout(
            options_box
        )

        self.mode_combo = QComboBox()

        self.mode_combo.addItem(
            "Standard Mode",
            GENERATE_MODE_STANDARD,
        )

        self.mode_combo.addItem(
            "AI Style Mode",
            GENERATE_MODE_AI_STYLE,
        )

        form.addRow(
            "Chế độ",
            self.mode_combo,
        )

        self.language_mode_combo = QComboBox()

        self.language_mode_combo.addItem(
            "Tự động phát hiện",
            "auto",
        )

        self.language_mode_combo.addItem(
            "Chọn ngôn ngữ cố định",
            "fixed",
        )

        self.language_mode_combo.addItem(
            "Văn bản đa ngôn ngữ",
            "multilingual",
        )

        form.addRow(
            "Ngôn ngữ",
            self.language_mode_combo,
        )

        self.fixed_language_combo = QComboBox()

        form.addRow(
            "Ngôn ngữ cố định",
            self.fixed_language_combo,
        )

        self.language_preview = QLabel(
            "Language route: -"
        )

        self.language_preview.setWordWrap(
            True
        )

        form.addRow(
            "Preview route",
            self.language_preview,
        )

        self.variant_combo = QComboBox()

        form.addRow(
            "Variant",
            self.variant_combo,
        )

        self.allow_all_variants = QCheckBox(
            "Tất cả Variant"
        )

        form.addRow(
            "",
            self.allow_all_variants,
        )

        self.variant_list = QListWidget()

        form.addRow(
            "Variant AI",
            self.variant_list,
        )

        self.allow_all_styles = QCheckBox(
            "Tất cả Style"
        )

        form.addRow(
            "",
            self.allow_all_styles,
        )

        self.style_list = QListWidget()

        form.addRow(
            "Style AI",
            self.style_list,
        )

        self.preset_combo = QComboBox()

        self.preset_combo.addItem(
            "Mặc định",
            "",
        )

        form.addRow(
            "Preset",
            self.preset_combo,
        )

        self.reference_style_combo = QComboBox()

        self.reference_style_combo.addItem(
            "Không chọn",
            "",
        )

        form.addRow(
            "Reference Style",
            self.reference_style_combo,
        )

        self.text_profile_combo = QComboBox()

        self.text_profile_combo.addItem(
            "Mặc định",
            "",
        )

        form.addRow(
            "Text Profile",
            self.text_profile_combo,
        )

        self.speed_combo = QComboBox()

        for speed in [
            0.5,
            0.75,
            1.0,
            1.1,
            1.2,
            1.3,
            1.5,
        ]:

            self.speed_combo.addItem(
                str(speed),
                speed,
            )

        form.addRow(
            "Speed",
            self.speed_combo,
        )

        self.output_folder = QLineEdit()

        self.output_button = QPushButton(
            "Chọn Output"
        )

        output_row = QHBoxLayout()

        output_row.addWidget(
            self.output_folder
        )

        output_row.addWidget(
            self.output_button
        )

        form.addRow(
            "Output Folder",
            output_row,
        )

        self.output_name = QLineEdit(
            "output"
        )

        form.addRow(
            "Tên file",
            self.output_name,
        )

        self.output_format = QComboBox()

        self.output_format.addItem(
            "WAV",
            "wav",
        )

        self.output_format.addItem(
            "MP3",
            "mp3",
        )

        form.addRow(
            "Định dạng",
            self.output_format,
        )

        self.mp3_bitrate = QSpinBox()

        self.mp3_bitrate.setRange(
            128,
            320,
        )

        self.mp3_bitrate.setSingleStep(
            64
        )

        self.mp3_bitrate.setValue(
            192
        )

        form.addRow(
            "MP3 kbps",
            self.mp3_bitrate,
        )

        root.addWidget(
            options_box
        )

        status_box = QGroupBox(
            "Trạng thái"
        )

        status_layout = QVBoxLayout(
            status_box
        )

        self.selection_label = QLabel(
            "Variant: 0 | Style: 0"
        )

        self.model_label = QLabel(
            "Model: -"
        )

        self.runtime_label = QLabel(
            "Runtime: -"
        )

        self.ready_label = QLabel(
            "Sẵn sàng: chưa kiểm tra"
        )

        self.errors_label = QLabel(
            "Thiếu: -"
        )

        status_layout.addWidget(
            self.selection_label
        )

        status_layout.addWidget(
            self.model_label
        )

        status_layout.addWidget(
            self.runtime_label
        )

        status_layout.addWidget(
            self.ready_label
        )

        status_layout.addWidget(
            self.errors_label
        )

        root.addWidget(
            status_box
        )

        self.choose_txt_button.clicked.connect(
            lambda: self.choose_file("*.txt")
        )

        self.choose_docx_button.clicked.connect(
            lambda: self.choose_file("*.docx")
        )

        self.output_button.clicked.connect(
            self.choose_output_folder
        )

        self.mode_combo.currentIndexChanged.connect(
            self.update_mode
        )

        self.language_mode_combo.currentIndexChanged.connect(
            self.update_language_mode
        )

        self.allow_all_variants.stateChanged.connect(
            self.update_counts
        )

        self.allow_all_styles.stateChanged.connect(
            self.update_counts
        )

        self.update_mode()

        self.update_language_mode()

    def choose_file(
        self,
        pattern,
    ):

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn văn bản",
            "",
            pattern,
        )

        if file:

            self.input_path.setText(
                file
            )

    def choose_output_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Chọn Output Folder",
        )

        if folder:

            self.output_folder.setText(
                folder
            )

    def load_voice(
        self,
        voice,
    ):

        self.variant_combo.clear()

        self.variant_list.clear()

        if not voice:

            self.load_language_capabilities(
                None
            )

            return

        self.load_language_capabilities(
            {
                "enabled_languages": getattr(
                    voice.config,
                    "enabled_languages",
                    [
                        "vi",
                    ],
                ),
                "languages": [],
            }
        )

        for variant in voice.variants:

            variant_id = variant.get(
                "id",
                "",
            )

            name = variant.get(
                "name",
                variant_id,
            )

            self.variant_combo.addItem(
                name,
                variant_id,
            )

            item = QListWidgetItem(
                name
            )

            item.setData(
                Qt.UserRole,
                variant_id,
            )

            item.setCheckState(
                Qt.Unchecked
            )

            self.variant_list.addItem(
                item
            )

        self.style_list.clear()

        for style_id in self.style_ids(
            voice
        ):

            item = QListWidgetItem(
                style_id
            )

            item.setData(
                Qt.UserRole,
                style_id,
            )

            item.setCheckState(
                Qt.Unchecked
            )

            self.style_list.addItem(
                item
            )

        self.model_label.setText(
            "Model: "
            + (
                voice.config.gpt_model
                or "-"
            )
        )

        self.update_counts()

    def load_language_capabilities(
        self,
        capabilities,
    ):

        self.fixed_language_combo.clear()

        languages = []

        if capabilities:

            language_items = capabilities.get(
                "languages",
                [],
            )

            if language_items:

                languages = [
                    item
                    for item in language_items
                    if item.get(
                        "enabled"
                    )
                ]

            else:

                names = {
                    "vi": "Tiếng Việt",
                    "zh": "Tiếng Trung",
                    "en": "Tiếng Anh",
                    "ja": "Tiếng Nhật",
                    "ko": "Tiếng Hàn",
                    "yue": "Tiếng Quảng Đông",
                }

                languages = [
                    {
                        "code": code,
                        "display_name_vi": names.get(
                            code,
                            code,
                        ),
                        "route": {
                            "status": "BLOCKED",
                            "reason": "NOT_PREVIEWED",
                        },
                    }
                    for code in capabilities.get(
                        "enabled_languages",
                        [
                            "vi",
                        ],
                    )
                ]

        for item in languages:

            route = item.get(
                "route",
                {},
            )

            label = (
                item.get(
                    "display_name_vi",
                    item.get(
                        "code",
                        "",
                    ),
                )
                + " - "
                + route.get(
                    "status",
                    "BLOCKED",
                )
            )

            if route.get(
                "reason",
            ):

                label += (
                    " / "
                    + route.get(
                        "reason",
                        "",
                    )
                )

            self.fixed_language_combo.addItem(
                label,
                item.get(
                    "code",
                    "",
                ),
            )

        self.update_language_mode()

    def update_language_mode(
        self,
    ):

        fixed = (
            self.language_mode_combo.currentData()
            == "fixed"
        )

        self.fixed_language_combo.setEnabled(
            fixed
        )

    def selected_language(
        self,
    ):

        mode = self.language_mode_combo.currentData()

        if mode == "fixed":

            return self.fixed_language_combo.currentData() or ""

        return ""

    def preview_language_routes(
        self,
        router,
        voice_id,
    ):

        mode = self.language_mode_combo.currentData()

        language = self.selected_language()

        result = router.route_text(
            voice_id,
            self.direct_text.toPlainText(),
            explicit_language=language if mode == "fixed" else "",
        )

        lines = []

        for item in result.get(
            "segments",
            [],
        ):

            route = item.get(
                "route",
                {},
            )

            lines.append(
                f"{item.get('segment_id')}: "
                f"{item.get('language_code')} -> "
                f"{route.get('engine_id', '-')}"
                f" [{route.get('status')}] "
                f"{route.get('reason', '')}"
            )

        self.language_preview.setText(
            "\n".join(
                lines
            )
            or "Language route: -"
        )

        return result

    def style_ids(
        self,
        voice,
    ):

        result = []

        if voice.config.default_style_id:

            result.append(
                voice.config.default_style_id
            )

        result.extend([
            "natural",
            "story",
            "dramatic",
            "soft",
        ])

        return list(
            dict.fromkeys(
                result
            )
        )

    def update_mode(self):

        is_ai = (
            self.mode_combo.currentData()
            == GENERATE_MODE_AI_STYLE
        )

        self.variant_combo.setEnabled(
            not is_ai
        )

        self.variant_list.setEnabled(
            is_ai
        )

        self.style_list.setEnabled(
            is_ai
        )

        self.allow_all_variants.setEnabled(
            is_ai
        )

        self.allow_all_styles.setEnabled(
            is_ai
        )

        self.update_counts()

    def checked_items(
        self,
        widget,
    ):

        result = []

        for index in range(
            widget.count()
        ):

            item = widget.item(
                index
            )

            if item.checkState():

                result.append(
                item.data(
                    Qt.UserRole
                )
                )

        return result

    def update_counts(self):

        variant_count = (
            self.variant_list.count()
            if self.allow_all_variants.isChecked()
            else len(
                self.checked_items(
                    self.variant_list
                )
            )
        )

        style_count = (
            self.style_list.count()
            if self.allow_all_styles.isChecked()
            else len(
                self.checked_items(
                    self.style_list
                )
            )
        )

        self.selection_label.setText(
            f"Variant: {variant_count} | Style: {style_count}"
        )

    def build_request(
        self,
        project_id="",
        voice_id="",
    ):

        mode = self.mode_combo.currentData()

        selection = GenerateSelectionConfig(
            mode=mode,
            voice_id=voice_id,
            selected_variant_id=self.variant_combo.currentData()
            or "",
            allow_all_variants=self.allow_all_variants.isChecked(),
            allowed_variant_ids=self.checked_items(
                self.variant_list
            ),
            allow_all_styles=self.allow_all_styles.isChecked(),
            allowed_style_ids=self.checked_items(
                self.style_list
            ),
            preset_id=self.preset_combo.currentData()
            or "",
            reference_style_id=(
                self.reference_style_combo.currentData()
                or ""
            ),
            text_profile_id=self.text_profile_combo.currentData()
            or "",
            input_path=self.input_path.text(),
            output_folder=self.output_folder.text(),
            output_name=self.output_name.text(),
            output_format=self.output_format.currentData(),
            mp3_bitrate_kbps=self.mp3_bitrate.value(),
            language=self.selected_language(),
            speed=SpeedProfile(
                speed=float(
                    self.speed_combo.currentData()
                    or 1.0
                )
            ),
        )

        profile = GenerateAudioProfile(
            output_format=selection.output_format,
            mp3_bitrate_kbps=selection.mp3_bitrate_kbps,
        )

        return GenerateRequest(
            text=self.direct_text.toPlainText(),
            text_file=self.input_path.text(),
            selection=selection,
            project_id=project_id,
            audio_profile=profile,
        )
