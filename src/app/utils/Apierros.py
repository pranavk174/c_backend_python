class AppError(Exception):
    def __init__(
        self,
        message: str,
        status: int,
        error: str
    ):
        self.message = message
        self.status = status
        self.error = error
        self.success = False