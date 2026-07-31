# exceptions.py

class IsoMoneyError(Exception):
    """Base exception for all isomoney errors."""


class InvalidFormatSpecError(IsoMoneyError):
    """Raised when a money format specification is invalid."""


class CurrencyMismatchError(IsoMoneyError):
    """Raised when operations involve different currencies."""