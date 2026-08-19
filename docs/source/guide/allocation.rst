.. _guide-allocation:

==========
Allocation
==========

The allocating method in the ``Money`` class is kept at its bare minimum.
The core of the method is to divide the money exactly according
to the ratios and return equal shares along with leftover money all packed
in a dedicated type ``AllocationResult``.

The reason **Apportionment**

.. code-block:: python

    >>> mny = Money.from_major(100, "USD")
    >>> shares, leftover = mny.allocate()
    >>> print(", ".join(str(share) for share in shares))
    16.66 USD, 33.33 USD, 50.00 USD
    >>> print(leftover)
    0.01 USD

.. note::

    If you need to divide the money equally into n parts, instead of
    calling allocate with a list of equal ratios, you can use ``divmod(money, n)``.
    This method returns a tuple of the equal shares, and the remainder.


Realistic example
-----------------

For example, imagine a furniture manufacturing company has three assembly line stages in
its wooden furniture manufacturing process:

* Cutting Wood
* Assembly
* Prime & Paint


Largest Fractional Remainder (The Hamilton Method)
--------------------------------------------------

.. code-block:: python

    def hamilton(ratios):
        pass # implementation omitted

This is considered the mathematically "fairest" approach and is widely
used in corporate finance and voting systems (like the Hare-Niemeyer method).

* You calculate the exact unrounded mathematical share for everyone.
* Everyone gets the base integer value of their share.
* You look at the decimal leftovers of everyone's exact share.
  The remaining pennies are handed out one-by-one to the parties with
  the highest decimal remainders.


Largest Share (The "Whale" Absorber)
------------------------------------

The remaining pennies are given to the party (or parties) that received the largest initial allocation.

* **Rationale:** A one-cent variance is mathematically least significant to
  the person receiving the largest amount. A penny added to a $1,000 share
  changes the ratio far less than a penny added to a $0.05 share.


Sequential / Round-Robin (Index Order)
--------------------------------------

You distribute the remainder one penny at a time starting from the very first person in the list,
then the second, and so on, until the remainder is exhausted.

* **Rationale:** It is perfectly deterministic and requires no complex sorting.
  It is often used when dividing a bill equally among peers where mathematical
  precision matters less than execution speed.


The Last Bucket (The "Sweep" Method)
------------------------------------

All remainder pennies are aggregated and dumped onto the very last party in the array.

* **Rationale:** Often, the final party in an allocation is the house,
  the tax authority, or the merchant. It acts as the final balancing
  entry to ensure the ledger equals zero.


The Suspense Account (Dust Sweeping)
------------------------------------

The leftover pennies are not distributed to any of the ratio participants.
Instead, the exact base integer amounts are allocated, and the remainder is
routed to a dedicated internal corporate ledger account (often called a "Rounding Variance",
"Suspense", or "Dust" account).

* **Rationale:** Strictly enforces that no party receives a fraction of a percent more than
  their exact contractual ratio. The business absorbs the rounding variance.


Random Allocation
-----------------

The pennies are distributed entirely at random among the participants.

* **Rationale:** In high-frequency environments (like ad-tech bidding or micro-dividend distribution),
  deterministic strategies (like Round-Robin or Largest Share) can introduce systemic
  bias over millions of transactions. Random allocation ensures statistical fairness
  over the long term.


Smallest Share
--------------

The inverse of your mentioned strategy. The extra pennies are given to
the parties with the smallest base allocation.

* **Rationale:** Rarely used in strict accounting, but sometimes used in equity distributions
  or progressive subsidy logic to favor minority stakeholders.


References
----------

* `Understanding Apportionment in Insurance, Real Estate & More <https://www.investopedia.com/terms/a/apportionment.asp>`_
* `7 Methods of Cost Allocation in Accounting <https://www.costperform.com/7-methods-of-cost-allocation-in-accounting/>`_
