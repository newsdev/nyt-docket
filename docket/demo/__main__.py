from docket import grants
from docket import slipopinions

o = slipopinions.Load()
o.scrape()

for case in o.cases:
    print case.__dict__

g = grants.Load()
g.scrape()

for case in g.cases:
    print case.__dict__