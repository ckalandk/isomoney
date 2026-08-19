============
Installation
============

IsoMoney supports Python **3.12** and later.


Install from PyPI
-----------------

.. code-block:: bash

    pip install isomoney


Optional formatting backends
----------------------------

IsoMoney provides a locale agnostic lightweight core implementation for formatting money.
Locale-aware currency formatting is available through optional formatting backends.

Babel
^^^^^

.. code-block:: bash

    pip install babel

ICU (PyICU)
^^^^^^^^^^^

.. code-block:: bash

    pip install PyICU

.. warning::

    Babel and PyICU are provided as optional dependencies.
    See the :doc:`User Guide <../guide/formatting>` for more information
    on how to configure a locale-aware formatter backend like ``babel`` or ``icu``.


Next steps
----------

Continue with the :doc:`quickstart`.
