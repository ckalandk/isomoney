.. _guide-allocation:

==========
Allocation
==========

We introduced briefly in the quickstart guide through an example the concept of **allocation**,
in this guide we will explore in much more depth other aspect of the ``allocation`` module.

But first let's explain what allocation is and what problem it solve.

What is Money Allocation?
-------------------------

In finance, **allocation** is the process of splitting a discrete monetary amount
accross multiple parties according to a set of ratios, percentages, or weights.

Before we look at the technical challenges, here are a few everyday scenarios where allocation
is required:

* **By Percentage (Taxes and Fees)**: You process a cart checkout for $150.00 and need to allocate
  exactly 20% to VAT, 5% to the payment gateway fee, and 75% to the merchant's revenue.

* **Profit Sharing**: Divide profits or an acquisition payout of a company among founders
  according to their original equity shares.

* **Cost allocation**: A logistic company charges a $500 flat shipping fee for
  a container holding three different products. The cost might be divided across
  the three products based on their physical weights.

The Lost Penny Problem:
-----------------------

Consider dividing $100.00 invoice equally among 3 clients, this invoice represent
exactly $10000 in minor units (cents), and it is important to use minor units here
to better undestand the problem.
How would you divide this 10000 cents into 3 equal parts?
The naive approach is to divide the invoice by 3 to determine the exact share
of each client:

* **Exact share** = 10000 / 3 = 3333.3333...

The problem here is that 0.33.. cent is not a real monetary amount!
We cannot divide 1 cent.

The obvious solution is to round down the shares to the nearest integer. In our
example, everyone we'll be charged exactly 3333 cents after rounding.
This is called the **base share**. But if you add all the base shares you will get 9999 cents,
not 10000 cents. So the ultimate question is who will paye the missing cent?


Apportionment and Allocation
----------------------------

This is exactly where an apportionment strategy (also called an allocation strategy)
comes into play.

.. note::

   In the context of this library, the terms "allocation" and "apportionment"
   mean exactly the same thing and are used interchangeably.

An apportionment strategy is the mathematical algorithm used to distribute those
unallocated leftover cents (the remainder), based on some criterias, among the parties
so that the final total matches the original amount perfectly.
In our example, the algorithm decides which of the three clients gets
charged 3,334 cents instead of 3,333 cents.

.. note::

   Interestingly, these algorithms didn't originate in banking, they started in politics!
   you can read more about it `here <https://en.wikipedia.org/wiki/Mathematics_of_apportionment>`_.


PyCents provide two built-in apportionment strategies:

* **Hamilton Method** (Largest Remainder): Calculates each recipient's exact fractional
  share and assigns the integer base amount. Leftover cents are then distributed one by
  one to the recipients with the **largest fractional remainders**.

* **Round-Robin Method**: Distributes leftover cents sequentially in order.

Hamilton Strategy Example
~~~~~~~~~~~~~~~~~~~~~~~~~

This is the default apportionment strategy used in the ``allocate`` function.
We'll pick up the same example used in the QuickStart guide:

.. code-block:: python

    from pycents import allocation as alloc
    from pycents import Money

    rent = Money.from_major(100_000, "USD")
    ratios = [1000, 2000, 3000]

    allocation_result = alloc.allocate(rent, ratios)

    print(", ".join(str(share) for share in allocation_result))
    # Output: USD 16666.67, USD 33333.33, USD 50000.00

Round-Robin Strategy Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With the Round-Robin strategy, leftover cents are assigned sequentially starting from a given index:

.. code-block:: python

    from pycents import Money
    from pycents import allocation as alloc

    total = Money.from_major(1, "USD")

    # Distribute leftover cents sequentially starting at recipient 0
    shares = allocate(
        total,
        ratios=[1, 1, 1],
        strategy=alloc.round_robin
    )

    print(", ".join(str(share) for share in shares))
    # USD 0.34, USD 0.33, USD 0.33

Extracting Base Shares with ``allocate_base``
---------------------------------------------

While ``allocate()`` automatically distributes leftover cents back to the recipients,
``allocate_base()`` stops before the apportionment phase.
It calculates each party's exact floor share and exposes the remaining unallocated
money separately.

It returns a tuple containing:

1. A list of ``Money`` instances representing the base shares.
2. A single ``Money`` instance representing the unallocated remainder.

.. code-block:: text

    (base_shares, remainder)

