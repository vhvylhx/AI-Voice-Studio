class AppContext:

    current_project = None

    current_engine = None

    current_voice = None

    current_rule = None

    @classmethod
    def clear(cls):

        cls.current_project = None
        cls.current_engine = None
        cls.current_voice = None
        cls.current_rule = None