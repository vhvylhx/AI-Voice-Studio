try:

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QFrame
    from PySide6.QtWidgets import QHBoxLayout
    from PySide6.QtWidgets import QLabel
    from PySide6.QtWidgets import QPushButton
    from PySide6.QtWidgets import QScrollArea
    from PySide6.QtWidgets import QSizePolicy
    from PySide6.QtWidgets import QVBoxLayout
    from PySide6.QtWidgets import QWidget

except Exception:

    Qt = None
    QWidget = object
    QFrame = object
    QLabel = None
    QPushButton = None
    QScrollArea = None
    QSizePolicy = None
    QVBoxLayout = None
    QHBoxLayout = None


class PageHeader(QWidget):

    def __init__(
        self,
        title,
        subtitle="",
        parent=None,
    ):

        super().__init__(
            parent
        )

        layout = QVBoxLayout(
            self
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "pageTitle"
        )

        subtitle_label = QLabel(
            subtitle
        )

        subtitle_label.setObjectName(
            "pageSubtitle"
        )

        subtitle_label.setWordWrap(
            True
        )

        layout.addWidget(
            title_label
        )

        if subtitle:

            layout.addWidget(
                subtitle_label
            )


class SectionCard(QFrame):

    def __init__(
        self,
        title="",
        description="",
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.setObjectName(
            "sectionCard"
        )

        self.setFrameShape(
            QFrame.StyledPanel
        )

        self.body = QVBoxLayout(
            self
        )

        if title:

            title_label = QLabel(
                title
            )

            title_label.setObjectName(
                "sectionTitle"
            )

            self.body.addWidget(
                title_label
            )

        if description:

            description_label = QLabel(
                description
            )

            description_label.setWordWrap(
                True
            )

            description_label.setObjectName(
                "sectionDescription"
            )

            self.body.addWidget(
                description_label
            )


class StatusBadge(QLabel):

    def __init__(
        self,
        text,
        level="info",
        parent=None,
    ):

        super().__init__(
            text,
            parent,
        )

        self.setObjectName(
            f"statusBadge_{level}"
        )


class EmptyState(SectionCard):

    def __init__(
        self,
        title,
        message,
        action_text="",
        parent=None,
    ):

        super().__init__(
            title,
            message,
            parent,
        )

        self.action_button = None

        if action_text:

            self.action_button = QPushButton(
                action_text
            )

            self.body.addWidget(
                self.action_button
            )


class SettingsRow(QWidget):

    def __init__(
        self,
        label,
        control,
        hint="",
        parent=None,
    ):

        super().__init__(
            parent
        )

        layout = QVBoxLayout(
            self
        )

        label_widget = QLabel(
            label
        )

        label_widget.setObjectName(
            "settingsRowLabel"
        )

        layout.addWidget(
            label_widget
        )

        layout.addWidget(
            control
        )

        if hint:

            hint_widget = QLabel(
                hint
            )

            hint_widget.setWordWrap(
                True
            )

            hint_widget.setObjectName(
                "settingsRowHint"
            )

            layout.addWidget(
                hint_widget
            )


class ContentScrollArea(QScrollArea):

    def __init__(
        self,
        content=None,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.setWidgetResizable(
            True
        )

        if Qt is not None:

            self.setHorizontalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff
            )

        if content is not None:

            self.set_content(
                content
            )

    def set_content(
        self,
        content,
    ):

        if QSizePolicy is not None:

            content.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Preferred,
            )

        self.setWidget(
            content
        )

        return content


class ScrollablePage(QWidget):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent
        )

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.content = QWidget()

        self.body = QVBoxLayout(
            self.content
        )

        self.scroll = ContentScrollArea(
            self.content
        )

        root.addWidget(
            self.scroll
        )