Example: Sweeping Account
~~~~~~~~~~~~~~~~~~~~~~~~~

A common financial pattern is allocating exact base amounts to sub-accounts and "sweeping"
the unallocated remainder into a central holding or reserve account rather than distributing
it among parties:

.. code-block:: python

    from pycents import Money
    from pycents.allocation import allocate_base

    total = Money.from_major("1", "USD")

    # Allocate base shares for a 1:1:1 split across 3 accounts
    account_shares, sweep_remainder = allocate_base(total, ratios=[1, 1, 1])

    print("Sub-account Shares:", f'{[", ".join(str(share) for share in shares)]}')
    # Sub-account Shares: ['USD 0.33, USD 0.33, USD 0.33']

    print("Swept to Reserve:", sweep_remainder)
    # Swept to Reserve: USD 0.01 (1 cent)

Working with Decimal and Percentage Ratios
------------------------------------------

``allocate()`` and ``allocate_base()`` require integer ratios.
If your allocation weights are expressed as decimals, floats, or percentages
(e.g., 12.5%, 37.5%, and 50.0%), you must scale or normalize them to integers
before passing them to the function.

Normalizing Decimals
~~~~~~~~~~~~~~~~~~~~

To convert decimal weights into valid integer ratios, multiply each ratio by a power
of 10 large enough to remove all fractional parts:

.. code-block:: python

    from decimal import Decimal
    from pycents import Money, allocation

    total = Money.from_major("100.00", "USD")

    # Target allocation percentages: 12.5%, 37.5%, 50.0%
    decimal_weights = [Decimal("12.5"), Decimal("37.5"), Decimal("50")]

    # Scale by 1,000 to eliminate decimals -> [125, 375, 500]
    integer_ratios = [int(w * 10) for w in decimal_weights]

    shares = allocate(total, ratios=integer_ratios)

Allocating with Named Accounts (Dictionaries)
---------------------------------------------

When working with keyed structures like dictionaries (mapping accounts, categories, or clients to weights), pass the dict values into ``allocate()`` or ``allocate_base()`` and combine the results back using ``zip()``.

Because Python 3.7+ dictionaries strictly preserve insertion order, re-pairing keys with allocated shares is completely safe and deterministic.

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

    from pycents import Money, allocate

    total = Money("100.00", "USD")

    account_ratios = {
        "reserve_fund": 2,
        "operations": 1,
        "tax_vault": 1,
    }

    # Extract values, allocate, and zip back into a dict
    allocated_budget = dict(
        zip(
            account_ratios.keys(),
            allocate(total, ratios=list(account_ratios.values())),
        )
    )

    print(allocated_budget)
    # {
    #     "reserve_fund": Money("50.00", "USD"),
    #     "operations": Money("25.00", "USD"),
    #     "tax_vault": Money("25.00", "USD")
    # }

Custom Apportionment Strategies
-------------------------------

In ``pycents``, an apportionment strategy is any callable matching the
``Apportionment`` type signature:

.. code-block:: python

    Callable[[int, Sequence[int]], list[int]]

You can implement custom remainder logic by writing a function that accepts the total amount
in minor units (as an integer) and a sequence of integer ratios, and returns a list of
integer shares summing **exactly** to the original amount.

Creating a Custom Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example defines a **Random Apportionment** strategy.
It calculates the base integer shares and then randomly selects eligible recipients
to receive the unallocated leftover units:

.. code-block:: python

    import random
    from collections.abc import Sequence
    from pycents import Money, allocation

    def random_apportionment(amount: int, ratios: Sequence[int]) -> list[int]:
        total_ratio = sum(ratios)
        leftover = amount
        results = []

        # Calculate base integer shares
        for ratio in ratios:
            share = (amount * ratio) // total_ratio
            leftover -= share
            results.append(share)

        # Collect indices of recipients with non-zero ratios
        eligible_indices = [i for i, ratio in enumerate(ratios) if ratio != 0]

        # Randomly select recipient indices for the remaining leftover cents
        chosen_indices = random.sample(eligible_indices, k=leftover)
        for idx in chosen_indices:
            results[idx] += 1

        return results

    # Usage with allocate()
    total = Money(100, Currency.from_code("USD")) # 100 cents

    shares = allocate(
        total,
        ratios=[1, 1, 1],
        strategy=random_apportionment,
    )

    print(shares)
    # E.g., [Money(33, 'USD'), Money(33, 'USD'), Money(34, 'USD')]
