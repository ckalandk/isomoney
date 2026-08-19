=============================
References & Further Reading
=============================

Building financial software requires strict adherence to international standards and numerical precision. Below is a curated list of standards, design patterns, and technical resources that influenced the design of ISOMoney.

International Standards
-----------------------

* **ISO 4217 Currency Codes:** The international standard describing three-letter codes (like USD, EUR, JPY) and numeric codes for currencies. ISOMoney enforces these specifications.

  * `Official ISO 4217 Documentation <https://www.iso.org/iso-4217-currency-codes.html>`_
  * `Wikipedia: ISO 4217 <https://en.wikipedia.org/wiki/ISO_4217>`_

* **Unicode CLDR (Common Locale Data Repository):** The standard providing locale-specific data for formatting monetary values, including currency symbols, grouping separators (commas vs. periods), and placement.

  * `CLDR Project Home <https://cldr.unicode.org/>`_
  * `CLDR Currency Formatting Charts <https://unicode.org/cldr/charts/latest/summary/root.html#Numbers>`_

Software Engineering Patterns
-----------------------------

* **The "Money" Pattern by Martin Fowler:** The foundational enterprise software pattern for representing monetary values. It dictates that money should be represented as an object consisting of a numeric amount and a currency, preventing the accidental mixing of different currencies.

  * `Enterprise Application Architecture: Money <https://martinfowler.com/eaaCatalog/money.html>`_

* **Falsehoods Programmers Believe About Prices:** A great read on the edge cases of financial software, explaining why naive assumptions about money usually lead to critical bugs.

  * `Falsehoods about Prices <https://github.com/kdeldycke/awesome-falsehood#money>`_

Precision and Arithmetic
------------------------

* **Why not use Floats for Money?** ISOMoney relies strictly on Python's ``decimal.Decimal``. Using standard IEEE 754 floating-point math for financial calculations introduces rounding errors (e.g., ``0.1 + 0.2 = 0.30000000000000004``).

  * `0.30000000000000004.com <https://0.30000000000000004.com/>`_
  * `Python Decimal FAQ <https://docs.python.org/3/library/decimal.html#floating-point-notes>`_

* **Banker's Rounding (Round Half to Even):** The default rounding mode used in most financial contexts and by ISOMoney. It rounds to the nearest value, but rounds halfway values to the nearest *even* number, which prevents statistical bias in large datasets.

  * `Wikipedia: Rounding (Round half to even) <https://en.wikipedia.org/wiki/Rounding#Round_half_to_even>`_
