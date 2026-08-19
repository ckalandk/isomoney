==========
Formatting
==========

In this section we'll dive deep into how ``ISOMoney`` formatting works.

All formatting is routed through the ``formatting`` module. By default,
``ISOMoney`` uses a locale-agnostic global formatter that produces consistent,
predictable output regardless of the host machine's environment.

You can format a ``Money`` object in two ways: indirectly via Python's built-in
string interpolation, or directly through the formatting API.

The Quick Way: String Interpolation
-----------------------------------
Because ``ISOMoney`` tightly integrates with Python's formatting protocol,
the most idiomatic way to display money is using standard f-strings.

.. code-block:: python

    >>> from isomoney import Money

    >>> mny = Money.from_major("2.99", "USD")
    >>> f"{mny}"
    'USD\xa02.99'

Under the Hood: The Direct API
------------------------------
When you use an f-string, Python implicitly calls ``formatting.format()`` under the hood.
For advanced use cases, you can call this function directly.

.. code-block:: python

    >>> from isomoney import Money, formatting

    >>> mny = Money.from_major("2.99", "USD")
    >>> result = formatting.format(mny, "")
    >>> result
    'USD\xa02.99'

The Global Formatter
--------------------
By default, the ``format`` function delegates the rendering to a globally configured formatter.
The formatting is orchestrated by ``MoneyFormatter`` class, which is responsible for
parsing the format specification string and hand over the datas to the backend formatter,
which will display the final result.

``ISOMoney`` ships with three fully implemented backend formatters. ```StdFormatter`` which
is a locale-agnostic formatter (the default), ``BabelFormatter`` which as its name suggest
use ``babel`` library as backend to format money, and ``IcuFormatter`` which uses the ``PyIcu``
library.

Choosing a backend formatter is a matter of calling a simple function ``use_backend``:abbr:

.. code-block:: python

    from isomoney import Money, formatting
    formatting.use_backend('babel') # Other options are 'std' (the default) and 'icu'.

    mny = Money.from_major("-2.99", "USD")
    print(f"{mny:a}") # Output: ($2.99)

.. note::

    ``babel`` and ``pyicu`` are provided as optional dependencies, installing ``ISOMoney``
    will not install those libraries, you must install them separately.

You can inspect the currently active backend formatter by calling ``formatting.get_formatter()``.

.. code-block:: python

    >>> from isomoney import formatting
    >>> formatter = formatting.get_formatter()
    >>> formatter.backend_name
    'Babel'  # or 'PyICU' depending on your environment

Retrieving the active formatter is essential when your application needs to globally switch locales,
swap backends to support advanced numbering systems (like Eastern Arabic numerals),
or dynamically inject custom formatting specifications.

Global Configuration
--------------------

Every backend formatter in ``ISOMoney`` possesses a ``default_spec``.
This specification is used whenever a ``Money`` object is formatted without explicit
formatting fields (e.g., ``format(mny, "")`` or ``f"{mny}"``).

You can globally override this default behavior—such as enforcing compact notation
or accounting formats across your entire application—using by calling ``configure()``
on the active backend.

.. code-block:: python

    from isomoney import formatting

    # Configure the global default: use compact notation with 2 decimal places
    formatting.get_formatter().configure(compact=True, compact_precision=2)

    # Now, all empty format specs will use this configuration globally
    mny = Money.from_major("1500000", "USD")
    print(f"{mny}")  # Outputs: $1.50M

.. warning::
    **Thread Safety and Global State**

    ``basicConfig()`` and ``configure()`` mutate the global formatting state.
    They are designed to be called **exactly once** during application startup
    (e.g., in ``main.py``, Django's ``settings.py``, or a FastAPI startup event).

    **Never call these methods dynamically at runtime**
    (such as inside a web request handler or a background Celery task).
    Modifying the global configuration inside an active thread will cause race conditions,
    immediately overriding the formatting rules for all other concurrent users.

Handling Dynamic Runtime Formatting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need to change formatting dynamically based on user preferences or runtime context,
do not mutate the global default. Instead, use the inline format specification grammar
in your f-strings.

**DON'T do this (Race Condition):**

.. code-block:: python

    def user_dashboard(request):
        # DANGER: Mutates the global formatter for ALL concurrent users!
        if request.user.prefers_accounting_format:
            formatting.get_formatter().configure(accounting=True)

        return f"Balance: {user.balance}"

**DO this (Thread-Safe):**

.. code-block:: python

    def user_dashboard(request):
        # SAFE: The formatting grammar is evaluated locally on the call stack
        if request.user.prefers_accounting_format:
            return f"Balance: {user.balance:a}"  # 'a' flag overrides default_spec

        return f"Balance: {user.balance}"
