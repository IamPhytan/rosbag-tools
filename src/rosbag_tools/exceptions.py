class InvalidTimestampError(ValueError):
    """Exception for invalid timestamps"""

    pass


class FileContentError(ValueError):
    """Exception that can be raised when the content of a file did not match what is expected"""

    pass
