class UnknownStartTimeError(ValueError):
    """Exception for start times"""

    pass


class UnknownEndTimeError(ValueError):
    """Exception for end times"""

    pass


class UnorderedTimeError(ValueError):
    """Exception for time order (Start < End)"""

    pass
