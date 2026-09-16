from pathlib import Path


class DirectoryDoesNotExist(Exception):
    def __init__(self,
                 file_dir: str, ):
        super().__init__(f'Directory does not exist "{file_dir}".')
        ...



class WrongFileExtension(Exception):
    def __init__(self,
                 file_dir: str,
                 expected_extension: str, ):
        super().__init__(f'Wrong file extension "{Path(file_dir).name}", '
                         f'"{expected_extension}" extension was expected.')


class NoFileToDelete(Exception):
    def __init__(self,
                 file_dir: str | Path, ):
        super().__init__(f'Can not delete file "{Path(file_dir).name}"'
                         f' from directory "{Path(file_dir).parent}"')


class DownloadError(Exception):
    def __init__(self, ):
        super().__init__(f'An Error occurred while downloading the file.')