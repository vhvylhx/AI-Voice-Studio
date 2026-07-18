from PySide6.QtWidgets import QListWidget


class Sidebar(QListWidget):

    def __init__(self):

        super().__init__()

        #
        # Mặc định hiển thị các chức năng chính để smoke test
        # và người dùng không bị lạc giữa stack/page.
        #

        self.basic_items = [

            "🏠 Tổng quan",

            "🎬 Tạo Audio",

            "🧬 Phong cách đọc",

            "🎤 Voice",

            "🏋 Huấn luyện",

            "🧾 Công việc",

            "🖥 Resource",

            "📂 Dự án",

            "⚙ Cài đặt",

        ]

        #
        # Chức năng nâng cao chưa có page riêng trong sprint này.
        #

        self.advanced_items = [

            "📖 Từ điển",

        ]

        self.show_advanced(
            False
        )

        self.setFixedWidth(
            260
        )

        self.setMinimumHeight(
            420
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
            # Chèn trước Dự án.
            #

            self.insertItem(
                7,
                self.advanced_items[0],
            )
