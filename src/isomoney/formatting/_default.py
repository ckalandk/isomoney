from collections.abc import Callable
from typing import Any, TypeVar

from isomoney.rounding import RoundingPolicy

from .moneyformat import MoneyFormat
from .protocols import CcyFormatter, _SupportMoneyOperation
from .std_formatter import StdFormatter


def _create_icu_formatter() -> CcyFormatter:
    try:
        from .pyicu import IcuFormatter

        return IcuFormatter()
    except ImportError as exc:
        raise ImportError("The 'icu' backend requires the PyICU package.") from exc


def _create_babel_formatter() -> CcyFormatter:
    raise NotImplementedError(
        "The 'babel' backend is not yet implemented. "
        "Please use the 'icu' or 'std' backend instead."
    )


_BACKENDS = {
    "std": lambda: StdFormatter(),
    "icu": _create_icu_formatter,
    "babel": _create_babel_formatter,
}

_default = MoneyFormat(formatter=StdFormatter())


def format(money: _SupportMoneyOperation, format_spec: str) -> str:
    return _default.format(money, format_spec)


def basicConfig(
    *, locale:str,
    precision: int=2,
    rounding: RoundingPolicy=RoundingPolicy.HALF_EVEN,
    omit_trailing_zeros: bool=True
) -> None:
    _default.backend_formatter.locale = locale
    _default.precision = precision
    _default.rounding = rounding
    _default.omit_trailing_zeros = omit_trailing_zeros


def get_formatter() -> CcyFormatter:
    return _default.backend_formatter


def available_backends() -> list[str]:
    return list(_BACKENDS.keys())


def current_backend() -> str:
    return _default.backend_formatter.__class__.__name__


def use_backend(backend_formatter: CcyFormatter) -> None:
    _default.backend_formatter = backend_formatter


def register_backend(name: str, factory_function: Callable[[], CcyFormatter]) -> None:
    if not callable(factory_function):
        raise ValueError("The factory_function must be callable.")
    _BACKENDS[name] = factory_function


T = TypeVar("T", bound=CcyFormatter)


def register(name: str | None = None, **kwargs: Any) -> Callable[[type[T]], type[T]]:
    def inner_decorator(cls: type[T]) -> type[T]:
        _name = name if name is not None else cls.__name__.lower()
        register_backend(_name, lambda: cls(**kwargs))
        return cls

    return inner_decorator
