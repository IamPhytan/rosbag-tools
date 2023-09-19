class UnknownStartTimeError(ValueError):
    """Exception for start times"""

    pass


class UnknownEndTimeError(ValueError):
    """Exception for end times"""

    pass


class UnorderedTimeError(ValueError):
    """Exception for time order (Start < End)"""

    pass


class FileContentError(ValueError):
    """Exception that can be raised when the content of a file did not match what is expected"""

    pass
