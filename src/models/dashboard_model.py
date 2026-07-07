from dataclasses import dataclass


@dataclass
class DashboardModel:
    voice_count: int = 0
    audio_count: int = 0
    docx_count: int = 0
    txt_count: int = 0

    @property
    def total_text(self):
        return self.docx_count + self.txt_count