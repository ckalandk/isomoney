==================
SubUnit Arithmetic
==================

Addition and subtraction are **safe** operations because they always produce
values that can be represented exactly in the currency's minor units.

Multiplication and division by non-integer factors are different.

.. note::

    The term **unsafe** could be misleading here; there is nothing unsafe
    with these operations, apart from the fact that the amount they carry
    cannot be represented exactly in the currency's minor units. Also,
    I couldn't think of a better name.


For example, dividing one cent by two yields half a cent, which cannot be
represented as a ``Money`` instance.

Rather than silently rounding the result, PyCents returns an intermediate
``Unrounded`` object.

.. code-block:: python

    >>> vat = price * Decimal("0.20")

    >>> type(vat)
    Unrounded(...)

PyCents follows one simple principle:

    **Rounding should always be explicit, and should never be performed internally**

.. important::
    Unrounded type use Decimal internally to hold the result calculation
    as a consequence of that, some intermediate rounding could be performed
    by Decimal, when representing some numbers with more, for example 100/3 can't
    be represented exactly so Decimal round the result, if you want to control
    the type of rounding you can always wrap you arithmetics expression
    with localcontext() as ctx: ctx.rounding = ....#choose you rounding.

Returning an intermediate result allows several arithmetic operations to be
performed before a single rounding step is applied.
The user is responsible for

The results of multiplication/division by a decimal are eagerly evaluated, while
retaining full precision within the limit of Python's ``Decimal`` context.
The rounding is deferred until the user calls ``round()`` explicitly. Either
by supplying an explicit rounding policy argument, or using the default which is
rounding half even.


Performing unsafe arithmetic
----------------------------

Multiplication and division can be chained to form complex expressions:

.. code-block:: python

    >>> result = ((price * Decimal("1.20"))
    ...           / Decimal("3"))


Converting back to ``Money``
----------------------------

Call ``quantize()`` to round the intermediate value and obtain a ``Money``
instance.

.. code-block:: python

    >>> result = (
    ...     (price * Decimal("1.20"))
    ...     / Decimal("3")
    ... ).quantize()

The rounding policy may be specified explicitly.

.. code-block:: python

    >>> result.quantize(RoundingPolicy.HALF_UP)

If omitted, ``RoundingPolicy.HALF_EVEN`` is used.


Design rationale
----------------

Keeping intermediate values unrounded has two important advantages.

Explicit rounding
^^^^^^^^^^^^^^^^^

No rounding is ever performed implicitly.

Users always decide **when** rounding occurs and **which** rounding policy
should be used.


Better numerical behaviour
^^^^^^^^^^^^^^^^^^^^^^^^^^

Several unsafe operations may be chained before a single rounding step is
applied.

This generally produces more accurate results than rounding after every
operation.

Take this pricing calculation for example:

.. code-block:: python

    from decimal import Decimal
    from pycents import Money

    # JPY has 0 minor units, meaning final amounts must be integers.

    chair = Money.from_major(101, "JPY")
    desk = Money.from_major(104, "JPY")

    tax = Decimal("1.10")

    chair_taxed = chair * tax    # 111.10 JPY
    desk_taxed = desk * tax      # 114.40 JPY

    # APPROACH A: Rounding at the end (Recommended)
    # 111.10 + 114.40 = 225.50 -> rounds half even up to 226 JPY
    total_amount = (chair_taxed + desk_taxed).quantize()

    # APPROACH B: Rounding at each step (Loses precision)
    # 111 (from 111.10) + 114 (from 114.40) -> 225 JPY
    total_amount2 = chair_taxed.quantize() + desk_taxed.quantize()


.. important::

    **Always perform rounding by calling ``quantize()`` at the final stage of unsafe operations.**


Precision guarantees
--------------------

Unsafe arithmetic relies on Python's ``Decimal`` type.

Within the practical precision limits of the active decimal context, the
following identities are preserved:

* ``(money * a) * b == money * (a * b)``
* ``((money / a) * a).quantize() == money``

Very large monetary amounts or factors with excessive precision may exceed the
active decimal context, causing ``Decimal`` to round intermediate values. In such cases,
these identities are no longer guaranteed.


Tips
----
