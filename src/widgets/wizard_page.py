from PySide6.QtWidgets import QWidget


class WizardPage(QWidget):

    def __init__(self):

        super().__init__()

    def validate(self):

        return True

    def on_enter(self):

        pass

    def on_leave(self):

        pass