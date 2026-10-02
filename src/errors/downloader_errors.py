class DownloadError(Exception):
    def __init__(self, ):
        super().__init__(f'An Error occurred while downloading the file.')
        
class CanNotCreateDirectory(Exception):
    def __init__(self, ):
        super().__init__(f'Error while creating directory.')