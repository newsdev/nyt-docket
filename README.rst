.. figure:: https://cloud.githubusercontent.com/assets/109988/10271018/de09785a-6ad0-11e5-90d9-f50582d62824.png
   :alt: 

Getting started
===============

::

    pip install nyt-docket

Using nyt-docket
================

Demo app
--------

Run the demo app.

::

    python -m docket.demo

Modules
-------

Use the docket loader manually from within your Python script.

Grants (new cases)
~~~~~~~~~~~~~~~~~~

.. code:: python

    from docket import grants

    g = grants.Load()
    g.scrape()

    for case in g.cases:
        print case.__dict__

Slip opinions (decisions)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from docket import slipopinions

    o = slipopinions.Load()
    o.scrape()

    for case in o.cases:
        print case.__dict__
