"""Field type exception classes"""


class HeterogenousArrayException(ValueError):
    """Raised when Array implementation is found to be not homogenous within assertion method"""


class EmptyArrayException(ValueError):
    """Raised when Array implementation is found to be empty within assertion method"""


class InvalidMemberException(ValueError):
    """Raised when Array is found to contain a member that is not of Array's type"""


class EmptyMemberException(ValueError):
    """Raised when Array is found to contain a member that is of Array's type but is empty"""


class NullMemberException(ValueError):
    """Raised when Array is found to contain a member that is of Array's type but is Null"""
