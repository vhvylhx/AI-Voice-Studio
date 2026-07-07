from dataclasses import dataclass


@dataclass
class FilePair:

    name: str

    docx: bool = False

    txt: bool = False

    mp3: bool = False

    wav: bool = False

    @property
    def has_text(self):

        return self.docx or self.txt

    @property
    def has_audio(self):

        return self.mp3 or self.wav

    @property
    def matched(self):

        return self.has_text and self.has_audio