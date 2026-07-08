class CurrentProjectService:

    _project = None

    @classmethod
    def set(cls, project):

        cls._project = project

    @classmethod
    def get(cls):

        return cls._project

    @classmethod
    def clear(cls):

        cls._project = None

    @classmethod
    def has_project(cls):

        return cls._project is not None

    @classmethod
    def name(cls):

        if cls._project is None:

            return ""

        return cls._project.name