from PySide6.QtWidgets import QListWidget


class Sidebar(QListWidget):

    def __init__(self):

        super().__init__()

        #
        # Mặc định chỉ hiện các chức năng thường dùng.
        #

        self.basic_items = [

            "🏠 Tổng quan",

            "🎬 Tạo Audio",

            "📂 Dự án",

            "⚙ Cài đặt",

        ]

        #
        # Chức năng nâng cao.
        #

        self.advanced_items = [

            "🎤 Voice",

            "🏋 Huấn luyện",

            "📖 Từ điển",

        ]

        self.show_advanced(
            False
        )

        self.setFixedWidth(
            230
        )

    def show_advanced(
        self,
        enabled: bool,
    ):

        self.clear()

        self.addItems(
            self.basic_items
        )

        if enabled:

            #
            # Chèn trước Cài đặt.
            #

            self.insertItem(
                3,
                self.advanced_items[0],
            )

            self.insertItem(
                4,
                self.advanced_items[1],
            )

            self.insertItem(
                5,
                self.advanced_items[2],
            )