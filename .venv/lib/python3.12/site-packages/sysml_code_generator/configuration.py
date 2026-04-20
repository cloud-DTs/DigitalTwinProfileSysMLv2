from pathlib import Path


class Configuration:
    def __init__(self):
        template_folder_path = Path(__file__).parent / "template"
        self.__template_folder = str(template_folder_path.resolve())

    @property
    def template_folder(self) -> str:
        return self.__template_folder
