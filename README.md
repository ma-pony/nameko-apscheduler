Nameko Apscheduler
=================

A [Nameko](http://nameko.readthedocs.org) dependency provider for easy use with [apscheduler](https://github.com/agronholm/apscheduler).

Quick Start
-----------

Install from [PyPI](https://pypi.python.org/pypi/nameko-apscheduler):

    pip install nameko-apscheduler

``` {.sourceCode .python}
# service.py

from nameko.rpc import rpc
from nameko_apscheduler import Scheduler

class Service:

    name = 'example'

    scheduler = Scheduler()

```

Create a config file with essential settings:

``` {.sourceCode .yaml}
# config.yaml

AMQP_URI: 'pyamqp://guest:guest@localhost'
APSCHDULER:
    jobstores:
        default:
            type: sqlalchemy
            url: mysql+mysqlconnector://${DB_USER:root}:${DB_PASS:}@${DB_SERVER:localhost}/${DB_NAME:crm}
    executors:
        default:
            type: threadpool
            max_workers: 20
    job_defaults:
        coalesce: False
        max_instances: 1
        misfire_grace_time: 1
    timezone: UTC
```
