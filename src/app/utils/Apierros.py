class AppError(Exception):
    def __init__(self, message: str, status: int, error: str, success: bool = False):
        self.message = message
        self.status = status
        self.error = error
        self.success = False
