.. _guide-allocation:

==========
Allocation
==========

.. warning::
   **Under Construction**

   This section is currently under heavy development.
   For now, please refer to the Quickstart guide or check the source code directly!

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

This is exactly where an apportionment strategy (also called an allocation strategy) comes into play.

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


References
----------

* `Understanding Apportionment in Insurance, Real Estate & More <https://www.investopedia.com/terms/a/apportionment.asp>`_
* `7 Methods of Cost Allocation in Accounting <https://www.costperform.com/7-methods-of-cost-allocation-in-accounting/>`_
