class CurrentVoiceService:

    _voice = None

    @classmethod
    def set(cls, voice):

        cls._voice = voice

    @classmethod
    def get(cls):

        return cls._voice

    @classmethod
    def has_voice(cls):

        return cls._voice is not None

    @classmethod
    def clear(cls):

        cls._voice = None