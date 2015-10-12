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
for o in z.orders:
    print o.__dict__