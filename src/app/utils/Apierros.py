class AppError(Exception):
    def __init__(
        self, message: str, status: int, error: str | None = None, success: bool = False
    ):
        self.message = message
        self.status = status
        self.error = error
        self.success = success
        super().__init__(message)
