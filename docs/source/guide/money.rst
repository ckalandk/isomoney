=====
Money
=====

.. warning::
   **Under Construction**

   This section is currently under heavy development.
   You can still read this section, but some parts are missing or not fully explained.

The ``Money`` class represents a monetary amount expressed in a specific ISO 4217 currency.

A ``Money`` instance combines two pieces of information:

* a monetary amount stored internally in **minor units** (for example, cents) which is
  stored internally as an `int`,
* a currency represented by a ``Currency`` instance.


Immutability
------------

``Money`` objects are immutable.

Every arithmetic operation returns a new instance.

.. code-block:: python

    >>> wallet = Money.from_major("10.00", "USD")
    >>> id1 = id(wallet)
    >>> wallet += Money.from_major("5.00", "USD")
    >>> id2 = id(wallet)
    >>> assert id1 != id2


Creating money
--------------

From minor units using ``Money`` constructor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Creating a ``Money`` instance using the constructor requires instantiating
a ``Currency`` object explicitly, either by using its constructor with
a ``Ccy`` enum, or ``Currency.from_code()`` with a ``Ccy`` enum or code string.

.. code-block:: python

    from pycents import Money, Currency, Ccy
    >>> price = Money(1999, Currency(Ccy.USD))
    >>> print(price)
    USD 19.99
    >>> price = Money(1999, Currency.from_code("USD"))
    >>> print(price)
    USD 19.99

``Currency`` instances are cached internally for subsequent use.

