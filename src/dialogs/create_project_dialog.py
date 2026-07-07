from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLineEdit

from dialogs.wizard_dialog import WizardDialog
from widgets.wizard_page import WizardPage


class NamePage(WizardPage):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Tên Project"))

        self.name = QLineEdit()

        layout.addWidget(self.name)

    def validate(self):

        return self.name.text().strip() != ""


class CreateProjectDialog(WizardDialog):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Tạo Project"
        )

        self.add_page(
            NamePage()
        )