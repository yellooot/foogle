class FoogleException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class FoogleBadQueryError(FoogleException):
    def __init__(self):
        self.message = "Bad query."
        super().__init__(self.message)


class FoogleSyntaxError(FoogleException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
