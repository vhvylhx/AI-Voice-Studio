from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.app_context import AppContext
from models.training_reference_config import (
    REFERENCE_MODE_APP_STYLE_PROFILE,
    REFERENCE_MODE_CREATE_STYLE_PROFILE,
    REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
    SPEAKER_REFERENCE_SELECTED_FILE,
    SPEAKER_REFERENCE_TRAINING_DATASET,
    TrainingReferenceConfig,
)
from widgets.ui_components import PageHeader
from widgets.ui_components import ScrollablePage
from widgets.ui_components import SectionCard
from widgets.ui_components import StatusBadge


class TrainingPage(ScrollablePage):

    def __init__(self):

        super().__init__()

        self.dataset = ""

        self.reference_config = TrainingReferenceConfig()

        self.build_ui()

        self.refresh_reference_options()

    def build_ui(self):

        self.body.addWidget(
            PageHeader(
                "Huấn luyện",
                (
                    "Tách rõ dữ liệu huấn luyện, Phong cách đọc / Voice DNA "
                    "và âm thanh tham chiếu clone giọng. Trang này chỉ chuẩn bị "
                    "workflow, không tự chạy train thật."
                ),
            )
        )

        self.build_dataset_section()

        self.build_reference_section()

        self.build_style_section()

        self.build_speaker_section()

        self.build_help_section()

        self.build_preflight_section()

        self.body.addStretch(
            1
        )

    def build_dataset_section(self):

        card = SectionCard(
            "Dữ liệu huấn luyện",
            (
                "Owner: Training domain. Dữ liệu này dùng cho Scan, Health, "
                "Repair, Review, Alignment, metadata.list và train readiness."
            ),
        )

        row = QHBoxLayout()

        self.source = QLabel(
            "Dataset: Chưa chọn"
        )

        self.source.setWordWrap(
            True
        )

        self.choose_button = QPushButton(
            "Chọn Dataset"
        )

        self.prepare_button = QPushButton(
            "Chuẩn bị Dataset"
        )

        row.addWidget(
            self.source,
            1,
        )

        row.addWidget(
            self.choose_button
        )

        row.addWidget(
            self.prepare_button
        )

        self.use_dataset_reference = QCheckBox(
            "Dùng chính dữ liệu huấn luyện làm âm thanh tham chiếu"
        )

        card.body.addLayout(
            row
        )

        card.body.addWidget(
            self.use_dataset_reference
        )

        self.body.addWidget(
            card
        )

        self.choose_button.clicked.connect(
            self.choose_dataset
        )

        self.prepare_button.clicked.connect(
            self.prepare_dataset
        )

        self.use_dataset_reference.stateChanged.connect(
            self.on_dataset_reference_changed
        )

    def build_reference_section(self):

        card = SectionCard(
            "Dữ liệu tham chiếu",
            (
                "Ba lựa chọn loại trừ nhau. Mode không active được giữ draft "
                "nhưng không resolve vào engine."
            ),
        )

        self.mode_group = QButtonGroup(
            self
        )

        self.mode_style_existing = QRadioButton(
            "Dùng Phong cách đọc có sẵn của AI Voice Studio"
        )

        self.mode_create_style = QRadioButton(
            "Dùng MP3 + văn bản để tạo Phong cách đọc mới"
        )

        self.mode_speaker_only = QRadioButton(
            "Chỉ dùng âm thanh tham chiếu để clone chất giọng"
        )

        modes = [
            (
                self.mode_style_existing,
                REFERENCE_MODE_APP_STYLE_PROFILE,
            ),
            (
                self.mode_create_style,
                REFERENCE_MODE_CREATE_STYLE_PROFILE,
            ),
            (
                self.mode_speaker_only,
                REFERENCE_MODE_SPEAKER_REFERENCE_ONLY,
            ),
        ]

        for button, mode in modes:

            self.mode_group.addButton(
                button
            )

            button.setProperty(
                "reference_mode",
                mode,
            )

            card.body.addWidget(
                button
            )

        self.mode_panels = QStackedWidget()

        self.mode_panels.addWidget(
            self.build_existing_style_panel()
        )

        self.mode_panels.addWidget(
            self.build_create_style_panel()
        )

        self.mode_panels.addWidget(
            self.build_speaker_only_panel()
        )

        card.body.addWidget(
            self.mode_panels
        )

        self.body.addWidget(
            card
        )

        self.mode_style_existing.setChecked(
            True
        )

        for button, _ in modes:

            button.toggled.connect(
                self.on_reference_mode_changed
            )

    def build_existing_style_panel(self):

        panel = QWidget()

        layout = QVBoxLayout(
            panel
        )

        self.style_profile_combo = QComboBox()

        self.style_status = QLabel(
            "Trạng thái: chưa chọn"
        )

        self.style_status.setWordWrap(
            True
        )

        self.open_style_button = QPushButton(
            "Mở thư viện Phong cách đọc"
        )

        layout.addWidget(
            QLabel(
                "Chọn Style Profile đã lưu:"
            )
        )

        layout.addWidget(
            self.style_profile_combo
        )

        layout.addWidget(
            self.style_status
        )

        layout.addWidget(
            self.open_style_button
        )

        self.style_profile_combo.currentIndexChanged.connect(
            self.update_reference_config_from_ui
        )

        self.open_style_button.clicked.connect(
            self.open_style_library
        )

        return panel

    def build_create_style_panel(self):

        panel = QWidget()

        layout = QVBoxLayout(
            panel
        )

        self.new_style_name = QLineEdit()

        self.new_style_name.setPlaceholderText(
            "Tên Phong cách đọc mới"
        )

        self.new_style_description = QTextEdit()

        self.new_style_description.setPlaceholderText(
            "Mô tả ngắn phong cách đọc..."
        )

        self.new_style_description.setFixedHeight(
            80
        )

        self.create_style_button = QPushButton(
            "Tạo yêu cầu phân tích"
        )

        self.create_style_note = QLabel(
            "Analyzer Voice DNA chưa sẵn sàng nên profile mới sẽ ở trạng thái pending/blocked, không tạo dữ liệu giả."
        )

        self.create_style_note.setWordWrap(
            True
        )

        layout.addWidget(
            self.new_style_name
        )

        layout.addWidget(
            self.new_style_description
        )

        layout.addWidget(
            self.create_style_note
        )

        layout.addWidget(
            self.create_style_button
        )

        self.create_style_button.clicked.connect(
            self.create_style_profile_request
        )

        return panel

    def build_speaker_only_panel(self):

        panel = QWidget()

        layout = QVBoxLayout(
            panel
        )

        file_row = QHBoxLayout()

        self.reference_audio = QLineEdit()

        self.reference_audio.setPlaceholderText(
            "MP3/WAV tham chiếu..."
        )

        self.choose_reference_audio = QPushButton(
            "Chọn file"
        )

        file_row.addWidget(
            self.reference_audio,
            1,
        )

        file_row.addWidget(
            self.choose_reference_audio
        )

        self.reference_text = QTextEdit()

        self.reference_text.setPlaceholderText(
            "Transcript tham chiếu (tùy chọn nếu workflow chưa yêu cầu)"
        )

        self.reference_text.setFixedHeight(
            90
        )

        layout.addLayout(
            file_row
        )

        layout.addWidget(
            self.reference_text
        )

        self.choose_reference_audio.clicked.connect(
            self.choose_speaker_reference
        )

        self.reference_audio.textChanged.connect(
            self.update_reference_config_from_ui
        )

        self.reference_text.textChanged.connect(
            self.update_reference_config_from_ui
        )

        return panel

    def build_style_section(self):

        card = SectionCard(
            "Phong cách đọc / Voice DNA",
            (
                "Owner: Style Profile domain. TrainingPage chỉ chọn hoặc tạo "
                "yêu cầu draft; quản lý đầy đủ nằm ở trang Phong cách đọc."
            ),
        )

        self.style_badge = StatusBadge(
            "foundation",
            "warning",
        )

        card.body.addWidget(
            self.style_badge
        )

        self.body.addWidget(
            card
        )

    def build_speaker_section(self):

        card = SectionCard(
            "Âm thanh tham chiếu clone giọng",
            (
                "Owner: Voice/Speaker Reference domain. Đây là dữ liệu clone "
                "chất giọng, không phải Voice DNA và không phải dataset train."
            ),
        )

        self.speaker_validation = QLabel(
            "Chưa kiểm tra."
        )

        self.speaker_validation.setWordWrap(
            True
        )

        card.body.addWidget(
            self.speaker_validation
        )

        self.body.addWidget(
            card
        )

    def build_help_section(self):

        card = SectionCard(
            "Hướng dẫn lựa chọn",
            (
                "MP3 + TXT để train model → Dữ liệu huấn luyện.\n"
                "MP3 + TXT để giữ cách kể chuyện → Tạo Style Profile.\n"
                "Chỉ MP3/WAV để clone chất giọng → Speaker Reference.\n"
                "Đổi chất giọng nhưng giữ cách kể chuyện → Speaker Reference mới + Style Profile cũ.\n"
                "Giữ chất giọng nhưng đổi cách đọc → Speaker Reference cũ + Style Profile mới."
            ),
        )

        self.body.addWidget(
            card
        )

    def build_preflight_section(self):

        card = SectionCard(
            "Kiểm tra trước huấn luyện",
            (
                "Sprint này không chạy train thật. Nút kiểm tra chỉ validate "
                "workflow/reference và ghi log rõ ràng."
            ),
        )

        button_row = QHBoxLayout()

        self.validate_button = QPushButton(
            "Kiểm tra cấu hình"
        )

        self.train_button = QPushButton(
            "Train thật (bị khóa)"
        )

        self.preview_button = QPushButton(
            "Preview"
        )

        button_row.addWidget(
            self.validate_button
        )

        button_row.addWidget(
            self.train_button
        )

        button_row.addWidget(
            self.preview_button
        )

        button_row.addStretch(
            1
        )

        self.log = QTextEdit()

        self.log.setReadOnly(
            True
        )

        self.log.setMinimumHeight(
            160
        )

        card.body.addLayout(
            button_row
        )

        card.body.addWidget(
            self.log
        )

        self.body.addWidget(
            card
        )

        self.validate_button.clicked.connect(
            self.validate_reference
        )

        self.train_button.clicked.connect(
            self.train
        )

        self.preview_button.clicked.connect(
            self.preview
        )

    def refresh_reference_options(self):

        current = self.style_profile_combo.currentData()

        self.style_profile_combo.blockSignals(
            True
        )

        self.style_profile_combo.clear()

        self.style_profile_combo.addItem(
            "Chưa chọn",
            "",
        )

        try:

            for profile in AppContext.style_profile_service.list_profiles():

                self.style_profile_combo.addItem(
                    f"{profile.display_name} ({profile.style_profile_id})",
                    profile.style_profile_id,
                )

        except Exception:

            pass

        if current:

            index = self.style_profile_combo.findData(
                current
            )

            if index >= 0:

                self.style_profile_combo.setCurrentIndex(
                    index
                )

        self.style_profile_combo.blockSignals(
            False
        )

        self.update_reference_config_from_ui()

    def choose_dataset(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục Dataset",
        )

        if not folder:

            return

        self.dataset = folder

        self.source.setText(
            f"Dataset: {folder}"
        )

        self.reference_config = (
            AppContext.training_reference_service
            .suggest_reference_from_folder(
                folder,
                self.reference_config,
            )
        )

        if (
            self.reference_config.reference_source_origin
            == "dataset_suggestion"
        ):

            self.reference_audio.setText(
                self.reference_config.speaker_reference_audio
            )

        self.log.append(
            "Đã chọn Dataset."
        )

    def prepare_dataset(self):

        voice = AppContext.current_voice.get()

        if voice is None:

            QMessageBox.warning(
                self,
                "Thông báo",
                "Chưa chọn Voice.",
            )

            return

        if not self.dataset:

            QMessageBox.warning(
                self,
                "Thông báo",
                "Chưa chọn Dataset.",
            )

            return

        AppContext.training_service.prepare_dataset(
            self.dataset,
            voice,
        )

        self.log.append(
            "Dataset đã được chuẩn bị bằng workflow cũ. Train thật vẫn bị khóa ở trang này."
        )

    def on_reference_mode_changed(self):

        for index, button in enumerate(
            [
                self.mode_style_existing,
                self.mode_create_style,
                self.mode_speaker_only,
            ]
        ):

            if button.isChecked():

                self.mode_panels.setCurrentIndex(
                    index
                )

                break

        self.update_reference_config_from_ui()

    def on_dataset_reference_changed(self):

        if self.use_dataset_reference.isChecked():

            self.mode_speaker_only.setChecked(
                True
            )

            self.reference_config.speaker_reference_mode = (
                SPEAKER_REFERENCE_TRAINING_DATASET
            )

            self.reference_config.use_training_dataset_as_reference = True

        else:

            self.reference_config.use_training_dataset_as_reference = False

        self.update_reference_config_from_ui()

    def update_reference_config_from_ui(self):

        checked = self.mode_group.checkedButton()

        if checked is not None:

            self.reference_config.reference_mode = checked.property(
                "reference_mode"
            )

        self.reference_config.style_profile_id = (
            self.style_profile_combo.currentData()
            or ""
        )

        if (
            self.reference_config.reference_mode
            == REFERENCE_MODE_SPEAKER_REFERENCE_ONLY
            and not self.reference_config.use_training_dataset_as_reference
        ):

            self.reference_config.speaker_reference_mode = (
                SPEAKER_REFERENCE_SELECTED_FILE
            )

        self.reference_config.speaker_reference_audio = (
            self.reference_audio.text().strip()
        )

        self.reference_config.speaker_reference_text = (
            self.reference_text.toPlainText().strip()
        )

        if self.reference_config.reference_mode == REFERENCE_MODE_APP_STYLE_PROFILE:

            self.update_style_status()

    def update_style_status(self):

        style_profile_id = self.style_profile_combo.currentData() or ""

        if not style_profile_id:

            self.style_status.setText(
                "Trạng thái: chưa chọn"
            )

            return

        readiness = AppContext.style_profile_service.readiness(
            style_profile_id
        )

        self.style_status.setText(
            "Trạng thái: "
            + readiness.get(
                "status",
                "unknown",
            )
            + " | "
            + readiness.get(
                "message_vi",
                "",
            )
        )

    def choose_speaker_reference(self):

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn audio tham chiếu",
            "",
            "Audio (*.wav *.mp3 *.flac *.m4a)",
        )

        if not file:

            return

        self.reference_audio.setText(
            file
        )

        self.reference_config.reference_source_origin = "manual"

        self.update_reference_config_from_ui()

    def create_style_profile_request(self):

        name = self.new_style_name.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "Thiếu tên",
                "Vui lòng nhập tên Phong cách đọc.",
            )

            return

        profile = AppContext.style_profile_service.create_profile(
            display_name=name,
            description=self.new_style_description.toPlainText(),
            language="vi",
            dataset_reference={
                "source": self.dataset,
                "state": "draft_from_training_page",
            },
        )

        AppContext.style_profile_service.prepare_extraction(
            profile.style_profile_id
        )

        self.reference_config.style_profile_draft_id = (
            profile.style_profile_id
        )

        self.reference_config.create_style_profile = True

        self.mode_create_style.setChecked(
            True
        )

        self.refresh_reference_options()

        self.log.append(
            f"Đã tạo draft Style Profile {profile.style_profile_id}. Analyzer chưa sẵn sàng nên không tạo Voice DNA giả."
        )

    def open_style_library(self):

        QMessageBox.information(
            self,
            "Phong cách đọc",
            "Dùng thanh bên để mở trang Phong cách đọc / Voice DNA.",
        )

    def validate_reference(self):

        self.update_reference_config_from_ui()

        result = AppContext.training_reference_service.validate(
            self.reference_config,
            voice=AppContext.current_voice.get(),
            dataset_reference={
                "dataset": self.dataset,
            }
            if self.dataset
            else None,
        )

        self.reference_config = TrainingReferenceConfig.from_dict(
            result["config"]
        )

        self.speaker_validation.setText(
            "Trạng thái: "
            + result["state"]
            + "\n"
            + "\n".join(
                f"- {item.get('code')}: {item.get('reason')}"
                for item in result["messages"]
            )
        )

        if result["ok"]:

            self.log.append(
                "Reference hợp lệ."
            )

        else:

            self.log.append(
                "Reference chưa hợp lệ: "
                + ", ".join(
                    item.get(
                        "code",
                        ""
                    )
                    for item in result["messages"]
                )
            )

    def train(self):

        QMessageBox.information(
            self,
            "Train thật đang bị khóa",
            "Sprint này chỉ chuẩn hóa workflow/reference. Không chạy train thật từ UI.",
        )

        self.log.append(
            "Train thật bị khóa: cần validation gate và xác nhận người dùng."
        )

    def preview(self):

        voice = AppContext.current_voice.get()

        if voice is None:

            QMessageBox.warning(
                self,
                "Thông báo",
                "Chưa chọn Voice.",
            )

            return

        AppContext.training_service.create_preview(
            voice
        )

        self.log.append(
            "Đã tạo Preview."
        )
