=================
Rounding Policies
=================

PyCents provides a collection of rounding policies through the
``RoundingPolicy`` enumeration, defined in the ``pycents.rounding``
module.

.. code-block:: python

    from pycents.rounding import RoundingPolicy

The library uses these policies whenever an operation requires converting
a value that cannot be represented exactly in minor units.


Where rounding policies are used
--------------------------------

``Money.from_major()``
^^^^^^^^^^^^^^^^^^^^^^

When constructing a ``Money`` instance from a decimal value, the input may
contain more fractional digits than the currency supports.

For example, USD supports two fractional digits:

.. code-block:: python

    Money.from_major("12.345", "USD")

In this case, the value must be rounded before constructing the ``Money``
instance. By default, ``RoundingPolicy.HALF_EVEN`` is used, although any
supported rounding policy may be specified explicitly.


``UnroundedMoney.round()``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Multiplication and division by non-integer factors produce an
unrounded result.

Calling ``round()`` converts this result back to a ``Money`` instance
using the specified rounding policy.

.. code-block:: python

    vat = (price * Decimal("0.20")).quantize(
        RoundingPolicy.HALF_UP
    )

If no rounding policy is specified,
``RoundingPolicy.HALF_EVEN`` is used.


Formatting
^^^^^^^^^^

Rounding policies are also required when performing formatting in compact format.
TODO: add link to formatting doc


Available policies
------------------

See the API reference for the complete list of rounding policies provided
by ``RoundingPolicy``.
