![](https://cloud.githubusercontent.com/assets/109988/10271018/de09785a-6ad0-11e5-90d9-f50582d62824.png)

## Getting started
Run the demo app.
```
python -m docket.demo
```

Use the docket loader manually.
```
from docket import grants

g = grants.Load()
g.scrape()

print g.cases
```