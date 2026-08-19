=====
Money
=====

The ``Money`` class represents a monetary amount expressed in a specific ISO 4217 currency.

A ``Money`` instance combines two pieces of information:

* a monetary amount stored internally in **minor units** (for example, cents),
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

    from isomoney import Money, Currency, Ccy
    >>> price = Money(1999, Currency(Ccy.USD))
    >>> print(price)
    USD 19.99
    >>> price = Money(1999, Currency.from_code("USD"))
    >>> print(price)
    USD 19.99

The example above represents **1999 cents**, or **19.99 USD**.

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
from the ``isomoney.rounding`` package. See :doc:`/guide/rounding`.

.. code-block:: python

    # USD Supports only two fractional digits
    >>> from isomoney.rounding import RoundingPolicy

    >>> price = Money.from_major(150.756, "USD")
    >>> print(price)
    USD 150.76
    >>> price = Money.from_major(150.754, "USD", rounding=RoundingPolicy.DOWN)
    >>> print(price)
    USD 150.75


Arithmetic
----------

``ISOMoney`` categorizes arithmetic operations into two types:

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


Sub-Unit arithmetics
^^^^^^^^^^^^^^^^^^^^

Operations that introduce fractional minor units and preserve sub-unit precision.

This type of operations do not produce an actual ``Money`` instance. ``ISOMoney``
uses a special type ``Unrounded`` to hold the result of this type of operations,
maintaining the full precision of the calculation while ignoring completely
the currency's standard minor units.

Consider for example the case where we have a salary of **$1500.45**, and we need to apply
a bonus of **30%**. Multiplying **1500.45** by **1.3** yields **1950.585** which has more
fractional digits than the **USD** currency supports. In simple terms, **1950.585** is not
a valid ISO **USD** monetary amount!

In order to get an actual valid money, you need to call a special method on an ``UnroundedMoney``
instance, namely: ``round()``. Either by supplying a **rounding policy** as an argument, or use
the default rounding policy **round half even**.

.. code-block:: python

    >>> salary = Money.from_major(1500.45, "USD")
    >>> bonified_salary = (salary * 1.3).round() # round half even
    >>> print(bonified_salary)
    USD 1950.58

Sub-Unit arithmetics are explained in much more detail in the dedicated section:
:doc:`/guide/subunit_arithmetics`.


Comparison
----------

Money objects support the standard comparison operators.

.. code-block:: python

    >>> wallet > savings
    >>> wallet == savings
    >>> wallet <= savings

Comparisons are only valid between identical currencies.

Attempting to compare different currencies raises ``MismatchCurrencyError``.


Design guarantees
-----------------

IsoMoney provides the following guarantees:

* ``Money`` objects are immutable.
* Addition and subtraction are mathematically correct, (Money, +) is
  a commutative group.
* Sub-Unit arithmetic operations (multiplication and division by non-integer
  factors) preserve the standard algebraic identities, such as:

  - ``(money * a) * b == money * (a * b)``
  - ``((money / a) * a).round() == money``

  provided the operands remain within the practical precision limits of
  Python's ``Decimal`` arithmetic.
* Monetary values are represented internally using integer minor units.
* Rounding is always explicit.
