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

Grants are cases that have been granted certiorari and will be heard by
the Court in this term. The most interesting thing about a grant,
besides its existence, is the question the Court will be deciding. This
is associated as a separate PDF file on the Court's site but the parser
attaches it to the case as a text blob.

.. code:: python

    from docket import grants

    g = grants.Load()
    g.scrape()

    for case in g.cases:
        print case.__dict__

Slip opinions (decisions)
~~~~~~~~~~~~~~~~~~~~~~~~~

Slip opinions are decisions in cases the Court has either heard
arguments on or has made a procedural decision on. These opinions are
not final, but it's the fastest way to know when the Court has acted on
a case. The most important feature of a slip opinion is the opinion
text, which is a separate PDF file. This is associated with the opinion
as a hyperlink.

.. code:: python

    from docket import slipopinions

    o = slipopinions.Load()
    o.scrape()

    for case in o.cases:
        print case.__dict__

Orders (all kinds of things)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Orders are the daily business of the Court. Denials of certiorari as
well as various other procedural motions are resolved in the orders
list. This plugin grabs the long orders list itself as a PDF link and
then parses it out into individual cases. WARNING: The individual cases
rely on regex and tomfoolery. The methods for parsing them are fragile,
so YMMV.

.. code:: python

    from docket import orders

    z = orders.Load()
    z.scrape()
    z.parse()

    for order in z.orders:
        print order.__dict__

    for case in z.cases:
        print "%s\t%s\t%s" % (case.docket, case.orders_type, case.casename)
