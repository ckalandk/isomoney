"""
Formatting support for ISOMoney.

The :mod:`isomoney.formatting` module provides the default formatting
interface for monetary values.

Examples:
    >>> from isomoney import Money, formatting
    >>> mny = Money.from_major(2.99, "USD")
    >>> formatting.format(mny, "")
    'USD 2.99'
    >>> print(f"{mny}")
    USD 2.99
    >>> formatting.format(mny, "n")
    '2.99 US Dollar'
    >>> print(f"{mny:n}")
    2.99 US Dollar

The ``format`` method uses the default local agnostic formatter
to format monetary values according to the format specification.
See :py:meth:`isomoney.money.Money.__format__` for a complete
description of the format spec language.

ISOMoney supports different local aware backend formatters.
To find the available backend formatters use :func:`available_backends`.
The active formatting backend can be changed with :func:`use_backend`.


Note:
    Ensure that the backend is installed beforehand.
    PyICu and babel are provided as optional dependencies

Examples:
    >>> from isomoney import formatting
    >>> formatting.use_backend("icu") # or "babel"
    >>> formatting.basicConfig(local="en_US")
    >>> mny = Money.from_major(2.99, "USD")
    >>> formatting.format(mny, "")
    '$2.99'
    >>> formatting.format(mny, "h")
    '2.99'
    >>> formatting.format(mny, "n")
    '2.99 US Dollars'

Note that :meth:`~Money.__format__` from :class:`Money` calls
the :func:`~formatting.format` function on a preconfigured global formatter.

There are two levels for formatting configuration options.

* Formatting at :mod:`~isomoney.formatting` package level:

    The method :func:`~formatting.basicConfig` let's you configure:

    * the local to use,(Ignored when using the default backend formatter)
    * the rounding mode when displaying in compact format
      (The default is to round half even)

* **Formatting at the backend level**:

    Every formatter provide a `configure` method. This let's you
    controls the default behavior of :meth:`formatting.format` when called
    with an empty format spec.

    Examples:
        >>> formatting.get_formatter().configure(compact=True)

    Now everytime you call `formatting.format` with an empty format spec
    the compact format will be used.
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
from .moneyformat import MoneyFormatter

__all__ = [
    "basicConfig",
    "MoneyFormatter",
    "format",
    "use_backend",
    "get_formatter",
    "available_backends",
    "current_backend",
    "register_backend",
    "register",
]
