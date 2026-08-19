![Isomoney Logo](./assets/logo3.svg)

![Tests](https://github.com/ckalandk/isomoney/actions/workflows/tests.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%20%20%7C%203.14-blue)
![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![codecov](https://codecov.io/gh/ckalandk/isomoney/graph/badge.svg?token=vOH2wc2alW)](https://codecov.io/gh/ckalandk/isomoney)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

# isomoney

**isomoney** is a strongly typed Python library for representing and manipulating monetary
values with ISO 4217-compliant currencies and explicit rounding semantics and rich formatting options.

* **ISO 4217 compliance** — currencies are represented with their standardized codes and minor-unit definitions, while Money uses integer minor units for exact monetary representation.

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

### Pre-1.0, but API-stable

The library is functionally complete and the public API is currently considered stable.
The test suite is comprehensive, and breaking changes are not expected.

The project remains below 1.0.0 intentionally, to allow the API and design to receive feedback from users before the first stable release. Breaking changes may still be introduced before 1.0.0 if feedback reveals opportunities to improve the public API or overall design.

Documentation is still being completed.

Feedback on the API, design, and overall usability is especially welcome at this stage.

## License

isomoney is distributed under the MIT License.
See the [LICENSE](./LICENSE) file for details.
