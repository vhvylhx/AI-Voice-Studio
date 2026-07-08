from PySide6.QtWidgets import QListWidget


class Sidebar(QListWidget):

    def __init__(self):

        super().__init__()

        self.addItems([
            "🏠 Tổng quan",
            "🎬 Tạo Audio",
            "🎤 Thư viện giọng",
            "🧠 Huấn luyện",
            "📂 Dự án",
            "⚙ Engine",
            "⚙ Cài đặt",
        ])

        self.setFixedWidth(230)