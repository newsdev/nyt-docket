from docket import grants

g = grants.Load()
g.scrape()

print g.cases