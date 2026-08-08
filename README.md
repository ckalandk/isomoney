![Isomoney Logo](./assets/logo3.svg)

# isomoney

**isomoney** is a strongly typed Python library for representing and manipulating monetary
values with ISO 4217-compliant currencies and explicit rounding semantics.

* **SO 4217 compliance** — currencies are represented with their standardized codes and minor-unit definitions, while Money uses integer minor units for exact monetary representation.

* **Explicit rounding** — monetary rounding is never performed implicitly during arithmetic.
Rounding occurs only when explicitly requested by the application.
(Note: Intermediate arithmetic remains bound by the standard limits of Python's underlying decimal context. See the [Guide] for technical details)."

## Features

* ISO 4217 currency definitions
* Immutable `Money` type
* Precise decimal arithmetic
* Explicit rounding semantics.
* Locale-aware currency formatting
* Pluggable formatting backends
* Custom format specification

## Status

> **⚠️ Work in Progress**
>
> **isomoney** is currently under active development. The public API is **not yet stable** and may change without notice. Documentation, features, and formatting capabilities are still evolving.

## Goals

* Correct monetary arithmetic
* Predictable formatting behavior
* Strong typing
* Backend-independent formatting architecture
* Well-tested, production-quality implementation

## License

License information will be added before the first public release.
