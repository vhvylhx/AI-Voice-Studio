from textwrap import dedent


class RuntimeTrainingHelpService:

    def profile_help(
        self,
    ):

        return {
            "auto": {
                "name": "Tự động",
                "short": (
                    "Khuyến nghị cho hầu hết người dùng. Ứng dụng tự kiểm tra "
                    "phần cứng và Runtime để chọn cấu hình an toàn."
                ),
                "detail": (
                    "Tự động là lựa chọn khuyến nghị. Ứng dụng kiểm tra GPU, "
                    "VRAM, CPU, RAM, CUDA và Runtime đã cài, sau đó chọn cấu "
                    "hình phù hợp với máy. Khi đổi máy hoặc nâng cấp phần cứng, "
                    "bạn chỉ cần bấm Phát hiện lại phần cứng. Chế độ này không "
                    "tự tải hoặc cài Runtime mới nếu bạn chưa đồng ý. Phù hợp "
                    "với người dùng không rành kỹ thuật."
                ),
            },
            "compatibility": {
                "name": "Tương thích",
                "short": (
                    "Dành cho máy yếu, GPU ít VRAM hoặc khi cần ổn định hơn "
                    "tốc độ."
                ),
                "detail": (
                    "Tương thích dùng batch nhỏ và số worker thấp. Train có thể "
                    "chậm hơn, nhưng giảm nguy cơ hết VRAM, treo hoặc lỗi xử lý "
                    "đa tiến trình trên Windows. Đây là lựa chọn phù hợp với GPU "
                    "khoảng 4 GB VRAM như cấu hình hiện tại."
                ),
            },
            "performance": {
                "name": "Hiệu năng",
                "short": (
                    "Dành cho máy mạnh hơn, có nhiều VRAM/RAM và Runtime đã "
                    "validate tốt."
                ),
                "detail": (
                    "Hiệu năng có thể dùng batch và worker cao hơn để train "
                    "nhanh hơn. Đổi lại, chế độ này dùng nhiều VRAM, RAM và CPU "
                    "hơn. Chỉ nên dùng khi Auto Detect và Kiểm tra Runtime đều "
                    "đạt. Nếu Runtime mạnh hơn chưa được cài, ứng dụng vẫn dùng "
                    "Runtime tương thích hiện có."
                ),
            },
            "custom": {
                "name": "Tùy chỉnh",
                "short": (
                    "Dành cho người hiểu rõ tham số train và chấp nhận tự kiểm "
                    "soát rủi ro."
                ),
                "detail": (
                    "Tùy chỉnh cho phép chỉnh Runtime, Compute, Batch Size, "
                    "Workers, Epoch, Save Interval và Resume Policy. Thiết lập "
                    "sai có thể gây hết VRAM, lỗi train hoặc kết quả không ổn "
                    "định. Ứng dụng vẫn phải validation trước khi cho Train."
                ),
            },
        }

    def parameter_help(
        self,
    ):

        return {
            "Runtime": (
                "Runtime là bộ môi trường chạy GPT-SoVITS, gồm Python, Torch, "
                "CUDA, script và pretrained model. Runtime không phải model "
                "Voice đã train. Khi đổi máy, bạn có thể chọn Runtime khác đã "
                "cài. Ứng dụng không tự sửa Runtime gốc."
            ),
            "Compute": (
                "Compute là nơi chạy tính toán. Tự động để ứng dụng tự chọn. "
                "CUDA dùng GPU NVIDIA và thường nhanh hơn. CPU rất chậm, chỉ "
                "nên dùng khi không có GPU phù hợp."
            ),
            "Batch Size": (
                "Batch Size là số mẫu được xử lý cùng lúc. Batch lớn có thể "
                "nhanh hơn nhưng dùng nhiều VRAM hơn. GPU 4 GB nên bắt đầu từ "
                "1. Người dùng phổ thông nên để Tự động."
            ),
            "Workers": (
                "Workers là số tiến trình phụ dùng để tải và chuẩn bị dữ liệu. "
                "Workers cao có thể tăng tốc đọc dữ liệu nhưng dùng thêm RAM/CPU "
                "và có thể gây lỗi trên Windows. Tương thích dùng 0."
            ),
            "VRAM Profile": (
                "VRAM Profile là cấu hình mức dùng bộ nhớ GPU. Low VRAM dành "
                "cho GPU khoảng 4 GB. Không nên tự chọn profile cao hơn dung "
                "lượng thật nếu chưa kiểm tra."
            ),
            "GPT Epochs": (
                "GPT Epochs là số vòng train ở GPT stage. Nhiều epoch hơn không "
                "phải lúc nào cũng tốt hơn; có thể tăng thời gian train và nguy "
                "cơ overfit. Nên giữ khuyến nghị nếu chưa có kinh nghiệm."
            ),
            "SoVITS Epochs": (
                "SoVITS Epochs là số vòng train ở SoVITS stage. Tham số này ảnh "
                "hưởng trực tiếp đến thời gian train. Nên nghe checkpoint trước "
                "khi quyết định tăng thêm."
            ),
            "Save Interval": (
                "Save Interval là khoảng cách giữa các lần lưu checkpoint. Lưu "
                "thường xuyên an toàn hơn khi mất điện hoặc lỗi, nhưng dùng thêm "
                "dung lượng ổ cứng."
            ),
            "Resume Policy": (
                "Resume Policy quy định cách tiếp tục train từ checkpoint. "
                "Manual nghĩa là chỉ resume khi người dùng xác nhận, tránh dùng "
                "nhầm checkpoint."
            ),
            "Auto Detect Hardware": (
                "Auto Detect Hardware tự kiểm tra lại phần cứng và Runtime. Khi "
                "đổi GPU, tăng RAM hoặc chuyển máy, nên bật tùy chọn này. Nếu "
                "phần cứng thay đổi, app tính lại cấu hình Auto nhưng không làm "
                "mất cấu hình Custom cũ."
            ),
        }

    def warning_message(
        self,
        code,
    ):

        messages = {
            "cuda_unavailable": (
                "Ứng dụng không thể dùng GPU NVIDIA. Hãy kiểm tra driver, CUDA "
                "hoặc chọn CPU. Train bằng CPU sẽ rất chậm."
            ),
            "runtime_missing": (
                "Chưa tìm thấy GPT-SoVITS Runtime. Hãy chọn đúng thư mục Runtime "
                "hoặc cài Runtime phù hợp."
            ),
            "out_of_memory": (
                "GPU không đủ bộ nhớ cho cấu hình hiện tại. Hãy chuyển sang "
                "Tương thích hoặc giảm Batch Size."
            ),
            "pretrained_model_missing": (
                "Runtime đang thiếu model nền cần thiết. Hãy kiểm tra thư mục "
                "pretrained_models."
            ),
        }

        return messages.get(
            code,
            "Cấu hình hiện tại chưa sẵn sàng. Hãy xem chi tiết kỹ thuật và kiểm tra lại Runtime.",
        )

    def hardware_summary(
        self,
        hardware,
        profile,
    ):

        gpu = hardware.get(
            "gpu",
            "Chưa phát hiện",
        ) or "Chưa phát hiện"

        vram = hardware.get(
            "vram_mb",
            0,
        )

        cuda = (
            "đạt"
            if hardware.get(
                "cuda_available",
                False,
            )
            else "chưa khả dụng"
        )

        return dedent(
            f"""
            Máy hiện tại:

            - GPU: {gpu}
            - VRAM: khoảng {round(int(vram or 0) / 1024, 1)} GB
            - CUDA: {cuda}
            - Runtime: {profile.get('runtime_profile_id', 'Chưa chọn')}
            - Profile được đề xuất: {profile.get('compatibility_mode', profile.get('mode', 'auto'))}
            - Batch Size: {profile.get('batch_size', 1)}
            - Workers: {profile.get('num_workers', 0)}
            - Compute: {profile.get('compute_mode', 'auto')}

            Đây là cấu hình an toàn theo kết quả phát hiện hiện tại. Train có thể
            chậm hơn máy mạnh nhưng ổn định hơn. Không nên tự tăng Batch Size
            hoặc Workers nếu chưa kiểm tra VRAM. Khi nâng cấp máy, hãy bật Tự
            động và bấm Phát hiện lại phần cứng.
            """
        ).strip()

    def migration_guide(
        self,
    ):

        return dedent(
            """
            Khi chuyển app sang máy khác:

            1. Sao chép toàn bộ thư mục AI Voice Studio.
            2. Cài đúng driver GPU.
            3. Cài hoặc chọn GPT-SoVITS Runtime phù hợp.
            4. Mở Cài đặt → Runtime & Training.
            5. Bật Tự động.
            6. Bấm Phát hiện lại phần cứng.
            7. Bấm Kiểm tra Runtime.
            8. Chỉ Train khi trạng thái báo Sẵn sàng.

            Nếu thiếu Python, FFmpeg, Runtime hoặc model nền, ứng dụng sẽ báo rõ
            thành phần thiếu, phiên bản cần kiểm tra và lệnh hoặc hướng dẫn phù
            hợp. Ứng dụng không tự tải Runtime mới nếu chưa được người dùng đồng ý.
            """
        ).strip()

    def full_guide(
        self,
        hardware=None,
        profile=None,
    ):

        hardware = hardware or {}

        profile = profile or {}

        profile_help = self.profile_help()

        parameter_help = self.parameter_help()

        parts = [
            "# Hướng dẫn sử dụng Runtime & Training",
            "",
            "## Các chế độ cấu hình",
        ]

        for item in profile_help.values():

            parts.extend(
                [
                    "",
                    f"### {item['name']}",
                    item["detail"],
                ]
            )

        parts.extend(
            [
                "",
                "## Giải thích tham số",
            ]
        )

        for name, text in parameter_help.items():

            parts.extend(
                [
                    "",
                    f"### {name}",
                    text,
                ]
            )

        if hardware or profile:

            parts.extend(
                [
                    "",
                    "## Trạng thái máy hiện tại",
                    self.hardware_summary(
                        hardware,
                        profile,
                    ),
                ]
            )

        parts.extend(
            [
                "",
                "## Hướng dẫn đổi máy",
                self.migration_guide(),
            ]
        )

        return "\n".join(
            parts
        )

