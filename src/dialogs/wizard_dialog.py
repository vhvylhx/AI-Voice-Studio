from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
)


class WizardDialog(QDialog):

    def __init__(self):

        super().__init__()

        self.setMinimumSize(700, 500)

        root = QVBoxLayout(self)

        self.stack = QStackedWidget()

        root.addWidget(self.stack)

        bottom = QHBoxLayout()

        self.back_button = QPushButton("← Quay lại")
        self.next_button = QPushButton("Tiếp →")
        self.finish_button = QPushButton("Hoàn thành")

        bottom.addWidget(self.back_button)
        bottom.addStretch()
        bottom.addWidget(self.next_button)
        bottom.addWidget(self.finish_button)

        root.addLayout(bottom)

        self.pages = []

        self.back_button.clicked.connect(self.back)
        self.next_button.clicked.connect(self.next)

        self.update_buttons()

    def add_page(self, page):

        self.pages.append(page)

        self.stack.addWidget(page)

        self.update_buttons()

    def next(self):

        page = self.pages[self.stack.currentIndex()]

        if not page.validate():

            return

        page.on_leave()

        index = self.stack.currentIndex()

        if index + 1 >= len(self.pages):

            return

        self.stack.setCurrentIndex(index + 1)

        self.pages[index + 1].on_enter()

        self.update_buttons()

    def back(self):

        index = self.stack.currentIndex()

        if index == 0:

            return

        self.stack.setCurrentIndex(index - 1)

        self.update_buttons()

    def update_buttons(self):

        index = self.stack.currentIndex()

        self.back_button.setEnabled(index > 0)

        self.next_button.setVisible(
            index < len(self.pages) - 1
        )

        self.finish_button.setVisible(
            index == len(self.pages) - 1
        )