.. note::

    ``Currency`` contains other standard informations that you might find
    useful. See the API documentation for [#TODO reference to Currency API doc].


From major units
^^^^^^^^^^^^^^^^

Use ``Money.from_major()`` when constructing money in major units from decimal values.
This method accepts either an ``int``, ``str`` or a ``Decimal``.

.. code-block:: python

    >>> from decimal import Decimal

    >>> salary = Money.from_major(
    ...     Decimal("3500.75"),
    ...     "USD",
    ... )
    >>> salary = Money.from_major("3500.75", "USD")
    >>> salary = Money.from_major(3500, "USD")
    >>> print(salary)
    USD 3500.75


The value is converted to minor units according to the currency's
number of decimal places.

The class method ``from_major`` accepts an optional third keyword argument that
represents the rounding mode to apply when the money amount has more fractional digits
than the currency supports. If omitted, the rounding policy defaults to **round half even**.

The Rounding Policies are provided through the enum ``RoundingPolicy``
from the ``pycents.rounding`` package. See :doc:`/guide/rounding`.

.. code-block:: python

    # USD Supports only two fractional digits
    >>> from pycents.rounding import RoundingPolicy

    >>> price = Money.from_major(150.756, "USD")
    >>> print(price)
    USD 150.76
    >>> price = Money.from_major(150.754, "USD", rounding=RoundingPolicy.DOWN)
    >>> print(price)
    USD 150.75


ZERO Monetary amount
^^^^^^^^^^^^^^^^^^^^

Whenever you need a `Money` instance with zero amount, prefer using
the classmethod `zero` to enable caching

.. code-block:: python

    from pycents import Money, Currency

    # zero1 will be cached internally
    zero1 = Money.zero("USD")

    # using from_major with a zero amount, will return
    # the cached value if present
    zero2 = Money.from_major(0, "USD")
    assert zero2 is zero1

    # Using Money Constructor bypasses the cache
    zero3 = Money(0, Currency.from_code("USD"))
    assert zero3 is not zero1

Arithmetic
----------

``PyCents`` categorizes arithmetic operations into two types:

* **Minor-Unit arithmetic operations**
* **Sub-Unit arithmetic operations**


Minor-Unit arithmetics
^^^^^^^^^^^^^^^^^^^^^^

Operations whose results amount natively fit inside the standard
currency's minor units. This type of operations produce a ``Money`` instance.

.. note::

    Some operations naturally yield a valid amount; for example,
    adding $19.12 and $15.12 yields $34.24, which already satisfies the "USD"
    currency minor units without needing any rounding.


List of all the Minor-Unit operations
"""""""""""""""""""""""""""""""""""""

* **Addition/Subtraction**

  Adding/Subtracting two ``Money`` objects are Minor-Unit operations:

  .. code-block:: python

      >>> salary = Money.from_major(2500, "USD")
      >>> bonus = Money.from_major(50.55, "USD")
      >>> total = salary + bonus
      >>> assert type(total) is Money

      >>> price = Money.from_major(12.99, "USD")
      >>> discount = Money.from_major(2, "USD")
      >>> final_price = price - discount
      >>> assert type(final_price) is Money


* **Multiplication by an integer factor**

  Multiplying a ``Money`` instance by an ``int`` returns another ``Money`` instance.

  .. code-block:: python

      >>> unit_price = Money.from_major(12.99, "USD")
      >>> number_of_items = 15
      >>> total_price = unit_price * number_of_items
      >>> assert type(total_price) is Money

* **Negation**

  .. code-block:: python

      >>> -balance

  returns a new ``Money`` instance with the opposite sign.

* **abs**

.. code-block:: python

    >>> mny = Money.from_major("-299", "USD")
    >>> print(abs(mny))
    USD 299.00

Sub-Unit arithmetics
^^^^^^^^^^^^^^^^^^^^

Operations that introduce fractional minor units and preserve sub-unit precision.

This type of operations do not produce an actual ``Money`` instance. ``PyCents``
uses a special type ``UnroundedMoney`` to hold the result of this type of operations,
maintaining the full precision of the calculation while ignoring completely
the currency's standard minor units.

Consider for example the case where we have a salary of **$1500.45**, and we need to apply
a bonus of **30%**. Multiplying **1500.45** by **1.3** yields **1950.585** which has more
fractional digits than the **USD** currency supports. In simple terms, **1950.585** is not
a valid ISO **USD** monetary amount!

In order to get an actual valid money, you need to call a special method on an ``UnroundedMoney``
instance, namely: ``round()``. Either by supplying a **rounding mode** as an argument, or use
the default rounding mode **round half even**.

.. code-block:: python

    >>> salary = Money.from_major(1500.45, "USD")
    >>> bonified_salary = (salary * 1.3).round() # round half even
    >>> print(bonified_salary)
    USD 1950.58

Arithmetic rules:
^^^^^^^^^^^^^^^^^

Arithmetic operations work according to this rules
(we'll abbreviate UnroundedMoney to Unrounded):

.. code-block:: text

    Money + Money = Mone
    Money - Money = Money
    Money + Unrounded = Unrounded
    Unrounded + Unrounded = Unrounded
    Money * IntegerFactor = Money
    Money * DecimalFactor = Unrounded
    Money / Factor = Unrounded
    Money / Money = Decimal
    Unrounded * factor = Unrounded

Converting an `UnroundedMoney` instance to `Money` via the `round` method,
must be performed at the very end of the arithmetic pipeline.

.. warning::

    Although no implicit rounding is performed at the library level, python
    Decimal might still implicitly round when the amount exceed the Decimal
    default precision. Consider the case where you need to multiply a `Money`
    instance by the Decimal `Decimal(1)/3`, since this number has infinite
    decimals, it will be rounded to fit within the Decimal default precision.
    If you need tight control over what rounding mode is used by python Decimal, or
    completely rejects this implicit rounding, consider wrapping any arithmetics involving
    `UnroundedMoney` objects within a  `decimal.localcontext` context manager. See the example
    below:

.. code-block:: python

    from pycents import Money
    from pycents.rounding import RoundingMode, as_decimal_rounding
    from decimal import Decimal, localcontext

    mny = Money.from_major(10, "USD")
    with localcontext() as ctx:
        ctx.rounding = as_decimal_rounding(RoundingMode.UP)
        factor = Decimal(3)
        unr = mny / factor
        print(unr)

.. danger::
    Whenever a number is involved be it in arithmetic operations or methods (like `Money.from_major`),
    PyCents use either an `int` when it is appropriate, an `str` representing an exact decimal number
    or a python Decimal as an argument, but never use `floats`. if you use `float` as an argument, the type checker will
    scream at you, but the code will run without any errors. PyCents doesn't enforce the ban on `float`, but
    you must be aware that you should never use `floats` in financial/accounting softwares!

Bulk summation
^^^^^^^^^^^^^^

If you find yourself doing a lot of summation inside a tight loop, consider
using `Money.sum` classmethod to perform a bulk summation which is more efficient
then a loop.

.. code-block:: python

    from decimal import Decimal
    from pycents import Money, UnroundedMoney, RoundingMode

    items = [
        {"name": "item1", "price": "249.99", "discount": "0.15"},
        {"name": "item2", "price": "119.50", "discount": "0.0"},
        {"name": "item3", "price": "389.00", "discount": "0.10"},
        {"name": "item4", "price": "12.99", "discount": "0.0"},
        {"name": "item5", "price": "89.99", "discount": "0.20"},
        {"name": "item6", "price": "199.95", "discount": "0.05"},
        {"name": "item7", "price": "149.00", "discount": "0.0"},
        {"name": "item8", "price": "24.50", "discount": "0.0"},
        {"name": "item9", "price": "34.99", "discount": "0.125"},
        {"name": "item10", "price": "59.99", "discount": "0.0"},
    ]

    prices = [Money.from_major(item["price"], "USD") for item in items]
    prices_after_discounts = [
        mny - mny * Decimal(item["discount"]) for mny, item in zip(prices, items)
    ]

    # `total` is either a `Money` or a `UnroundedMoney` instance
    # You can, either supply a rounding mode via the keyword argument `rounding`
    # to get a Money instance

    total = Money.sum(prices_after_discounts, rounding=RoundingMode.UP)
    assert isinstance(total, Money)

    print(total) # Output: USD 1221.14
    # If you don't provide a rounding mode the result will be an
    # `UnroundedMoney` instance if there is at least one `UnroundedMoney`
    # instance in the provided list, or a `Money` object otherwise

    total = Money.sum(prices_after_discounts)
    assert isinstance(total, UnroundedMoney)

    # At this stage you can carry on with any remainding calculation
    # or round the result to get a `Money` instance
    final_price = total.round()
    print(final_price) # Output: USD 1221.14

Comparison
----------

Money/Unrounded objects support the standard comparison operators.

.. code-block:: python

    >>> wallet > savings
    >>> wallet == savings
    >>> wallet <= savings

Comparisons are only valid between identical currencies.
Attempting to compare different currencies raises ``MismatchCurrencyError``.

.. warning::

    You cannot directly compare `Money` and `UnroudedMoney` objects, doing
    so will raise a `TypeError` exception. You need to convert the Unrounded object
    to `Money` instance before trying to compare them.


Design guarantees
-----------------

PyCents provides the following guarantees:

* ``Money``, ``UnroundedMoney`` objects are immutable.
* Addition and subtraction are mathematically correct; (Money, +) is
  a commutative group.
* Sub-Unit arithmetic operations (multiplication and division by non-integer
  factors) preserve the standard algebraic identities, such as:

  - ``(money * a) * b == money * (a * b)``
  - ``((money / a) * a).round() == money``

  provided the operands remain within the practical precision limits of
  Python's ``Decimal`` arithmetic.
* Monetary values are represented internally using integer minor units.
