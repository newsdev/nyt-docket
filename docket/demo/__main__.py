from docket import grants
from docket import orders
from docket import slipopinions

# Load slip opinions.
o = slipopinions.Load()
o.scrape()
for case in o.cases:
    print case.__dict__

# Load new case grants.
g = grants.Load()
g.scrape()
for case in g.cases:
    print case.__dict__

# Load orders of the court.
z = orders.Load()
z.scrape()
z.parse()

# An order contains many cases.
# This is the orders list itself.
for order in z.orders:
    print order.__dict__

# And these are the cases.
for case in z.cases:
    print "%s\t%s\t%s" % (case.docket, case.orders_type, case.casename)