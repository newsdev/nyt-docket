from docket import grants

g = grants.Load()
g.scrape()

for case in g.cases:
    print case.__dict__