from pathlib import Path


class Runtime:

    def __init__(
        self,
        root,
    ):

        self.root = Path(root)

    #
    # Root
    #

    def exists(self):

        return self.root.exists()

    #
    # Python
    #

    def python(self):

        python = (

            self.root
            / "runtime"
            / "python.exe"

        )

        if python.exists():

            return python

        return None

    #
    # WebUI
    #

    def webui(self):

        file = (

            self.root
            / "webui.py"

        )

        if file.exists():

            return file

        return None

    #
    # CLI
    #

    def inference_cli(self):

        file = (

            self.root
            / "GPT_SoVITS"
            / "inference_cli.py"

        )

        if file.exists():

            return file

        return None

    #
    # Batch
    #

    def launcher(self):

        file = (

            self.root
            / "go-webui.bat"

        )

        if file.exists():

            return file

        return None

    #
    # Check
    #

    def ready(self):

        return (

            self.python() is not None

            and

            self.webui() is not None

            and

            self.inference_cli() is not None

        )

    #
    # String
    #

    def __str__(self):

        return str(self.root)


## ===== KẾT THÚC FILE =====