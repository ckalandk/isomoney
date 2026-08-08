"""Formatting support for ISOMoney.

The :mod:`isomoney.formatting` module provides the default formatting
interface for monetary values.

Example:
    >>> from isomoney import Money, formatting
    >>> mny = Money.from_major(2.99, "USD)
    >>> formatting.format(mny, "")
    '2.99 USD'
    >>> formatting.format(mny, "n")
    '2.99 US Dollar

The :func:`format` method uses the default local agnostic formatter
to format monetary values according to the format specification.
See :meth:`~Money.__format__` for a complete description of the format spec
language.

ISOMoney supports different local aware backend formatters.
To find the available backend formatters use :func:`available_backends`.
 The active formatting backend can be changed with :func:`use_backend`.


note:
    Ensure that the backend is installed before hand. PyICu
    and babel are provided as optional dependencies

Examples:
    >>> from isomoney import formatting
    >>> formatting.use_backend("icu") # or babel
    >>> formatting.basicConfig(local="en_US")
    >>> mny = Money.from_major(2.99, "USD)
    >>> formatting.format(mny, "")
    '$2.99'
    >>> formatting.format(mny, "h")
    '2.99'
    >>> formatting.format(mny, "n")
    '2.99 US Dollars'

Note that :meth:`~Money.__format__` from :class:`Money` calls
the :meth:`formatting.format` method on a preconfigured global formatter.

There are two levels for formatting configuration options.

* Formatting at :mod:`~isomoney.formatting` package level:
    The method :meth:`formatting.basicConfig` let's you configure:
        * the local to use,(Ignored when using the default backend formatter)
        * The precision limit when displaying currencies
          (default to the currency's minor unit),
        * the rounding mode when displaying in compact format
          (The default is to round half even)
        * Whether to omit non signicant zeros or not (Default is True).

    Examples:
        >>> mny = Money.from_major(2.00, "USD")
        >>> formatting.format(mny, "")
        2 USD
        >>> formatting.basicConfig(omit_trailing_zeros=False)
        >>> formatting.format(mny, "")
        2.00 USD
        >>> formatting.basicConfig(precision=4)
        >>> formatting.format(mny, "")
        2.0000 USD

* Formatting at the backend level:
    Every formatter provide a `configure` method. This let's you
    controls the default behavior of :meth:`formatting.format` when called
    with an empty format spec.

    Examples:
        >>> formatting.get_formatter().configure(compact=True)
    def configure(
            self,
            *,
            compact: bool = False,
            accounting: bool = False,
            group_separator: bool = True,
            ccy_display: Display = "symbol",

"""

from ._default import (
    available_backends,
    basicConfig,
    current_backend,
    format,
    get_formatter,
    register,
    register_backend,
    use_backend,
)
from .moneyformat import MoneyFormat

__all__ = [
    "basicConfig",
    "MoneyFormat",
    "format",
    "use_backend",
    "get_formatter",
    "available_backends",
    "current_backend",
    "register_backend",
    "register",
]
